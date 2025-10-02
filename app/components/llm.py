from app.common.logger import get_logger
from app.common.custom_exception import CustomException
from app.config.config import HUGGINGFACE_REPO_ID, HF_TOKEN, HUGGINGFACE_API_TOKEN
from langchain_huggingface import HuggingFaceEndpoint

logger = get_logger(__name__)

def load_llm(repo_id=HUGGINGFACE_REPO_ID, hf_token=HF_TOKEN):
    try:
        logger.info(f"Initializing HuggingFace LLM model: {repo_id}")

        # Always use conversational for Mistral
        if repo_id.startswith("mistralai/"):
            task = "conversational"
        else:
            task = "text-generation"
        logger.info(f"Selected task: {task} for repo_id: {repo_id}")
        
        llm = HuggingFaceEndpoint(
            repo_id=repo_id,
            task=task,
            huggingfacehub_api_token=hf_token or HUGGINGFACE_API_TOKEN,
            temperature=0.3,
            max_new_tokens=256,
            return_full_text=False,
        )

        logger.info(f"HuggingFace LLM model loaded successfully with task: {task}")
        return llm

    except Exception as e:
        logger.error(f"Error loading HuggingFace LLM model: {e}")
        raise CustomException("Error loading HuggingFace LLM model", e)
