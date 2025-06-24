import torch
from sentence_transformers import SentenceTransformer, util
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os
import pandas as pd
from SentimentIQ.SyntheticGeneration import SyntheticReviewGenerator
# from SyntheticGeneration import SyntheticReviewGenerator

class SemanticAnalyzer:
   

    # Loading for semantic similarity
    def __init__(self, absa_model_path, st_model_name='all-MiniLM-L6-v2'):


        self.absa_tokenizer = AutoTokenizer.from_pretrained(absa_model_path)
        self.absa_model = AutoModelForSequenceClassification.from_pretrained(absa_model_path)
        self.absa_model.eval()

        self.st_model = SentenceTransformer(st_model_name)


        # MAP DESCRIPTIVE ASPECTS TO SIMPLE ASPECTS
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


        # Pre-computes embeddings for all ASPECTS
        self.aspect_embeddings = self.st_model.encode(self.descriptive_aspect_categories, convert_to_tensor=True)
        self.aspect_keywords = SyntheticReviewGenerator.CATEGORY_PHRASES




    def _get_sentiment_for_aspect(self, sentence, aspect):

        # Tokenize sentece:aspect pair
        inputs = self.absa_tokenizer(f"[CLS] {sentence} [SEP] {aspect} [SEP]", return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            logits = self.absa_model(**inputs).logits    #Runs through ABSA Model
        predicted_class_id = torch.argmax(logits, dim=1).item()
        return predicted_class_id + 1





    # Check if any keyword is in the text
    def _keyword_in_text(self, keywords, text):
        
        text_lower = text.lower()
        return any(kw.lower() in text_lower for kw in keywords)



    def get_aspect_sentiments(self, review_text, similarity_threshold=0.25, max_aspects=3):
        """
        Return {aspect: sentiment_score} for the most relevant aspects in the review.
        """
        # 1. Get review embedding and compare with aspect embeddings
        review_embedding = self.st_model.encode(review_text, convert_to_tensor=True)
        similarities = util.cos_sim(review_embedding, self.aspect_embeddings)[0]

        keyword_matched = []
        non_keyword_candidates = []

        # 2. For each aspect, check for keyword or high similarity
        for i, descriptive_aspect in enumerate(self.descriptive_aspect_categories):
            simple_aspect = self.category_to_simple_aspect_map.get(descriptive_aspect, descriptive_aspect)
            keywords = self.aspect_keywords.get(simple_aspect, [])
            has_keyword = keywords and self._keyword_in_text(keywords, review_text)
            sim = similarities[i].item()

            # 2a. If keyword present, add to keyword_matched
            if has_keyword:
                keyword_matched.append((simple_aspect, sim))


                
            # 2b. If similarity > threshold, add to non_keyword_candidates
            elif sim > similarity_threshold:
                non_keyword_candidates.append((simple_aspect, sim))

        # 3. Always include all keyword-matched aspects
        included_aspects = keyword_matched.copy()



        # 4. Fill up to max_aspects with highest-similarity non-keyword aspects
        non_keyword_candidates = sorted(non_keyword_candidates, key=lambda x: x[1], reverse=True)
        for aspect, sim in non_keyword_candidates:
            if len(included_aspects) >= max_aspects:
                break
            if aspect not in [a[0] for a in included_aspects]:
                included_aspects.append((aspect, sim))



        # 5. If nothing found, return empty
        if not included_aspects:
            return {}

        # 6. For each included aspect, get sentiment score
        analysis_results = {}
        for simple_aspect, _ in included_aspects:
            sentiment_score = self._get_sentiment_for_aspect(review_text, simple_aspect)
            analysis_results[simple_aspect] = sentiment_score
        return analysis_results



# --- Evaluation helpers ---
def evaluate_review_text(analyzer, review_text):
    print(f"\nAnalyzing Review: '{review_text}'")
    sentiments = analyzer.get_aspect_sentiments(review_text, similarity_threshold=0.22, max_aspects=2)
    if not sentiments:
        print("  -> No relevant aspects found.")
    else:
        for aspect, stars in sentiments.items():
            print(f"    - {aspect}: {stars} star(s)")





def evaluate_from_csv(analyzer, csv_path, num_samples=5):
    if not os.path.exists(csv_path):
        print(f"\nError: CSV file not found at {csv_path}")
        return []
    df = pd.read_csv(csv_path)
    unique_reviews = df['Review'].unique()
    sample_reviews = pd.Series(unique_reviews).sample(min(len(unique_reviews), num_samples), random_state=42)
    results = []
    print(f"\n--- Evaluating on {len(sample_reviews)} samples from {os.path.basename(csv_path)} ---")
    for review in sample_reviews:
        sentiments = analyzer.get_aspect_sentiments(review, similarity_threshold=0.22, max_aspects=2)
        results.append({"review": review, "sentiments": sentiments})
    return results




if __name__ == '__main__':
    absa_path = os.path.join(os.path.dirname(__file__), '5star-absa-v3')
    analyzer = SemanticAnalyzer(absa_model_path=absa_path)
    text = "The pasta was overcooked and bland, but the waiter was incredibly friendly and the ambience was cozy."
    
    
    aspect_sentiments = analyzer.get_aspect_sentiments(
        text,
        similarity_threshold=0.30,
        max_aspects=4
    )

    
    print(aspect_sentiments)
