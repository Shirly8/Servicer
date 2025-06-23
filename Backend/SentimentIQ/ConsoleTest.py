import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TextClassificationPipeline
import csv


#Load model, tokenizer and classifier
model_path = 'yangheng/deberta-v3-base-absa-v1.1'
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
classifier = TextClassificationPipeline(model=model, tokenizer=tokenizer, device=-1)

aspects = [
        "Service", "Ambience", "Price", "Food Quality", "Taste", "Value", "Menu", "Location", "Drinks"
    ]

#Make prediction for each text
def predict_sentiment(text):
    results = []
    for aspect in aspects:
        result = classifier(text, text_pair=aspect)
        sentiment_label = result[0]['label']
        score = result[0]['score']
        
        sentiment = {
            "Aspect": aspect,
            "Sentiment": sentiment_label,
            "Score": score
        }
        results.append(sentiment)
    return results


def main():

    while True:
        print(f"\n\n\nWelcome to Sentiment Reviewer.")

        text = input("Enter your review: ")
 
        sentiment_results = predict_sentiment(text)

        print("Aspect-Based Sentiment Scores:")
        for result in sentiment_results:
            print(f"  - {result['Aspect']}: {result['Sentiment']} (Score: {result['Score']:.2f})")


def reviewCSV(filename):
    df = pd.read_csv(filename)


    with open('sentiment_scores2.csv', 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['Review', 'Aspect', 'Sentiment', 'Score'])

        for index, row in df.iterrows():
            sentiment_results = predict_sentiment(row['Review'])
            for result in sentiment_results:
                writer.writerow([row['Review'], result['Aspect'], result['Sentiment'], result['Score']])



if __name__ == "__main__":
    main()

    # FOR REVIEWING CSV FILES
    # reviewCSV('./reviews.csv')

