import requests
from langcodes import Language, find
import os


RAPID_KEY= os.getenv("RAPID_KEY")


def translate(text: str, detected_language: str, translated_language: str) -> str:
    url = "https://google-api31.p.rapidapi.com/translate"
    payload = {
        "text": text,
        "to": translated_language,
        "from_lang": detected_language
    }
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_KEY,
        "X-RapidAPI-Host": "google-api31.p.rapidapi.com"
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()[0]['translated']


def translate2(text:str, detected_language: str, translated_language: str)->str:
    url = "https://microsoft-translator-text.p.rapidapi.com/translate"
    querystring = {"to[0]": translated_language, "api-version": "3.0", "from": detected_language, "profanityAction": "NoAction",
                   "textType": "plain"}

    payload = [{"Text": text}]
    headers = {
        "content-type": "application/json",
        "X-RapidAPI-Key": RAPID_KEY,
        "X-RapidAPI-Host": "microsoft-translator-text.p.rapidapi.com"
    }
    response = requests.post(url, json=payload, headers=headers, params=querystring)
    return response.json()[0]['translations'][0]['text']


def language_name_to_iso6391(language_name: str) -> str:
    """
    Convert language name to ISO 639-1 code
    i.e.: English -> en

    :param language_name: string
    :return: ISO 639-1 code (as string)
    """
    return find(language_name).language


def iso6391_to_language_name(language_code: str, name_in_same_language: bool = False) -> str:
    """
    Convert ISO 639-1 code to language name

    :param language_code: ISO 639-1 code (as string)
    :param name_in_same_language: if True, name is returned in that language. Otherwise, name returns in English
                                  True: fr -> Français | False: fr -> French
    :return: language name
    """
    display_lang = language_code if name_in_same_language else "en"
    return Language.get(language_code).display_name(display_lang)


def locale_code_to_language(locale_code: str, name_in_same_language: bool = False):
    """
    Convert language code and locale (i.e. "fr-FR") to language name

    :param locale_code: string
    :param name_in_same_language: if True, name is returned in that language. Otherwise, name returns in English
                                  True: es-US -> Español (Estados Unidos) | False:es-US -> Spanish (United States)
    :return: language name
    """
    display_lang = locale_code.split('-')[0] if name_in_same_language else "en"
    return Language.get(locale_code).display_name(display_lang).title()
