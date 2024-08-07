# RAG for Medscape website

This application provides an integrated solution for information retrieval and content management using a combination of tools and services. It employs Google URL search for discovering relevant URLs, Apify content crawler for extracting text from these URLs, and LangChain for managing text chunks. The application utilizes FaissDB as a vector database for similarity search and Groq for hosting Llama3-70B language model. The backend is built with FastAPI, while Streamlit is used for creating an user interface. The entire setup is containerized using Docker, ensuring easy deployment and scalability.

This demo utilizes the following tools:
- Google URL search - for finding corresponding URLs
- Apify content crawler - for parsing text from URLs
- LangChain - for managing text chunks
- FaissDB - as the vector database
- Groq - for Llama3-70B hosting service
- FastAPI - for the REST API
- Streamlit - for the interface
- Docker - for containerization

This program is already configured and can be started on a server via the following steps:
```
# Install Docker and Docker Compose
sudo apt-get update
sudo apt-get install docker.io
sudo apt-get install docker-compose

# Clone the GitHub repository
git clone https://github.com/maksym-lysyi/mediascape_rag.git
cd mediascape_rag

# Run the application
docker-compose up --build
```

After these steps, the application should be accessible via port 8501.