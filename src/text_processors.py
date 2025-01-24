import json

from llama_index.core.llms import ChatMessage
import numpy as np
import tiktoken

from config.config import embeddings_model, llm
from config.prompts import subquerying_system, subquerying_user

def cosine_similarity(x, y) -> float:
    """
    Compute the cosine similarity between two vectors.
    
    Args:
        x: The first vector.
        y: The second vector.
        
    Returns:
        float: The cosine similarity between the two vectors
    """
    return np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))

def double_pass_merge(sentences, initial_threshold: float = 0.25, appending_threshold: float = 0.25, merging_threshold: float = 0.25) -> list:
    """
    Merge similar sentences into chunks.
    
    Args:
        sentences: The sentences to merge.
        initial_threshold: The similarity threshold for the first pass.
        appending_threshold: The similarity threshold for appending sentences.
        merging_threshold: The similarity threshold for merging chunks.
        
    Returns:
        list: The merged chunks.
    """
    embeddings = embeddings_model.get_text_embedding_batch(sentences)
    segments = list(zip(sentences, embeddings))
    
    # First pass
    chunks = []
    while segments:
        # First two segments
        chunk = [segments.pop(0)]
        if not segments:
            chunks.append(chunk)
            break
        if cosine_similarity(chunk[0][1], segments[0][1]) > initial_threshold:
            chunk.append(segments.pop(0))
            while segments:
                current_chunk_embedding = embeddings_model.get_text_embedding(chunk[-1][0] + chunk[-2][0])
                if cosine_similarity(current_chunk_embedding, segments[0][1]) > appending_threshold:
                    chunk.append(segments.pop(0))
                else:
                    break
        chunks.append(chunk)
        
    # Second pass
    merged_chunks = []
    while chunks:
        new_chunk = chunks.pop(0)
        if not chunks:
            merged_chunks.append(new_chunk)
            break
        # Similarity between chunks
        while chunks:
            merged_chunk_text = " ".join([sentence for sentence, _ in new_chunk])
            current_chunk_text = " ".join([sentence for sentence, _ in chunks[0]])
            embeddings = embeddings_model.get_text_embedding_batch([merged_chunk_text, current_chunk_text])
            
            if cosine_similarity(embeddings[0], embeddings[1]) > merging_threshold:
                new_chunk.extend(chunks.pop(0))
            elif len(chunks) > 1:
                next_chunk_text = " ".join([sentence for sentence, _ in chunks[1]])
                next_chunk_embedding = embeddings_model.get_text_embedding(next_chunk_text)
                if cosine_similarity(embeddings[0], next_chunk_embedding) > merging_threshold:
                    new_chunk.extend(chunks.pop(0))
                    new_chunk.extend(chunks.pop(0))
                else:
                    break
            else:
                break
        merged_chunks.append(new_chunk)    
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
        ChatMessage(role="system", content=subquerying_system),
        ChatMessage(role="user", content=subquerying_user.format(query))
    ]
    
    subqueries = llm.chat(messages).message.content    
    return json.loads(subqueries)["sqs"]

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