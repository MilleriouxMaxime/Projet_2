import requests
from bs4 import BeautifulSoup

def extraire_html():
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"

    # Envoyer une requête pour récupérer le contenu HTML de la page
    response = requests.get(url)

    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser') 

    product_page_url = url
    print(f"L'URL de la page est : {product_page_url}")

    table = soup.find_all("td")
    universal_product_code = table[0].string
    print(universal_product_code)

    title = soup.h1.string
    print(f"Le titre du livre est : {title}")

    price_including_tax = table[3].string[1:]
    print(price_including_tax)

    price_excluding_tax = table[2].string[1:]
    print(price_excluding_tax)

    number_available = table[5].string
    print(number_available)

    paragraphes = soup.find_all("p")
    product_description = paragraphes[-1].string
    print(product_description)

    category = soup.find_all("li")[2].a.string
    print(category)

    review_rating = soup.find_all("p")[2]["class"][1]
    print(review_rating)

    image_url = f"https://books.toscrape.com{soup.img["src"][5:]}"
    print(image_url)












def main():
    extraire_html()

if __name__ == "__main__":
    main()