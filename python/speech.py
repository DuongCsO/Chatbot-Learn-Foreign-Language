import requests
import os
from requests import post

RAPID_KEY= os.getenv("RAPID_KEY")
TEXT_TO_SPEECH_KEY= os.getenv("TEXT_TO_SPEECH_KEY")

# api_key_text_to_speech='85a038085cb74ee9a56461fbef691977'
def text_to_speech(language: str, text: str, filename: str) -> str:
    """
    Initialize custom text-to-speech client
    :param language: language code in iso6391
    :param text: text for text-to-speech
    :param filename: path to save audio file
    """
    lang = ['ar-eg', 'bg-bg', 'ca-es', 'zh-cn', 'hr-hr', 'cs-cz', 'da-dk',
    'nl-be', 'nl-nl', 'en-us', 'fi-fi',
    'fr-fr', 'de-de', 'el-gr', 'he-il', 'hi-in', 'hu-hu', 'id-id',
    'it-it', 'ja-jp', 'ko-kr', 'ms-my', 'nb-no', 'pl-pl', 'pt-pt', 'ro-ro', 'ru-ru',
    'sk-sk', 'sl-si', 'es-es', 'sv-se', 'ta-in', 'th-th', 'tr-tr', 'vi-vn']
    #Transfer language code to api define
    for i in lang:
        if language in i:
            lang_code = i
            break
    # Define the base URL for the custom text-to-speech API
    url = "https://voicerss-text-to-speech.p.rapidapi.com/"
    # Set query parameters (in this case, just the API key)
    querystring = {"key": TEXT_TO_SPEECH_KEY}
    # Payload containing the text and other options for text-to-speech
    payload = {
        "src": text,
        "hl": lang_code,
        "r": "0",
        "c": "mp3",
        "f": "8khz_8bit_mono"
    }
    # Headers required for the API request
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "X-RapidAPI-Key": RAPID_KEY,
        "X-RapidAPI-Host": "voicerss-text-to-speech.p.rapidapi.com"
    }
    # Make a POST request to the custom text-to-speech API
    response = requests.post(url, data=payload, headers=headers, params=querystring)
    if os.path.exists(filename):
        os.remove(filename)
        print("Đã xóa")
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename


def speech_to_text(filename: str) -> str:
    with open(filename, 'rb') as f:
        files = {"file": f.read()}
    url = "https://chatgpt-42.p.rapidapi.com/whisperv3"
    headers = {
        "X-RapidAPI-Key": RAPID_KEY,
        "X-RapidAPI-Host": "chatgpt-42.p.rapidapi.com"
    }

    response = post(url, files=files, headers=headers)
    if response.status_code==200:
        return response.json()['text']
    else:
        print("Error:", response.text)
        # text_to_speech(api_key, "vi-vn", "Xin chào!")