import pyttsx3

class Synthesiser:
    '''
    Synthesise speech from text (text-to-speech)
    '''

    def __init__(self, source_lang: str, device: str='cpu'):
        self.source_lang = source_lang
        engine = pyttsx3.init()
        engine.say('Hello')
        engine.runAndWait()
        self.engine = engine

Synthesiser('en')