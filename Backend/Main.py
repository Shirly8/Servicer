from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from SentimentIQ.SyntheticGeneration import SyntheticReviewGenerator
import asyncio
import aiohttp
import os
import csv
import json
from SentimentIQ.SemanticAnalyzer import SemanticAnalyzer
from QueryIQ import Query
from QueryIQ import RAG
from RecommendIQ import NCF
from SentimentIQ import Evaluator
import pandas as pd
import threading
import time
import subprocess


app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)

# --- Load Models and Data on Start ---
base_dir = os.path.dirname(os.path.abspath(__file__))
absa_model_path = os.path.join(base_dir, 'SentimentIQ', '5star-absa-v3')
reviews_csv_path = os.path.join(base_dir, 'SentimentIQ', 'SyntheticReviews.csv')
analyzer = SemanticAnalyzer(absa_model_path=absa_model_path)

# Clear training log on backend startup
log_path = os.path.join(base_dir, 'SentimentIQ', 'training.log')
with open(log_path, 'w') as f:
    f.write('')


# SENTIMENTIQ: Endpoint to get the pre-generated list of reviews
@app.route('/getInitialReviews', methods=['GET'])
def get_initial_reviews():

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
    num_reviews = 26
    SyntheticReviewGenerator.generate_reviews_to_csv(model, num_reviews, reviews_csv_path)
    
    # Append new reviews to the master file
    master_path = os.path.join(base_dir, 'SentimentIQ', 'AllSyntheticReviews.csv')
    if os.path.exists(reviews_csv_path):
        new_reviews = pd.read_csv(reviews_csv_path)
        if os.path.exists(master_path):
            master = pd.read_csv(master_path)
            combined = pd.concat([master, new_reviews], ignore_index=True)
            combined = combined.drop_duplicates()
            combined.to_csv(master_path, index=False)
        else:
            new_reviews.to_csv(master_path, index=False)


    # After generating new reviews, update evaluation_results.json
    output_path = os.path.join(base_dir, 'SentimentIQ', 'evaluation_results.json')
    Evaluator.evaluate_absa_multiclass(reviews_csv_path, absa_model_path, output_path)
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
@app.route('/recommenditems', methods=['POST'])
def recommend():
    print("Getting recommendations...")
    data = request.get_json()
    item_name = data.get("item_name")
    
    if not item_name:
        return jsonify({"error": "Item name not provided."}), 400
    
    recs = NCF.get_recommendations(item_name)
    if recs is None:
        return jsonify({"error": f"Item '{item_name}' not found in menu."}), 404
    
    return jsonify(recs)


@app.route('/computeMetrics', methods=['GET'])
def evaluate_model():
    output_path = os.path.join(base_dir, 'SentimentIQ', 'evaluation_results.json')
    if not os.path.exists(output_path):
        return jsonify({"error": "No evaluation results found."}), 404
    with open(output_path, 'r', encoding='utf-8') as f:
        metrics = json.load(f)
    return jsonify(metrics)


@app.route('/getReviewsForAspect')
def get_reviews_for_aspect():
    aspect = request.args.get('aspect')
    if not aspect:
        return jsonify({"error": "No aspect provided."}), 400

    reviews_csv_path = os.path.join(base_dir, 'SentimentIQ', 'SyntheticReviews.csv')
    filtered_reviews = []
    if not os.path.exists(reviews_csv_path):
        return jsonify(filtered_reviews)

    with open(reviews_csv_path, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Case-insensitive match
            if row.get("Aspect", "").lower() == aspect.lower():
                filtered_reviews.append({
                    "message": row.get("Review", ""),
                    "rating": row.get("Rating", ""),
                    "aspect": row.get("Aspect", "")
                })
    return jsonify(filtered_reviews)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
