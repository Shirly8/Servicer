import csv
import aiohttp
import os
import time
import logging
import random
import asyncio
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
API_URL = "http://localhost:11434/api/generate"

# Menu string for Aretti
ARETTI_MENU = (
    "Drinks: cocktails, wine, beer, beverages. "
    "Appetizers: bruschetta, calamari, arancini, prosciutto e melone, truffle fries. "
    "Salads: caesar salad, caprese salad, arugula salad, panzanella. "
    "Pasta: spaghetti, penne, fettuccine, gnocchi, lasagna, risotto, ravioli. "
    "Main: osso buco, lamb chops, veal marsala, chicken piccata, short ribs. "
    "Seafood: swordfish, salmon, shrimp, lobster, scallops, octopus, crab cakes. "
    "Desserts: tiramisu, panna cotta, crème brûlée, cheesecake, gelato, sorbet."
)

CATEGORY_PHRASES = {
    "Service": ["service", "wait times", "reservations", "staff", "waiter", "waitress", "wait", "waited", "check"],
    "Ambience": ["ambience", "atmosphere", "decor", "noise level", "music", "lighting", "seating", "table setting", "noisy", "noise", "loud"],
    "Price": ["pricing", "cost", "affordability"],
    "Food Quality": ["food", "food quality", "freshness", "ingredients", "presentation", "temperature of the food", "cooked"],
    "Taste": ["taste of the food", "flavor", "seasoning", "texture"],
    "Value": ["value for money", "portion size"],
    "Menu": ["menu variety", "menu options", "selection of dishes"],
    "Location": ["location", "accessibility", "parking"],
    "Drinks": ["drinks", "cocktails", "wine", "beer", "beverages"],
    "Appetizers": ["appetizers", "starters", "bruschetta", "calamari", "arancini", "prosciutto e melone", "truffle fries"],
    "Salads": ["salads", "caesar salad", "caprese salad", "arugula salad", "panzanella"],
    "Pasta": ["pasta", "spaghetti", "penne", "fettuccine", "gnocchi", "lasagna", "risotto", "ravioli"],
    "Main": ["main course", "entrees", "osso buco", "lamb chops", "veal marsala", "chicken piccata", "short ribs"],
    "Seafood": ["seafood", "fish", "swordfish", "salmon", "shrimp", "lobster", "scallops", "octopus", "crab cakes"],
    "Desserts": ["desserts", "tiramisu", "panna cotta", "crème brûlée", "cheesecake", "gelato", "sorbet"],
    "Culture": ["Italian", "European"]
}

# Send prompt to Ollama API and return the generated message
async def fetch_review_from_api(session, model, generation_type='simple'):
    
    STAR_RATING_DESCRIPTIONS = {
        1: "an unambiguously terrible, 1-star",
        2: "a clearly disappointing, 2-star",
        3: "a mixed or average, 3-star",
        4: "a solidly good, 4-star",
        5: "an exceptionally great, 5-star"
    }

    PROMPT_TEMPLATE_SIMPLE = "Generate a single, realistic restaurant review sentence. The review MUST ONLY discuss '{phrase}' and it should reflect {rating_description} rating. Do not add any extra text, explanations, or scores."
    PROMPT_TEMPLATE_COMPLEX = "Generate a SINGLE, realistic restaurant review sentence that contains both a POSITIVE sentiment about '{phrase1}' reflecting a {rating_description1} rating, and a NEGATIVE sentiment about '{phrase2}' reflecting a {rating_description2} rating. Do not mention any other aspects. The sentence must flow naturally."

    headers = {"Content-Type": "application/json"}
    

    if generation_type == 'simple':
        aspect = random.choice(list(CATEGORY_PHRASES.keys()))
        phrase = random.choice(CATEGORY_PHRASES[aspect])
        star_rating = random.randint(1, 5)
        rating_description = STAR_RATING_DESCRIPTIONS[star_rating]
        prompt = PROMPT_TEMPLATE_SIMPLE.format(phrase=phrase, rating_description=rating_description)
        data = {"model": model, "prompt": prompt, "stream": False, "options": {"stop": ["\n"]}}
        
        try:
            async with session.post(API_URL, headers=headers, json=data) as response:
                response.raise_for_status()
                llm_response = await response.json()
                message = llm_response["response"].strip().replace('"', '')
                return [(message, aspect, star_rating)]
        except (aiohttp.ClientError, ValueError, KeyError) as e:
            logging.error(f"Error in simple review generation: {e}")
            return None


    #COMPLEX GENERATION
    else: 

        # Pick two different aspects ensuring one is positive and one is negative
        aspect1, aspect2 = random.sample(list(CATEGORY_PHRASES.keys()), 2)
        phrase1, phrase2 = random.choice(CATEGORY_PHRASES[aspect1]), random.choice(CATEGORY_PHRASES[aspect2])        
        rating1, rating2 = random.choice([4, 5]), random.choice([1, 2])
        

        # Randomly assign which is which
        if random.random() > 0.5:
            positive_aspect, negative_aspect = aspect1, aspect2
            positive_phrase, negative_phrase = phrase1, phrase2
            positive_rating, negative_rating = rating1, rating2
        else:
            positive_aspect, negative_aspect = aspect2, aspect1
            positive_phrase, negative_phrase = phrase2, phrase1
            positive_rating, negative_rating = rating2, rating1


        rating_desc_pos = STAR_RATING_DESCRIPTIONS[positive_rating]
        rating_desc_neg = STAR_RATING_DESCRIPTIONS[negative_rating]

        prompt = PROMPT_TEMPLATE_COMPLEX.format(
            phrase1=positive_phrase, rating_description1=rating_desc_pos,
            phrase2=negative_phrase, rating_description2=rating_desc_neg
        )

        data = {"model": model, "prompt": prompt, "stream": False, "options": {"stop": ["\n"]}}

        try:
            async with session.post(API_URL, headers=headers, json=data) as response:
                response.raise_for_status()
                llm_response = await response.json()
                message = llm_response["response"].strip().replace('"', '')


                # Return two inputs from the single generated sentence
                return [
                    (message, positive_aspect, positive_rating),
                    (message, negative_aspect, negative_rating)
                ]
            

        except (aiohttp.ClientError, ValueError, KeyError) as e:
            logging.error(f"Error in complex review generation: {e}")
            return None


async def generate_messages_to_csv_with_session(filename, model, num_total_datapoints, session, generation_type='mixed'):
    try:
        with open(filename, 'w', encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)
            writer.writerow(["Review", "Aspect", "Ratings"])
            logging.info("WRITING HEADER...")
            
            generated_count = 0
            while generated_count < num_total_datapoints:
                
                if generation_type == 'mixed':
                    # Generate a mix of simple and complex reviews (e.g., 60% simple, 40% complex)
                    gen_type = 'simple' if random.random() < 0.6 else 'complex'
                else:
                    # Use the specified generation type
                    gen_type = generation_type
                
                start_time = time.time()
                results = await fetch_review_from_api(session, model, generation_type=gen_type)
                end_time = time.time()
                
                if results:
                    for message, aspect, star_rating in results:
                        if generated_count < num_total_datapoints:
                            writer.writerow([message, aspect, star_rating])
                            logging.info(f"{message} \nType: {gen_type.upper()}, Aspect: {aspect}, Ratings: {star_rating} ({(end_time - start_time) * 1000:.2f}ms)\n\n")
                            generated_count += 1
            

            logging.info(f"FINISHED WRITING {generated_count}.")

    except Exception as e:
        logging.error(f"Error writing to file: {e}")


def generate_one_review_sync(model):
    async def _get_one():
        star_rating = random.randint(1, 5)
        aspect = random.choice(list(CATEGORY_PHRASES.keys()))
        phrase = random.choice(CATEGORY_PHRASES[aspect])
        prompt = (
            f"You are a customer at Aretti, an Italian restaurant in Toronto. "
            f"Write a single-sentence review for Aretti that clearly reflects a {star_rating}-star experience, "
            f"focusing only on '{phrase}'. Do not mention the star rating explicitly."
        )
        headers = {"Content-Type": "application/json"}
        data = {"model": model, "prompt": prompt, "stream": False, "options": {"stop": ["\n"]}}
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, headers=headers, json=data) as response:
                    response.raise_for_status()
                    llm_response = await response.json()
                    message = llm_response["response"].strip().replace('"', '')


                    print(f"[GENERATED REVIEW] {message} (Rating: {star_rating})")
                    return {"Review": message, "Aspect": aspect, "Rating": star_rating}
        except Exception as e:
            
            return None
    return asyncio.run(_get_one())


def generate_reviews_to_csv(model, num_reviews, csv_path):
    reviews = []
    for _ in range(num_reviews):
        review = generate_one_review_sync(model)
        if review:
            reviews.append(review)
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["Review", "Aspect", "Rating"])
        writer.writeheader()
        writer.writerows(reviews)


# --- UI-facing function: Only generates simple aspect-based reviews ---
async def generate_simple_review_for_ui(session, model):
    """
    UI-facing function to generate a single, simple aspect-based review.
    Returns a dict with Review, Aspect, and Rating keys, or None on failure.
    """
    results = await fetch_review_from_api(session, model, generation_type='simple')
    if results:
        message, aspect, star_rating = results[0]
        return {"Review": message, "Aspect": aspect, "Rating": star_rating}
    return None


if __name__ == "__main__":
    async def run_generation():
        async with aiohttp.ClientSession() as session:
            
            # File output path
            output_file = os.path.join(os.path.dirname(__file__), "SyntheticReviews.csv")
            
            # MODEL NAME, NUMBER OF DATA, and GENERATION TYPE ('simple', 'complex', or 'mixed')
            await generate_messages_to_csv_with_session(output_file, "llama3:8b", 16, session, generation_type='simple')
    
    asyncio.run(run_generation())