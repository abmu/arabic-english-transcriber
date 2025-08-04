from transformers import MarianMTModel, MarianTokenizer


class Translator:
    def __init__(self, source_lang: str, target_lang: str, device: str='cpu'):
        self.source_lang, self.target_lang = source_lang, target_lang
        model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
        self.tokenizer = MarianTokenizer.from_pretrained(model_name)
        self.model = MarianMTModel.from_pretrained(model_name)
        self.device = device
        if device == 'cuda':
            self.model = self.model.to('cuda')


    def translate(self, source_text: str) -> str:
        if not source_text.strip():
            return ''
        
        # convert text to tokens and translate
        inputs = self.tokenizer(source_text, return_tensors='pt', padding=True, truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()} # move inputs to same device as model

        # convert output tokens into translated text
        outputs = self.model.generate(**inputs)
        translation = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return translation