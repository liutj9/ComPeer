Here is the prompt of ComPeer. We have listed these prompt on the appendix in our [paper]([ComPeer: A Generative Conversational Agent for Proactive Peer Support (arxiv.org)](https://arxiv.org/pdf/2407.18064)).

- `personas_{user_id}.txt`: The prompt of CA's Personas Initialization.
- `event_detector.txt`: The prompt of Event Detector Module.
- `reflection.txt`: The prompt of the Reflection Module.
- `schedule_generation_{user_id}.txt`: The prompt of the Schedule Module for schedule generation.
- `eval.txt`: The prompt of the Schedule Module for evaluate importance of the event.
- `psychological_companion_proactive.txt`/`psychological_companion_reply.txt`:The prompt of the LLM-1 in the Dialogue Generation Module. 
- `proactive_{user_id}.txt`: The prompt of the LLM-3 in the Dialogue Generation Module

For the prompt of LLM-2 in Dialogue Generation Module, it has been combined in the code (`src/dialogue_module.py`).

