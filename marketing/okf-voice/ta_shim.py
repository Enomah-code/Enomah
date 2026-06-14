"""Route torchaudio I/O through soundfile.

torch >= 2.9 defers audio decoding to torchcodec, whose prebuilt core libs
dlopen a CUDA runtime (libnvrtc). On CPU-only hosts that load fails hard, which
breaks `torchaudio.load` — the call XTTS uses to read the speaker reference.

XTTS only ever needs plain WAV I/O, so we replace `torchaudio.load`/`.save`
with soundfile-backed equivalents. Import this module before importing TTS.
"""
import soundfile as sf
import torch
import torchaudio


def _load(path, **_):
    data, sr = sf.read(str(path), dtype="float32", always_2d=True)  # (samples, ch)
    return torch.from_numpy(data.T).contiguous(), sr


def _save(path, tensor, sample_rate, **_):
    arr = tensor.detach().cpu().numpy()
    if arr.ndim == 2:
        arr = arr.T  # (ch, samples) -> (samples, ch)
    sf.write(str(path), arr, sample_rate)


def install():
    torchaudio.load = _load
    torchaudio.save = _save
