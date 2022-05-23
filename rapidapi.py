import os
import requests
import json
from typing import Union
from History import Users

def get_location_id(location: str) -> Union[list[str], dict]:
    url = "https://hotels4.p.rapidapi.com/locations/search"
    querystring = {"query": location,
                   "locale": "ru_RU"}
    headers = {
        'x-rapidapi-host': os.getenv('x-rapidapi-host'),
        'x-rapidapi-key': os.getenv('x-rapidapi-key')}
    try:
        response = requests.request("GET", url, headers=headers, params=querystring,
                                timeout=10)
    except requests.exceptions.ConnectTimeout:
        return ["Что-то пошло не так"]
    if response.status_code == 200:
        result = json.loads(response.text)["suggestions"][0]["entities"]
        result = {elem["name"]: elem["destinationId"] for elem in result}
        return result
    else:
        return ["Что-то пошло не так"]


def get_search_hotels(message, page: int = 1) -> dict:
    url = "https://hotels4.p.rapidapi.com/properties/list"
    usr = Users.get_user(message.chat.id)
    querystring = {"destinationId": f"{usr.city}",
                   "pageNumber": str(page),
                   "pageSize": "25",
                   "checkIn": usr.check_in,
                   "checkOut": usr.check_out,
                   "adults1": "1",
                   "sortOrder": usr.mode,
                   "locale": "ru_RU", "currency": "RUB",
                   "landmarkIds": "City center",
                   "priceMin": usr.price_min, "priceMax": usr.price_max}

    headers = {
        'x-rapidapi-host': os.getenv('x-rapidapi-host'),
        'x-rapidapi-key': os.getenv('x-rapidapi-key')
        }
    try:
        response = requests.request("GET", url, headers=headers,
                                    params=querystring, timeout=10)
    except requests.exceptions.ConnectTimeout:
        return ["Что-то пошло не так"]
    if response.status_code == 200:
        if usr.mode == "DISTANCE_FROM_LANDMARK":
            hotels = json.loads(response.text)["data"]["body"]["searchResults"]\
                ["results"]
            hotels = sorted(
                hotels, key=lambda x: (0, float(str(x["landmarks"][0]
                                                ["distance"]).replace(
                    " км", "").replace(",", ".")), float(x["ratePlan"]["price"]
                                                            ["current"]
                                                         .repalace(",", ".")
                                                         .replace("RUB", "")
                                                         .replace(" ", "")))

                if str(x["landmarks"][0]["label"]) == "" else
                (1, float(str(x["landmarks"][0]["distance"]).replace(
                    " км", "").replace(",", ".")),
                 float(x["ratePlan"]["price"]["current"].replace(",", ".")
                       .replace("RUB", "").replace(" ", "")))
            )
            hotels = filter(lambda x: usr.min_distance <= \
                                      float(x["landmarks"][0]
                                            ["distance"].replace(" км", "") \
                                            .replace(",", ".")) \
                                      <= usr.max_distanse, hotels)
            hotels = list(hotels)
            if len(hotels) == 0 and page <= 3:
                get_search_hotels(message, page=page+1)
            return hotels
        return json.loads(response.text)["data"]["body"]["searchResults"]\
        ["results"]

    else:
        return ["Что-то пошло не так"]


def get_photo(hotel_id: int) -> list["URL"]:

    def search_max(sizes: list) -> str:
        result = {"type": 0, "suffix": ""}
        for elem in sizes:
            if int(result["type"]) < int(elem["type"]):
                result = elem
        return result["suffix"]

    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": f"{hotel_id}"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "beb5153422msh10d86b9d8d66b69p1d0b86jsn2dffe442b880"
    }
    try:
        response = requests.request("GET", url, headers=headers,
                                    params=querystring, timeout=10)
    except requests.exceptions.ConnectTimeout:
        return ["Что-то пошло не так"]
    if response.status_code == 200:
        response = json.loads(response.text)
        result = [photo["baseUrl"].replace("{size}", search_max(photo["sizes"]))
                  for photo in response["hotelImages"]]
        return result
    else:
        return ["Что-то пошло не так."]
