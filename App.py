import re
import os
import requests
from flask import Flask, render_template, request, jsonify
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Import your scraper functions
# Assuming they are in a folder named 'scrapers'
from scrapers.amazon_scraper import scrape_amazon  # noqa: E402
from scrapers.flipkart_scraper import scrape_flipkart  # noqa: E402
from scrapers.croma_scraper import scrape_croma  # noqa: E402
from scrapers.reliancedigital_scraper import scrape_reliancedigital  # noqa: E402

app = Flask(__name__)

def normalize_price(price):
    """Removes currency symbols and commas to convert price string to float."""
    # Handles prices like '₹1,23,456.78'
    cleaned_price = re.sub(r'[^\d.]', '', str(price))
    try:
        return float(cleaned_price)
    except (ValueError, TypeError):
        # Return infinity if price is invalid, so it's sorted last
        return float('inf')

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/search')
def search():
    """API endpoint for price comparison, using parallel scraping for speed."""
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "A search query is required."}), 400

    # List of scraper functions to run
    scrapers = [scrape_amazon, scrape_flipkart, scrape_croma, scrape_reliancedigital]
    all_results = []

    # Use a ThreadPoolExecutor to run scrapers concurrently
    with ThreadPoolExecutor(max_workers=len(scrapers)) as executor:
        # map each scraper function to the query and execute
        future_to_scraper = {executor.submit(scraper, query): scraper for scraper in scrapers}
        for future in future_to_scraper:
            try:
                result = future.result()
                if result:
                    all_results.append(result)
            except Exception as exc:
                print(f'{future_to_scraper[future].__name__} generated an exception: {exc}')

    if not all_results:
        return jsonify({"error": f"Could not find '{query}' on any platform."}), 404
        
    # Sort results by normalized price
    sorted_results = sorted(all_results, key=lambda x: normalize_price(x.get('price')))
    best_deal = sorted_results[0] if sorted_results else None

    # Group results by platform
    results_by_platform = defaultdict(list)
    for result in all_results:
        results_by_platform[result['platform']].append(result)
    
    response_data = {
        "best_deal": best_deal,
        "all_results": dict(results_by_platform)
    }
    
    return jsonify(response_data)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Handles chatbot queries by securely calling the Gemini API."""
    try:
        data = request.get_json()
        product_name = data.get('product_name')

        if not product_name:
            return jsonify({"error": "Product name is required."}), 400

        # Securely get API key from environment variables
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Error: GEMINI_API_KEY environment variable not set.")
            return jsonify({"error": "AI service is not configured by the administrator."}), 500

        prompt = f"Provide a brief, one-paragraph description for the following product, focusing on its key features: {product_name}"
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
        
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        headers = {"Content-Type": "application/json"}
        
        api_response = requests.post(api_url, json=payload, headers=headers)
        api_response.raise_for_status() 
        
        result = api_response.json()
        # Safely access the description text from the API response
        description = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Could not retrieve a description.')
        
        return jsonify({'description': description})

    except requests.exceptions.RequestException as e:
        print(f"API request error: {e}")
        return jsonify({"error": "Failed to connect to the AI service."}), 503
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({"error": "Sorry, I couldn't fetch the product description right now."}), 500

if __name__ == '__main__':
    app.run(debug=True)
