import os
from dotenv import load_dotenv
load_dotenv()

from netfree_unstrict_ssl import unstrict_ssl
unstrict_ssl()

#loading

from llama_index.core import SimpleDirectoryReader

# Read all .md files from data/Cursor (Cursor-generated docs)
# and also include any .md files directly under data/ (e.g. kiro_PROJECT_DOCS.md).
# SimpleDirectoryReader with input_files lets us combine both locations
# without hardcoding filenames — new files added to data/Cursor are picked
# up automatically on the next run.
import glob

cursor_files = glob.glob("data/Cursor/*.md")   # all Cursor markdown files
kiro_files   = glob.glob("data/*.md")          # kiro_PROJECT_DOCS.md and any future root-level docs

all_files = cursor_files + kiro_files

reader = SimpleDirectoryReader(input_files=all_files)
documents = reader.load_data()
print(len(documents))

#chunking

from llama_index.core.node_parser import SentenceSplitter

node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)

nodes = node_parser.get_nodes_from_documents(
    documents= documents, show_progress=True
)
print(len(nodes))

#embedding

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

from llama_index.embeddings.cohere import CohereEmbedding

# with input_typ='search_query'
embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",
    input_type="search_document",
)

texts = [n.get_text() if hasattr(n, "get_text") else getattr(n, "text", str(n)) for n in nodes]
embeddings = embed_model.get_text_embedding_batch(texts)

# print(len(embeddings))
# print(embeddings[:5])

#indexing and saving

from pinecone import Pinecone
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import StorageContext, VectorStoreIndex

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("rag-docs-index")
namespace = "rag-namespace"

vector_store = PineconeVectorStore(pinecone_index=pinecone_index, namespace=namespace)
storage_context = StorageContext.from_defaults(vector_store=vector_store)

index = VectorStoreIndex(
    nodes=nodes,
    storage_context=storage_context,
    embed_model=embed_model,
    show_progress=True,
)

print("Done! Index saved to Pinecone.")