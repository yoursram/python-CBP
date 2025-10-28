import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

def scrape_croma(product_name):
    try:
        formatted_query = product_name.replace(' ', '%20')
        url = f"https://www.croma.com/searchB?q={formatted_query}%3Arelevance"
        
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "lxml")
        
        product_div = soup.find('li', {'class': 'product-list-item'})
        if not product_div:
            return None

        price_span = product_div.find('span', {'data-testid': 'pdp-product-price'})
        price = price_span.text.strip() if price_span else "Price not found"

        rating = "Not Rated"

        link_tag = product_div.find('a', {'class': 'product-img'})
        product_url = "https://www.croma.com" + link_tag['href'] if link_tag else "#"

        return {
            "platform": "Croma",
            "title": product_name,
            "price": price,
            "rating": rating,
            "url": product_url
        }
    except Exception as e:
        print(f"Croma scraping error: {e}")
        return None
