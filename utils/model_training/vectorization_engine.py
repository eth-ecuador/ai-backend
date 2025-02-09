from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
import uuid

class VectorizationEngine:
    def __init__(self):
        self.code_model = SentenceTransformer(CODE_MODEL)
        self.text_model = SentenceTransformer(TEXT_MODEL)
        self.pc = Pinecone(PINECONE_API_KEY)
        self.pc.delete_index(name=INDEX_NAME) #DEBUG
        self.pc.create_index(INDEX_NAME, dimension=768,metric='cosine', spec=ServerlessSpec(
                                cloud="aws",
                                region="us-east-1"
                            ) )
        self.index = self.pc.Index(INDEX_NAME)

    def generate_embeddings(self, content_batch):
        embeddings = []
        for item in content_batch:
            model = self.code_model if item['type'] == 'code' else self.text_model
            embedding = model.encode(item['content'])
            embeddings.append({
                'id': str(uuid.uuid4()),
                'values': embedding.tolist(),
                'metadata': item['metadata']
            })
        return embeddings

    def upsert_to_db(self, embeddings):
        self.index.upsert(vectors=embeddings)