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

class SyntheticReviewGenerator:

    API_URL = "http://localhost:11434/api/generate"

    @classmethod
    def generate_one_review_sync(cls, model):
        async def _get_one():
            star_rating = random.randint(1, 5)
            aspect = random.choice(list(cls.CATEGORY_PHRASES.keys()))
            phrase = random.choice(cls.CATEGORY_PHRASES[aspect])

            prompt = (
                f"Write a single-sentence review for Aretti that clearly reflects a {star_rating}-star experience, "
                f"focusing only on '{phrase}'. Do not mention the star rating explicitly. Try to be very natural and ensure the review is exactly {star_rating} stars."
            )
            headers = {"Content-Type": "application/json"}
            data = {"model": model, "prompt": prompt, "stream": False, "options": {"stop": ["\n"]}}
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(cls.API_URL, headers=headers, json=data) as response:
                        response.raise_for_status()
                        llm_response = await response.json()
                        message = llm_response["response"].strip().replace('"', '')
                        print(f"[GENERATED REVIEW] {message} (Rating: {star_rating})")
                        return {"Review": message, "Aspect": aspect, "Rating": star_rating}
            except Exception as e:
                return None
        return asyncio.run(_get_one())


    @classmethod
    def generate_reviews_to_csv(cls, model, num_reviews, csv_path):
        reviews = []
        for _ in range(num_reviews):
            review = cls.generate_one_review_sync(model)
            if review:
                reviews.append(review)
        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=["Review", "Aspect", "Rating"])
            writer.writeheader()
            writer.writerows(reviews)


    CATEGORY_PHRASES = {
        "Service": ["service", "wait times", "reservations", "staff", "waiter", "waitress", "wait", "waited", "check"],
        "Ambience": ["ambience", "atmosphere", "decor", "noise level", "music", "lighting", "seating", "table setting", "noisy", "noise", "loud", "cozy"],
        "Price": ["pricing", "cost", "affordability"],
        "Food Quality": ["food", "food quality", "freshness", "ingredients", "presentation", "temperature of the food", "cooked"],
        "Taste": ["taste of the food", "flavor", "seasoning", "texture"],
        "Value": ["value for money", "portion size"],
        "Menu": ["menu variety", "menu options", "selection of dishes"],
        "Location": ["location", "accessibility", "parking"],
        "Drinks": ["drinks", "cocktails", "wine", "beer", "beverages"],
        "Appetizers": ["appetizers", "starters", "bruschetta", "calamari", "arancini", "prosciutto e melone", "truffle fries"],
        "Salads": ["salads", "caesar salad", "caprese salad", "arugula salad", "panzanella"],
        "Pasta": ["pasta", "spaghetti", "penne", "fettuccine", "gnocchi", "lasagna", "risotto", "ravioli", "bland", "overcooked", "undercooked"],
        "Main": ["main course", "entrees", "osso buco", "lamb chops", "veal marsala", "chicken piccata", "short ribs"],
        "Seafood": ["seafood", "fish", "swordfish", "salmon", "shrimp", "lobster", "scallops", "octopus", "crab cakes"],
        "Desserts": ["desserts", "tiramisu", "panna cotta", "crème brûlée", "cheesecake", "gelato", "sorbet"],
        "Culture": ["Italian", "European"]
    }

