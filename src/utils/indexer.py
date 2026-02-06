#from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

class Indexer:
    """Class to handle FAISS indexing.
    """

    def __init__(self, index_name: str):    
        self.index_name = index_name
        #try to load locally the index
        try:
            # Use local Ollama server for embeddings (default port 11434)
            # Recommend an embedding-capable model like "nomic-embed-text"
            self.embedding_model = OllamaEmbeddings(
                model="llama3",#"nomic-embed-text",
                base_url="http://localhost:11434",
            )
            self.vector_store = FAISS.load_local(folder_path=self.index_name, embeddings=self.embedding_model, allow_dangerous_deserialization=True)
            self.loading_success = True
        except Exception as e:
            print(f"Error loading FAISS index from {self.index_name}: {e}")
            self.vector_store = None
            self.loading_success = False

    def index_documents(self, documents: list[Document], ids: list[str]):
        """Add documents to the FAISS vector store.

        Args:
            documents (list[Document]): _description_
            ids (list[str]): _description_
        """
        if self.vector_store is not None:
            self.vector_store = FAISS.from_documents([], self.embedding_model)

        self.vector_store = FAISS.from_documents(documents, self.embedding_model)


    def save_index(self):
        """Save the FAISS index to disk.
        """
        self.vector_store.save_local(self.index_name)  

    def query(self, query: str, top_k: int = 5) -> list[Document]:
        """Query the vector_store index.

        Args:
            query (str): _description_
            top_k (int, optional): _description_. Defaults to 5.

        Returns:
            _type_: _description_
        """
        results = self.vector_store.similarity_search_with_score(query, k=top_k)
        return results

    def get_document_by_id(self, doc_id: str) -> Document:
        """Retrieve a document from the index by its ID.

        Args:
            doc_id (str): The ID of the document to retrieve.
        Returns:
            Document: The retrieved document.
        """
        if self.vector_store is None:
            raise Exception("No vector store loaded. Index is empty.")
        
        # Get docstore from FAISS vector_store
        docstore = self.vector_store.docstore
        
        # Retrieve the document by its ID
        document = docstore.search(doc_id)
        return document

    def display_index_contents(self, max_docs: int = None):
        """Display all documents stored in the FAISS index.

        Args:
            max_docs (int, optional): Maximum number of documents to display. 
                                     If None, displays all documents. Defaults to None.
        """
        if self.vector_store is None:
            print("No vector store loaded. Index is empty.")
            return
        
        # Get docstore from FAISS vector_store
        docstore = self.vector_store.docstore
        index_to_docstore_id = self.vector_store.index_to_docstore_id
        
        total_docs = len(index_to_docstore_id)
        print(f"\n{'='*80}")
        print(f"FAISS Index: {self.index_name}")
        print(f"Total documents: {total_docs}")
        print(f"{'='*80}\n")
        
        display_count = max_docs if max_docs else total_docs
        
        for idx, doc_id in enumerate(sorted(index_to_docstore_id.items())[:display_count]):
            index, docstore_id = doc_id
            doc = docstore.search(docstore_id)
            
            print(f"[Document {idx + 1}]")
            print(f"  Index ID: {index}")
            print(f"  Docstore ID: {docstore_id}")
            print(f"  Content: {doc.page_content[:200]}..." if len(doc.page_content) > 200 else f"  Content: {doc.page_content}")
            print(f"  Metadata: {doc.metadata}")
            print()
        
        if max_docs and max_docs < total_docs:
            print(f"... ({total_docs - max_docs} more documents)")
        print(f"{'='*80}\n")

if __name__ == "__main__":
    # Example usage
    indexer = Indexer(index_name="/Volumes/Data/Research/Publications/2026/EDM/experiments/skills-base/RNCP38637_resources.idx")
    indexer = Indexer(index_name="/Volumes/Data/Research/Publications/2026/EDM/experiments/skills-base/RNCP38637_problems_family.idx")
    indexer.display_index_contents(max_docs=20)
    #indexer.query(" Elaborer, suivre et piloter un budget", top_k=3)