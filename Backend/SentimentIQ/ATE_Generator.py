import csv
import aiohttp
import os
import time
import logging
import asyncio
import pandas as pd
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- PROMPT DEFINITION ---
# This prompt is highly structured to instruct the LLM on how to perform Aspect Term Extraction
# and format the output in the required BIO tagging scheme.
PROMPT_TEMPLATE = """Your task is to perform Aspect Term Extraction on a restaurant review sentence. I will provide you with a sentence. You must identify all words that are part of an aspect term. An aspect term is a specific phrase that refers to a conceptual category.

Here are the categories to consider:
Service, Ambience, Price, Food Quality, Taste, Value, Menu, Location, Drinks, Appetizers, Salads, Pasta, Main, Seafood, Desserts, Culture.

Format your output *only* in the BIO (Beginning, Inside, Outside) format. Each word from the sentence must be on a new line, followed by a tab character (\\t), and then its tag. The tags are:
- B-ASPECT: The beginning of an aspect term.
- I-ASPECT: A word inside a multi-word aspect term.
- O: A word outside of any aspect term.

Do not provide any explanation, preamble, or summary. Your output must contain only the tab-separated words and tags.

Example:
Sentence: 'The fresh food and table setting were great.'
Your Output:
The\tO
fresh\tB-ASPECT
food\tI-ASPECT
and\tO
table\tB-ASPECT
setting\tI-ASPECT
were\tO
great\tO
.\tO

---
Now, process this sentence:
Sentence: '{sentence}'
Your Output:
"""

# API URL for Ollama
API_URL = "http://localhost:11434/api/generate"

async def fetch_bio_tags_from_api(session, sentence):
    """Sends a sentence to the LLM and gets back the BIO-tagged version."""
    prompt = PROMPT_TEMPLATE.format(sentence=sentence)
    headers = {"Content-Type": "application/json"}
    # Using a powerful model is important for this complex instruction-following task
    data = {"model": "llama3:8b", "prompt": prompt, "stream": False}
    
    try:
        async with session.post(API_URL, headers=headers, json=data) as response:
            response.raise_for_status()
            llm_response = await response.json()
            # Clean up the response to only get the BIO-tagged output
            message = llm_response.get("response", "").strip()
            # Additional check to remove any accidental preamble the model might add
            if "Your Output:" in message:
                message = message.split("Your Output:")[-1].strip()
            return message
    except aiohttp.ClientError as e:
        logging.error(f"Error making request: {e}")
        return None
    except (ValueError, KeyError) as e:
        logging.error(f"Error parsing response: {e}")
        return None

async def generate_ate_data(input_csv, output_tsv, session, num_samples=500):
    """
    Reads sentences from an input CSV, generates BIO-tagged data, and writes to a TSV file.
    """
    try:
        # Read sentences from the existing review CSV
        df = pd.read_csv(input_csv)
        # Ensure we don't have duplicate sentences
        sentences = df['Review'].unique().tolist()
        
        # Take a random sample if the dataset is large
        if len(sentences) > num_samples:
            sentences = random.sample(sentences, num_samples)

        with open(output_tsv, 'w', encoding='utf-8', newline='') as tsv_file:
            logging.info(f"Starting BIO tag generation for {len(sentences)} unique sentences.")
            
            for i, sentence in enumerate(sentences):
                start_time = time.time()
                bio_tagged_output = await fetch_bio_tags_from_api(session, sentence)
                end_time = time.time()
                
                if bio_tagged_output:
                    # Write the BIO-tagged output, followed by a blank line to separate sentences
                    tsv_file.write(bio_tagged_output + "\n\n")
                    logging.info(f"({i+1}/{len(sentences)}) Processed sentence. ({(end_time - start_time) * 1000:.2f}ms)")
                else:
                    logging.warning(f"Failed to process sentence: {sentence}")
            
            logging.info(f"FINISHED WRITING BIO-TAGGED DATA to {output_tsv}")
            
    except FileNotFoundError:
        logging.error(f"Input file not found: {input_csv}")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    async def main():
        # Define file paths relative to the script location
        script_dir = os.path.dirname(__file__)
        input_csv_path = os.path.join(script_dir, 'ASPAGeneratedReviews_5Star.csv')
        output_tsv_path = os.path.join(script_dir, 'ATE_Training_Data.tsv')

        # Run the generation process
        async with aiohttp.ClientSession() as session:
            # We will generate BIO tags for 500 unique sentences as a starting point.
            await generate_ate_data(input_csv_path, output_tsv_path, session, num_samples=500)
    
    asyncio.run(main()) 