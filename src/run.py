# The action of ComPeer in the interaction, including sending passive and proactive message, event detect, reflect, schedule management
from src.dialogue_module import dialogue_module
from src.extract_module import event_detector, reflection_module
from src.schedule_module import schedule_module
from src.tools import get_today_info,load_prompt
import requests
import random
import json
import threading
from datetime import datetime,timedelta,time,timezone

east_8 = timezone(timedelta(hours=8))

def load_user_ids(file_path):
    try:
        with open(file_path, 'r') as file:
            return [int(line.strip()) for line in file if line.strip()]
    except FileNotFoundError:
        return []

user_ids = load_user_ids('user_state/user_ids.txt') # user_lists
chat_agent = dialogue_module(user_ids) # dialogue_module (include memory and dialogue generation module)
schedule_assistant = event_detector('event_detector.txt') # event_detector
reflector = reflection_module('reflection.txt', user_ids) # reflection_module
schedule_generator = schedule_module(user_ids) # schedule module
user_flag = {user_id:True for user_id in user_ids} # user_flag means user previous reaction.
last_proactive_time = {user_id:datetime.now(east_8) for user_id in user_ids} # last_proactive_time means user's previous react timing

def send_message(user_id, message):
    get_request = "http://127.0.0.1:5700/send_private_msg?user_id={}&message={}".format(user_id, message)
    requests.get(get_request)

def run_passive_reply(user_id,user_input):
    response = chat_agent.send_passive_reply(user_id, user_input)
    user_flag[user_id] = True
    send_message(user_id,response)

    reflector.store_today_history(user_id, "user", user_input)
    reflector.store_today_history(user_id, "assistant", response)
    
    return response

def run_event_detector(user_id, dialogue_content):
    event_is_json, extracted_event = schedule_assistant.extract_event(user_id,dialogue_content)
    if event_is_json == True:
        schedule_generator.update_schedule(user_id,extracted_event)

def load_schedule(user_id):
    with open(f'schedule/today_schedule_{user_id}.json', 'r', encoding='utf-8') as f:
        return json.load(f)
    
def run_proactive_message():
    now = datetime.now(east_8).strftime("%H:%M")
    print("now is "+str(now))
    print("user_ids is"+str(user_ids))
    
    for user_id in user_ids:
        print(f"{user_id}'s flag is {user_flag[user_id]}")
        for event in load_schedule(user_id):
            print(event)
            now_time = datetime.now(east_8)
            if now_time-last_proactive_time[user_id] >= timedelta(hours=3) and user_flag[user_id] == False:
                user_flag[user_id]=True
            # step1: user_flag: consider user's previous reaction.
            if now == event['Timing'] and user_flag[user_id] == True:
                random_float = random.random()
                # step2: eval importance of the event.
                event_importance = schedule_generator.compute_importance(str(event))
                print(f"this event's importance is {event_importance}")
                if random_float >= event_importance:
                    print(f"Random_float is {random_float} and threshold is {event_importance}. Therefore decide not to send")
                    continue
                print("Begin to send proactive message.")
                # step3: generate proactive message to the user. 
                proactive_message = chat_agent.send_proactive_message(user_id, event)
                print(f"The proactive message to {user_id} is '{proactive_message}'.")
                # user_flag will be true until user reply or to the next day.
                user_flag[user_id] = False
                last_proactive_time[user_id] = datetime.now(east_8)
                send_message(user_id, proactive_message)
                reflector.store_today_history(user_id, "assistant", proactive_message)
    threading.Timer(60, run_proactive_message).start() 

def run_schedule_initialization():
    now = datetime.now(east_8)
    print("generate is waiting...")
    if now.hour == 23 and now.minute == 59:
        for user_id in user_ids:
            user_flag[user_id] = True
        reflction_outputs=reflector.reflection()
        schedule_generator.initialize_schedule(reflction_outputs)
    threading.Timer(60, run_schedule_initialization).start()
