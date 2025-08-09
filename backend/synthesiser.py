from piper import PiperVoice
import io
import wave

class Synthesiser:
    '''
    Synthesise speech from text (text-to-speech)
    '''

    def __init__(self, source_lang: str, device: str='cpu'):
        self.source_lang = source_lang
        use_cuda = device == 'cuda'
        self.voice = PiperVoice.load(f'./voices/{source_lang}.onnx', use_cuda=use_cuda)

    def synthesise(self, text: str) -> bytes:
        # convert text into audio bytes
        buffer = io.BytesIO()
        with wave.open(buffer, 'wb') as wav_file:
            self.voice.synthesize_wav(text, wav_file)
        return buffer.getvalue()