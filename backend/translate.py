from transformers import MarianMTModel, MarianTokenizer

class ArabicToEnglishTranslator:
    def __init__(self):
        model_name = 'Helsinki-NLP/opus-mt-tc-big-ar-en'
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)

    def translate(self, arabic_text: str) -> str:
        if not arabic_text.strip():
            return ''
        
        inputs = self.tokenizer(arabic_text, return_tensors='pt', padding=True, truncation=True)
        translated = self.model.generate(**inputs)

        english_text = self.tokenizer.decode(translated[0], skip_special_tokens=True)
        return english_text
    

if __name__ == '__main__':
    translator = ArabicToEnglishTranslator()
    arabic = ' السلام عليكم، نهاية القصة، النهاية، مع السلامة، نهاية القصة، توتو، توتو، حلو أو ملتوٍ، هكذا تنتهي قصة اليوم. مع السلامة..'
    english = translator.translate(arabic)
    print('Translated:', english)