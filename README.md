# RAG AI Search

An intelligent search system based on RAG (Retrieval-Augmented Generation) that supports multiple LLM models, including GPT and local Ollama models.

![alt text](documents/web_search.png)

For Chinese version, please check [README_cn.md](documents/README_cn.md)

## Features

- Support for multiple LLM models (GPT and local Ollama models)
- Streaming output generation
- Display of reference document sources
- History record saving and querying
- Responsive interface design

## System Requirements

- Python 3.8+
- Flask
- Azure OpenAI API access (for GPT)
- Ollama service (for local models)

# Installation Steps

1. Clone the project
```bash
git clone https://github.com/your-repo/rag-ai-search.git
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Install Ollama

- Install Ollama

  Reference: [Ollama Installation](documents/Install_ollama.md)

- Install Ollama model after installation

  ```bash
  ollama run llama3:8b
  ```

- Configure Ollama service address

  Configure Ollama service address in config/settings.py

  ```bash
  OllamaConfig.BASE_URL = "http://127.0.0.1:4008"
  ```

4. Install Search Engine

- Install search engine

  Reference: [Install Search Engine](documents/Install_search_engine.md)

- Configure search engine

    Configure search engine in config/settings.py

  ```bash
  SearchConfig.SEARX_BASE_URL = "http://127.0.0.1:11434"
  ```

5. Configure Azure OpenAI API

    Create a .env file in the project root directory and configure the following environment variables:

```bash
gpt4o_mini_api_key='your_api_key'
gpt4o_mini_api_version='your_api_version'
gpt4o_mini_azure_endpoint='your_azure_endpoint'
```

    GPT calling method: utils/gpt4_client.py

    Note: If you don't have a GPT key, you can directly use the Ollama model without configuring Azure OpenAI

## Starting the Search System

1. Start Web Service

```python
python web/app.py
```

2. Open browser and visit: http://localhost:5000

3. Select Model:
   - GPT: Uses Azure OpenAI service
   - Ollama Model: Uses locally deployed model

4. Enter your question and wait for the answer
   - System will display reference document sources
   - Real-time streaming display of generated results
   - Support for viewing history records

# Technical Architecture

![alt text](documents/architecture.png)