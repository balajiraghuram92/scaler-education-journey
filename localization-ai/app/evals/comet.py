"""Optional COMET-Kiwi scorer (reference-free MT quality).

Importing this module never requires the ``unbabel-comet`` package. When the
package or the model is not available the scorer reports "unavailable" and
every score comes back None; the run records null for the metric and nothing
else fails.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class CometKiwiScorer:
    """Thin wrapper over a COMET-Kiwi checkpoint. Call load() once; without
    a loaded model every score_batch() returns Nones with available False."""

    def __init__(self, model_name: str, *, gpus: int = 0) -> None:
        self.model_name = model_name
        self.gpus = gpus
        self._model: Any = None
        self._reason = "not loaded"

    @property
    def available(self) -> bool:
        return self._model is not None

    @property
    def status(self) -> str:
        return "ready" if self.available else f"unavailable: {self._reason}"

    def load(self) -> bool:
        """Download (if needed) and load the checkpoint. Never raises."""
        try:
            from comet import download_model, load_from_checkpoint
        except ImportError:
            self._reason = "unbabel-comet is not installed (see requirements-comet.txt)"
            logger.warning("COMET-Kiwi unavailable: %s", self._reason)
            return False
        try:
            checkpoint = download_model(self.model_name)
            self._model = load_from_checkpoint(checkpoint)
        except Exception as exc:
            self._reason = f"model {self.model_name!r} could not be loaded: {exc}"
            logger.warning("COMET-Kiwi unavailable: %s", self._reason)
            self._model = None
            return False
        self._reason = ""
        return True

    def score_batch(self, sources: list[str], translations: list[str]) -> list[float | None]:
        """Score aligned (source, translation) pairs; Nones when unavailable."""
        if self._model is None or len(sources) != len(translations):
            if len(sources) != len(translations):
                logger.error("COMET-Kiwi: %d sources vs %d translations; scoring nothing", len(sources), len(translations))
            return [None] * len(sources)
        data = [{"src": s, "mt": t} for s, t in zip(sources, translations, strict=True)]
        try:
            output = self._model.predict(data, batch_size=8, gpus=self.gpus)
        except Exception:
            logger.exception("COMET-Kiwi scoring failed; recording null for this batch")
            return [None] * len(sources)
        scores = list(output.scores)
        if len(scores) != len(sources):
            logger.error("COMET-Kiwi returned %d scores for %d pairs; recording null", len(scores), len(sources))
            return [None] * len(sources)
        return [float(s) for s in scores]
