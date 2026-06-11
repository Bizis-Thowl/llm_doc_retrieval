import os
from dotenv import load_dotenv
import instructor
import json

from uuid import uuid4
from retriever import doc_retriever, doc_chunker, doc_embedder, init_phoenix
from langchain_text_splitters import RecursiveJsonSplitter
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_ollama import OllamaEmbeddings







class JSONRetriever(doc_retriever.DocRetriever):
    def __init__(self):
        self.tracer = init_phoenix("json_retriever")
        self.embedder = doc_embedder.DocEmbedder()
        self.chunker = doc_chunker.DocChunker()


class JSONEmbedder(doc_embedder.DocEmbedder):
    
    def __init__(self):
        super().__init__()
        self.client = QdrantClient(path="/src/json_retriever/local_data/embeddings") #


    def create_vectorstore(self, name:str):
        #Delete preexisting collection with the same name
        #self.client.delete_collection(name)
        #Create new collection with the given name
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=4096, distance=Distance.COSINE),
        )

    def create_json_embedding(self,json_data, collection_name):
        embeddings = OllamaEmbeddings(model="qwen3_emb_8b_40k",validate_model_on_init=True,base_url=os.getenv("EMB_BASE_URL"))
        vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=collection_name,
            embedding=embeddings
        )
        uuids = [str(uuid4()) for _ in range(len(json_data))]
        vector_store.add_texts(
            texts=json_data,
            ids=uuids)

    


class JSONChunker:
    
    def __init__(self):
        pass

    def chunk_json(self, json):
        splitter = RecursiveJsonSplitter(max_chunk_size=300)
        json_chunks = splitter.split_json(json_data=json)       
        return json_chunks


if __name__ == "__main__":
    load_dotenv()
    json_chunker = JSONChunker()
    with open("src\json_retriever\local_data\Datenmodell-2026-06-10_18-13-17-Entwicklung.json", "r", encoding="utf-8") as f:
        json_data = json.load(f)
    chunks = json_chunker.chunk_json(json_data)
    #for chunk in chunks:
    #        print(chunk)
    
    json_embedder = JSONEmbedder()

    collection_name = "json_collection_1"
    print(chunks)
    for i, c in enumerate(chunks):
        chunks[i]=str(c)

    #json_embedder.create_vectorstore(collection_name)

    embedding = json_embedder.create_json_embedding(chunks, collection_name)



    
    

