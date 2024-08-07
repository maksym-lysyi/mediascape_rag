import os
import asyncio
import logging
from fastapi import FastAPI
from apify_client import ApifyClientAsync
from dotenv import load_dotenv
from preprocessing import get_urls, colect_crawled_content, init_retriever, init_llm, get_answer, get_text
from pydantic import BaseModel


load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
apify_api = os.getenv("APIFY_API_KEY")

logging.basicConfig(
    level=logging.INFO, 
    filename="log.log", 
    filemode="w",
    format='%(asctime)s, %(levelname)s, %(message)s'
)

logger = logging.getLogger(__name__)

client = ApifyClientAsync(apify_api)
app = FastAPI()

semaphore = asyncio.Semaphore(4) 

class UserInput(BaseModel):
    question: str

class ModelOutput(BaseModel):
    response: str

@app.post("/test/")
async def main(input: UserInput):
    urls = get_urls(question=input.question)
    logger.info(f"We have URLs: {urls}")

    # parsed_text = get_text(urls)  # faster method for testing
    parsed_text = await colect_crawled_content(urls, client, semaphore)
    logger.info(f"We have context with length {len(parsed_text)}")

    llm = init_llm(api_key=groq_key)
    logger.info("We have LLM")

    frm = init_retriever(text=parsed_text)
    logger.info("We have retriever model")

    response = get_answer(question=input.question, frm=frm, llm=llm)

    return ModelOutput(response=response)
