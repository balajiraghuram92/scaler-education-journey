"""Ported from api/Services/Exercises/LocalDockerExerciseRunner.cs.

The runner executes untrusted learner code. Every isolation flag below is ported
exactly as the C# passes it; none was relaxed or simplified.

Isolation ledger (C# line -> Python):
- L45-46  Image + Name (`studytracker-exercise-{runId:N}`) -> create_container(image=..., name=...)
- L47     WorkingDir = "/workspace" -> working_dir="/workspace"
- L48-52  Labels com.studytracker.exercise-runner/run-id -> labels={...}
- L53     HostConfig -> create_host_config(...)
- L132    Init = true -> init=True
- L133    AutoRemove = false -> auto_remove=False (explicit removal in finally)
- L134    NetworkMode = "bridge" (java) -> network_mode="bridge"
- L135    Memory = MemoryLimitBytes -> mem_limit=...
- L136    NanoCPUs = NanoCpus -> nano_cpus=...
- L137    PidsLimit = PidsLimit -> pids_limit=...
- L143    NetworkMode = "none" (python, fully offline) -> network_mode="none"
- L147-155 Maven cache volume -> /root/.m2 (java only) -> mounts=[Mount(/root/.m2, volume)]
- (no Cmd/Entrypoint override) -> image ENTRYPOINT runs (runner/*/run.sh)
- L219-227 tar workspace -> /workspace -> put_archive("/workspace", tar)
- L229-242 timeout -> SIGKILL -> kill(signal="SIGKILL")
- L251-257 logs stdout+stderr, no follow/timestamps -> logs(stdout, stderr, follow=False, timestamps=False)
- L277    Surefire at /workspace/target/surefire-reports -> get_archive(same path)
- L336-337 Remove Force=true, RemoveVolumes=false -> remove_container(force=True, v=False)
"""

from __future__ import annotations

import asyncio
import io
import logging
import os
import tarfile
import time
from datetime import timedelta

import docker
import requests.exceptions
from docker.errors import APIError, ImageNotFound, NotFound

from ...settings import ExerciseExecutionSettings, get_settings
from .exercise_execution_exceptions import (
    ExerciseInfrastructureException,
    ExerciseRunnerUnavailableException,
)
from .exercise_execution_models import PreparedExerciseWorkspace, RunnerExecutionResult
from .exercise_manifest_models import ExerciseDefinition, ExerciseRuntimeProfiles

logger = logging.getLogger(__name__)

_SUREFIRE_PATH = "/workspace/target/surefire-reports"


class LocalDockerExerciseRunner:
    def __init__(
        self,
        docker_client: docker.DockerClient | None = None,
        options: ExerciseExecutionSettings | None = None,
    ) -> None:
        self._options = options or get_settings().exercise_execution
        # C# builds the client with a 30s default timeout (Program.cs line 83).
        self._docker_client = docker_client or docker.DockerClient(
            base_url=self._options.docker_endpoint, timeout=30
        )

    @property
    def _api(self):  # type: ignore[no-untyped-def]
        return self._docker_client.api

    async def run_async(self, workspace: PreparedExerciseWorkspace) -> RunnerExecutionResult:
        started = time.perf_counter()
        container_name = f"studytracker-exercise-{workspace.run_id.hex}"
        container_id: str | None = None
        timed_out = False
        runner_image = self._resolve_runner_image(workspace.definition)

        try:
            await asyncio.to_thread(self._ensure_runner_image, runner_image)

            def _create() -> dict:
                return self._api.create_container(  # type: ignore[no-untyped-call]
                    image=runner_image,
                    name=container_name,
                    working_dir="/workspace",
                    labels={
                        "com.studytracker.exercise-runner": "true",
                        "com.studytracker.run-id": workspace.run_id.hex,
                    },
                    host_config=self._build_host_config(workspace.definition),
                )

            created = await asyncio.to_thread(_create)
            container_id = created["Id"]

            tar_bytes = _tar_directory(workspace.path)
            await asyncio.to_thread(
                self._api.put_archive, container_id, "/workspace", tar_bytes
            )
            await asyncio.to_thread(self._api.start, container_id)

            timeout = self._get_execution_timeout(workspace.definition)
            try:

                def _wait() -> dict:
                    return self._api.wait(container_id, timeout=int(timeout.total_seconds()))  # type: ignore[no-untyped-call]

                wait_response = await asyncio.to_thread(_wait)
            except requests.exceptions.Timeout:
                timed_out = True
                await asyncio.to_thread(self._kill_container, container_id)
                wait_response = await asyncio.to_thread(self._api.wait, container_id)

            stdout, stderr = await asyncio.to_thread(
                self._read_container_logs, container_id
            )
            surefire_xml = await asyncio.to_thread(
                self._read_surefire_xml, container_id
            )
            return RunnerExecutionResult(
                run_id=workspace.run_id,
                exit_code=int(wait_response.get("StatusCode", 0) or 0),
                timed_out=timed_out,
                standard_output=stdout,
                standard_error=stderr,
                surefire_xml=surefire_xml,
                duration=timedelta(seconds=time.perf_counter() - started),
            )
        except asyncio.CancelledError:
            raise
        except (ExerciseRunnerUnavailableException, ExerciseInfrastructureException):
            raise
        except ImageNotFound as exc:
            raise ExerciseRunnerUnavailableException(
                "The configured exercise runner image is unavailable.", exc
            ) from exc
        except APIError as exc:
            if _status_code(exc) in (400, 404):
                raise ExerciseRunnerUnavailableException(
                    "The configured exercise runner is unavailable.", exc
                ) from exc
            raise ExerciseInfrastructureException(
                "The Docker runner failed to execute the exercise.", exc
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise ExerciseRunnerUnavailableException(
                "The Docker daemon did not respond in time.", exc
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise ExerciseRunnerUnavailableException(
                "The Docker daemon is unavailable.", exc
            ) from exc
        finally:
            if container_id:
                await asyncio.to_thread(self._remove_container_quietly, container_id)

    def _build_host_config(self, definition: ExerciseDefinition):  # type: ignore[no-untyped-def]
        if ExerciseRuntimeProfiles.is_python(definition.manifest):
            # Python exercises run fully offline: all libraries are baked into the runner image.
            return self._api.create_host_config(  # type: ignore[no-untyped-call]
                init=True,
                auto_remove=False,
                network_mode="none",
                mem_limit=self._options.memory_limit_bytes,
                nano_cpus=self._options.nano_cpus,
                pids_limit=self._options.pids_limit,
            )
        return self._api.create_host_config(  # type: ignore[no-untyped-call]
            init=True,
            auto_remove=False,
            network_mode="bridge",
            mem_limit=self._options.memory_limit_bytes,
            nano_cpus=self._options.nano_cpus,
            pids_limit=self._options.pids_limit,
            mounts=[
                docker.types.Mount(
                    target="/root/.m2",
                    source=self._options.maven_cache_volume,
                    type="volume",
                )
            ],
        )

    def _resolve_runner_image(self, definition: ExerciseDefinition) -> str:
        profile = definition.manifest.runtime.profile
        if profile and profile.strip():
            images_by_profile = {
                key.lower(): value
                for key, value in (self._options.runner_images_by_profile or {}).items()
            }
            image = images_by_profile.get(profile.lower())
            if image and image.strip():
                return image
            normalized = images_by_profile.get(profile.replace("-", "_").lower())
            if normalized and normalized.strip():
                return normalized
        if ExerciseRuntimeProfiles.is_python(definition.manifest):
            return self._options.python_runner_image
        return self._options.runner_image

    def _ensure_runner_image(self, runner_image: str) -> None:
        try:
            self._docker_client.images.get(runner_image)
        except ImageNotFound as exc:
            raise ExerciseRunnerUnavailableException(
                f"The configured exercise runner image '{runner_image}' is unavailable.", exc
            ) from exc
        except APIError as exc:
            raise ExerciseRunnerUnavailableException(
                f"The Docker daemon could not inspect the exercise runner image '{runner_image}'.",
                exc,
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise ExerciseRunnerUnavailableException(
                "The Docker daemon did not respond in time.", exc
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            raise ExerciseRunnerUnavailableException(
                "The Docker daemon is unavailable.", exc
            ) from exc

    def _kill_container(self, container_id: str) -> None:
        try:
            self._api.kill(container_id, signal="SIGKILL")
        except NotFound:
            # The container already exited while the timeout path was being handled.
            pass

    def _read_container_logs(self, container_id: str) -> tuple[str, str]:
        stdout_bytes, stderr_bytes = self._api.logs(  # type: ignore[misc]
            container_id, stdout=True, stderr=True, follow=False, timestamps=False, demux=True
        )
        return (
            self._truncate((stdout_bytes or b"").decode("utf-8", errors="replace")),
            self._truncate((stderr_bytes or b"").decode("utf-8", errors="replace")),
        )

    def _read_surefire_xml(self, container_id: str) -> str | None:
        try:
            stream, _stat = self._api.get_archive(container_id, _SUREFIRE_PATH)
            data = b"".join(stream)
        except NotFound:
            return None
        with tarfile.open(fileobj=io.BytesIO(data)) as tar:
            for member in tar.getmembers():
                if (
                    not member.isfile()
                    or not member.name.lower().endswith(".xml")
                    or not os.path.basename(member.name).lower().startswith("test-")
                ):
                    continue
                extracted = tar.extractfile(member)
                if extracted is None:
                    continue
                return self._truncate(
                    extracted.read().decode("utf-8", errors="replace")
                )
        return None

    def _get_execution_timeout(self, definition: ExerciseDefinition) -> timedelta:
        manifest_seconds = definition.manifest.runtime.timeout_seconds
        if manifest_seconds > 0:
            seconds = min(
                manifest_seconds + self._options.execution_startup_grace_seconds,
                self._options.max_execution_seconds,
            )
        else:
            seconds = self._options.max_execution_seconds
        return timedelta(seconds=max(1, seconds))

    def _truncate(self, value: str) -> str:
        # C# compares string.Length (UTF-16 units); learner output is ASCII in
        # practice, where this matches exactly.
        if len(value) <= self._options.max_output_bytes:
            return value
        return value[: self._options.max_output_bytes] + "\n[output truncated]"

    def _remove_container_quietly(self, container_id: str) -> None:
        try:
            self._api.remove_container(container_id, force=True, v=False)
        except Exception as exc:  # noqa: BLE001 - cleanup must never fail the run
            logger.warning(
                "Failed to remove exercise runner container %s: %s", container_id, exc
            )


def _status_code(exc: APIError) -> int | None:
    response = getattr(exc, "response", None)
    return getattr(response, "status_code", None) if response is not None else None


def _tar_directory(workspace_path: str) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as tar:
        for entry in sorted(os.listdir(workspace_path)):
            tar.add(os.path.join(workspace_path, entry), arcname=entry, recursive=True)
    return buffer.getvalue()
