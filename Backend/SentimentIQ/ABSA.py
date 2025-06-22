from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import csv

# Loading the ABSA model/tokenizer/Classfier
model_name = './ABSA'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)
classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)

aspects = [
        "Service", "Ambience", "Price", "Food Quality", "Taste", "Value", "Menu", "Location", "Drinks"
    ]

def analyzeSentence(sentence):

    results = []

    for aspect in aspects:
        result = classifier(sentence, text_pair=aspect)

        #find the label
        sentiment_label = result[0]['label']
        scores = result[0]['score']

        if (sentiment_label == 'Positive' or sentiment_label == 'Negative') and scores >= 0.95:
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
    # Dictionary to store aspect sentiment scores
    aspect_scores = {aspect: [] for aspect in aspects}
    
    with open(input_csv, 'r') as infile:
        reader = csv.DictReader(infile)

        # Clean up column names to remove BOM and any extra whitespace
        fieldnames = [field.lstrip('\ufeff').strip() for field in reader.fieldnames]
        reader = csv.DictReader(infile, fieldnames=fieldnames)

        print(f"CSV Columns: {reader.fieldnames}")

        for row in reader:
            review = row['"Review"']  # Note that the column is named with quotes.
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
    
    sentence = input("Please enter a sentence to analyze: ")
    analyzeSentence(sentence)

if __name__ == "__main__":
    main()
