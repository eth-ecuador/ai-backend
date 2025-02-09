from pinecone import Pinecone
import requests

from agent_graphs.retrieval_graph.retrieval import make_text_encoder
from api.stores.content_processor import ContentProcessor
from api.stores.documentation_scraper import DocumentationScraper

embedding_model = make_text_encoder("openai/text-embedding-3-small")
vector_db:Pinecone = Pinecone(embedding=embedding_model)

def scrape_pages(base_url, urls):
    scraper = DocumentationScraper(base_url, urls)
    processor = ContentProcessor()

    processed_docs = []
    for url in urls:
        sample_content = requests.get(url).content
        processed = processor.process_page(url, sample_content)
        processed_docs.append(processed)
    
    return processed_docs