import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import pandas as pd

class SemanticAnalyzer:


    def __init__(self, absa_model_path, st_model_name='all-MiniLM-L6-v2'):
        
        # Load ABSA model and sentence transformer for sentiment scoring
        self.absa_tokenizer = AutoTokenizer.from_pretrained(absa_model_path)
        self.absa_model = AutoModelForSequenceClassification.from_pretrained(absa_model_path)
        self.absa_model.eval()
        print("✅ ABSA MODEL LOADED")

        self.st_model = SentenceTransformer(st_model_name)
        print(f"✅ SENTENCE TRANSFORMER MODEL LOADED")


        # Aspects categories for our semantic search and mapping
        self.descriptive_aspect_categories = [
            "Service and Staff", "Restaurant Ambience", "Price and Value", "Food Quality", "Taste and Flavor",
            "Menu Variety", "Location and Parking", "Drinks and Cocktails", "Appetizers", "Salads", "Pasta Dishes", 
            "Main Course", "Seafood", "Desserts"
        ]

        self.category_to_simple_aspect_map = {
            "Service and Staff": "Service", "Restaurant Ambience": "Ambience", "Price and Value": "Price",
            "Food Quality": "Food Quality", "Taste and Flavor": "Taste", "Menu Variety": "Menu",
            "Location and Parking": "Location", "Drinks and Cocktails": "Drinks", "Appetizers": "Appetizers",
            "Salads": "Salads", "Pasta Dishes": "Pasta", "Main Course": "Main",
            "Seafood": "Seafood", "Desserts": "Desserts"
        }
        

        # Pre-compute embeddings for all categories for fast lookup
        self.aspect_embeddings = self.st_model.encode(self.descriptive_aspect_categories, convert_to_tensor=True)
        print("✅ Aspect embeddings computed.")



    def _get_sentiment_for_aspect(self, sentence, aspect):

        # Format into classification an seperator token   [CLS] Waiter friendly [SEP] Service [SEP]
        inputs = self.absa_tokenizer(f"[CLS] {sentence} [SEP] {aspect} [SEP]", return_tensors="pt", truncation=True, max_length=512)
        
        with torch.no_grad():
            logits = self.absa_model(**inputs).logits                  #get predictions
        predicted_class_id = torch.argmax(logits, dim=1).item()        # raw score
        return predicted_class_id + 1                                  # star rating



    def get_aspect_sentiments(self, review_text, similarity_threshold=0.25, max_aspects=3):

        # 1. Find relevant aspects w/ semantic similarity
        review_embedding = self.st_model.encode(review_text, convert_to_tensor=True)
        similarities = util.cos_sim(review_embedding, self.aspect_embeddings)

        found_aspects = {}
        for i, score in enumerate(similarities[0]):
            if score > similarity_threshold:
                aspect = self.descriptive_aspect_categories[i]
                found_aspects[aspect] = score.item()
        
        if not found_aspects:
            return {}

        # 2. SOFT THE SCORE
        sorted_aspects = sorted(found_aspects.items(), key=lambda item: item[1], reverse=True)
        top_aspects = sorted_aspects[:max_aspects]
        

        # 3. Score sentiment for each of the top aspects and return a simple dict
        analysis_results = {}

        for descriptive_aspect, _ in top_aspects:
            # Map descriptive category to simple aspect for scoring
            simple_aspect = self.category_to_simple_aspect_map.get(descriptive_aspect, descriptive_aspect)
            sentiment_score = self._get_sentiment_for_aspect(review_text, simple_aspect)
            analysis_results[descriptive_aspect] = sentiment_score
            
        return analysis_results

# --- Evaluations ---
def evaluate_review_text(analyzer, review_text):
    print(f"\\nAnalyzing Review: '{review_text}'")
    sentiments = analyzer.get_aspect_sentiments(review_text, similarity_threshold=0.22, max_aspects=2)
    
    if not sentiments:
        print("  -> No relevant aspects found.")
    else:
        for aspect, stars in sentiments.items():
            print(f"    - {aspect}: {stars} star(s)")



def evaluate_from_csv(analyzer, csv_path, num_samples=5):
    if not os.path.exists(csv_path):
        print(f"\\nError: CSV file not found at {csv_path}")
        return []
        
    df = pd.read_csv(csv_path)
    unique_reviews = df['Review'].unique()
    sample_reviews = pd.Series(unique_reviews).sample(min(len(unique_reviews), num_samples), random_state=42)
    
    results = []
    print(f"\\n--- Evaluating on {len(sample_reviews)} samples from {os.path.basename(csv_path)} ---")
    for review in sample_reviews:
        sentiments = analyzer.get_aspect_sentiments(review, similarity_threshold=0.22, max_aspects=2)
        result = {"review": review, "sentiments": sentiments}
        results.append(result)
    
    return results



     
# --- Main Execution Block ---
if __name__ == '__main__':
    absa_path = os.path.join(os.path.dirname(__file__), '5star-absa-v2')
    analyzer = SemanticAnalyzer(absa_model_path=absa_path)

    # --- Testing---
    test_reviews = [
        "The employees are slow but the pasta was incredible.",
        "The restaurant was beautiful, but it was way too expensive.",
        "I didn't like the flavor of the fish, it tasted old.",
        "The parking situation is a complete nightmare.",
        "The waiters were friendly and the tiramisu was divine."
    ]
    for review in test_reviews:
        evaluate_review_text(analyzer, review)

    generated_csv_path = os.path.join(os.path.dirname(__file__), "ASPAGeneratedReviews_5Star_Complex.csv")
    csv_results = evaluate_from_csv(analyzer, generated_csv_path)
    for result in csv_results:
        print(f"\\nAnalyzing Review: '{result['review']}'")
        if not result['sentiments']:
            print("  -> No relevant aspects found.")
        else:
            for aspect, stars in result['sentiments'].items():
                print(f"    - {aspect}: {stars} star(s)")