import asyncio
import dspy
from googlesearch import search
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dspy.retrieve.faiss_rm import FaissRM
import requests
from bs4 import BeautifulSoup
import time


def get_text(urls):
    all_content = []
    for url in urls:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            try:
                article_content = soup.find('div', class_='article-content')
                article_text = article_content.text if article_content else None
                print("Article content using class")
            except:
                pass
            try:
                article_content = soup.find('div', id='article-content')
                article_text = article_content.text if article_content else None
                print("Article content using id")
            except:
                pass


            if article_text:


                lines = [line.strip() for line in article_text.split("\n") if line.strip()]
                cleaned_text = "\n".join(lines)

                all_content.append(cleaned_text)
                time.sleep(3)
            else:
                print(f"No article content found for URL: {url}")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching content from {url}: {e}")
        except Exception as ex:
            print(f"An error occurred for URL {url}: {ex}")

    return " ".join(all_content)


def get_urls(question, num_results=10):

    site = "https://www.medscape.com/"

    search_query = f"{question} site:{site}"
    search_results = search(search_query, num_results=num_results)

    articles = []
    idx = 0
    for result in search_results:
        if "medscape.com" in result and idx < 4:
            idx += 1
            articles.append(result)
            print(result)

    print(f"We have {len(articles)} URLs")

    return articles


async def run_content_crawler(url, semaphore, client):
    async with semaphore:
        run = await client.actor("apify/website-content-crawler").call(
                    run_input={
                        "startUrls": [{"url": url}],
                        "maxCrawlDepth": 0
                    },
                    memory_mbytes=2048,
                    timeout_secs=200,
        )

        dataset_client = client.dataset(run['defaultDatasetId'])
        items = await dataset_client.list_items()
        item = items.items[0]
        url_text = item["text"]

        return url_text


async def colect_crawled_content(urls, client, semaphore):

    
    tasks = [run_content_crawler(url, semaphore, client) for url in urls]

    results = await asyncio.gather(*tasks)

    return " ".join(results)



def init_retriever(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 2000, chunk_overlap=200)
    docs = text_splitter.create_documents([text])
    document_chunks = [doc.page_content for doc in docs]
    frm = FaissRM(document_chunks, k=10)
    return frm


def init_llm(api_key):
    return dspy.GROQ(api_key=api_key, max_tokens=2048, temperature=0.0)


class GenerateAnswer(dspy.Signature):
    ("""Answer questions based only on information from 'context'.""",
     """Refuse to answer questions unrelated to context.""",
     """Refuse to answer questions unrelated to medicine.""")

    context = dspy.InputField(desc="may contain relevant facts")
    question = dspy.InputField()
    answer = dspy.OutputField(desc="often between 300 and 500 words. Refuse to answer questions unrelated to medicine.")



class RAG(dspy.Module):
    def __init__(self, num_passages=6):
        super().__init__()

        self.retrieve = dspy.Retrieve(k=num_passages)
        
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)
    
    def forward(self, question):
        context = self.retrieve(question).passages
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)
    

def get_answer(question, frm, llm):
    dspy.settings.configure(lm=llm, rm=frm)
    rag = RAG()
    response = rag(question=question)
    return response.answer