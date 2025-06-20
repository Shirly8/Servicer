from flask import Flask, request, jsonify
from flask_cors import CORS
import SyntheticGenerator
import asyncio
import ConsoleTest
import Evaluator
from QueryIQ import Query
from QueryIQ import RAG
import ABSA
from RecommendIQ import NCF


app = Flask(__name__, static_folder='static')
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)


# SENTIMENTIQ: Function to initiate message generation
@app.route('/generateReviews', methods = ['POST'])
def generateReview():
    filename = 'SyntheticData.csv'
    model = 'llama3'
    num_messages = 16

    print("GenerateReviews!!!!!")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    generated_messages = loop.run_until_complete(SyntheticGenerator.generate_messages_to_csv(filename, model, num_messages))
    loop.close()


    return jsonify(generated_messages)


#SENTIMENT IQ - GETS THE TEXT AND SENDS TO THE MODEL
@app.route('/analyzeSentiment', methods=['POST'])
def analyzeSentiment():
    data = request.get_json()

    text = data['text']
    sentiment_score = ConsoleTest.predict_sentiment(text)
    print(f"Text: {text} \nSentiment Score: {sentiment_score}")

    aspect_results = ABSA.analyzeSentence(text)
    return jsonify({'score': sentiment_score,
                    'aspect_analysis': aspect_results})


@app.route('/computeMetrics', methods = ['GET'])
def computeMetrics():
    filename = 'SyntheticData.csv'
    results = Evaluator.computing(filename)

    abas_results = ABSA.analyze_csv(filename)
    return jsonify({'results': results,
                    'abasresults': abas_results}
                   )


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


if __name__ == '__main__':
    app.run(debug=True)
