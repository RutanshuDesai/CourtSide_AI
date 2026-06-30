### Use this file to peak into the Chroma db index


from chroma_utils import ChromaUtils
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    project=os.getenv("GCP_PROJECT_ID"),
    location=os.getenv("GCP_REGION", "us-east1"),
    vertexai=True,
)

dir_path = os.environ.get("VECTOR_INDEX_DB_PATH")
c = ChromaUtils(collection_name="rag_tennis_notes", persist_db_directory=dir_path+"/vertex_db", embeddings_model=embeddings)

### EXPLORE VECTOR DATABASE COLLECTIONS. Considers the entire chroma db path directory.
collections = c.list_collections()
print(collections)

### VIEW VECTOR DATABASE ITEMS AS A PANDAS DATAFRAME. Can run this code in notebook for more detailed analysis.
data_df = c.view_vector_items(limit=25)
print(data_df)
