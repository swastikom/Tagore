from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from config import GOOGLE_API_KEY

class VectorMemory:
    def __init__(self, persist_directory="./chroma_db"):
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004", 
            google_api_key=GOOGLE_API_KEY
        )
        self.vector_store = Chroma(
            collection_name="novel_continuity",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )

    def add_facts(self, entity_name: str, category: str, facts: list[str]):
        documents = []
        metadatas = []
        for fact in facts:
            # Format the fact clearly for the LLM
            doc_text = f"{entity_name} ({category}): {fact}"
            documents.append(doc_text)
            metadatas.append({"entity": entity_name, "category": category})
            
        if documents:
            self.vector_store.add_texts(texts=documents, metadatas=metadatas)

    def get_relevant_context(self, query: str, k: int = 10) -> str:
        """Fetches the top 'k' most relevant facts based on the query's meaning."""
        results = self.vector_store.similarity_search(query, k=k)
        if not results:
            return ""
        return "\n".join(f"- {doc.page_content}" for doc in results)