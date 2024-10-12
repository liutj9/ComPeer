# The extact_module of ComPeer, including event detector and reflection_module.
from src.tools import load_prompt
from datetime import datetime
from openai import OpenAI
import json
import os

class event_detector:
    def __init__(self,role):
        self.role_prompt = load_prompt(role)
    
    def extract_event(self, user_id, dialogue_content): 
        '''
        extract user event from a round of dialogue.
        '''  
        # step1: get current timing to help LLM reason the timing of proactive message
        now = datetime.now().strftime("%H:%M")
        client = OpenAI()
        dialogue_content.insert(0, {"role": "system", "content": self.role_prompt+'\n'+'Time:'+str(now)+'\n Conversation:'})
        
        # step2: identify events
        event = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=dialogue_content
        ).choices[0].message.content
        
        # step3: transfer output into json that can queue to the schedule.
        event_is_json, extracted_event = self.process_output(event)
        print(event_is_json, extracted_event)
        return event_is_json,extracted_event
    
    def process_output(self,output):
        if output==None:
            return False, output
        try:
            output=output.replace("'''", "").replace("json","").strip()
            output_json = json.loads(output)
            if "Timing" in output_json and "Content" in output_json:
                return True, output_json
        except json.JSONDecodeError:
            # if not json, do not queue to the schedule.
            return False, output
    
class reflection_module:
    def __init__(self, role_prompt, user_ids):
        self.user_ids = user_ids
        self.role = load_prompt(role_prompt)
        self.summary_history = {user_id: [{"role": "system", "content": self.role}] for user_id in user_ids}
        self.reflection_output = {user_id: "" for user_id in user_ids}

        for user_id in self.user_ids:
            log_file = f"reflection_logs/reflection_log_{user_id}.jsonl"
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    self.summary_history[user_id] = [json.loads(line) for line in f]
            else:
                self.summary_history[user_id] = [{"role": "system", "content": self.role}]
                self.save_to_log(user_id, self.summary_history[user_id][0])

    def save_to_log(self, user_id, entry):
        log_file = f"reflection_logs/reflection_log_{user_id}.jsonl"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')

    def store_today_history(self, user_id, role, content):
        entry = {"role": role, "content": content}
        self.summary_history[user_id].append(entry)
        self.save_to_log(user_id, entry)

    def reflection(self):
        for user_id in self.user_ids:
            if len(self.summary_history[user_id]) > 1:
                client = OpenAI()
                messages = self.summary_history[user_id]
                self.reflection_output[user_id] = client.chat.completions.create(
                    model="gpt-4o", messages=messages).choices[0].message.content

                self.summary_history[user_id] = [{"role": "system", "content": self.role}]
                self.save_to_log(user_id, self.summary_history[user_id][0])

        return self.reflection_output