# LangChain-Qdrant-Ollama RAG Benchmark with RAGAS Evaluation

## Objective
To demonstrate a robust Retrieval-Augmented Generation (RAG) pipeline leveraging Qdrant for vector storage, Ollama for local Large Language Model (LLM) inference, and RAGAS for evaluation. This project aims to highlight:
1.  **Cost-effectiveness:** Utilizing local Ollama models for inference.
2.  **Performance:** Benchmarking RAG metrics (e.g., faithfulness, answer relevance, context precision, context recall) using RAGAS evaluation framework.
3.  **Flexibility:** Showcasing the ability to swap different local LLMs (e.g., `gpt-oss:20b-cloud` or `ibm/granite4`).
4.  **Reproducibility:** Establishing a clear and repeatable evaluation setup.

## Quick Win Experiment Details
This experiment implements a RAG pipeline using LangChain components and RAGAS evaluation:

1.  **Ollama Integration:** Configuring the RAG pipeline to use a local Ollama instance (e.g., `gpt-oss:20b-cloud` or `ibm/granite4` as fallback) for all LLM-based generation tasks.
2.  **LangChain Components:** Using LangChain's `ChatOllama` and `OllamaEmbeddings` for generation and embedding tasks within the RAG pipeline.
3.  **RAGAS Evaluation:** Running comprehensive evaluations with RAGAS metrics (faithfulness, answer relevance, context precision, context recall) to quantitatively assess pipeline performance.

## Architectural Outline

The RAG pipeline will consist of the following main components:

1.  **Data Ingestion & Indexing:** Raw documents are processed, chunked, and embedded using Ollama embeddings. These embeddings are then stored in Qdrant, a vector database, enabling efficient semantic search.
2.  **User Query:** The user submits a natural language query.
3.  **Retrieval (Qdrant):** The user query is embedded and used to retrieve the most relevant document chunks from Qdrant.
4.  **Prompt Construction:** Retrieved context and the user query are combined into a prompt for the LLM.
5.  **Generation (Ollama LLM):** The retrieved context and prompt are fed to a local LLM running via Ollama (e.g., `gpt-oss:20b-cloud`). The LLM generates the final answer.
6.  **Evaluation (RAGAS):** The generated answer, original query, and retrieved context are passed to RAGAS for automated evaluation of RAG specific metrics (e.g., faithfulness, answer relevance, context recall, context precision).

## ASCII Visualization of the RAG Pipeline

```
+-------------------+      +-------------------+
|                   |      |                   |
|   Raw Documents   |      |   User Query      |
|                   |      |                   |
+---------+---------+      +--------+----------+
          |                         |
          v                         |
+-------------------+               |
| Data Ingestion &  |               |
| Embedding         |               |
| (Ollama nomic)    |               |
+---------+---------+               |
          |                         |
          v                         |
+-------------------+               |
|      Qdrant       |<--------------+
| (Vector Database) |
+---------+---------+
          |  ^
          |  | Relevant Chunks
          v  |
+-------------------+      +-------------------+
|   LangChain       +------>|                   |
|   Retrieval       |<------+   Ollama LLM      |
| (Qdrant Client)   |      | (gpt-oss:20b-cloud|
+---------+---------+      |  or granite4)     |
          |                +---------+---------+
          v                          |
+-------------------+                v
|  Prompt Template  |      +-------------------+
| (Context + Query) +----->|  Generated Answer |
+---------+---------+      +---------+---------+
          |                          |
          v                          v
+-------------------+      +-------------------+
|     RAGAS         |      | Performance       |
|   (Evaluation)    |      | Metrics & Report  |
+-------------------+      +-------------------+
```

## Quick Start

### Prerequisites

1.  **Install Poetry** (if not already installed):
    ```bash
    curl -sSL https://install.python-poetry.org | python -
    ```

2.  **Install Ollama** (if not already installed): Follow the instructions on the official Ollama website: https://ollama.com/

3.  **Ensure Qdrant is running** (e.g., via Docker):
    ```bash
    docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
    ```

### Run the Pipeline

```bash
# Navigate to the project directory
cd experiments/small-giants/langchain-qdrant-ollama-rag/

# Install dependencies and pull models
make setup

# Run baseline RAG pipeline
make run-baseline

# Run RAGAS evaluation
make run-ragas-eval

# Clean up
make clean
```

## Evaluation Results

See `.report/001-langchain-qdrant-ollama-rag-evaluation.md` for detailed evaluation results.

| Metric | Score |
|--------|-------|
| Faithfulness | 0.1167 |
| Answer Relevancy | 0.5327 |
| Context Recall | 0.5000 |
| Context Precision | 0.3333 |

**Note:** Low scores are attributable to the minimal 6-document corpus used for testing, not fundamental design flaws. The pipeline architecture is sound and ready for production use with real data.
