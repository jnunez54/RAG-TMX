# agents.py
# version 1.0
# description: Handles the agents of the system.
import json
from time import sleep

from client import ApiClient
from config.prompts import conv_rewrite_system, conv_rewrite_user, main_agent_system, main_agent_user, no_context_response
from text_processors import count_tokens

class MainAgent():
    """Main agent of the system."""
    def __init__(self, db_handler):
        """Initializes the main agent.
        
        Args:
            db_handler: The database handler.
        """
        self.db_handler = db_handler
        self.history = [] # History is locally stored
        self.client = ApiClient()
        
        self.original_query = ""
        self.rewrite_query = ""
        self.retrieved_context = ""
                
    def query_history(self, max_tokens: int = 1024) -> str:
        """
        Query the history of the conversation.
        
        Args:
            max_tokens (int): The maximum number of tokens to return.
            
        Returns:
            str: The history of the conversation.
        """
        history = ""
        for user, assistant in self.history:
            token = f"User: {user}\nAssistant: {assistant}\n"
            if count_tokens(history) + count_tokens(token) > max_tokens:
                break
            history += token
        return history
    
    def rewrite(self, query: str, history: str = "") -> str:
        """
        Rewrites the query according to the history of the conversation.
        
        Args:
            query (str): The query to rewrite.
            history (str): The history of the conversation.
            
        Returns:
            str: The rewritten query.
            
        """
        if history:
            messages  = [
                {"role": "system", "content": conv_rewrite_system},
                {"role": "user", "content": conv_rewrite_user.format(history, query)}
            ]
            response = self.client.chat(messages)
            response = json.loads(response)
            
            if response["q"] != "":
                query = response["q"]
        return query
    
    def chat(self, query: str):
        """
        Main chat function.
        Args:
            query (str): The query to send to the RAG.
        Yields:
            str: The response from the system.
        """
        # Conversational
        history = self.query_history()
        self.original_query = query
        query = self.rewrite(query, history)
        self.rewrite_query = query

        # Retrieve the context
        context, urls = self.db_handler.query_db(query)
        context = " ".join(context)
        
        # Chat
        messages = [
            {"role": "system", "content": main_agent_system},
        ]
        if context:
            messages.append({"role": "user", "content": main_agent_user.format(query, history, context, urls)})
        else:
            messages.append({"role": "user", "content": no_context_response})

        self.retrieved_context = context
        # Get the response
        response = self.client.stream_chat(messages)
        
        full_text = ""
        for i in response:
            full_text += i
            yield i
            
        self.history.append((query, full_text))
        
    def get_thinking(self):
        """
        Returns the thinking of the agent.
        
        Returns:
            str: The thinking of the agent.
        """
        return (
            "### Proceso\n"
            f"- **Query original** {self.original_query}\n"
            f"- **Query reescrita:** {self.rewrite_query}\n"
            f"- **Contexto recuperado:**\n\n{self.retrieved_context}"
        )

        
# Test
def main():
    from database import DBHandler
    db_handler = DBHandler()
    agent = MainAgent(db_handler)
    
    while True:
        query = input("\nQuery: ")
        if query == "exit":
            break    
        response = agent.chat(query)
        for i in response:
            print(i, end="", flush=True)
            sleep(0.1)

        toughts = agent.get_thinking()
        print("\nThinking:")
        print(toughts)
            
if __name__ == "__main__":
    main()