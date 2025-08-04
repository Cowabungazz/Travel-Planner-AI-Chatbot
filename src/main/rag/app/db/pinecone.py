from pinecone import Pinecone, ServerlessSpec
import os
import uuid
import openai
from dotenv import load_dotenv
import json
import logging

# Configure the logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

load_dotenv()

API_KEY=os.getenv("PINECONE_API")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

pc = Pinecone(api_key=API_KEY, environment="us-east-1")
from pinecone import Pinecone
import uuid

# Define index name
index_name = "chatbot-memory"
index = pc.Index(index_name)


def embed_texts(texts): 
    """
    Converts a list of text inputs into embeddings.
    """
    return pc.inference.embed(
        model="llama-text-embed-v2",
        inputs=texts,
        parameters={"input_type": "passage"}
    )
#--------------

import json
import openai
import logging
import os

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

import json
import openai
import logging
import os

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def extract_embeddings(message):
    """
    Uses OpenAI to extract different meanings from a message and assign a persistence score.
    Ensures the response is valid JSON before parsing.
    """
    prompt = f"""
    You are a classifier that extracts different meanings from a given user message and assigns each a persistence score from 0 to 1.

    **Rules:**
    - 1 means the meaning should persist across all chat sessions.
    - 0 means the meaning is only relevant for the current session.

    **Example Responses:**
    ```json
    [
        {{"phrase": "I am a software engineer and I love coding.", "persistence": 1.0}},
        {{"phrase": "I am studying computer science at university.", "persistence": 1.0}},
        {{"phrase": "I enjoy playing tennis and I run marathons.", "persistence": 1.0}}
    ]
    ```

    Now, analyze the following message: "{message}"

    **Output:**
    - Return the results as a **valid JSON array of dictionaries**.
    - Do NOT include any explanations, only return JSON inside triple backticks (```json ... ```).
    """

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)  # ✅ New OpenAI client format

        response = client.chat.completions.create(  # ✅ New OpenAI SDK format
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        
        raw_response = response.choices[0].message.content.strip()

        # ✅ Extract JSON from OpenAI response if it's wrapped in triple backticks
        if raw_response.startswith("```json"):
            raw_response = raw_response.strip("```json").strip("```")

        parsed_response = json.loads(raw_response)  # Convert to Python dictionary
        
        if not isinstance(parsed_response, list):
            raise ValueError("Parsed response is not a list")

        return parsed_response  # ✅ Returns a list of dictionaries

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        logger.error(f"Failed to parse JSON response: {str(e)}")
        return []




def store_embeddings(user_id, session_id, message):
    """
    Splits message into multiple meanings, assigns persistence scores, embeds them, and upserts into Pinecone.
    - Persistent vectors -> Indexed as "{user_id}-persistent-{i}"
    - Temporary vectors -> Indexed as "{user_id}-{session_id}-temp-{i}"
    """

    # Extract meanings and persistence scores
    extracted_data = extract_embeddings(message)  # ✅ This is already a Python list of dictionaries
    
    if not extracted_data:
        logger.error(f"No embeddings extracted for message: {message}")
        return

    meanings = [entry["phrase"] for entry in extracted_data]
    persistence_scores = [entry["persistence"] for entry in extracted_data]

    # Embed the meanings
    embeddings = embed_texts(meanings)

    vectors = []
    for i, (meaning, embedding, persistence_score) in enumerate(zip(meanings, embeddings, persistence_scores)):
        embedding_type = "persistent" if persistence_score >= 0.7 else "temporary"  # Define threshold
        
        vector_id = f"{user_id}-persistent-{i}" if embedding_type == "persistent" else f"{user_id}-{session_id}-temp-{i}"
        
        vectors.append({
            "id": vector_id,
            "values": embedding.values,
            "metadata": {"text": meaning, "type": embedding_type, "user_id": user_id, "persistence_score": persistence_score}
        })

    # Upsert into Pinecone
    index.upsert(
        vectors=vectors,
        namespace="ns1"
    )
    
    print(f"Stored {len(vectors)} embeddings.")



def search_embeddings(user_id, session_id, query, k=3):
    """
    Queries the vector database for the k nearest vectors, considering only:
    - Persistent vectors linked to `user_id`
    - Temporary vectors linked to `user_id` and `session_id`
    """
    # Generate query embedding
    query_embedding = pc.inference.embed(
        model="llama-text-embed-v2",
        inputs=[query],
        parameters={"input_type": "query"}
    )[0].values

    # Define Pinecone filter: match only relevant vectors
    filter_conditions = {
        "$or": [
            {"user_id": user_id, "type": "persistent"},  # Persistent vectors for user
            {"user_id": user_id, "session_id": session_id, "type": "temporary"}  # Temporary vectors for user+session
        ]
    }

    # Query Pinecone
    search_results = index.query(
        namespace="ns1",
        vector=query_embedding,
        top_k=k * 2,  # Fetch more to ensure we get a mix of both types if available
        include_metadata=True,
        filter=filter_conditions
    )

    # Separate results into temporary and persistent lists
    temp_results = []
    persistent_results = []

    for match in search_results["matches"]:
        metadata = match["metadata"]
        meaning_text = metadata["text"]
        embedding_type = metadata["type"]

        if embedding_type == "temporary":
            temp_results.append(meaning_text)
        else:
            persistent_results.append(meaning_text)

    # If all top-k results are temporary, return only temporary results
    if len(temp_results) >= k:
        return temp_results[:k]

    # Otherwise, return a mix of both persistent and temporary results
    return (temp_results + persistent_results)[:k]



