import requests
from bs4 import BeautifulSoup
import csv
import os
from slugify import slugify

BASE_URL = "https://books.toscrape.com/"
SESSION = requests.Session()


# Permet d'éviter de refaire le code "BeautifulSoup" à chaque fois qu'on en a besoin
def get_soup(url):
    response = SESSION.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    if not response.ok:
        print("URL introuvable.")
        return None
    else:
        return soup
    

# Récupération des données demandées sur un livre unique et retourne en dictionnaire
def extract_book(book_url):
    soup = get_soup(book_url)

    table = soup.find_all("td")
    universal_product_code = table[0].string

    title = soup.h1.string

    price_including_tax = table[3].string[2:]

    price_excluding_tax = table[2].string[2:]

    number_available = int(table[5].string[10:12])

    product_div = soup.find('div', id="product_description")
    if product_div is None:
        product_description = ""
    else:
        product_description = product_div.find_next_sibling().string

    category = soup.find_all("li")[2].a.string

    review_rating = soup.find_all("p")[2]["class"][1]

    image_url = f"{BASE_URL}{soup.img["src"][6:]}"

    ratings = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    
    result = {"Product Page URL": book_url,
        "Universal Product Code": universal_product_code,
        "Title": title,
        "Price including tax": price_including_tax,
        "Price excluding tax": price_excluding_tax,
        "Number Available": number_available,
        "Product Description": product_description,
        "Category": category,
        "Review Rating": ratings[review_rating],
        "Image URL": image_url}
    
    return result


# Extraction des catégories et retour en liste
def extract_categories():
    soup = get_soup(BASE_URL)

    categories_div = soup.find(class_="side_categories")

    table = categories_div.find_all("li")
    categories = table[1:]
    results = []
    for category in categories:
        url = f"{BASE_URL}{category.a["href"].strip()}"
        category_name = category.a.string.strip()
        results.append([category_name, url])
    
    return results


# Récupère les livres dans une catégorie en applicant la pagination (si pas bouton "next" alors STOP, sinon )
def extract_book_urls(category_url):
    products = []

    base_url = category_url.rsplit('/', 1)[0]

    while True:
        soup = get_soup(category_url)
        section = soup.section
        products_li = section.ol.find_all("li")
    
        for product in products_li:
            products.append(f"{BASE_URL}catalogue{product.a["href"][8:]}")
        
        if section.find(class_="next") is None:
            break
        else:
            category_url = f"{base_url}/{section.find(class_='next').a['href']}"

    return products
        

def create_csv_for_category(category_name, category_books):

    headers = category_books[0].keys()
    with open(f'Library/{category_name}/{category_name}.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(category_books)

def create_folder_for_category(category_name):
    os.makedirs("Library", exist_ok=True)
    os.makedirs(f"Library/{category_name}", exist_ok=True)

def create_images_for_category(category_name, category_books):
    folder_path = f"Library/{category_name}/images"
    os.makedirs(folder_path, exist_ok=True)

    for book in category_books:
        url = book["Image URL"]
        file_name = f"{slugify(book["Title"])[:20]}.jpg"
        image_path = f"{folder_path}/{file_name}"
        response = requests.get(url)
        with open(image_path, "wb") as file:
            file.write(response.content)

# Script pour créer le fichier csv et y écrire les données ainsi que créer le dossier images et les y ajouter en fichiers
def main():

    categories = extract_categories()
    
    for category in categories:
        print(f"category : {category}")
        create_folder_for_category(category[0])
        book_urls = extract_book_urls(category[1])

        category_books = []
        for book_url in book_urls:
            print(f"book : {book_url}")
            category_books.append(extract_book(book_url))

        create_csv_for_category(category[0], category_books)

        create_images_for_category(category[0], category_books)


if __name__ == "__main__":
    main()

