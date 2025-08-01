from transformers import MarianMTModel, MarianTokenizer
from faster_whisper import WhisperModel
from pydub import AudioSegment
import io
from datetime import datetime

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    audio_filename = f"debug_audio_{timestamp}.wav"
    
    # Save the raw bytes to a file first (for debugging)
    with open(audio_filename, 'wb') as f:
        f.write(raw_audio_bytes)
    print(f"Debug: Raw audio saved to {audio_filename}")

    # convert audio bytes to AUdioSegment
    audio = AudioSegment.from_file(io.BytesIO(raw_audio_bytes), format='wav')

    # export audio to in-memory WAV buffer
    wav_io = io.BytesIO()
    audio.export(wav_io, format='wav')
    wav_io.seek(0)

    # transcribe audio
    segments, _ = model.transcribe(wav_io, language='ar', beam_size=5)
    transcript = " ".join([segment.text for segment in segments])

    # translate text
    translation = translator.translate(transcript)
    return translation 
    
