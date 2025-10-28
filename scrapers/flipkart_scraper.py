import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

def scrape_flipkart(product_name):
    """Scrapes Flipkart for a given product and returns its details."""
    try:
        formatted_query = "+".join(product_name.split())
        url = f"https://www.flipkart.com/search?q={formatted_query}"
        
        # NOTE: Added 'lxml' parser for consistency, though it was in the original code.
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "lxml")
        
        # --- FIX: Updated the product container class name ---
        # Look for the main product result container (one of the large divs holding product cards).
        # Class 'DOjaWF' is replaced with a commonly observed one for grid items: '_1AtVbE'
        # and then drilling down into the first main product card ('_13oc-S').
        
        # Search for the main grid item wrapper
        product_list_wrapper = soup.find('div', {'class': '_1AtVbE'})
        if not product_list_wrapper:
             return {"platform": "Flipkart", "title": product_name, "error": "Main product list wrapper not found."}

        # Find the first individual product card inside the wrapper
        # The class 'DOjaWF' is replaced by one of the current card container classes.
        product_div = product_list_wrapper.find('div', {'class': '_13oc-S'})
        if not product_div:
            # Fallback for different search result layouts (e.g., large-card layout)
            product_div = soup.find('div', {'class': '_1AtVbE'})

        if not product_div:
            return {"platform": "Flipkart", "title": product_name, "price": "Price not found", "rating": "Rating not found", "url": "URL not found"}


        # Title scraping logic is no longer needed
        # --- FIX: Finding Title using a current, common class
        title_tag = product_div.find('a', {'class': 's1Q9rs'}) or product_div.find('div', {'class': '_4rR01T'})
        title = title_tag.text.strip() if title_tag else product_name # Fallback to input name

        # --- FIX: Updated the price class name ---
        # The original class 'Nx9bqj' is replaced by a common price class
        price_tag = product_div.find('div', {'class': '_30jeq3'}) 
        price = price_tag.text.strip() if price_tag else "Price not found"

        # --- FIX: Updated the rating class name ---
        # The original class 'XQDdHH' is replaced by a common rating class
        rating_tag = product_div.find('div', {'class': '_3LWZlK'})
        rating = rating_tag.text.strip() if rating_tag else "Rating not found"

        # --- FIX: Updated the link class name ---
        # The original class 'wU_t2p' is replaced by a common link class
        link_tag = product_div.find('a') # Links are often just the first <a> tag in the product card
        product_url = "https://www.flipkart.com" + link_tag['href'] if link_tag and link_tag.get('href') else "URL not found"

        return {
            "platform": "Flipkart",
            "title": title,
            "price": price,
            "rating": rating,
            "url": product_url
        }

    except requests.exceptions.HTTPError as http_err:
        # Catch specific HTTP errors (like the 529 Server Error)
        return {"platform": "Flipkart", "title": product_name, "error": f"HTTP Error: {http_err}"}
    except Exception as e:
        # Catch all other exceptions (e.g., if a selector fails to find anything)
        print(f"Flipkart scraping error: {e}")
        return {"platform": "Flipkart", "title": product_name, "error": f"Scraping failed: {e}"}