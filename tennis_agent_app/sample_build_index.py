from chroma_utils import ChromaUtils
from langchain_ollama import OllamaEmbeddings
import glob

### use the same embedding model to do the indexing that will be available in production. So if hosting on GCP, then vertex model should be used instead Ollama based model or any other model. 
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(usecwd=True))

embeddings = GoogleGenerativeAIEmbeddings(
    model=os.getenv("VERTEX_EMBEDDING_MODEL", "gemini-embedding-001"),
    project=os.getenv("GCP_PROJECT_ID"),
    location="us-central1",
    vertexai=True,
)

c = ChromaUtils(collection_name="tennis_notes", persist_db_directory='app_db', embeddings_model=embeddings)

### READ and CHUNK documents. Also add to the ChromaDb
for path in glob.glob("data/*.pdf"): ## edit this to your own data folder
    docs=c.read_documents(file_path=path)
    chunks=c.split_documents(documents=docs)
    c.add_chunked_documents(chunks=chunks)