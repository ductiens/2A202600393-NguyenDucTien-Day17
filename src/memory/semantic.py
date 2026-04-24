"""
Semantic memory module
Handles Chroma connection for RAG and domain knowledge
"""

import chromadb
from typing import List, Dict, Any, Optional

class SemanticMemory:
    def __init__(self, collection_name: str = "knowledge_base", persist_directory: str = "./chroma_db"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.client = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """Connect to ChromaDB"""
        try:
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Failed to connect to ChromaDB: {e}")
            self.client = None
            self.collection = None
    
    def add_knowledge(self, documents: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Add knowledge documents to the collection"""
        if not self.collection:
            return False
        
        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            print(f"Failed to add knowledge: {e}")
            return False
    
    def query_knowledge(self, query_text: str, n_results: int = 5) -> Optional[Dict[str, Any]]:
        """Query knowledge from the collection"""
        if not self.collection:
            return None
        
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"Failed to query knowledge: {e}")
            return None
    
    def get_similar_documents(self, document_id: str, n_results: int = 5) -> Optional[Dict[str, Any]]:
        """Get similar documents based on document ID"""
        if not self.collection:
            return None
        
        try:
            results = self.collection.query(
                query_ids=[document_id],
                n_results=n_results
            )
            return results
        except Exception as e:
            print(f"Failed to get similar documents: {e}")
            return None
    
    def delete_knowledge(self, ids: List[str]):
        """Delete knowledge documents from the collection"""
        if not self.collection:
            return False
        
        try:
            self.collection.delete(ids=ids)
            return True
        except Exception as e:
            print(f"Failed to delete knowledge: {e}")
            return False
    
    def get_collection_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the collection"""
        if not self.collection:
            return None
        
        try:
            return self.collection.count()
        except Exception as e:
            print(f"Failed to get collection info: {e}")
            return None
