# Dialogue module of ComPeer, which combine the dialogue generation module and memory module.
import logging
from typing import Union
import math
import os 
from datetime import datetime
from openai import OpenAI
import json
from langchain_openai import OpenAIEmbeddings

from src.dialogue_generation_module import psychological_companion, passive_replyer, proactive_sender
from src.tools import load_prompt
from src.VectorDB import vectorDB
from src.settings import API_KEY
from src.memory import Memory

class dialogue_module:
    def __init__(self,user_ids):
        # include memory module and dialogue generation module
        self.memory_module = Memory(user_ids)
        self.LLM_1 = psychological_companion()
        self.LLM_2 = passive_replyer()
        self.LLM_3 = proactive_sender()
    
    def send_passive_reply(self, user_id, user_words):
        db_memory = []
        # step1: LLM_1 select strategy
        selected_strategy = "Dialogue strategy suggestions: you should refer to these strategies to organize dialogue content:"
        strategy = self.LLM_1.select_response_strategy(user_words)
        selected_strategy += strategy
        print(f"selected_strategy is {strategy}")
        # step2: sent related memory and memory to LLM_2
        relative_memory, relativeness = self.memory_module.search_related_memory(user_id,user_words)
        mem_info = ''
        for i in range(len(relative_memory)):
            mem_info += f'{relative_memory[i]}[relativeness: {relativeness[i]}]\n'

        if len(relative_memory) > 0:
            memory_prompt = f'Related memory: The memory that related to the dialogue:\n\n{str(relative_memory)}'
        else:
            memory_prompt = ''
        
        # step3: LLM_2 generate passive reply
        response=self.LLM_2.generate_passive_reply(user_words, memory_prompt, self.memory_module.short_term_memory[user_id], selected_strategy)
        
        # step4: Update memory
        db_memory.append({"role":"user", "content":user_words})
        db_memory.append({"role":"assistant", "content":response})
        self.memory_module.store_short_term_memory(user_id, db_memory)
        return response
        
    def send_proactive_message(self, user_id, event):

        # step1: LLM_1 select strategy
        selected_strategy = "Dialogue strategy suggestions: you should refer to these strategies to organize dialogue content:"
        selected_strategy += self.LLM_1.select_proactive_strategy(str(event))
        
        # step2: set prompt of LLM_3
        persona = self.memory_module.proactive_personas[user_id]
        
        # step3: LLM_3 generate the proactive memssage
        message = self.LLM_3.generate_proactive_message(str(event),persona, selected_strategy)
        
        # step4: Update the Memory
        self.memory_module.store_short_term_memory(user_id,[{"role":"assistant", "content":message}])
        return message

