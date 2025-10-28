import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

def scrape_reliancedigital(product_name):
    try:
        formatted_query = product_name.replace(' ', '%20')
        url = f"https://www.reliancedigital.in/search?q={formatted_query}"
        
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "lxml")
        
        product_div = soup.find('div', {'class': 'g-product-box'})
        if not product_div:
            return None
        
        price_div = product_div.find('div', {'class': 'g-price'})
        price = "Price not found"
        if price_div:
            price_span = price_div.find_all('span')[1]
            price = price_span.text.strip() if price_span else "Price not found"

        rating = "Not Rated"

        link_tag = product_div.find_parent('a')
        product_url = "https://www.reliancedigital.in" + link_tag['href'] if link_tag else "#"

        return {
            "platform": "Reliance Digital",
            "title": product_name,
            "price": price,
            "rating": rating,
            "url": product_url
        }
    except Exception as e:
        print(f"Reliance Digital scraping error: {e}")
        return None
