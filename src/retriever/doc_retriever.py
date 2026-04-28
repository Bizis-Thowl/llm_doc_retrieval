import os
from dotenv import load_dotenv
import instructor



import numpy as np
#import tiktoken
from openai import OpenAI
#from typing import Dict, Any
from opentelemetry.trace import StatusCode

from retriever.prompts.qa_prompt import QA_SYSTEM_PROMPT, QA_RAG_PROMPT, SELECTION_SYSTEM_PROMPT, SELECTION_PROMPT
from retriever.doc_chunker import DocChunker
from retriever.doc_embedder import DocEmbedder
from retriever.response_model.Retriever import URLRetrievalResponse, URLSelectionResponse

from retriever.init_phoenix import init_phoenix
#from process_extraction.response_model.Process import ProcessResponse

class DocRetriever:

    """
    Retrieval of documents making use of LLMs. 
    """
    def __init__(self, embedder: DocEmbedder | None, scraped_url):
        #self.client_emb = self.init_client_emb()
        if embedder is not None:
            self.embedder = embedder
        else:
            self.embedder = DocEmbedder()
        self.client = self.init_client()
        self.tracer = init_phoenix("doc-retrieval")
        self.scraped_url = scraped_url

    def init_client(self):
        # Initialize OpenAI client
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))
        client = instructor.from_openai(client, mode=instructor.Mode.JSON)
        return client
    """
    def init_client_emb(self):
        client_emb = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("EMB_BASE_URL"))
        client_emb = instructor.from_openai(client_emb, mode=instructor.Mode.JSON)
        return client_emb
    
    # After: https://learn.microsoft.com/en-us/azure/foundry/openai/tutorials/embeddings 
    
    def tokenize(self, df_text, token_limit):
        tokenizer = tiktoken.get_encoding("cl100k_base")
        df_text['n_tokens'] = df_text["text"].apply(lambda x: len(tokenizer.encode(x)))
        df_text = df_text[df_text.n_tokens<token_limit]
        return df_text
    """
    def cosine_similarity(self, a, b):
        # Return cosine similarity between two embeddings
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search_docs(self,df, user_query, df_chunk_emb, top_n=4):
        """
        Searches documents for the highest similarity between chunk-embeddings and the embedded query
        """
        model = os.getenv("EMB_MODEL")
        embedding = self.embedder.get_embedding(user_query, model=model)
        
        df_chunk_emb["similarities"] = df_chunk_emb['embedding'].apply(lambda x: self.cosine_similarity(x, embedding))

        res = (df_chunk_emb.sort_values("similarities", ascending=False).head(top_n))
        return res
    
    
    def create_prompt(self, search_result: str, query_str: str):
        prompt = QA_RAG_PROMPT.format(search_result,query_str=query_str)    
        return prompt
    """
    def refine_prompt(self, context_str: str,explain_str: str,query_str: str, existing_answer: str):
        prompt = QA_REFINE_PROMPT.format(context_str=context_str,explain_str=explain_str,query_str=query_str,existing_answer=existing_answer)
        return prompt
    """

    def get_url(self, search_res, df_text):
        dir = df_text.loc[df_text['name'] == str(search_res['name'])]['url'].values[0]
        sub_url = dir.split("/skim/")[1]
        url = self.scraped_url+"skim/"+sub_url
        return url
    

    def query(self, user_query, df, top_n = 4, response_model = URLRetrievalResponse): #context,
        MODEL = os.getenv("MODEL")
        search_res = self.search_docs(df,user_query, top_n=top_n)
        prompt = self.create_prompt(search_res,user_query)
        
        for i, res in enumerate(search_res):
            with self.tracer.start_as_current_span("Process", openinference_span_kind="agent") as span:
                span.set_input(prompt)
                
                response = self.client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {"role": "system", "content": QA_SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ],
                    response_model=response_model
                )
                span.set_output(response.model_dump())
                span.set_status(StatusCode.OK)
                #prompt = self.refine_prompt(context,search_res,user_query,response)
        return response
    
    def query_select(self, user_query, df, df_chunk_emb,response_model = URLSelectionResponse):
        """
        Lets a language model pick the best result from the top 3 retrieved results and returns a response
        """
        MODEL = os.getenv("MODEL")
        # Embedding driven search of the document chunks for semantic similarity
        search_res = self.search_docs(df,user_query, df_chunk_emb, top_n=3)
        search_res = search_res.reset_index(drop = True)
        prompt = SELECTION_PROMPT.format(user_query = user_query,
                                      chunk_1 =search_res.loc[0]['chunk'],
                                      chunk_2 =search_res.loc[1]['chunk'],
                                      chunk_3 =search_res.loc[2]['chunk'])
        
        # Query to language model that should pick out the best chunk from the search results
        with self.tracer.start_as_current_span("Process", openinference_span_kind="agent") as span:
            span.set_input(prompt)
            
            response = self.client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SELECTION_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_model=response_model
            )
            span.set_output(response.model_dump())
            span.set_status(StatusCode.OK)
        
        # Extract chunk from response
        chunk_res = search_res.loc[int(response.chunk_nr)-1]['chunk']
        response.chunk ={'chunk': chunk_res}
        response.url = self.get_url(search_res.loc[int(response.chunk_nr)-1], df)
        #print(chunk_res)
        
        return response
    


class Retriever_Controller:
    
    _scraped_url = "https://www.th-owl.de/"
    embedder = DocEmbedder()
    retriever = DocRetriever(embedder=embedder,scraped_url=_scraped_url)

    def retriever_simple_query(user_query):
        """
        Returns a answer for self.query_select with minimal input
        """
        df_text, df_chunk_emb = Retriever_Controller.embedder.open_embedding()
        return Retriever_Controller.retriever.query_select(user_query,df_text,df_chunk_emb)

if __name__ == "__main__":
    load_dotenv()
    #tracer = init_phoenix("doc_retriever")
    chunker = DocChunker()
    
    #HTML_DIRECTORY = os.getenv("HTML_DIRECTORY")
    #df_text = chunker.get_chunks(chunker.get_docs(HTML_DIRECTORY))
    embedder = DocEmbedder()
    
    #embedder.init_mongodb_client()
    df_text, df_chunk_emb = embedder.open_embedding()
    
    url = "https://www.th-owl.de/"
    retriever = DocRetriever(embedder=embedder,scraped_url=url)
    user_query = "Wozu dient ein Passwortmanager?"
    response = retriever.query_select(user_query,df_text, df_chunk_emb)
    print(response)

