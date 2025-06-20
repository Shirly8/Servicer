import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from transformers import XLNetTokenizer, XLNetForSequenceClassification, TextClassificationPipeline


#Load classifier from pretrained model
def load_classifier(model_path): 
    tokenizer = XLNetTokenizer.from_pretrained(model_path)
    model = XLNetForSequenceClassification.from_pretrained(model_path)
    return TextClassificationPipeline(model = model, tokenizer = tokenizer, top_k=None, device=-1)


#Function for Computing Metrics and returning dictionary
def compute_metrics(labels, predictions):
 precision, recall, f1, _ = precision_recall_fscore_support(labels, predictions, average='binary')
 acc = accuracy_score(labels, predictions)
 return {
        'accuracy': acc, # % of correct predictions (+/-)
        'precision': precision, # % of correct positive predictions 
        'recall': recall, # % of correct positive predictions of all actual positive instances
        'f1': f1 # Harmonic mean of precision and recall
    }

def computing(datafile):
    print("Running...")
    classifier = load_classifier('./SentimentFilter')

    #Load validation set, split into texts and labels
    data = pd.read_csv(datafile, encoding='utf-8-sig')

    print(data)


    validation_texts = data['Review'].tolist()
    validation_labels = data['Label'].tolist()


    #Tokenize the text
    predictions = classifier(validation_texts)

    #Convert predictions to binary formats
    predicted_labels = [0 if pred[0]['label'] == 'LABEL_0' else 1 for pred in predictions]

    # Print table: 
    print(f"{'Predicted':<10} {'Actual':<10}")
    print("-" * 20)
    for actual_label, predicted_label in zip(validation_labels, predicted_labels):
        print(f" {predicted_label:<10} {actual_label:<10}")
        print("-" * 20)

    metrics = compute_metrics(validation_labels, predicted_labels)
    print(metrics)

    return metrics

if __name__ == "__main__":
    computing('./SyntheticData.csv')

    # calculate_metrics('./sentiment_scores.csv', './reviews.csv')

