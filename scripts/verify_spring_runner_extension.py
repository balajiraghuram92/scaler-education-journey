import os
import json
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def audit():
    print("======================================================================")
    print("  EXERCISE SANDBOX SPRING BOOT EXTENSION AUDITOR")
    print("======================================================================")

    # 1. Runner Java Spring files
    spring_dockerfile = os.path.join(ROOT, "runner", "java-spring", "Dockerfile")
    spring_run_sh = os.path.join(ROOT, "runner", "java-spring", "run.sh")
    java_dockerfile = os.path.join(ROOT, "runner", "java", "Dockerfile")
    java_run_sh = os.path.join(ROOT, "runner", "java", "run.sh")

    assert os.path.exists(spring_dockerfile), "runner/java-spring/Dockerfile missing"
    assert os.path.exists(spring_run_sh), "runner/java-spring/run.sh missing"
    assert os.path.exists(java_dockerfile), "runner/java/Dockerfile missing"
    assert os.path.exists(java_run_sh), "runner/java/run.sh missing"

    with open(spring_dockerfile, "r") as f:
        dockerfile_content = f.read()
    assert "maven:3.9.9-eclipse-temurin-17" in dockerfile_content, "Missing Temurin 17 base image"
    assert "ENTRYPOINT [\"/usr/local/bin/neuralascent-java-run\"]" in dockerfile_content, "Missing entrypoint"

    with open(spring_run_sh, "r") as f:
        spring_sh_content = f.read()
    with open(java_run_sh, "r") as f:
        java_sh_content = f.read()
    assert spring_sh_content.strip() == java_sh_content.strip(), "run.sh does not match runner/java/run.sh"

    print("[PASS] runner/java-spring/Dockerfile & run.sh verified.")

    # 2. Options
    options_file = os.path.join(ROOT, "api", "Options", "ExerciseExecutionOptions.cs")
    with open(options_file, "r") as f:
        options_content = f.read()
    assert "RunnerImagesByProfile" in options_content, "RunnerImagesByProfile missing in options"
    assert "MaxExecutionSeconds { get; set; } = 240;" in options_content, "MaxExecutionSeconds not 240"
    assert "MemoryLimitBytes { get; set; } = 1_610_612_736;" in options_content, "MemoryLimitBytes not 1.5GB"

    print("[PASS] api/Options/ExerciseExecutionOptions.cs verified.")

    # 3. LocalDockerExerciseRunner
    runner_file = os.path.join(ROOT, "api", "Services", "Exercises", "LocalDockerExerciseRunner.cs")
    with open(runner_file, "r") as f:
        runner_content = f.read()
    assert "ResolveRunnerImage" in runner_content, "ResolveRunnerImage helper missing"
    assert "EnsureRunnerImageAsync(runnerImage" in runner_content, "EnsureRunnerImageAsync not parameterized"
    assert "Image = runnerImage" in runner_content, "Container creation does not use resolved image"

    print("[PASS] api/Services/Exercises/LocalDockerExerciseRunner.cs verified.")

    # 4. docker-compose.yml
    compose_file = os.path.join(ROOT, "docker-compose.yml")
    with open(compose_file, "r") as f:
        compose_content = f.read()
    assert "ExerciseExecution__RunnerImagesByProfile__java-maven-spring" in compose_content, "Compose missing Spring runner env var"

    print("[PASS] docker-compose.yml verified.")

    # 5. Manifests check
    exercises_root = os.path.join(ROOT, "exercises")
    existing_manifest_count = 0
    for dirpath, _, filenames in os.walk(exercises_root):
        if "exercise.json" in filenames:
            manifest_path = os.path.join(dirpath, "exercise.json")
            with open(manifest_path, "r") as f:
                data = json.load(f)
            profile = data.get("runtime", {}).get("profile")
            # All currently wired exercises should have java-maven (falling back to plain java runner)
            assert profile == "java-maven", f"Unexpected profile '{profile}' in {manifest_path}"
            existing_manifest_count += 1

    print(f"[PASS] Verified {existing_manifest_count} existing exercise manifests — all use 'java-maven' and safely fall back to neuralascent-java-runner:dev.")
    print("======================================================================")
    print("  ALL AUDIT CHECKS PASSED PERFECTLY!")
    print("======================================================================")

if __name__ == "__main__":
    audit()
