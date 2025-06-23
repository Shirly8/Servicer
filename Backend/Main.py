from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from SentimentIQ import SyntheticGeneration
import asyncio
import aiohttp
import os
import csv
import json
from SentimentIQ.SemanticAnalyzer import SemanticAnalyzer
from QueryIQ import Query
from QueryIQ import RAG
from RecommendIQ import NCF


app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

# --- Load Models and Data on Start ---
base_dir = os.path.dirname(os.path.abspath(__file__))
absa_model_path = os.path.join(base_dir, 'SentimentIQ', '5star-absa-v2')
reviews_csv_path = os.path.join(base_dir, 'SentimentIQ', 'SyntheticReviews.csv')
analyzer = SemanticAnalyzer(absa_model_path=absa_model_path)


# SENTIMENTIQ: Endpoint to get the pre-generated list of reviews
@app.route('/getInitialReviews', methods=['GET'])
def get_initial_reviews():
    print("--- Received request for /getInitialReviews ---")
    reviews = []
    try:
        with open(reviews_csv_path, mode='r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                reviews.append({"message": row["Review"], "rating": row["Rating"]})


    except FileNotFoundError:
        return jsonify({"error": "Initial reviews file not found."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    print(f"--- Found {len(reviews)} reviews. Sending to frontend. ---")
    return jsonify(reviews)


# SENTIMENTIQ: Generate new reviews and write to CSV
@app.route('/generateReviews', methods=['POST'])
def generate_reviews():
    model = 'llama3:8b'
    num_reviews = 15
    SyntheticGeneration.generate_reviews_to_csv(model, num_reviews, reviews_csv_path)
    return jsonify({"success": True})


# SENTIMENT IQ - GETS THE TEXT AND SENDS TO THE MODEL
@app.route('/analyzeSentiment', methods=['POST'])
def analyzeSentiment():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "Invalid request. 'text' field is required."}), 400

    text = data['text']
    print(f"Analyzing text: '{text}'")
    
    # Use SemanticAnalyzer
    aspect_sentiments = analyzer.get_aspect_sentiments(text, similarity_threshold=0.22, max_aspects=3)
    
    print("Analysis Results:", aspect_sentiments)
    return jsonify({'aspect_analysis': aspect_sentiments})


#QUERYIQ:  Get directory with the QueryIQ module
@app.route('/Querychat', methods = ['POST'])
def queryChat():

    print("Sending to Query...")
    data = request.get_json()
    query_text = data['text']
    response_text = Query.query_rag(query_text)
    print(response_text)
    return jsonify({'response': response_text})


# RECOMMENDIQ: get recommendaiton
# @app.route('/recommenditems', methods=['POST'])
# def recommend():

#     print("Getting recommendations...")
#     data = request.get_json()
#     item_name = data.get("item_name")
    
#     if not item_name:
#         return jsonify({"error": "Item name not provided."}), 400
    
#     recs = NCF.get_recommendations(item_name)
#     if recs is None:
#         return jsonify({"error": f"Item '{item_name}' not found in menu."}), 404
    
#     return jsonify(recs)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
