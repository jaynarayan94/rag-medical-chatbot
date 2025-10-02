from langchain_community.vectorstores import FAISS
from app.config.config import DB_FAISS_PATH
from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.components.embeddings import get_embedding_model
import os

logger = get_logger(__name__)


def load_vector_store(db_path=DB_FAISS_PATH):
    try:
        if not os.path.exists(db_path):
            raise CustomException(f"FAISS database path {db_path} does not exist.")
        
        logger.info(f"Loading FAISS vector store from {db_path}")
        embeddings = get_embedding_model()
        vector_store = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)
        
        logger.info("FAISS vector store loaded successfully")
        return vector_store
    
    except Exception as e:
        logger.error(f"Error loading FAISS vector store: {e}")
        raise CustomException("Error loading FAISS vector store", e)

# Create a function to save the FAISS vector store
# Creating new vectorstore function
def save_vector_store(text_chunks):
    try:
        if not text_chunks:
            raise CustomException("No chunks were found..")
        
        logger.info("Generating your new vectorstore")

        embedding_model = get_embedding_model()

        db = FAISS.from_documents(text_chunks,embedding_model)

        logger.info("Saving vectorstore locally...")

        db.save_local(DB_FAISS_PATH)

        logger.info("Vectorstore saved successfully...")

        return db
    
    except Exception as e:
        error_message = CustomException("Failed to create new vectorstore " , e)
        logger.error(str(error_message))
        raise error_message