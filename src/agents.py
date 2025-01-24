import json
from time import sleep


from llama_index.core.llms import ChatMessage

from config.config import llm
from config.prompts import conv_rewrite_system, conv_rewrite_user, main_agent_system, main_agent_user, no_context_response
from text_processors import count_tokens

class MainAgent():
    def __init__(self, db_handler):
        self.db_handler = db_handler
        self.history = [] # History is locally stored for development purposes, it should be stored in a database later..
        self.llm = llm
        
    def query_history(self, max_tokens = 1024):
        history = ""
        for user, assistant in self.history:
            token = f"User: {user}\nAssistant: {assistant}\n"
            if count_tokens(history) + count_tokens(token) > max_tokens:
                break
            history += token
        return history
    
    def rewrite(self, query,  history):
        if history:
            messages = [ChatMessage(role="system", content=conv_rewrite_system),
                        ChatMessage(role="user", content=conv_rewrite_user.format(history, query))]
            response = llm.chat(messages)
            response = json.loads(response.message.content)
            
            if response["q"] != "":
                query = response["q"]
        return query
    
    def chat(self, query):
        # Conversational
        history = self.query_history()
        query = self.rewrite(query, history)

        # Retrieve the context
        context, urls = self.db_handler.query_db(query)
        context = " ".join(context)
        
        # Chat
        messages = [ChatMessage(role="system", content=main_agent_system), ]
        if context:
            messages.append(ChatMessage(role="user", content=main_agent_user.format(query, history, context, urls)))
        else:
            messages.append(ChatMessage(role="user", content=no_context_response))

        # Get the response
        response = llm.stream_chat(messages)
        
        text_prev = ""
        full_text = ""
        for i in response:
            sleep(0.015)
            text = i.message.content.replace(text_prev, "")
            text_prev = i.message.content
            full_text += text

            yield text
        
        self.history.append((query, full_text))