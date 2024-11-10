import requests
from bs4 import BeautifulSoup
import csv

def get_soup(url):
        # Envoyer une requête pour récupérer le contenu HTML de la page
    response = requests.get(url)

    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup
    
def extract_html(url):
    soup = get_soup(url)

    table = soup.find_all("td")
    universal_product_code = table[0].string

    title = soup.h1.string

    price_including_tax = table[3].string[2:]

    price_excluding_tax = table[2].string[2:]

    number_available = table[5].string[10:12]

    paragraphes = soup.find_all("p")
    product_description = paragraphes[-1].string

    category = soup.find_all("li")[2].a.string

    review_rating = soup.find_all("p")[2]["class"][1]

    image_url = f"https://books.toscrape.com{soup.img["src"][5:]}"

    result = {"Product Page URL": url,
        "Universal Product Code": universal_product_code,
        "Title": title,
        "Price including tax": price_including_tax,
        "Price excluding tax": price_excluding_tax,
        "Number Available": number_available,
        "Product Description": product_description,
        "Category": category,
        "Review Rating": review_rating,
        "Image URL": image_url}
    
    return result

def extract_categories():
    soup = get_soup("https://books.toscrape.com/")


    categories_div = soup.find(class_="side_categories")

    table = categories_div.find_all("li")
    categories = table[1:]
    results = []
    for category in categories:
        results.append(f"https://books.toscrape.com/{category.a["href"].strip()}")
    
    return results

def main():
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html" 
    result = extract_html(url)
    #print(result)
    categories = extract_categories()
    print(categories)
    

if __name__ == "__main__":
    main()

