"""Wake word: 'Hey Jarvis' (openWakeWord, runs on this machine; the code is Apache-2.0, the pretrained
model is CC BY-NC-SA 4.0, so non-commercial use only)."""
from pathlib import Path
from typing import Callable

import numpy as np

FRAME = 1280          # samples per step: 80 ms at 16 kHz, what openWakeWord expects
MODEL_NAME = "hey_jarvis_v0.1"


class WakeError(Exception):
    """Plain-text problem the user can act on."""


class WakeWord:
    """Turns a stream of scores into 'wake now' events, with a short pause after each so one
    'Hey Jarvis' counts once."""

    def __init__(self, predict: Callable[[np.ndarray], float], threshold: float = 0.5, cooldown_frames: int = 25):
        self.predict, self.threshold, self.cooldown_frames = predict, threshold, cooldown_frames
        self._cool = 0
        self.last_score = 0.0

    def reset(self) -> None:
        """Forget old audio and the pause after the last detection (call before listening again)."""
        self._cool, self.last_score = 0, 0.0
        reset = getattr(self.predict, "reset", None)
        if reset:
            try:
                reset()
            except Exception:  # a failed reset must not stop listening
                pass

    def process(self, frame: np.ndarray) -> bool:
        self.last_score = score = float(self.predict(frame))
        if self._cool > 0:
            self._cool -= 1
            return False
        if score >= self.threshold:
            self._cool = self.cooldown_frames
            return True
        return False


def load_predictor() -> Callable[[np.ndarray], float]:
    """The real model. Downloads the 'hey jarvis' model on first use (a few MB, into the virtual env)."""
    try:
        import openwakeword
        from openwakeword.model import Model
    except (ImportError, OSError) as exc:
        raise WakeError(f"openwakeword is not installed ({exc}). Run scripts/setup.sh") from exc
    path = Path(openwakeword.__file__).parent / "resources" / "models" / f"{MODEL_NAME}.onnx"
    try:
        if not path.exists():
            print(f"Downloading the wake word model {MODEL_NAME} (first time only) ...")
            openwakeword.utils.download_models([MODEL_NAME])
        model = Model(wakeword_models=[str(path)], inference_framework="onnx")
    except Exception as exc:  # download and model loading fail in many ways
        raise WakeError(f"cannot load the wake word model: {exc}") from exc

    def predict(frame: np.ndarray) -> float:
        return max(model.predict(frame).values(), default=0.0)

    predict.reset = model.reset  # type: ignore[attr-defined]
    return predict
