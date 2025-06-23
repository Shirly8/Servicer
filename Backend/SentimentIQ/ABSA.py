from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import csv
import os
import re
from ASPAGeneration import CATEGORY_PHRASES

# Loading the fine-tuned ABSA model/tokenizer/Classifier
script_dir = os.path.dirname(__file__)
model_name = os.path.join(script_dir, '5star-absa-v2')
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

        # The model outputs 'LABEL_X', where X is 0-4. Convert to 1-5 stars.
        label = result[0]['label']
        star_rating = int(label.split('_')[-1]) + 1
        confidence_score = result[0]['score']

        sentiment = {
            "Aspect": aspect,
            "Stars": star_rating,
            "Confidence": confidence_score
        }
        results.append(sentiment)
        print(f"Aspect: {aspect}, Stars: {star_rating}, Confidence: {confidence_score:.4f}")

    return results

def main():
    print("==============================================")
    print("=        Aspect-Based Sentiment Analyzer     =")
    print("=            (5-Star Rating Model)           =")
    print("==============================================")
    print("Enter a review sentence to analyze, or type 'exit' to quit.")
    
    while True:
        sentence = input("\nReview: ")
        if sentence.lower() == 'exit':
            break
        analyzeSentence(sentence)

if __name__ == "__main__":
    main()
