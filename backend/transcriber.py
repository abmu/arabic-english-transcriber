from transformers import MarianMTModel, MarianTokenizer
from faster_whisper import WhisperModel
from pydub import AudioSegment
import uuid
import io

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

model = WhisperModel("small", device='cpu', compute_type='int8')
translator = ArabicToEnglishTranslator()

def transcribe_and_translate(raw_audio_bytes: bytes) -> str:
    # generate unique filename
    audio_id = str(uuid.uuid4())
    temp_path = f'temp_{audio_id}.wav'

    # export audio to wav file
    audio = AudioSegment.from_file(io.BytesIO(raw_audio_bytes), format='webm')
    audio.export(temp_path, format='wav')

    # transcribe audio
    segments, _ = model.transcribe(temp_path, language='ar', beam_size=5)
    transcript = " ".join([segment.text for segment in segments])

    # translate text
    translation = translator.translate(transcript)
    return translation 
    
