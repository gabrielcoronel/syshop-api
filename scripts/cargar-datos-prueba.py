#! /usr/bin/python3

import requests
import csv
from base64 import b64encode
from random import randint

def download_file_in_base64(url):
    response = requests.get(url)
    base64_bytes = b64encode(response.content)
    base64_string = base64_bytes.decode("utf-8")

    return base64_string


def create_store(email, phone_number, name, description):
    picture = download_file_in_base64("https://www.southernliving.com/thmb/dvvxHbEnU5yOTSV1WKrvvyY7clY=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/GettyImages-1205217071-2000-2a26022fe10b4ec8923b109197ea5a69.jpg")
    first_multimedia = download_file_in_base64("https://cdn.apartmenttherapy.info/image/upload/f_auto,q_auto:eco,c_fill,g_center,w_730,h_487/stock%2Fshutterstock_373602469")
    second_multimedia = download_file_in_base64("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/DGRegisterStore.jpg/640px-DGRegisterStore.jpg")

    url = "http://localhost:8000/stores_service/sign_up_store_with_plain_account"
    payload = {
        "email": email,
        "password": "hola",
        "multimedia": [first_multimedia, second_multimedia],
        "name": name,
        "description": description,
        "picture": picture,
        "phone_number": phone_number,
        "location": {
            "place_name": "Condominio La Constancia",
            "street_address": "San Antonio",
            "city": "Desamparados",
            "state": "San José",
            "zip_code": "10305"
        }
    }

    response = requests.post(url, json=payload)

    if 200 <= response.status_code < 300:
        print("Éxito creando tienda", name)
    else:
        print("Hubo un error creando tienda", name)


def get_stores_ids():
    url = "http://localhost:8000/stores_service/search_stores_by_name" 
    payload = {
        "search": ""
    }

    response = requests.post(url, json=payload)

    if not (200 <= response.status_code < 300):
        print("Hubo un error con la conexión a Internet")

        return

    stores_ids = [
        store["user_id"]
        for store in response.json()
    ]

    return stores_ids


def read_product_dataset():
    dataset_path = "./amazon-product-dataset.csv"
    count = 0
    maximum = 10

    with open(dataset_path, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            count += 1

            if (count >= maximum):
                break

            image = download_file_in_base64(row["Image"])

            product = {
                "title": row["Product Name"],
                "description": row["Product Description"],
                "amount": 300,
                "price": 1000,
                "categories": [row["Category"]],
                "multimedia": [image]
            }

            yield product

    print("Dataset de productos cargado a memoria exitosamente")


def load_product_dataset():
    stores_ids = get_stores_ids()
    length = len(stores_ids)

    for product in read_product_dataset():
        url = "http://localhost:8000/posts_service/create_post"
        payload = {
            "store_id": stores_ids[randint(0, length - 1)],
            **product
        }

        response = requests.post(url, json=payload)

        if not (200 <= response.status_code < 300):
            print("Hubo un error cargando un producto", product)

            return

    print("Los productos del dataset se cargaron correctamente")


if __name__ == "__main__":
    create_store("gabrielcoronel0303@gmail.com", "88888888", "Tienda de Gabriel", "Esta es la tienda de Gabriel")
    create_store("kevinlatino9@gmail.com", "77777777", "Tienda de Kevin", "Esta es la tienda de Kevin")

    load_product_dataset()
