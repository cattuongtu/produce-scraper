import requests
from bs4 import BeautifulSoup

# Get html website to scrape.
URL = "https://snaped.fns.usda.gov/resources/nutrition-education-materials/seasonal-produce-guide"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

def get_produce(season_string):
    season_list = []
    elements = soup.find_all("div", class_=season_string)    
    for element in elements:
        unordered_list = element.find("ul", class_="usa-unstyled-list")
        list_items = unordered_list.find_all("a")
        for list_item in list_items:
            season_list.append(list_item.text)
    
    return season_list

if __name__ == "__main__":
    spring_produce = get_produce("spring")
    summer_produce = get_produce("summer")
    winter_produce = get_produce("winter")
    fall_produce = get_produce("fall")

        


