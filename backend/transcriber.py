from transformers import MarianMTModel, MarianTokenizer
from faster_whisper import WhisperModel
from pydub import AudioSegment
import io

SAMPLE_RATE = 16000
RMS_THRESHOLD = 800

class ArabicToEnglishTranslator:
    def __init__(self):
        model_name = 'Helsinki-NLP/opus-mt-tc-big-ar-en'
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)

    def translate(self, arabic_text: str) -> str:
        if not arabic_text.strip():
            return ''
        
        # convert text to tokens and translate
        inputs = self.tokenizer(arabic_text, return_tensors='pt', padding=True, truncation=True)
        translated = self.model.generate(**inputs)

        # convert output tokens into translated text
        english_text = self.tokenizer.decode(translated[0], skip_special_tokens=True)
        return english_text

def transcribe_and_translate(audio: AudioSegment) -> tuple[str, str]:
    # export audio to in-memory WAV buffer
    wav_io = io.BytesIO()
    audio.export(wav_io, format='wav')
    wav_io.seek(0)

    # transcribe audio
    segments, _ = model.transcribe(wav_io, language='ar', beam_size=5)
    transcript = " ".join([segment.text for segment in segments])

    # translate text
    translation = translator.translate(transcript)
    return transcript, translation 
    
def is_silent(audio: AudioSegment, rms_threshold: int=RMS_THRESHOLD) -> bool:
    # check if rms amplitude of audio data is smaller than threshold value
    return audio.rms < rms_threshold


model = WhisperModel("small", device='cpu', compute_type='int8')
translator = ArabicToEnglishTranslator()