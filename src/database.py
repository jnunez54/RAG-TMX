from chromadb import PersistentClient

from config.config import GLOBAL_PATH, embeddings_model
from config.logger_config import setup_logger

from text_processors import double_pass_merge, get_subqueries

logger = setup_logger(__name__, f"logs/{__name__}.log")

class DBHandler():
    def __init__(self):
        self.client = PersistentClient(f"{GLOBAL_PATH}/DB")
        self.collection = self.client.get_or_create_collection(name = 'processes',
                                                               metadata={"hnsw:space": "cosine"})        
    def store_segments(self, content):
        """
        Stores the segments of the content in the database.
        
        Args:
            content: The content to store.
        """       
        documents = []
        metadatas = []
        ids = []
        embeddings = []
        
        for process, content in content.items():
            logger.info(f"Chunking the content of the process: {process}")
            chunks = double_pass_merge(content["segments"])
            logger.info(f"Done: {len(chunks)} chunks created.")
            for i, chunk in enumerate(chunks):
                metadata = {"process_name" : process, "url": content["url"]}
                full_text = " ".join([segment for segment, _ in chunk])
                if len(full_text) > 10:
                    documents.append(full_text)
                    metadatas.append(metadata)
                    ids.append(f"{process}_{i}")
                    embeddings.append(embeddings_model.get_text_embedding(full_text))
            logger.info(f"Done: {i+1} chunks stored for process: {process}")
        self.collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
        
    def query_db(self, query, k=5, threshold = 0.5) -> list:
        """
        Returns the k most similar segments to the query.
        
        Args:
            query: The query to search for.
            k: The number of results to return.
            threshold: The similarity threshold. (Cosine distance is close to 0 for similar vectors)
        
        Returns:
            segments: The segments that are similar to the query.
            urls: The urls of the segments.
        """
        logger.debug(f"Querying the database for the query: {query}")
        subqueries = get_subqueries(query)
        logger.debug(f"Done: {len(subqueries)} subqueries created. Querying the database...")
        
        embeddings = embeddings_model.get_text_embedding_batch(subqueries)
        results = self.collection.query(embeddings, include=["metadatas", "documents", "distances"], n_results=k)
        
        segments = []
        urls = []
        for i, item in enumerate(results["distances"]):
            idxs = [idx for idx, distance in enumerate(item) if distance < threshold]
            for idx in idxs:
                segments.append(results["documents"][i][idx]) if results["documents"][i][idx] not in segments else None
                if results["metadatas"][i][idx]["url"] not in urls:
                    urls.append(results["metadatas"][i][idx]["url"])
                    
        return segments, urls