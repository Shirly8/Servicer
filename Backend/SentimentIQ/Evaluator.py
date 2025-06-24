import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
import os
import sys
import json
sys.path.append(os.path.dirname(__file__))
from SemanticAnalyzer import SemanticAnalyzer


def compute_metrics(true_labels, pred_labels):
    acc = accuracy_score(true_labels, pred_labels)
    report = classification_report(true_labels, pred_labels, output_dict=True, zero_division=0)
    return {
        'accuracy': acc,
        'precision': report['weighted avg']['precision'],
        'recall': report['weighted avg']['recall'],
        'f1': report['weighted avg']['f1-score'],
        'full_report': report
    }

def evaluate_absa_multiclass(csv_path, absa_model_path, output_path=None):
    print(f"Evaluating ABSA multi-class on {csv_path}")
    analyzer = SemanticAnalyzer(absa_model_path=absa_model_path)
    df = pd.read_csv(csv_path)

    y_true = []
    y_pred = []
    missed = 0

    # For aspect averages
    aspect_sums = {}
    aspect_counts = {}

    for idx, row in df.iterrows():
        review = row['Review']
        aspect = row['Aspect']
        true_rating = int(row['Rating'])
        # Track aspect averages
        aspect_sums[aspect] = aspect_sums.get(aspect, 0) + true_rating
        aspect_counts[aspect] = aspect_counts.get(aspect, 0) + 1


        # Predicted aspect sentiments
        pred_aspects = analyzer.get_aspect_sentiments(review, similarity_threshold=0.22, max_aspects=3)
        # Try to match the labeled aspect (case-insensitive, allow mapping)
        matched = False
        for pred_aspect, pred_rating in pred_aspects.items():
            if aspect.lower() in pred_aspect.lower() or pred_aspect.lower() in aspect.lower():
                y_true.append(true_rating)
                y_pred.append(pred_rating)
                matched = True
                break
        if not matched:

            
            # If the labeled aspect is not found, count as missed
            missed += 1
    
    print(f"Total reviews: {len(df)} | Evaluated: {len(y_true)} | Missed: {missed}")
    metrics = compute_metrics(y_true, y_pred)

    # Compute aspect averages
    aspect_averages = {aspect: aspect_sums[aspect] / aspect_counts[aspect] for aspect in aspect_sums}
    metrics['aspect_averages'] = aspect_averages
    print(f"Accuracy: {metrics['accuracy']:.3f}")
    print(f"Precision: {metrics['precision']:.3f}")
    print(f"Recall: {metrics['recall']:.3f}")
    print(f"F1: {metrics['f1']:.3f}")
    print("\nClassification Report:")
    print(pd.DataFrame(metrics['full_report']).transpose())
    print("\nAspect Averages:")
    print(aspect_averages)
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, ensure_ascii=False, indent=2)
    return metrics




if __name__ == "__main__":
    absa_model_path = os.path.join(os.path.dirname(__file__), '5star-absa-v3')
    csv_path = os.path.join(os.path.dirname(__file__), 'SyntheticReviews.csv')
    output_path = os.path.join(os.path.dirname(__file__), 'evaluation_results.json')
    evaluate_absa_multiclass(csv_path, absa_model_path, output_path)

