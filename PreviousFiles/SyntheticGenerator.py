import csv
import aiohttp
import os
import time
import logging
import random
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define constants for categories
CATEGORIES = {
    1: ("One review must be a 1 star review (Negative).", 1, 0),
    2: ("One review must be a 1 star review (Negative).", 1, 0),
    3: ("One review must be a 5 star review (Extremely Positive).", 5, 1),
    4: ("One review must be a 5 star review (Extremely Positive).", 5, 1),
    5: ("One review must be a 5 star review (Extremely Positive).", 5, 1),
    6: ("One review must be a 4 star review (Positive).", 4, 1),
    7: ("One review must be a 2 star review (Negative).", 2, 0),
}


# API URL
API_URL = "http://localhost:11434/api/generate"

# Send prompt to Ollama API and return the generated message
async def fetch_review_from_api(session, model):
    category = random.choice(list(CATEGORIES.keys()))
    prompt = "Generate JUST ONE VERY EXTREMELY EXTREMELY SHORT (Should replicate what a SHORT real review looks like) realistic product review for a French-Italian fine-dining restaurant in Toronto called Aretti. \
        You can focus on one or more of the following aspect: Service, ambience, price, beverages, wait time, food quality, menu variety, appetizers, starters, entrees, main courses, taste, pasta, value, Italian, French, seafood, meat, desserts, drinks, location, and decoration. \
        Make it different each time. ONLY ONE. \
        Don't say anything else. Do not mention the stars. " + CATEGORIES[category][0]

    rating, label = CATEGORIES[category][1], CATEGORIES[category][2]    

    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    # Send HTTP request to Ollama
    try:
        async with session.post(API_URL, headers=headers, json=data) as response:
            response.raise_for_status()
            llm_response = await response.json()
            return llm_response["response"], label, rating
    except aiohttp.ClientError as e:
        logging.error(f"Error making request: {e}")
        return None, None
    except (ValueError, KeyError) as e:
        logging.error(f"Error parsing response: {e}")
        return None, None

# Write generated messages to a CSV file without overwriting existing content
async def generate_messages_to_csv(filename, model, num_messages):
    generated_messages = []

    async with aiohttp.ClientSession() as session:
        try:

            #Check if file exists:
            file_exists = os.path.exists(filename) and os.stat(filename).st_size > 0

            with open(filename, 'w', encoding='utf-8-sig', newline='') as csv_file:
                writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)

                # Write header only if the file is empty or doesn't exists
                writer.writerow(["Review", "Label", "Rating"])
                logging.info("WRITING HEADER...")
    

                # Generate and write new messages
                for _ in range(num_messages):
                    start_time = time.time()
                    message, label, rating = await fetch_review_from_api(session, model)
                    end_time = time.time()
                    generated_time = (end_time - start_time) * 1000  # Milliseconds

                    if message is not None and label is not None:
                        generated_messages.append({"text": message, "rating": rating})

                        sanitized_message = message.replace('\n', ' ').replace('\r', '').strip()

                        writer.writerow([sanitized_message, label, rating])
                        logging.info(f"Generated Message: {message} \nRATING: {rating} ({generated_time:.2f}ms)\n\n")
                
                logging.info("FINISH WRTIING")
        except Exception as e:
            logging.error(f"Error writing to file: {e}")

    return generated_messages

def generate_one_review_sync(model, menu):
   
    async def _get_one():
        star_rating = random.randint(1, 5)
        prompt = (
            f"You are a customer at Aretti, an Italian restaurant in Toronto. "
            f"Here is the menu: {menu}.\n"
            f"Write a single-sentence review for Aretti that clearly reflects a {star_rating}-star experience. "
            f"Do not mention the star rating explicitly."
        )
        headers = {"Content-Type": "application/json"}
        data = {"model": model, "prompt": prompt, "stream": False, "options": {"stop": ["\n"]}}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, headers=headers, json=data) as response:
                    response.raise_for_status()
                    llm_response = await response.json()
                    message = llm_response["response"].strip().replace('"', '')
                    return {"Review": message, "Rating": star_rating}
        except Exception as e:
            print(f"LLM call failed: {e}")
            return None

    return asyncio.run(_get_one())

def generate_reviews_to_csv(model, menu, num_reviews, csv_path):
    reviews = []
    for _ in range(num_reviews):
        review = generate_one_review_sync(model, menu)
        if review:
            reviews.append(review)
    # Write to CSV
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["Review", "Rating"])
        writer.writeheader()
        writer.writerows(reviews)