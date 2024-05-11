import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Pinecone Configuration
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# Vectorization Model
VECTOR_MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_DIMENSION = 384

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-3.5-turbo"

# Other Settings
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1", "t"]
