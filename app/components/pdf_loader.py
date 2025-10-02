import os 
from app.config.config import DATA_PATH, CHUNK_SIZE, CHUNK_OVERLAP
from app.common.logger import get_logger
from app.common.custom_exception import CustomException 
from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = get_logger(__name__)


def load_pdf_files(data_path=DATA_PATH):
    try:
        if not os.path.exists(data_path):
            raise CustomException(f"Data path {data_path} does not exist.")

        logger.info(f"Loading PDF files from {data_path}")
        loader = DirectoryLoader(data_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
        documents = loader.load()
        
        if not documents:
            raise CustomException(f"No PDF files found in the directory {data_path}.")
        
        logger.info(f"Loaded {len(documents)} documents from {data_path}")

        return documents
    except Exception as e:
        logger.error(f"Error loading PDF files: {e}")
        raise CustomException("Error loading PDF files", e)

def create_text_chunks(documents, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP):
    try:
        if not documents:
            raise CustomException("No documents to split.")
        
        logger.info(f"Splitting documents into chunks of size {chunk_size} with overlap {chunk_overlap}")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        text_chunks = text_splitter.split_documents(documents)

        logger.info(f"Split into {len(text_chunks)} chunks")
        return text_chunks
    
    except Exception as e:
        logger.error(f"Error splitting documents: {e}")
        raise CustomException("Error splitting documents", e)