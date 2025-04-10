from chromadb import PersistentClient
from config.config import GLOBAL_PATH
from config.logger_config import setup_logger
from tqdm import tqdm

from client import ApiClient
from text_processors import get_subqueries, SemanticChunker

client = ApiClient()
chunker = SemanticChunker()
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
        
        logger.info(f"Storing {len(content)} processes ({sum([len(content[process]['segments']) for process in content])} segments) in the database...")
        for process, content in tqdm(content.items()):
            #logger.info(f"Chunking the content of the process: {process}")
            chunks = chunker.chunk(content["segments"])
            #logger.info(f"Done: {len(chunks)} chunks created.")
            for i, chunk in enumerate(chunks):
                metadata = {"process_name" : process, "url": content["url"]}
                if len(chunk) > 10:
                    documents.append(chunk)
                    metadatas.append(metadata)
                    ids.append(f"{process}_{i}")
                    embeddings.append(client.get_embeddings(chunk))
            #logger.info(f"Done: {i+1} chunks stored for process: {process}")
        self.collection.add(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=documents)
        logger.info(f"Done: {len(documents)} segments stored in the database.")
    
    def query_db(self, query, k=3, threshold = 0.5) -> list:
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
        
        embeddings = [client.get_embeddings(subquery) for subquery in subqueries['sqs']]
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
    
# Test
def main():
    db = DBHandler()
    print(f"{db.collection.count()} items.")
    
    text = "Acta de nacimiento"    
    res = db.query_db(text, 5)
    print(res)

if __name__ == "__main__":
    main()