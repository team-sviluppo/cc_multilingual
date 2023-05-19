import requests
import json

from cat.mad_hatter.decorators import tool, hook
from cat.utils import log


def LoadConfiguration():
    with open("./cat/plugins/cc_multilingual/settings.json") as json_file:
        return json.load(json_file)


mutlilangual_conf = LoadConfiguration()


def translate_text(inputText, source, target):
    if "libretranslate_url" in mutlilangual_conf:
        url = mutlilangual_conf["libretranslate_url"] + "/translate"
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


def detect_language(inputText):
    if mutlilangual_conf["lang"] == "auto":
        url = mutlilangual_conf["libretranslate_url"] + "/detect"
        payload = {
            "q": inputText,
            "api_key": mutlilangual_conf["api_key"],
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        log("Language detected: " + response.text)
        detected = response.json()
        return detected[0]["language"]
    else:
        return mutlilangual_conf["lang"]


@hook(priority=1)
def before_cat_sends_message(message, cat):
    source = "en"
    if "libretranslate_url" in mutlilangual_conf:
        key = "source_lang"
        if key in cat.working_memory:
            target = cat.working_memory["source_lang"]
        else:
            target = "en"
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
        source = detect_language(user_message_json["text"])
    else:
        source = "en"
    log("Starting translation: " + user_message_json["text"] + " - lang: " + source)
    translated_message = translate_text(user_message_json["text"], source, target)
    log("End translation:" + translated_message + " - lang: " + target)
    user_message_json["text"] = translated_message
    cat.working_memory["source_lang"] = source
    return user_message_json
