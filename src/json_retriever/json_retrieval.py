import os
from dotenv import load_dotenv
import instructor
import json

from uuid import uuid4
from retriever import doc_retriever, doc_chunker, doc_embedder
from retriever.init_phoenix import init_phoenix
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_ollama import OllamaEmbeddings


class JSONRetriever():
    def __init__(self, collection_name ="json_embedding"):
        self.collection_name = collection_name
        self.tracer = init_phoenix("json_retriever")
        self.chunker = doc_chunker.DocChunker()
        self.embeddings = OllamaEmbeddings(model=os.getenv("EMB_MODEL"),validate_model_on_init=True,base_url=os.getenv("EMB_BASE_URL"))
        self.client = QdrantClient(path=os.getenv("PROJECT_DIR")+"/json_retriever/local_data/embeddings")
        self.create_collection(self.collection_name)
        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=self.embeddings
        )
        self.embedder = doc_embedder.DocEmbedder(self.embeddings,self.client,self.vector_store)
    
    def retrieve(self, query, num_results):
        query_emb = self.embedder.get_embedding(query)
        response = self.vector_store.similarity_search(query_emb, k=num_results)
        return response
    
    def embed_json(self,json):
        chunks = self.chunker.chunk_json(json_data)
        self.embedder.create_vectorstore(self.collection_name)
        embedding = self.embedder.create_json_embedding(chunks, collection_name)

    def create_collection(self, name:str):
        #Create new collection with the given name if it does not exist
        if not self.client.collection_exists(name):
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=4096, distance=Distance.COSINE),
            )



class JSONEmbedder(doc_embedder.DocEmbedder):
    def __init__(self,embeddings,client,vector_store):
        super().__init__()
        self.embeddings = embeddings
        self.client = client
        self.vector_store = vector_store

    def create_json_embedding(self,json_data, collection_name):
        
        uuids = [str(uuid4()) for _ in range(len(json_data))]
        self.vector_store.add_texts(
            texts=json_data,
            ids=uuids)


class JSONChunker:
    
    def __init__(self):
        pass

    def chunk_json(self, json):
        splitter = RecursiveJsonSplitter(max_chunk_size=300)
        json_chunks = splitter.split_json(json_data=json, convert_lists=True)       
        return json_chunks


class RetrievalController:

    def __init__(self):
        pass

    def simple_query(self):
        pass


if __name__ == "__main__":
    load_dotenv()
    json_chunker = JSONChunker()
    with open("src\json_retriever\local_data\Datenmodell-2026-06-10_18-13-17-Entwicklung.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
   
    
    #json_embedder = JSONEmbedder()
    
    collection_name = "json_collection_2"
    
    json_retriever = JSONRetriever(collection_name)

    json_retriever.embed_json(json_data)

    json_retriever.retrieve("Wie kann ich ein Objekt anlegen?")

    """

    
    #print(chunks)
    for i, c in enumerate(chunks):
        chunks[i]=str(c)
        print(f"Chunk{i} with a length of {len(c)}: {c}")
    #print(chunks)
    
    
    print(len(chunks))
    
    
    json_embedder.client.close()"""



    
    

