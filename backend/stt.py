from faster_whisper import WhisperModel

model = WhisperModel("small", compute_type="float32")

def transcribe_audio(file_path):
    segments, _ = model.transcribe(file_path, language='ar', beam_size=5)
    transcript = " ".join([segment.text for segment in segments])
    return transcript