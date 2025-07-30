import httpx

def translate_text(text: str, source_lang: str='ar', target_lang: str='en') -> str:
    url = 'https://translate.googleapis.com/translate_a/single'
    params = {
        'client': 'gtx',
        'sl': source_lang,
        'tl': target_lang,
        'dt': 't',
        'q': text
    }

    response = httpx.get(url, params=params)
    response.raise_for_status()

    result = response.json()
    translated_text = result[0][0][0]
    return translated_text


if __name__ == '__main__':
    text = translate_text('اسمي عبد المهيمن ابن عبد الحافظ')
    print(text)