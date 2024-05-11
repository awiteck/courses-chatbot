from config.settings import (
    PINECONE_API_KEY,
    PINECONE_ENVIRONMENT,
    PINECONE_INDEX_NAME,
    VECTOR_MODEL_NAME,
    VECTOR_DIMENSION,
)
from pinecone import Pinecone, ServerlessSpec


class PineconeManager:
    def __init__(self):
        # Initialize Pinecone with the API key from settings
        self.pc = Pinecone(api_key=PINECONE_API_KEY)

        # pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENVIRONMENT)
        self.index_name = PINECONE_INDEX_NAME
        self.vector_dimension = VECTOR_DIMENSION  # This should match the output dimension of your model (imported from settings if variable)
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        print("_ensure_index_exists")
        existing_indexes = self.pc.list_indexes()
        print(existing_indexes)
        print("----")
        index_names = [index["name"] for index in existing_indexes]
        # Check if the index exists, and if not, create it
        if self.index_name not in index_names:
            print("Not in index...")
            self.pc.create_index(
                name=self.index_name,
                dimension=self.vector_dimension,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region=PINECONE_ENVIRONMENT),
            )

    def upsert(self, items):
        # Connect to the index
        index = self.pc.Index(self.index_name)
        # Upsert data; items should be a list of tuples (id, vector)
        index.upsert(vectors=items)

    def query(self, vector, top_k=5):
        # Connect to the index
        index = self.pc.Index(self.index_name)
        # Query the index
        return index.query(vector, top_k=top_k)


# Example usage of the PineconeManager class, typically you would use it in your main.py or another script
if __name__ == "__main__":
    manager = PineconeManager()
    # Example vector for querying; this should be replaced with actual vectors
    example_vector = [0.1] * VECTOR_DIMENSION  # Assuming your model outputs 384
