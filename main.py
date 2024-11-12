import requests
from bs4 import BeautifulSoup
import csv
import os


def get_soup(url):
        # Envoyer une requête pour récupérer le contenu HTML de la page
    response = requests.get(url)

    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup
    

def extract_book(book_url):
    soup = get_soup(book_url)

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

    result = {"Product Page URL": book_url,
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


def extract_products(category_url):
    soup = get_soup(category_url)
    section = soup.section
    products_li = section.ol.find_all("li")
    products = []
    for product in products_li:
        products.append(f"https://books.toscrape.com/catalogue{product.a["href"][8:]}")

    return products
        

def main():

    categories = extract_categories()
    all_books = []
    for category in categories[:5]:
        products = extract_products(category)
        for product in products[:5]:
            all_books.append(extract_book(product))

    fieldnames = all_books[0].keys()
    with open('output.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_books)

    folder_path = "images"
    os.makedirs(folder_path, exist_ok=True)

    for book in all_books:
        url = book["Image URL"]
        file_name = f"{book["Title"]}.jpg"
        image_path = f"{folder_path}/{file_name}"

        # Create the folder if it doesn't exist
        

        # Fetch the image and save it to the specified path
        response = requests.get(url)
        with open(image_path, "wb") as file:
            file.write(response.content)



if __name__ == "__main__":
    main()

