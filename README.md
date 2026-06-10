## Whisper Model Setup

This project uses the **Systran Faster-Whisper Large-v2** model for speech-to-text transcription.

### Note

The model files are not included in this repository because they require several gigabytes of storage.

If the model is not available locally, Faster-Whisper will automatically download it from Hugging Face during the first execution.

### Installation

```bash
pip install faster-whisper
```

### Loading the Model

```python
from faster_whisper import WhisperModel

model = WhisperModel(
    "large-v2",
    device="cpu",
    compute_type="int8"
)
```

### Automatic Download

When the above code is executed for the first time, Faster-Whisper downloads the required model files automatically and stores them in the Hugging Face cache directory.

**Windows:**
```text
C:\Users\<username>\.cache\huggingface\
```

**Linux:**
```text
~/.cache/huggingface/
```

### Manual Download (Optional)

If automatic download is unavailable, the model can be downloaded manually from:

https://huggingface.co/Systran/faster-whisper-large-v2

### Storage Recommendation

The Large-v2 model occupies approximately 3 GB of disk space. If storage is limited, the model directory can be deleted and re-downloaded automatically when needed.
