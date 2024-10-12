# The schedule module of ComPeer, responsible for initialize schedule, eval the importance of event, and update the schedule.
from src.tools import load_prompt,get_today_info
from src.settings import USE_REAL_WORLD_INFORMATION
from datetime import datetime
from openai import OpenAI
import json
class schedule_module:
    def __init__(self,user_ids):
        self.user_ids=user_ids

    def initialize_schedule(self, reflection):
        for user_id in self.user_ids:
            guidance_prompt = load_prompt(f'schedule_generation_{user_id}.txt')
            print(f'Begin to generate the schedule of {user_id}.')
            if USE_REAL_WORLD_INFORMATION:
                today_data = get_today_info()
            else:
                today_data = ""
            schedule_is_json = False
            while not schedule_is_json:
                print(f"reflection of {user_id} is {reflection[user_id]}")
                client = OpenAI()
                schedule = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "system", "content": guidance_prompt + '\n' + 
                                                            " Environmental information, such as today’s date, temperature, and weather:" + 
                                                            str(today_data) + '\n' + 
                                                            "The reflection of today’s interaction, which summarizes the user’s current state and future challenges. You need to base your schedule for tomorrow’s support on its content: :" + 
                                                            reflection[user_id]+ '\n' +
                                                            "Now output the schedule."}],
                ).choices[0].message.content
                schedule = schedule.replace("```", "").replace("json","").strip()
                print(schedule)
                try:
                # transfer content to JSON
                    schedule_json = json.loads(schedule)
                    print(f"{user_id} generate successfully!")
                    schedule_is_json = True  
                    with open(f'schedule/today_schedule_{user_id}.json', 'w', encoding='utf-8') as f:
                        json.dump(schedule_json, f, ensure_ascii=False, indent=4)
                except json.JSONDecodeError:
                    print("it is not json and try begin...")

    
    def update_schedule(self, user_id, extracted_event):
        print(f"updating schedule...")
        print(f"the event is {extracted_event}")
        with open(f"schedule/today_schedule_{user_id}.json", "r",encoding="utf-8") as file:
            existing_data = json.load(file)
        updated_data = self.insert_sorted_json(existing_data, extracted_event)
        with open(f"schedule/today_schedule_{user_id}.json", "w",encoding="utf-8") as file:
            json.dump(updated_data, file, indent=4, ensure_ascii=False)
            print("update!")
    
    def insert_sorted_json(self,existing_data, new_data):
        new_time = new_data["Timing"]
        for i, data in enumerate(existing_data):
            if new_time < data["Timing"]:
                existing_data.insert(i, new_data)
                return existing_data
        existing_data.append(new_data)
        return existing_data
    
    def compute_importance(self, event):
        prompt=load_prompt('eval.txt')
        input=[{"role": "system", "content": prompt + event}]
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=input
        )
        try:
            float_number = float(response.choices[0].message.content)
        except ValueError:
        # return default
            float_number = 0.5
        return float_number
    