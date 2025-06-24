import csv
import aiohttp
import os
import time
import logging
import random
import asyncio
import re
from SyntheticGeneration import SyntheticReviewGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
API_URL = "http://localhost:11434/api/generate"

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
        aspect = random.choice(list(SyntheticReviewGenerator.CATEGORY_PHRASES.keys()))
        phrase = random.choice(SyntheticReviewGenerator.CATEGORY_PHRASES[aspect])
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



    # COMPLEX GENERATION
    else:
        aspect1, aspect2 = random.sample(list(SyntheticReviewGenerator.CATEGORY_PHRASES.keys()), 2)
        phrase1, phrase2 = random.choice(SyntheticReviewGenerator.CATEGORY_PHRASES[aspect1]), random.choice(SyntheticReviewGenerator.CATEGORY_PHRASES[aspect2])
        rating1, rating2 = random.choice([4, 5]), random.choice([1, 2])
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
                return [
                    (message, positive_aspect, positive_rating),
                    (message, negative_aspect, negative_rating)
                ]
        except (aiohttp.ClientError, ValueError, KeyError) as e:
            logging.error(f"Error in complex review generation: {e}")
            return None



async def generate_messages_to_csv_with_session(filename, model, num_total_datapoints, session, generation_type='mixed'):
    try:
        file_exists = os.path.exists(filename)
        with open(filename, 'a', encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.writer(csv_file, quotechar='"', quoting=csv.QUOTE_ALL)
            if not file_exists:
                writer.writerow(["Review", "Aspect", "Ratings"])


            
            logging.info("WRITING HEADER..." if not file_exists else "APPENDING...")


            generated_count = 0
            while generated_count < num_total_datapoints:
                if generation_type == 'mixed':
                    gen_type = 'simple' if random.random() < 0.6 else 'complex'
                else:
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

if __name__ == "__main__":

    
    async def run_generation():
        async with aiohttp.ClientSession() as session:
            output_file = os.path.join(os.path.dirname(__file__), "AllABSAReviews.csv")
            await generate_messages_to_csv_with_session(output_file, "llama3:8b", 1000, session, generation_type='simple')
    
    asyncio.run(run_generation())