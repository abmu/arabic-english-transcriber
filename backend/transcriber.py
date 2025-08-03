from faster_whisper import WhisperModel
from typing import Union, BinaryIO
from settings import WHISPER_MODEL_SIZE


class Transcriber:
    def __init__(self, source_lang: str, device: str='cpu'):
        self.source_lang = source_lang
        model_kwargs = {
            'device': device,
            'compute_type': 'float16' if device == 'cuda' else 'int8'
        }
        self.model = WhisperModel(WHISPER_MODEL_SIZE, **model_kwargs)

    def transcribe(self, audio: Union[str, BinaryIO]) -> str:
        # transcribe audio and concatenate segments
        segments, _ = self.model.transcribe(audio, language=self.source_lang, beam_size=5)
        transcription = " ".join([segment.text for segment in segments])
        return transcription