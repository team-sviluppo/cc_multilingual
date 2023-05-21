# Cheshire Cat Multilingual (cc_multilingual)

The plugin automatically translates user input (prompts, documents, url) from the user's chosen language into English. The request to the LLM is made in English and the response is automatically translated into the user's language. The plugin also allows you not to set a language for the user but identifies it automatically (pay attention to this feature)

## Installation

- Upgrade cheshire cat to the last version (the plugin need cheshire-cat 0.0.4 to work)
- Download the cc_multilingual folder into the cheshire-cat/core/cat/plugins one.
- Edit the settings.json file into cc_multilingual folder with your libretranslate info: url, api_key and language (for language if you set "auto" the plugin try do detect automatically the input language).
- **IMPORTANT:** Read next section to add libretranslate container to default cheshire-cat installation for a local instance of libretranslate. In this case you don't need modify the libretranslate url and api_key in settings.json.
- Interact with the cat in your languange (the same specified into settings.json file)

## Add libretranslate container to cheshire-cat

You can run a local instance of libretranslate simply adding to the cat's default docker-compose.yml the following code:

```yaml
libretranslate:
  image: libretranslate/libretranslate
  container_name: libretranslate
  restart: unless-stopped
  ports:
    - "5080:5000"
  ## Comment above command to load all language (with all laguanges container need some minutes to start)
  command: --load-only en,it,fr
```

**_Change the --load-only parameter with comma separated language code of languages you want to enable, in this example there are 3 languages enabled (en,it,fr). The en language code is mandatory_**

Here you can find an example of full docker-compose.yml with libretranslate service:

```yaml
version: "3.7"

services:
  cheshire-cat-core:
    build:
      context: ./core
    container_name: cheshire_cat_core
    depends_on:
      - cheshire-cat-vector-memory
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
    ports:
      - ${CORE_PORT}:80
    volumes:
      - ./core:/app
    command:
      - uvicorn
      - cat.main:cheshire_cat_api
      - --host
      - "0.0.0.0"
      - --port
      - "80"
      # - --log-config
      # - ./logger.yml
      - --reload # take away in prod
    restart: unless-stopped

  cheshire-cat-admin:
    build:
      context: ./admin
    container_name: cheshire_cat_admin
    depends_on:
      - cheshire-cat-core
    env_file:
      - .env
    ports:
      - ${ADMIN_PORT}:3000
    volumes:
      - ./admin:/app
    restart: unless-stopped

  cheshire-cat-vector-memory:
    image: qdrant/qdrant:v1.1.1
    container_name: cheshire_cat_vector_memory
    expose:
      - 6333
    volumes:
      - ./long_term_memory/vector:/qdrant/storage
    restart: unless-stopped

  libretranslate:
    image: libretranslate/libretranslate
    container_name: libretranslate
    restart: unless-stopped
    ports:
      - "5080:5000"
    ## Comment above command to load all language (with all laguanges container need some minutes to start)
    command: --load-only en,it,fr
```

## Plugin Settings

The plugin setting are defined into settings.json file in cc_multiligual folder:

```json
{ "libretranslate_url": "http://libretranslate:5000", "api_key": "", "lang": "auto" }
```

- **_libretranslate_url_**: the url of libretranslate instance. If you run a local container with docker-compose.yml above example you don't need to modify default value.
- **_api_key_**: the api_key of yout libretranslate instance. If you run a local container with docker-compose.yml above example you don't need to modify default value.
- **_lang_**: your language. If you leave this setting to "auto" the plugin try to detect your language and then translate to english. This feature sometimes not recogize correctly input language so is preferred to set the lang settings to a specific language (eg. "lang":"it"). The "auto" settings introduces a small delay due to the language recognition phase. For best performances it is recommended to specify a language

## Third party plugins integration

You can integrate your plugin with cc_multliligual to have the translation funcitonality simply adding the following code to your plugin file:

```python
try:
    from cat.plugins.cc_multilingual.multilingual import (
        cc_multilingual_translate,
    )
except ModuleNotFoundError:

    def cc_multilingual_translate(text):
        return text

    pass
```

And then wrapping your English string into cc_multilingual_translate funtion:

```python
translated_string = cc_multilingual_translate("I am en english string")
```

**_N.B. The cc_multilingual_translate function translate string into the language defined in settings.json file of cc_multilingual plugin_**

Here an example of plugin (cheshire-cat-switch-user-role) that support integration with cc_multilingual:

[Cheshire Cat Switch User Role](https://github.com/team-sviluppo/cheshire-cat-switch-user-role)

## Logging

The plugin write a log before and after a translation, when detect automatically a language, before and after translate a document (or a chunk) or an url. Some logs have a "MSG-IN" or "MSG-OUT" prefix ti simply indentify if is a translation about a message received from user (MSG-IN) or a translation about a LLM repsonse ("MSG-OUT").

Examples of logs you can find:

- Language detected: {"language"="it"}
- MSG-OUT Starting translation: Response in english
- MSG-OUT End translation: Risposta in italiano
- MSG-IN Starting translation: Testo in italiano
- MSG-IN End translation: Text in english
- Start document/url chunk (1/6) translation from it to en
