from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import csv
import os
import re
from ASPAGeneration import CATEGORY_PHRASES

# Loading the fine-tuned ABSA model/tokenizer/Classifier
script_dir = os.path.dirname(__file__)
model_name = os.path.join(script_dir, 'finetuned-ABSA')
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

def extract_aspects(text, category_phrases):
    """
    Extracts aspects from the text based on keywords.
    """
    present_aspects = set()
    text_lower = text.lower()
    for aspect, phrases in category_phrases.items():
        for phrase in phrases:
            # Using regex to find whole words to avoid matching parts of words
            if re.search(r'\b' + re.escape(phrase.lower()) + r'\b', text_lower):
                present_aspects.add(aspect)
                break  # Move to the next aspect once one phrase is found
    return list(present_aspects)

def analyzeSentence(sentence):
    # First, extract which aspects are present in the sentence
    present_aspects = extract_aspects(sentence, CATEGORY_PHRASES)

    if not present_aspects:
        print("No specific aspects found in the review.")
        return []

    results = []

    for aspect in present_aspects:
        result = classifier(sentence, text_pair=aspect)

        #find the label
        sentiment_label = result[0]['label']
        scores = result[0]['score']

        sentiment = {
            "Aspect": aspect,
            "Sentiment": sentiment_label,
            "Score": scores
        }
        results.append(sentiment)
        print(f"Aspect: {aspect}, Sentiment: {result[0]['label']} - {scores:.4f}")

    return results


import csv

def analyze_csv(input_csv):
    # Get all possible aspects from CATEGORY_PHRASES
    all_aspects = list(CATEGORY_PHRASES.keys())
    # Dictionary to store aspect sentiment scores
    aspect_scores = {aspect: [] for aspect in all_aspects}
    
    with open(input_csv, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        
        print(f"CSV Columns: {reader.fieldnames}")

        for row in reader:
            # The key should be 'Review' for a well-formed CSV.
            review = row.get('Review')
            if review:
                results = analyzeSentence(review)
                for result in results:
                    aspect_scores[result['Aspect']].append(result['Score'])

    # Calculate the average score for each aspect
    averaged_aspect_scores = {}
    for aspect, scores in aspect_scores.items():
        if scores:
            averaged_aspect_scores[aspect] = sum(scores) / len(scores)

    return averaged_aspect_scores




def main():
    
    while True:
        sentence = input("Please enter a sentence to analyze: ")
        analyzeSentence(sentence)

if __name__ == "__main__":
    main()
