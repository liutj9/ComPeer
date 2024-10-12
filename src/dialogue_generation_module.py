# The dialogue generation module of ComPeer, including LLM_1(psychological_companion), LLM_2(passive_replyer), and LLM_3(proactive_sender) of ComPeer.

from src.tools import load_prompt
from openai import OpenAI

class psychological_companion:
    def __init__(self):
        LLM_1_response_role = load_prompt("psychological_companion_proactive.txt")
        LLM_1_proactive_role = load_prompt("psychological_companion_proactive.txt")
        self.response_role_prompt = LLM_1_response_role
        self.proactive_role_prompt = LLM_1_proactive_role

    def select_response_strategy(self, user_input):
        history = [{"role": "system", "content": self.response_role_prompt}]
        history.append({"role": "user", "content": user_input})
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=history
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    
    def select_proactive_strategy(self, event):
        message=[{"role": "system", "content":self.proactive_role_prompt+'\n'+str(event)}]
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=message
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content

class passive_replyer:
    def __init__(self):
        return
    
    def generate_passive_reply(self, user_input, related_memory, short_term_memory, selected_strategy):
        conversation_context = short_term_memory.copy()
        print(f"user input: {user_input}, related_memory:{related_memory}, selected_strategy:{selected_strategy}")
        conversation_context.append({"role":"user","content":user_input + '\n' + related_memory + '\n' + selected_strategy})
        # print(conversation_context[-1])
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=conversation_context
        )
        return response.choices[0].message.content

class proactive_sender:
    def __init__(self):
        return
    
    def generate_proactive_message(self, event, persona, selected_strategy):
        content = persona + '\n' + '\n The event information:'+ event + '\n' + selected_strategy
        print(f"event: {event}, selected_strategy:{selected_strategy}")
        conversation_context = [{"role":"system","content":content}]
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o", 
            messages=conversation_context
        )
        return response.choices[0].message.content




