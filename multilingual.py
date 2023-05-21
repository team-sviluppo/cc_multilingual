import requests
import json

from cat.mad_hatter.decorators import tool, hook
from cat.utils import log

cat_instance = None


def LoadConfiguration():
    with open("./cat/plugins/cc_multilingual/settings.json") as json_file:
        return json.load(json_file)


mutlilangual_conf = LoadConfiguration()


@hook(priority=1)
def init_cat(cat):
    if mutlilangual_conf["lang"] == "auto":
        user_lang = "en"
    else:
        user_lang = mutlilangual_conf["lang"]
    cat.working_memory["cc_multilingual_lang"] = user_lang
    global cat_instance
    cat_instance = cat
    return None


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


def cc_multilingual_translate(text):
    if "cc_multilingual_lang" in cat_instance.working_memory:
        target = cat_instance.working_memory["cc_multilingual_lang"]
        translated_message = translate_text(text, "en", target)
        text = translated_message
    return text


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
        if "cc_multilingual_lang" in cat.working_memory:
            target = cat.working_memory["cc_multilingual_lang"]
        else:
            target = "en"
    else:
        target = "en"
    log("MSG-OUT Starting translation: " + message["content"])
    translated_message = translate_text(message["content"], source, target)
    log("MSG-OUT End translation:" + translated_message)
    message["content"] = translated_message
    return message


@hook(priority=1)
def before_cat_reads_message(user_message_json, cat):
    target = "en"
    if "libretranslate_url" in mutlilangual_conf:
        source = detect_language(user_message_json["text"])
    else:
        source = "en"
    log("MSG-IN Starting translation: " + user_message_json["text"] + " - lang: " + source)
    translated_message = translate_text(user_message_json["text"], source, target)
    log("MSG-IN End translation:" + translated_message + " - lang: " + target)
    user_message_json["text"] = translated_message
    cat.working_memory["cc_multilingual_lang"] = source
    return user_message_json


"""
@hook(priority=1)
def before_rabbithole_splits_text(doc, cat):
    target = "en"
    if "libretranslate_url" in mutlilangual_conf:
        source = detect_language(doc[0].page_content)
    else:
        source = "en"
    log("Start document/url translation from " + source + " to " + target)
    translated_message = translate_text(doc[0].page_content, source, target)
    doc[0].page_content = translated_message
    log("End document/url translation from " + source + " to " + target)
    return doc
"""


@hook(priority=1)
def after_rabbithole_splitted_text(chunks, cat):
    chunlks_len = str(len(chunks))
    i = 1
    for chunk in chunks:
        target = "en"
        if "libretranslate_url" in mutlilangual_conf:
            source = detect_language(chunk.page_content)
        else:
            source = "en"
        log(
            "Start document/url chunk (" + str(i) + "/" + chunlks_len + ") translation from " + source + " to " + target
        )
        translated_message = translate_text(chunk.page_content, source, target)
        chunk.page_content = translated_message
        log("End document/url chunk (" + str(i) + "/" + chunlks_len + ") translation from " + source + " to " + target)
        i = i + 1
    return chunks
