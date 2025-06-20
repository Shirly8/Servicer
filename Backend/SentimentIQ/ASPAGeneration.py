import csv
import aiohttp
import os
import time
import logging
import random
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define aspect categories and sentiments
CATEGORIES = {
    "Service": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the service and nothing else. Do not mention any restaurant names.",
    "Ambience": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the ambience and nothing else. Do not mention any restaurant names.",
    "Price": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the pricing and nothing else. Do not mention any restaurant names.",
    "Food Quality": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the food quality and nothing else. Do not mention any restaurant names.",
    "Taste": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the taste of the food and nothing else. Do not mention any restaurant names.",
    "Value": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the value for money and nothing else. Do not mention any restaurant names.",
    "Menu": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the menu variety and nothing else. Do not mention any restaurant names.",
    "Location": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the location and nothing else. Do not mention any restaurant names.",
    "Drinks": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the drinks and nothing else. Do not mention any restaurant names.",
    "Pasta": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the pasta and nothing else. Do not mention any restaurant names.",
    "Seafood": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the seafood and nothing else. Do not mention any restaurant names.",
    "Appetizer": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the appetizer and nothing else. Do not mention any restaurant names.",
    "Desserts": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the desserts and nothing else. Do not mention any restaurant names.",
    "Decoration": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the decoration and nothing else. Do not mention any restaurant names.",
    "Italian": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the Italian cuisine and nothing else. Do not mention any restaurant names.",
    "Main Entrees": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the main entrees and nothing else. Do not mention any restaurant names.",
    "Reservation / Waiting Time": "Generate a ONE SENTENCE, realistic restaurant review that ONLY discusses the reservation or waiting time and nothing else. Do not mention any restaurant names."
}


SENTIMENTS = {0: "Negative", 1: "Positive"}

# API URL
API_URL = "http://localhost:11434/api/generate"

# Send prompt to Ollama API and return the generated message
async def fetch_review_from_api(session, model):
    aspect = random.choice(list(CATEGORIES.keys()))
    sentiment = random.choice([0, 1])  # 0 = Negative, 1 = Positive
    prompt = CATEGORIES[aspect] + (" Make it a negative review." if sentiment == 0 else " Make it a positive review.")
    
    headers = {"Content-Type": "application/json"}
    data = {"model": model, "prompt": prompt, "stream": False}
    
    try:
        async with session.post(API_URL, headers=headers, json=data) as response:
            response.raise_for_status()
            llm_response = await response.json()
            return llm_response["response"], aspect, SENTIMENTS[sentiment]
    except aiohttp.ClientError as e:
        logging.error(f"Error making request: {e}")
        return None, None, None
    except (ValueError, KeyError) as e:
        logging.error(f"Error parsing response: {e}")
        return None, None, None

# Write generated messages to a CSV file
async def generate_messages_to_csv(filename, model, num_messages):
    async with aiohttp.ClientSession() as session:
        try:
            with open(filename, 'w', encoding='utf-8-sig', newline='') as csv_file:
                writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)
                writer.writerow(["Review", "Aspect", "Sentiment"])
                logging.info("WRITING HEADER...")
                
                for _ in range(num_messages):
                    start_time = time.time()
                    message, aspect, sentiment = await fetch_review_from_api(session, model)
                    end_time = time.time()
                    
                    if message is not None:
                        sanitized_message = message.replace('\n', ' ').replace('\r', '').strip()
                        writer.writerow([sanitized_message, aspect, sentiment])
                        logging.info(f"Generated Review: {message} \nAspect: {aspect}, Sentiment: {sentiment} ({(end_time - start_time) * 1000:.2f}ms)\n\n")
                
                logging.info("FINISHED WRITING")
        except Exception as e:
            logging.error(f"Error writing to file: {e}")
