from faster_whisper import WhisperModel

model = WhisperModel("small", device='cpu', compute_type='int8')

def transcribe_audio(file_path: str) -> str:
    segments, _ = model.transcribe(file_path, language='ar', beam_size=5)
    transcript = " ".join([segment.text for segment in segments])
    return transcript


if __name__ == '__main__':
    text = transcribe_audio('backend/arabic.wav')
    print('Transcription:', text)