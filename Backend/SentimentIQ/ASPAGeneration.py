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
CATEGORY_PHRASES = {
    "Service": ["service", "wait times", "reservations", "staff", "waiter", "waitress", "wait", "waited", "check", "server", "host", "hostess", "bartender", "attentiveness"],
    "Ambience": ["ambience", "atmosphere", "decor", "noise level", "music", "lighting", "seating", "table setting", "noisy", "noise", "loud", "vibe", "setting", "cleanliness"],
    "Price": ["pricing", "cost", "affordability", "bill", "expense", "overpriced", "cheap", "expensive"],
    "Food Quality": ["food quality", "freshness", "ingredients", "presentation", "temperature of the food", "cooked", "dish", "plate", "preparation"],
    "Taste": ["taste of the food", "flavor", "seasoning", "texture"],
    "Value": ["value for money", "portion size", "portions", "serving size", "deal", "rip-off"],
    "Menu": ["menu variety", "menu options", "selection of dishes"],
    "Location": ["location", "accessibility", "parking"],
    "Drinks": ["drinks", "cocktails", "wine", "beer", "beverages"],
    "Appetizers": ["appetizers", "starters", "bruschetta", "calamari", "arancini", "prosciutto e melone", "truffle fries"],
    "Salads": ["salads", "caesar salad", "caprese salad", "arugula salad", "panzanella"],
    "Pasta": ["pasta", "spaghetti", "penne", "fettuccine", "gnocchi", "lasagna", "risotto", "ravioli"],
    "Main": ["main course", "entrees", "osso buco", "lamb chops", "veal marsala", "chicken piccata", "short ribs", "main dish", "signature dish", "special"],
    "Seafood": ["seafood", "fish", "swordfish", "salmon", "shrimp", "lobster", "scallops", "octopus", "crab cakes"],
    "Desserts": ["desserts", "tiramisu", "panna cotta", "crème brûlée", "cheesecake", "gelato", "sorbet"],
    "Culture": ["culture", "Italian", "European"]
}



PROMPT_TEMPLATE = "Generate a ONE SIMPLE SHORT SENTENCE, realistic restaurant review that discusses the {phrase}. Do not talk about other aspects. Do not mention any restaurant names. Aretti is the only allowed name."
PROMPT_TEMPLATE_COMPLEX = "Generate a SINGLE, realistic restaurant review sentence that contains both a POSITIVE sentiment about {positive_phrase} and a NEGATIVE sentiment about {negative_phrase}. Do not mention any other aspects. Do not mention any restaurant names. Aretti is the only allowed name."

SENTIMENTS = {0: "Negative", 1: "Positive", 2: "Complex"}

# API URL
API_URL = "http://localhost:11434/api/generate"

# Send prompt to Ollama API and return the generated message
async def fetch_review_from_api(session, model):
    sentiment = random.choice([0, 1, 2])  # 0: Negative, 1: Positive, 2: Complex

    # Simple Positive/Negative Review
    if sentiment == 0 or sentiment == 1:
        aspect = random.choice(list(CATEGORY_PHRASES.keys()))
        phrase = random.choice(CATEGORY_PHRASES[aspect])
        sentiment_str = "positive" if sentiment == 1 else "negative"
        prompt = PROMPT_TEMPLATE.format(phrase=phrase) + f" Make it a {sentiment_str} review."

        headers = {"Content-Type": "application/json"}
        data = {"model": model, "prompt": prompt, "stream": False}
        
        try:
            async with session.post(API_URL, headers=headers, json=data) as response:
                response.raise_for_status()
                llm_response = await response.json()
                message = llm_response["response"]
                return [(message, aspect, SENTIMENTS[sentiment])]
        except (aiohttp.ClientError, ValueError, KeyError) as e:
            logging.error(f"Error in simple review generation: {e}")
            return None
    
    # Complex Mixed-Sentiment Review
    else: # sentiment == 2
        # Pick two different aspects
        aspect1, aspect2 = random.sample(list(CATEGORY_PHRASES.keys()), 2)
        
        # Assign one positive, one negative
        positive_aspect, negative_aspect = random.sample([aspect1, aspect2], 2)
        
        positive_phrase = random.choice(CATEGORY_PHRASES[positive_aspect])
        negative_phrase = random.choice(CATEGORY_PHRASES[negative_aspect])
        
        prompt = PROMPT_TEMPLATE_COMPLEX.format(positive_phrase=positive_phrase, negative_phrase=negative_phrase)

        headers = {"Content-Type": "application/json"}
        data = {"model": model, "prompt": prompt, "stream": False}

        try:
            async with session.post(API_URL, headers=headers, json=data) as response:
                response.raise_for_status()
                llm_response = await response.json()
                message = llm_response["response"]
                # Return two data points from one generated sentence
                return [
                    (message, positive_aspect, "Positive"),
                    (message, negative_aspect, "Negative")
                ]
        except (aiohttp.ClientError, ValueError, KeyError) as e:
            logging.error(f"Error in complex review generation: {e}")
            return None

# Write generated messages to a CSV file
async def generate_messages_to_csv(filename, model, num_messages):
    # Always create a new file, so no need to check for header
    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(["Review", "Aspect", "Sentiment"])
            logging.info("WRITING HEADER...")
            
            generated_count = 0
            while generated_count < num_messages:
                start_time = time.time()
                results = await fetch_review_from_api(session, model)
                end_time = time.time()
                
                if results:
                    for message, aspect, sentiment in results:
                        if generated_count < num_messages:
                            clean_message = message.replace('\n', ' ').replace('\r', '').replace('"', '').strip()
                            writer.writerow([clean_message, aspect, sentiment])
                            logging.info(f"{clean_message} \nAspect: {aspect}, Sentiment: {sentiment} ({(end_time - start_time) * 1000:.2f}ms)\n\n")
                            generated_count += 1
            
            logging.info("FINISHED WRITING")
    except Exception as e:
        logging.error(f"Error writing to file: {e}")

async def main_async(filename, model, num_messages):
    async with aiohttp.ClientSession() as session:
        # Pass the session to the generation function
        await generate_messages_to_csv_with_session(filename, model, num_messages, session)

async def generate_messages_to_csv_with_session(filename, model, num_messages, session):
    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(["Review", "Aspect", "Sentiment"])
            logging.info("WRITING HEADER...")
            
            generated_count = 0
            while generated_count < num_messages:
                start_time = time.time()
                results = await fetch_review_from_api(session, model)
                end_time = time.time()
                
                if results:
                    for message, aspect, sentiment in results:
                        if generated_count < num_messages:
                            clean_message = message.replace('\n', ' ').replace('\r', '').replace('"', '').strip()
                            writer.writerow([clean_message, aspect, sentiment])
                            logging.info(f"{clean_message} \nAspect: {aspect}, Sentiment: {sentiment} ({(end_time - start_time) * 1000:.2f}ms)\n\n")
                            generated_count += 1
            
            logging.info("FINISHED WRITING")
    except Exception as e:
        logging.error(f"Error writing to file: {e}")

if __name__ == "__main__":
    # Use a single session for all requests
    async def run_generation():
        async with aiohttp.ClientSession() as session:
            await generate_messages_to_csv_with_session("ASPAGeneratedReviews.csv", "llama3:8b", 5000, session)
    
    asyncio.run(run_generation())