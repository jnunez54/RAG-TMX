import os

from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

GLOBAL_PATH = (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace("\\", "/")
URL = "https://www.gob.mx/tramites/"
OPEN_AI_API_KEY = "your_openai_api_key"
MODEL = "gpt-4o-mini"
EMBEDDINGS_MODEL = "text-embedding-3-small"

os.environ["OPENAI_API_KEY"] = OPEN_AI_API_KEY

embeddings_model = OpenAIEmbedding(model=EMBEDDINGS_MODEL)
llm = OpenAI(model=MODEL)