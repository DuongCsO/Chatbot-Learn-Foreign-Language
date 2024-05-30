import os
import yaml
from typing import Optional
from python.utils import (
    split_to_sentences,
    init_openai,
    get_error_message_from_exception
)
import unidecode
from flask import Flask, render_template, request, jsonify, url_for, redirect, Response
import python
from python.memory import Memory
from python.config import Config
from python.chatbot import Chatbot
from python.app_cache import AppCache
from python.consts import TEMP_DIR_NAME, TEMP_DIR, LTM_DIR, SAVED_SESSION_FILE, MALE_TUTORS, FEMALE_TUTORS, INPUT_LANGUAGES


app = Flask(__name__)


config: Optional[Config] = None
memory: Optional[Memory] = None
chatbot: Optional[Chatbot] = None
app_cache = AppCache()
voices_by_features = dict()
audio_queue_reject_remaining_fragments = False


@app.template_filter('convert_special')
def convert_special_letters(input_str):
    return unidecode(input_str)


@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Web page, setup page
    """
    if request.method == 'POST':
        # filename = request.form.get('filename')
        filename = "config.yml"
        app_cache.config_file = filename
        data = {
            "user": {
                "name": request.form.get('username'),
                "gender": request.form.get('gender')
            },
            "bot": {
                "name": "Alex"
            },
            "language": {
                "native": request.form.get('user-lang-dropdown').lower(),
                "learning": request.form.get('tutor-lang-dropdown').split("-")[0].lower(),
                "level": request.form.get('lang-level')
            },
            "behavior": {
                "auto_send_recording": bool(request.form.get('auto-send-switch'))
            }
        }
        with open(os.path.join(os.getcwd(), filename), 'w') as outfile:
            yaml.dump(data, outfile, allow_unicode=True)
        global memory, chatbot, config
        should_restart = bool(request.args.get('restart', 0))
        if should_restart:
            restart()
        memory = Memory()
        config = Config()
        config.update_from_yml_file('config.yml')
        python.utils.init_openai(config)
        try:
            chatbot = Chatbot(config, memory)
        except Exception as e:
            app_cache.server_errors.append(python.utils.get_error_message_from_exception(e))
        if os.path.exists(TEMP_DIR):
            for f in os.listdir(TEMP_DIR):
                os.remove(os.path.join(TEMP_DIR, f))
        else:
            os.makedirs(TEMP_DIR)

        if not os.path.exists(LTM_DIR):
            os.makedirs(LTM_DIR)
        return jsonify({'status': 'successfully'})
    else:
        return render_template('index.html',
                               input_languages_codes_and_names=[[python.language.language_name_to_iso6391(lang), lang]
                                                                for lang in INPUT_LANGUAGES],
                               output_languages_locales_and_names=[[k, python.language.locale_code_to_language(k, name_in_same_language=True)]
                                                                   for k in voices_by_features.keys()]
                               )


@app.route("/text_to_speech", methods=['POST'])
def get_text_to_speech():
    data = request.get_json()
    print(data)
    text = data["message"]
    text_index = data["message_index"]
    filepath = os.path.join(TEMP_DIR, f"bot_speech_{text_index}.mp3")
    python.speech.text_to_speech(config.language.learning, text, filepath);
    return Response(filepath)


@app.route('/get_response', methods=['POST'])
def get_response():
    """
    Get response from chatbot
    """
    error_message = None
    try:
        is_initial_message = bool(int(request.form['is_initial_message']))
        app_cache.generated_message = chatbot.get_response(is_initial_message)
        app_cache.sentences_counter = 0
    except Exception as e:
        error_message = python.utils.get_error_message_from_exception(e)
    finally:
        return jsonify({'message': app_cache.generated_message,
                        'message_index': len(memory),
                        'error': error_message})


@app.route('/translate_text', methods=['POST'])
def translate_text():
    """
    Translate message
    """
    message = request.form["text"]
    sender = request.form["sender"]
    lang = config.language.native if sender == "assistant" else config.language.learning
    lang2 = config.language.learning if sender == "assistant" else config.language.native
    try:
        translated = python.language.translate2(message, lang2, lang)
    except Exception as e:
        app_cache.server_errors.append(python.utils.get_error_message_from_exception(e))
        translated = None
    return jsonify({'message': translated})


@app.route('/store_message', methods=['POST'])
def store_message(sender: Optional[str] = None, message: Optional[str] = None):
    """
    Save message in memory

    :param sender: role of message creator ("system", "user" or "assistant")
    :param message: message text
    """
    sender = sender or request.form['sender']
    message = message or request.form['message']
    memory.add(role=sender, message=message)
    return jsonify({'status': 'success'})


@app.route('/check_server_errors', methods=['GET'])
def check_server_errors():
    """
    Check for errors saved in `app_cache`, and display on web UI
    """
    server_errors = app_cache.server_errors.copy()
    app_cache.server_errors = []
    return jsonify({'server_errors': server_errors})


def restart() -> None:
    """
    Restart app
    """
    global config
    try:
        config = Config.from_yml_file(app_cache.config_file)
    except FileNotFoundError:
        app_cache.server_errors.append("Config file not found. Go to /setup to configure the app.")
        config = Config({'bot': {'voice': 'xx-xx'}})
    if app_cache.keys_file:
        config.update_from_yml_file(app_cache.keys_file)
    python.utils.init_openai(config)


if __name__ == '__main__':
    app.run()
