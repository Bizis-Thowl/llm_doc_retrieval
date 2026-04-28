import os
import re

#from bs4 import BeautifulSoup
import pandas as pd
from dotenv import load_dotenv

from langchain_text_splitters import HTMLSectionSplitter #, HTMLSemanticPreservingSplitter, RecursiveCharacterTextSplitter HTMLHeaderTextSplitter, 

class DocChunker:

    def __init__(self):
        pass
    
    def chunk_doc(self, html, h_to_split=[("h1", "Header 1"),("h2", "Header 2")]):
        # Chunks a given html document by using the provided headers.
        html_splitter = HTMLSectionSplitter(h_to_split)
        html_header_splits = html_splitter.split_text(html)
        return html_header_splits
    
    def get_docs(self,dir,df_text = pd.DataFrame(columns =['name','text','url'])):
        """
         Opens the scraped documents and returns them in a dataframe with
         'name' = Name of the file
         'text' = Content of the file
         as columns.
        """
        for file in os.scandir(dir):
            if file.is_dir():
                self.get_docs(os.path.normpath(file.path).replace("\\","/"), df_text)
            else:
                with open(file.path, "r", encoding = 'UTF8',errors='ignore') as f:
                    #soup = BeautifulSoup(f, "html.parser")
                    f_name = os.path.basename(os.path.dirname(file.path))
                    url = re.search("/skim/.+", os.path.dirname(file.path)).string
                    df_text.loc[len(df_text)]= [f_name,f.read(),url]
                    #df_text['name'].append(f.name)
                    #df_text['text'].append(f.read)
                
        return df_text

    def get_chunks(self, df_text):
        """
        Takes a dataframe of documents and adds a column with a list of chunks for each one.
        """
        chunks = []
        for i,row in df_text.iterrows():
            text = row['text']
            chunks.append(self.chunk_doc(text,h_to_split=[("h1", "Header 1"),("h2", "Header 2")])) 
        df_text['chunks'] = chunks
        return df_text

if __name__ == "__main__":
    load_dotenv()
    chunker = DocChunker()
    HTML_DIRECTORY = os.getenv("HTML_DIRECTORY","value does not exist")
    print(HTML_DIRECTORY)
    docs = chunker.get_docs(HTML_DIRECTORY)
    chunks = chunker.get_chunks(docs)
    #print(chunks)