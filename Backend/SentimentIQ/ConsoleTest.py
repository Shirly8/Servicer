import pandas as pd
from transformers import TextClassificationPipeline
from transformers import XLNetTokenizer, XLNetForSequenceClassification, TextClassificationPipeline
import csv


#Load model, tokenizer and classifier
model_path = './SentimentFilter'
tokenizer = XLNetTokenizer.from_pretrained(model_path)
model = XLNetForSequenceClassification.from_pretrained(model_path)
classifier = TextClassificationPipeline(model=model, tokenizer=tokenizer, top_k=None, device=-1)

#Make prediction for each text
def predict_sentiment(text):
    predictions = classifier(text)
    for prediction in predictions[0]:
        if prediction['label'] == 'LABEL_1':
            sentiment_score = prediction['score']
            return sentiment_score
    return 0


def main():

    threshold_positive = 0.75
    threshold_neutral = 0.50
    threshold_negative = 0.25

    while True:
        print(f"\n\n\nWelcome to Sentiment Reviewer. \n Threshold: \n  Positive: ", threshold_positive, "\n  Neutral: ", threshold_neutral, "\n  Negative: ", threshold_negative)

        text = input("Enter your review: ")
 
        sentiment_score = predict_sentiment(text)

        if sentiment_score >= threshold_positive:
            print(f"Positive Sentiment (Score: {sentiment_score:.2f})\n")
        elif sentiment_score > threshold_negative and sentiment_score < threshold_positive:
            print(f"Neutral Sentiment (Score: {sentiment_score:.2f})\n")
        else:
            print(f"Negative Sentiment (Score: {sentiment_score:.2f})\n")


def reviewCSV(filename):
    df = pd.read_csv(filename)


    with open('sentiment_scores2.csv', 'w') as file:
        writer = csv.writer(file)

        writer.writerow(['Review', 'Sentiment Score', 'Rating'])

        for index, row in df.iterrows():
            sentiment_score = predict_sentiment(row['Review'])
            writer.writerow([row['Review'], sentiment_score])



if __name__ == "__main__":
    main()

    # FOR REVIEWING CSV FILES
    # reviewCSV('./reviews.csv')

