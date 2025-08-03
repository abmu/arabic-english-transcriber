from pydub import AudioSegment
from datetime import datetime
from settings import SOURCRE_LANG, TARGET_LANG, RMS_THRESHOLD, DEBUG_AUDIO_SAVE_DIR, DEVICE
from transcriber import Transcriber
from translator import Translator
import io
import os


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