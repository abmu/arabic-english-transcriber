import wave
from piper import PiperVoice

class Synthesiser:
    '''
    Synthesise speech from text (text-to-speech)
    '''

    def __init__(self, source_lang: str, device: str='cpu'):
        self.source_lang = source_lang
        use_cuda = device == 'cuda'
        self.voice = PiperVoice.load(f'./voices/{source_lang}.onnx', use_cuda=use_cuda)

    def synthesise(self, text: str):
        output_path = 'output.wav'
        with wave.open(output_path, 'wb') as f:
            self.voice.synthesize_wav(text, f)

s = Synthesiser('er')
s.synthesise('Hello there!')