import json

from llama_index.core.llms import ChatMessage
import numpy as np
import tiktoken
from typing import *

from config.config import MERGING_SEPARATOR
from config.prompts import subquerying_system, subquerying_user
from client import ApiClient

client = ApiClient()

def cosine_similarity(x, y) -> float:
    """
    Compute the cosine similarity between two vectors.
    
    Args:
        x: The first vector.
        y: The second vector.
        
    Returns:
        float: The cosine similarity between the two vectors
    """
    # Closer to 0 means more similar
    return 1 - np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))

class SemanticChunker:
    def __init__(self, initial_threshold: float = 0.4, 
                 appending_threshold: float = 0.55, 
                 merging_threshold: float = 0.4, 
                 max_chunk_size: int = 1024):
        self.initial_threshold = initial_threshold
        self.appending_threshold = appending_threshold
        self.merging_threshold = merging_threshold
        self.max_chunk_size = max_chunk_size

    def create_initial_chunks(self, sentences: List[str]) -> List[str]:
        """Create initial chunks from the sentences."""
        initial_chunks: List[str] = []
        chunk = sentences[0]
        new = True
        for sentence in sentences[1:]:
            if new:
                if (cosine_similarity(client.get_embeddings(chunk), client.get_embeddings(sentence)) < self.initial_threshold 
                    and len(chunk) + len(sentence) + 1 <= self.max_chunk_size):
                    initial_chunks.append(chunk)
                    chunk = sentence
                    continue
                chunk_sentences = [chunk]
                
                if len(chunk) + len(sentence) + 1 <= self.max_chunk_size:
                    chunk_sentences.append(sentence)
                    chunk = MERGING_SEPARATOR.join(chunk_sentences)
                    new = False
                else:
                    new = True
                    initial_chunks.append(chunk)
                    chunk = sentence
                    continue
                last_sentences = MERGING_SEPARATOR.join(chunk_sentences[-2:])

            elif (cosine_similarity(client.get_embeddings(last_sentences), client.get_embeddings(sentence)) > self.appending_threshold
                and len(last_sentences) + len(sentence) + 1 <= self.max_chunk_size):
                chunk_sentences.append(sentence)
                last_sentences = MERGING_SEPARATOR.join(chunk_sentences[-2:])
                chunk += MERGING_SEPARATOR + sentence
            else:
                initial_chunks.append(chunk)
                chunk = sentence 
                new = True
        initial_chunks.append(chunk)
        return initial_chunks

    def merge_initial_chunks(self, initial_chunks: List[str]) -> List[str]:
        chunks: List[str] = []
        skip = 0
        current = initial_chunks[0]

        for i in range(1, len(initial_chunks)):
            # Avoid connecting same chunk multiple times
            if skip > 0:
                skip -= 1
                continue
            current_embedding = client.get_embeddings(current)
            if len(current) >= self.max_chunk_size:
                chunks.append(current)
                current = initial_chunks[i]

            # check if 1st and 2nd chunk should be connected
            elif (cosine_similarity(current_embedding, client.get_embeddings(initial_chunks[i])) > self.merging_threshold
                and len(current) + len(initial_chunks[i]) + 1 <= self.max_chunk_size):
                current += MERGING_SEPARATOR + initial_chunks[i]
            # check if there is a 3rd chunk
            
                
            # check if 1st and 3rd chunk are similar, if yes then merge 1st, 2nd, 3rd together
            elif (i+1 < len(initial_chunks) and  
                cosine_similarity(current_embedding, client.get_embeddings(initial_chunks[i])) > self.merging_threshold
                and len(current)
                + len(initial_chunks[i])
                + len(initial_chunks[i + 1])
                + 2
                <= self.max_chunk_size):
                current += (
                    MERGING_SEPARATOR
                    + initial_chunks[i]
                    + MERGING_SEPARATOR
                    + initial_chunks[i + 1]
                )
                skip = 1
            else:
                chunks.append(current)
                current = initial_chunks[i]

        chunks.append(current)
        return chunks
    
    def chunk(self, sentences: List[str]) -> List[str]:
        """
        Chunk the sentences into smaller chunks.
        
        Args:
            sentences: The sentences to chunk.
            
        Returns:
            chunks: The chunks created from the sentences.
        """
        initial_chunks = self.create_initial_chunks(sentences)
        merged_chunks = self.merge_initial_chunks(initial_chunks)
        return merged_chunks    

# Subqueying utility
def get_subqueries(query: str) -> list:
    """
    Generate subqueries for the given query.
    
    Args:
        query: The query to generate subqueries for.
        
    Returns:
        list: The generated subqueries
    """
    messages = [
        {"role": "system", "content": subquerying_system},
        {"role": "user", "content": subquerying_user.format(query)}
    ]
    subqueries = client.chat(messages)
    
    try:
        response = json.loads(subqueries)
        
    except:
        response = [query]
    return response

# Token counting
def count_tokens(string: str, encoding_name: str = "cl100k_base") -> int:
    """
    Count the number of tokens in a string.
    
    Args:
        string: The string to count the tokens of.
        encoding_name: The encoding to use for tokenization.
        
    Returns:
        int: The number of tokens in the string.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(string))

# Test merging
def main():
    chunker = SemanticChunker(
        initial_threshold=0.4,
        appending_threshold=0.55,
        merging_threshold=0.4,
        max_chunk_size=1024
    )
    texto = (
    "Pasaporte ordinario para menores de edad con la presencia de ambos padres o quienes ejercen patria potestad\n"
    "¿Planeas viajar al extranjero con tu hijo menor de edad? El pasaporte es un documento oficial de viaje, "
    "probatorio de nacionalidad e identidad, que solicita a las autoridades extranjeras proporcionen ayuda y protección.\n"
    "Documentos necesarios\n"
    "    Acreditación de nacionalidad\n"
    "    Acreditación de identidad\n"
    "    Comparecencia de los padres\n"
    "    Pago\n"
    "    Curp certificada\n"
    "¿Planeas viajar al extranjero con tu hijo menor de edad? El pasaporte es un documento oficial de viaje, "
    "probatorio de nacionalidad e identidad, que solicita a las autoridades extranjeras proporcionen ayuda y protección.\n"
    "Documentos necesarios Documento requerido \tPresentación\n"
    "Acta de nacimiento certificada por el Registro Civil. Sí el registro de nacimiento es extemporáneo, ocurrido "
    "después de 2 años de la fecha de nacimiento, se deberá presentar un documento complementario que se describe "
    "en el folleto “Documentación complementaria para actas de nacimiento con registro extemporáneo”.\n"
    "a) Para este supuesto, la Oficina de Pasaportes podrá consultar las bases de datos o sistemas a las que tenga acceso. "
    "De tal manera que, la generación del acta de nacimiento será por ese mecanismo, sin que sea necesario que usted la presente.\n"
    "b) Si de las consultas a las bases de datos o sistemas a las que tenga acceso la SRE, no se pueda acreditar la nacionalidad mexicana, "
    "la persona solicitante deberá entregar copia certificada del acta de nacimiento. En este caso, personal de la Oficina de Pasaportes "
    "le informará en el momento del trámite."
    )
    
    segments = texto.split("\n")
    print("Number of segments:", len(segments))
    print("-"*50)
    initial_chunks = chunker.create_initial_chunks(segments)
    print("Initial chunks:")
    for i, chunk in enumerate(initial_chunks):
        print(f"\nChunk {i}: {chunk}")
    print("-"*50)
    merged_chunks = chunker.merge_initial_chunks(initial_chunks)
    print("Merged chunks:")
    for i, chunk in enumerate(merged_chunks):
        print(f"\nChunk {i}: {chunk}")
    
if __name__ == "__main__":
    main()