import requests
import json

from cat.mad_hatter.decorators import tool, hook
from cat.utils import log


def LoadConfiguration():
    with open(
        "./cat/plugins/cheshire-cat-multilingual-libretranslate/settings.json"
    ) as json_file:
        return json.load(json_file)


mutlilangual_conf = LoadConfiguration()


def translate_text(inputText, source, target):
    if "libretranslate_url" in mutlilangual_conf:
        url = mutlilangual_conf["libretranslate_url"]
        payload = {
            "q": inputText,
            "source": source,
            "target": target,
            "format": "text",
            "api_key": mutlilangual_conf["api_key"],
        }
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            translated = response.json()
            return translated["translatedText"]
        except:
            return inputText
    else:
        return inputText


@hook(priority=1)
def before_cat_sends_message(message, cat):
    source = "en"
    if "libretranslate_url" in mutlilangual_conf:
        target = mutlilangual_conf["mylang"]
    else:
        target = "en"
    log("Starting translation: " + message["content"])
    translated_message = translate_text(message["content"], source, target)
    log("End translation:" + translated_message)
    message["content"] = translated_message
    return message


@hook(priority=1)
def before_cat_reads_message(user_message_json, cat):
    target = "en"
    if "libretranslate_url" in mutlilangual_conf:
        source = mutlilangual_conf["mylang"]
    else:
        source = "en"
    log("Starting translation: " + user_message_json["text"])
    translated_message = translate_text(user_message_json["text"], source, target)
    log("End translation:" + translated_message)
    user_message_json["text"] = translated_message
    return user_message_json
