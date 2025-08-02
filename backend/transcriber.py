from transformers import MarianMTModel, MarianTokenizer
from faster_whisper import WhisperModel
from pydub import AudioSegment
from typing import Union, BinaryIO
from datetime import datetime
from settings import SOURCRE_LANG, TARGET_LANG, RMS_THRESHOLD, DEBUG_AUDIO_SAVE_DIR, DEVICE
import io
import os


class Transcriber:
    def __init__(self, source_lang: str, device: str='cpu'):
        self.source_lang = source_lang
        model_kwargs = {
            'device': device,
            'compute_type': 'float16' if device == 'cuda' else 'int8'
        }
        self.model = WhisperModel('tiny', **model_kwargs)

    def transcribe(self, audio: Union[str, BinaryIO]) -> str:
        # transcribe audio and concatenate segments
        segments, _ = self.model.transcribe(audio, language=self.source_lang, beam_size=5)
        transcription = " ".join([segment.text for segment in segments])
        return transcription


class Translator:
    def __init__(self, source_lang: str, target_lang: str, device: str='cpu'):
        self.source_lang, self.target_lang = source_lang, target_lang
        # model_name = f'Helsinki-NLP/opus-mt-tc-big-{source_lang}-{target_lang}'
        model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)
        if device == 'cuda':
            self.model = self.model.to('cuda')


    def translate(self, source_text: str) -> str:
        if not source_text.strip():
            return ''
        
        # convert text to tokens and translate
        inputs = self.tokenizer(source_text, return_tensors='pt', padding=True, truncation=True)
        outputs = self.model.generate(**inputs)

        # convert output tokens into translated text
        translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translation


def transcribe_and_translate(audio: AudioSegment) -> tuple[str, str]:
    # export audio to in-memory WAV buffer
    wav_io = io.BytesIO()
    audio.export(wav_io, format='wav')
    wav_io.seek(0)

    # transcribe audio
    transcription = transcriber.transcribe(wav_io)

    # translate text
    translation = translator.translate(transcription)

    return transcription, translation 


def is_silent(audio: AudioSegment, rms_threshold: int=RMS_THRESHOLD) -> bool:
    # check if rms amplitude of audio data is smaller than threshold value
    return audio.rms < rms_threshold


def save_audio_to_file(audio: AudioSegment) -> None:
    # create audio directory if it doesn't exist
    os.makedirs(DEBUG_AUDIO_SAVE_DIR, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{DEBUG_AUDIO_SAVE_DIR}/{timestamp}.wav'
    audio.export(filename, format='wav')


transcriber = Transcriber(SOURCRE_LANG, device=DEVICE)
translator = Translator(SOURCRE_LANG, TARGET_LANG, device=DEVICE)