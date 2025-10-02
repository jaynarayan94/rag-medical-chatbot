# retriever.py

from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace

from app.components.vector_store import load_vector_store
from app.config.config import HF_TOKEN
from app.common.logger import get_logger
from app.common.custom_exception import CustomException


logger = get_logger(__name__)

CUSTOM_PROMPT_TEMPLATE = """Answer the following medical question in 2-3 lines maximum using only the information provided in the context.

Context:
{context}

Question:
{question}

Answer:
"""

def set_custom_prompt():
    return PromptTemplate(template=CUSTOM_PROMPT_TEMPLATE, input_variables=["context", "question"])


# Candidate chat-friendly models
CANDIDATE_MODELS = [
    "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "HuggingFaceH4/zephyr-7b-beta",
    "meta-llama/Llama-2-7b-chat-hf",
    "tiiuae/falcon-7b-instruct",
    "google/flan-t5-large",
]


def try_load_llm():
    """Try loading all candidate models until one works."""
    for repo_id in CANDIDATE_MODELS:
        try:
            logger.info(f"Attempting to load LLM model: {repo_id}")
            llm = ChatHuggingFace.from_model_id(
                model_id=repo_id,
                task="conversational",
                token=HF_TOKEN,
            )
            logger.info(f"Successfully loaded model: {repo_id}")
            return llm
        except Exception as e:
            logger.error(f"Failed to load {repo_id}: {e}")
            continue
    raise CustomException("All candidate models failed to load.")


def create_qa_chain():
    try:
        logger.info("Loading vector store for context")
        db = load_vector_store()

        if db is None:
            raise CustomException("Vector store not present or empty")

        llm = try_load_llm()

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={'k': 1}),
            return_source_documents=False,
            chain_type_kwargs={'prompt': set_custom_prompt()}
        )
        logger.info("QA chain created successfully with conversational LLM")
        return qa_chain

    except Exception as e:
        error_message = CustomException("Failed to make a QA chain", e)
        logger.error(str(error_message))
        return None
