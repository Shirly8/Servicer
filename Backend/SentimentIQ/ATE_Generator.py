import csv
import aiohttp
import os
import time
import logging
import asyncio
import pandas as pd
import random
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- PROMPT DEFINITION ---
# This prompt is highly structured to instruct the LLM on how to perform Aspect Term Extraction
# and format the output in the required BIO tagging scheme.
PROMPT_TEMPLATE = """Your task is to perform Aspect Term Extraction on a restaurant review sentence. I will provide you with a sentence. You must identify all words that are part of an aspect term. An aspect term is a specific phrase that refers to a conceptual category.

Here are the categories to consider:
Service, Ambience, Price, Food Quality, Taste, Value, Menu, Location, Drinks, Appetizers, Salads, Pasta, Main, Seafood, Desserts, Culture.

Format your output *only* as a JSON object with a single key "tags". The value should be a list of lists, where each inner list contains two strings: the word and its BIO tag. The tags are:
- B-ASPECT: The beginning of an aspect term.
- I-ASPECT: A word inside a multi-word aspect term.
- O: A word outside of any aspect term.

Do not provide any explanation, preamble, or summary. Your output must be only the JSON object.

Example:
Sentence: 'The fresh food and table setting were great.'
Your JSON Output:
{{
  "tags": [
    ["The", "O"],
    ["fresh", "B-ASPECT"],
    ["food", "I-ASPECT"],
    ["and", "O"],
    ["table", "B-ASPECT"],
    ["setting", "I-ASPECT"],
    ["were", "O"],
    ["great", "O"],
    [".", "O"]
  ]
}}

---
Now, process this sentence:
Sentence: '{sentence}'
Your JSON Output:
"""

# API URL for Ollama
API_URL = "http://localhost:11434/api/generate"

async def fetch_bio_tags_from_api(session, sentence):
    """Sends a sentence to the LLM and gets back the BIO-tagged version."""
    prompt = PROMPT_TEMPLATE.format(sentence=sentence)
    headers = {"Content-Type": "application/json"}
    # Using a powerful model and forcing JSON output for reliability
    data = {"model": "llama3:8b", "prompt": prompt, "stream": False, "format": "json"}
    
    try:
        async with session.post(API_URL, headers=headers, json=data) as response:
            response.raise_for_status()
            llm_response = await response.json()
            # The response itself is a JSON object, and the 'response' field contains a JSON *string*.
            json_string = llm_response.get("response", "{}")
            
            # Parse the JSON string from the response
            tagged_data = json.loads(json_string)
            
            # Convert the structured JSON back into the simple text format for the TSV file.
            output_lines = []
            tag_list = tagged_data.get("tags")

            if not isinstance(tag_list, list):
                logging.warning(f"JSON 'tags' is not a list for sentence '{sentence[:50]}...'. Skipping.")
                return None

            for item in tag_list:
                if isinstance(item, list) and len(item) == 2:
                    output_lines.append(f"{item[0]}\\t{item[1]}")
                else:
                    logging.warning(f"Skipping malformed item in 'tags' list: {item} for sentence '{sentence[:50]}...'")
            
            return "\n".join(output_lines)

    except (aiohttp.ClientError, json.JSONDecodeError) as e:
        logging.error(f"Error processing sentence '{sentence[:50]}...': {e}")
        return None
    except KeyError as e:
        logging.error(f"KeyError processing response for '{sentence[:50]}...': {e} - Response may not have expected structure.")
        return None

def _clean_bio_output(raw_output: str) -> str:
    """
    Cleans the raw output from the LLM to ensure it's in the correct BIO format.
    - Removes any preamble or extra text.
    - Ensures each line is a valid word-tag pair.
    """
    cleaned_lines = []
    
    # A set of valid tags for quick lookup
    valid_tags = {"O", "B-ASPECT", "I-ASPECT"}

    for line in raw_output.splitlines():
        line = line.strip()
        if not line:
            continue # Skip empty lines

        parts = line.split('\t')
        if len(parts) == 2 and parts[1].strip() in valid_tags:
            # This looks like a valid line, add it to our cleaned list
            cleaned_lines.append(f"{parts[0].strip()}\t{parts[1].strip()}")

    return "\n".join(cleaned_lines)

async def generate_ate_data(input_csv_list, output_tsv, session, num_samples=None):
    """
    Reads sentences from multiple input CSVs, generates BIO-tagged data, and writes to a TSV file.
    """
    try:
        # Read sentences from all provided CSV files
        all_sentences = []
        for input_csv in input_csv_list:
            if not os.path.exists(input_csv):
                logging.warning(f"Input file not found, skipping: {input_csv}")
                continue
            df = pd.read_csv(input_csv)
            all_sentences.extend(df['Review'].tolist())
        
        # Ensure we don't have duplicate sentences
        sentences = pd.Series(all_sentences).unique().tolist()
        
        # Take a random sample if num_samples is specified and the dataset is larger
        if num_samples and len(sentences) > num_samples:
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
        logging.error(f"Input file not found: {input_csv_list}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {type(e).__name__} - {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    async def main():
        # Define file paths relative to the script location
        script_dir = os.path.dirname(__file__)
        # Focusing only on the high-quality complex reviews for training the ATE model
        input_csv_path = os.path.join(script_dir, 'ASPAGeneratedReviews_5Star_Complex.csv')
        output_tsv_path = os.path.join(script_dir, 'ATE_Training_Data.tsv')

        # Run the generation process
        async with aiohttp.ClientSession() as session:
            
            # Process all unique sentences from the complex dataset
            await generate_ate_data(
                [input_csv_path], 
                output_tsv_path, 
                session
            )
    
    asyncio.run(main()) 