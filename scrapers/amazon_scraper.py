import requests
from bs4 import BeautifulSoup

SEARCH_URL = "https://www.amazon.in/s?k="
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
}

def scrape_amazon(product_name):
    """Scrapes Amazon for a given product and returns its details."""
    try:
        formatted_query = "+".join(product_name.split())
        url = f"{SEARCH_URL}{formatted_query}"
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "lxml")
        product_div = soup.find('div', {'data-asin': True, 'data-component-type': 's-search-result'})
        if not product_div:
            return None

        # Title scraping logic is no longer needed

        price_span = product_div.find('span', {'class': 'a-price-whole'})
        price = price_span.text.strip() if price_span else "Price not found"
        
        rating_span = product_div.find('span', {'class': 'a-icon-alt'})
        rating = rating_span.text.strip().split()[0] if rating_span else "Rating not found"
        
        link_tag = product_div.find('a', {'class': 'a-link-normal'})
        product_url = "https://www.amazon.in" + link_tag['href'] if link_tag else "URL not found"

        return {
            "platform": "Amazon",
            "title": product_name,  # Use the user's input directly as the title
            "price": f"₹{price}",
            "rating": rating,
            "url": product_url
        }
    except Exception as e:
        print(f"Amazon scraping error: {e}")
        return None