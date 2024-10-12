from flask import Flask, request, g
import requests
import yaml
import threading
import queue
import time
from datetime import datetime
import json
import requests
from flask import Flask, request, g
import yaml
from typing import Tuple
from src.run import run_passive_reply,run_event_detector,run_proactive_message,run_schedule_initialization,schedule_generator,user_ids
import os
from src.settings import API_KEY, BASE_URL

os.environ["OPENAI_API_BASE"] = BASE_URL
os.environ["OPENAI_API_KEY"] = API_KEY
app = Flask(__name__)

last_check=None
last_length=None
user_states = {}


@app.route('/', methods=["POST"])
def post_data():
    # send passive reply
    # global last_length,last_check,messages
    raw_package: dict = request.get_json()
    if 'message_type' in raw_package:
        message_type = raw_package['message_type']
        user_id = raw_package['sender']['user_id']
        message = raw_package['message']
        user_states[user_id]["messages"].append({"role": "user", "content": message})
        print(f"user_id is {user_id}, messages are"+str(message))
        response = run_passive_reply(user_id, message)
        user_states[user_id]["messages"].append({"role": "assistant", "content":response})
        print(f"messages length is {len(user_states[user_id]['messages'])}")

        # last_check is the user latest reply timing, last_length means the whole length in a round of conversation. 
        user_states[user_id]["last_check"]=time.time()
        user_states[user_id]["last_length"]=len(user_states[user_id]["messages"])
        print(f"{user_id}'s last length is "+str(user_states[user_id]["last_length"]))
    return 'ok'

def event_detect():
    for user_id in user_ids:
        # judge whether single round of conversation end and prevent repeated detect.
        if time.time() - user_states[user_id]["last_check"] >= 60 and len(user_states[user_id]["messages"]) == user_states[user_id]["last_length"] and len(user_states[user_id]["messages"]) != 0:
            print(f"begin event detecting for {user_id}...")
            print(f"dialogue content in {user_id} is:{user_states[user_id]['messages']}")
            run_event_detector(user_id,user_states[user_id]["messages"])
            user_states[user_id]["messages"]=[]
    threading.Timer(10, event_detect).start()

def get_host_port() -> Tuple[str, int]:
    with open('./config.yml', 'r', encoding='utf-8') as f:
        obj = yaml.load(f.read(), Loader = yaml.FullLoader)
    url = obj['servers'][0]['http']['post'][0]['url']
    host, port = url.replace('http://', '').split(':')
    return str(host), int(port)

thread1 = threading.Thread(target=run_schedule_initialization)
thread2 = threading.Thread(target=run_proactive_message)
thread3 = threading.Thread(target=event_detect)


if __name__ == '__main__':
    initial_reflection = {}
    for user_id in user_ids:
        user_states[user_id] = {"last_check": time.time(), "last_length": None, "messages": []}
        initial_reflection[user_id]=""
    # first initialize schedule
    # schedule_generator.initialize_schedule(initial_reflection)
    print(f"user_ids is...{user_ids}")
    print("finish init!")
    last_check=time.time()
    from gevent import pywsgi
    thread1.start()
    thread2.start()
    thread3.start()
    host, port = get_host_port()
    server = pywsgi.WSGIServer(
        listener=(host, port),
        application=app,
        log=None
    )
    server.serve_forever()