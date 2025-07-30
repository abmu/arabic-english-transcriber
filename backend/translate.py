from transformers import MarianMTModel, MarianTokenizer

class ArabicToEnglishTranslator:
    def __init__(self):
        model_name = 'Helsinki-NLP/opus-mt-ar-en'
        self.tokenizer - MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)