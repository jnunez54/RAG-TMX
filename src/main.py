import os

from agents import MainAgent
from config.config import GLOBAL_PATH
from config.logger_config import setup_logger
from database import DBHandler
from logging import DEBUG
from scrapper import Scrapper

logger = setup_logger(__name__, f"logs/{__name__}.log", console_level=DEBUG)


def create_db(db_handler: DBHandler):
    # Remove the current database
    if os.path.exists(f"{GLOBAL_PATH}/src/DB"):
        os.system(f"rm -r {GLOBAL_PATH}/src/DB")
        
    # Web scrapping
    scrapper = Scrapper()
    scrapper.get_urls()
    scrapper.get_content()
    
    # Store the data
    db_handler.store_segments(scrapper.content)
    logger.info(f"Data stored, {db_handler.collection.count()} segments stored")

def main():
    mode = "auto" # "auto" for the testing prompts
    db_handler = DBHandler()
    agent = MainAgent(db_handler)
    
    db_control = input("Do you want to create the database? The current database will be deleted (y/n): ")
    if db_control == "y":
        create_db(db_handler)
    
    elif db_control == "n":
        if db_handler.collection.count() == 0:
            logger.error("The database is empty, please create the database.")
            return
        
    # Test prompts
    prompts = ["Cuanto cuesta tramitar el CURP?",
               "Y el acta de nacimiento?",
               "En Puebla"]
    
    if mode == "auto":
        for prompt in prompts:
            print(f"User: {prompt}", flush=True)
            response = agent.chat(prompt)
            
            print("Assistant:", end=" ", flush=True)
            for i in response:
                print(i, end="", flush=True)
            print("\n", flush=True)
            
    else:
        while True:
            query = input("User: ")
            response = agent.chat(query)
            
            print("Assistant:", end=" ", flush=True)
            for i in response:
                print(i, end="", flush=True)
            print("\n", flush=True)
    
if __name__ == "__main__":
    main()