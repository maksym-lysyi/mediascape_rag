from fastapi import FastAPI
from apify_client import ApifyClientAsync
from preprocessing import get_urls, colect_crawled_content, init_retriever, init_llm, get_answer, get_text
import asyncio
import os


groq_key = os.getenv("GROQ_KEY")
apify_api = os.getenv("APIFY_API")

client = ApifyClientAsync(apify_api)
app = FastAPI()

semaphore = asyncio.Semaphore(4) 

@app.post("/test/")
async def main(question: str):
    urls = get_urls(question=question)
    print("We have URLs")

    # results = get_text(urls)  ||  faster method for testing
    results = await colect_crawled_content(urls, client, semaphore)
    print("We have context")

    llm = init_llm(api_key=groq_key)
    print("We have llm")

    frm = init_retriever(text=results)
    print("We have rm")

    answer = get_answer(question=question, frm=frm, llm=llm)

    return answer
