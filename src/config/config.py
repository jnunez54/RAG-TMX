import os

GLOBAL_PATH = (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))).replace("\\", "/")
URL = "https://www.gob.mx/tramites/"
MODEL = "ibm-granite/granite-3.2-2b-instruct"
EMBEDDINGS_MODEL = "jinaai/jina-embeddings-v3"
MERGING_SEPARATOR = ""