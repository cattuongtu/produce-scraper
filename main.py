import requests
import psycopg2
import os
import openai
import time
from bs4 import BeautifulSoup

DB_NAME = "produce"
DB_USER = "postgres"
DB_PASS = os.environ["PRODUCE_DB_PASSWORD"]
DB_HOST = "produce-in-season.ca9qtpohllrj.us-west-1.rds.amazonaws.com"
DB_PORT = "5432"

CHATGPT_API_KEY = os.environ["CHATGPT_API_KEY"]
# Get html website to scrape.
URL = "https://snaped.fns.usda.gov/resources/nutrition-education-materials/seasonal-produce-guide"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

class Product:
    def __init__(self, name, description, season, is_fruit):
        self.name = name
        self.description = description
        self.season = season
        self.is_fruit = is_fruit

    def to_tuple(self):
        return (self.name, self.is_fruit, self.description, self.season)

# Gets all the produce for its respective season
def get_produce(season_string):
    season_list = []
    elements = soup.find_all("div", class_=season_string)    
    for element in elements:
        unordered_list = element.find("ul", class_="usa-unstyled-list")
        list_items = unordered_list.find_all("a")
        for list_item in list_items:
            season_list.append(list_item.text)
    
    return season_list

def get_data(prompt):

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + CHATGPT_API_KEY,
    }

    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    print("Status Code:", response.status_code)
    print("Response Body:", response.json())
    print("Message returned: ", response_json['choices'][0]['message']['content'])
    
    return response_json['choices'][0]['message']['content']

def create_object(product, season):
    prompt = "Write a one sentence description about a(n) " + product.lower()
    description = get_data(prompt)
    prompt = "Is a(n) " + product.lower() + " a fruit? Please answer in 'Yes' or 'No'."
    is_fruit_answer = get_data(prompt)
    is_fruit = True if is_fruit_answer == 'Yes.' else False
    return Product(name=product, description=description, season=season, is_fruit=is_fruit)

def connect_db():
    try:
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT)
        print("Database connected successfully")
        return conn
    except:
        print("Database not connected successfully")

if __name__ == "__main__":
    seasons = ["Spring", "Summer", "Winter", "Fall"]
    conn = None
    try:
        conn = connect_db()
        cur = conn.cursor()
        for season in seasons:
            produce = get_produce(season.lower())
            for product in produce:
                product_object = create_object(product, season)
                cur.execute('INSERT INTO "Products"("Name", "IsFruit", "Description", "Season") VALUES (%s, %s, %s, %s)', product_object.to_tuple())
                conn.commit()

        cur.close()
    except psycopg2.DatabaseError as error:
        print(error)
    finally:
        if conn is not None:
            cur.close()
    

        


