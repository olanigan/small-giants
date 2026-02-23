import os
import pandas as pd
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
import ollama
from datasets import Dataset, Features, Value, Sequence
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from ragas.llms import LangchainLLMWrapper


load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "rag_benchmark_collection")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
OLLAMA_RAG_MODEL = os.getenv("OLLAMA_RAG_MODEL", "gpt-oss:20b-cloud")


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Generates embeddings for a list of texts using Ollama."""
    print(
        f"Generating embeddings for {len(texts)} texts using Ollama model: {OLLAMA_EMBEDDING_MODEL}"
    )
    embeddings = []
    for text in texts:
        response = ollama.embeddings(model=OLLAMA_EMBEDDING_MODEL, prompt=text)
        embeddings.append(response["embedding"])
    return embeddings


def create_qdrant_collection(client: QdrantClient):
    """Creates a Qdrant collection with a specified vector size."""
    # Assuming embedding size for nomic-embed-text is 768. This might need to be dynamic.
    vector_size = 768
    print(
        f"Creating Qdrant collection: {QDRANT_COLLECTION_NAME} with vector size: {vector_size}"
    )
    client.recreate_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=vector_size, distance=models.Distance.COSINE
        ),
    )


def delete_qdrant_collection(client: QdrantClient):
    """Deletes the Qdrant collection if it exists."""
    print(f"Attempting to delete Qdrant collection: {QDRANT_COLLECTION_NAME}")
    if client.collection_exists(QDRANT_COLLECTION_NAME):
        client.delete_collection(collection_name=QDRANT_COLLECTION_NAME)
        print(f"Collection '{QDRANT_COLLECTION_NAME}' deleted.")
    else:
        print(
            f"Collection '{QDRANT_COLLECTION_NAME}' does not exist, skipping deletion."
        )


def upload_data_to_qdrant(client: QdrantClient, csv_path: str):
    """Loads data from CSV, generates embeddings, and uploads to Qdrant."""
    print(f"Loading data from {csv_path}")
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(
            f"Error: CSV file not found at {csv_path}. Please ensure the file exists."
        )
        return

    # Assuming the CSV has a 'text' column for content
    if "text" not in df.columns:
        print("Error: CSV file must contain a 'text' column.")
        return

    texts = df["text"].tolist()
    embeddings = get_embeddings(texts)

    points = []
    for i, (text, embedding) in enumerate(zip(texts, embeddings)):
        points.append(
            models.PointStruct(
                id=i,
                vector=embedding,
                payload={"text": text},  # Store the original text as payload
            )
        )
    print(
        f"Uploading {len(points)} points to Qdrant collection: {QDRANT_COLLECTION_NAME}"
    )
    client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        wait=True,
        points=points,
    )
    print("Data upload complete.")


def rag_pipeline(
    client: QdrantClient, query: str, retrieve_limit: int = 3
) -> tuple[str, list[str]]:
    """Basic RAG pipeline: retrieves from Qdrant and generates response with Ollama.
    Returns generated response and a list of retrieved contexts."""
    # print(f"Processing query: {query}") # Suppress this print to avoid clutter during RAGAS eval
    query_embedding = get_embeddings([query])[0]

    # Retrieve relevant documents from Qdrant
    search_result = client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=query_embedding,
        limit=retrieve_limit,
    ).points

    contexts = [hit.payload["text"] for hit in search_result]
    context_str = "\n".join(contexts)

    # Construct prompt for Ollama
    prompt = (
        f"Given the following context:\n{context_str}\n\nAnswer the question: {query}"
    )
    # print("Generating response with Ollama...") # Suppress this print to avoid clutter during RAGAS eval
    response = ollama.generate(model=OLLAMA_RAG_MODEL, prompt=prompt)
    return response["response"], contexts


if __name__ == "__main__":
    qdrant_client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    # Create a 'data' directory if it doesn't exist
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    csv_file_path = os.path.join(data_dir, "rag_token_512.csv")

    # This part requires the user to manually place the CSV file, as I cannot do it.
    # For now, I will create a dummy CSV file for initial testing.
    # In a real scenario, the user would provide the actual CSV.
    dummy_csv_content = "text\nThis is the first document about AI.\nAI is transforming many industries.\nMachine learning is a subfield of AI.\nQdrant is a vector database.\nOllama runs large language models locally.\nDSPy optimizes prompts."
    with open(csv_file_path, "w") as f:
        f.write(dummy_csv_content)
    print(f"Created a dummy CSV file at: {csv_file_path}")

    # Always create and upload data for both baseline and RAGAS eval runs
    create_qdrant_collection(qdrant_client)
    upload_data_to_qdrant(qdrant_client, csv_file_path)

    # Define queries and ground truths for evaluation
    queries = [
        "What is DSPy used for?",
        "Tell me about Qdrant.",
        "What is AI?",
        "What are some subfields of AI?",
    ]
    ground_truths = [
        ["DSPy is used for optimizing prompts."],
        ["Qdrant is a vector database."],
        ["AI is transforming many industries."],
        ["Machine learning is a subfield of AI."],
    ]

    predictions = []
    print("\n--- Running Baseline RAG Pipeline ---")
    for i, query in enumerate(queries):
        response, contexts = rag_pipeline(qdrant_client, query)
        predictions.append(
            {
                "query": query,
                "answer": response,
                "contexts": contexts,
                "ground_truth": ground_truths[i],
            }
        )
        print(f"\nQuery: {query}")
        print(f"Response: {response}")
        print(f"Retrieved Contexts: {contexts}")

    # --- RAGAS Evaluation Integration (Conditional) ---
    if os.getenv("RUN_RAGAS_EVAL") == "true":
        print("\n--- Starting RAGAS Evaluation ---")

        # Prepare data for RAGAS
        ragas_data = {
            "question": [p["query"] for p in predictions],
            "answer": [p["answer"] for p in predictions],
            "contexts": [p["contexts"] for p in predictions],
            "ground_truth": [
                p["ground_truth"][0] if p["ground_truth"] else "" for p in predictions
            ],
        }

        features = Features(
            {
                "question": Value("string"),
                "answer": Value("string"),
                "contexts": Sequence(Value("string")),
                "ground_truth": Value("string"),
            }
        )
        dataset = Dataset.from_dict(ragas_data, features=features)

        # Configure Ragas to use Ollama
        ragas_ollama_llm = LangchainLLMWrapper(
            ChatOllama(model=OLLAMA_RAG_MODEL, base_url="http://localhost:11434")
        )
        ragas_ollama_embeddings = OllamaEmbeddings(
            model=OLLAMA_EMBEDDING_MODEL, base_url="http://localhost:11434"
        )

        # Define Ragas metrics and evaluate
        metrics = [faithfulness, answer_relevancy, context_recall, context_precision]

        result = evaluate(
            dataset, metrics, llm=ragas_ollama_llm, embeddings=ragas_ollama_embeddings
        )
        print("\nRAGAS Evaluation Results:")
        print(result)
        print("--- End of RAGAS Evaluation ---")
    else:
        print(
            "\nSkipping RAGAS evaluation. To run it, set environment variable RUN_RAGAS_EVAL=true."
        )
        print("For example: make run-ragas-eval")

    # Clean up dummy CSV - controlled by Makefile now via 'make clean' target
    # os.remove(csv_file_path)
    # print(f"\nRemoved dummy CSV file: {csv_file_path}")
