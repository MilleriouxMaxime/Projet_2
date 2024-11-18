import requests
from bs4 import BeautifulSoup
import csv
import os
from slugify import slugify

BASE_URL = "https://books.toscrape.com/"
SESSION = requests.Session()



def get_soup(url):
    """
    Récupère et parse le contenu HTML d'une URL avec BeautifulSoup.  
    Renvoie un objet BeautifulSoup si la requête réussit, sinon `None`.  
    Affiche un message d'erreur si l'URL est introuvable.
    """

    response = SESSION.get(url)

    soup = BeautifulSoup(response.content, 'html.parser')
    if not response.ok:
        print("URL introuvable.")
        return None
    else:
        return soup
    

def extract_book(book_url):
    """
    Extrait les informations d'un livre depuis une page produit.  
    Renvoie un dictionnaire contenant les détails du livre (titre, prix, stock, etc.).
    """

    soup = get_soup(book_url)
    if soup is None:
        return

    table = soup.find_all("td")

    universal_product_code = table[0].string

    title = soup.h1.string

    price_including_tax = table[3].string[2:]

    price_excluding_tax = table[2].string[2:]

    number_available = int(table[5].string[10:12])

    product_div = soup.find('div', id="product_description")
    if product_div is None:
        product_description = "Description Not Available"
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


def extract_categories():
    """
    Extrait les catégories de livres depuis la page d'accueil.  
    Renvoie une liste contenant les noms de catégories et leurs URLs respectives.  
    """

    soup = get_soup(BASE_URL)
    if soup is None:
        return 

    categories_div = soup.find(class_="side_categories")

    table = categories_div.find_all("li")
    categories = table[1:]
    results = []
    for category in categories:
        url = f"{BASE_URL}{category.a["href"].strip()}"
        category_name = category.a.string.strip()
        results.append([category_name, url])
    
    return results


def extract_book_urls(category_url):
    """
    Extrait les URLs des livres pour une catégorie donnée.  
    Renvoie une liste d'URLs en parcourant toutes les pages de la catégorie.  
    Gère la pagination automatiquement via la classe "next".
    """

    products = []

    base_url = category_url.rsplit('/', 1)[0]

    while True:
        soup = get_soup(category_url)
        if soup is None:
            return
    
        section = soup.section
        products_li = section.ol.find_all("li")
    
        for product in products_li:
            products.append(f"{BASE_URL}catalogue{product.a["href"][8:]}")
        
        if section.find(class_="next") is None:
            break
        else:
            category_url = f"{base_url}/{section.find(class_='next').a['href']}"

    return products
        

def create_folder_for_category(category_name):
    """
    Crée un dossier pour une catégorie de livres dans le répertoire "Library".  
    Assure l'existence du répertoire "Library" et de celui de la catégorie spécifiée.  
    N'a aucun effet si les dossiers existent déjà.
    """

    os.makedirs("Library", exist_ok=True)
    os.makedirs(f"Library/{category_name}", exist_ok=True)


def create_csv_for_category(category_name, category_books):
    """
    Crée un fichier CSV pour une catégorie de livres.  
    Écrit les données des livres dans un fichier CSV dans le dossier correspondant.  
    Utilise les clés du premier livre comme en-têtes de colonnes.
    """

    headers = category_books[0].keys()
    with open(f'Library/{category_name}/{category_name}.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(category_books)


def create_images_for_category(category_name, category_books):
    """
    Télécharge les images des livres pour une catégorie donnée.  
    Crée un sous-dossier "images" dans le dossier de la catégorie et y enregistre les images.  
    Les noms des fichiers sont basés sur les titres des livres, limités à 20 caractères.
    """

    folder_path = f"Library/{category_name}/images"
    os.makedirs(folder_path, exist_ok=True)

    for book in category_books:
        url = book["Image URL"]
        file_name = f"{slugify(book["Title"])[:20]}.jpg"
        image_path = f"{folder_path}/{file_name}"
        response = requests.get(url)
        with open(image_path, "wb") as file:
            file.write(response.content)


def main():
    """
    Exécute le processus principal pour extraire et sauvegarder les données des livres.  
    Pour chaque catégorie, crée un dossier, extrait les livres, génère un CSV et télécharge les images.  
    Affiche une progression en indiquant les catégories traitées.
    """

    categories = extract_categories()
    
    for category in categories:
        print(f"Traitement de la catégorie : {category[0]}, en cours, veuillez patienter...")
        create_folder_for_category(category[0])
        book_urls = extract_book_urls(category[1])

        category_books = []
        for book_url in book_urls:
            category_books.append(extract_book(book_url))

        create_csv_for_category(category[0], category_books)

        create_images_for_category(category[0], category_books)


if __name__ == "__main__":
    main()

