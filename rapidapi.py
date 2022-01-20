import os
import datetime
import requests
import json
from types import GeneratorType
import functools


def get_location_id(location: str) -> dict:
    url = "https://hotels4.p.rapidapi.com/locations/search"
    querystring = {"query": location,
                   "locale": "ru_RU"}
    headers = {
        'x-rapidapi-host': os.getenv('x-rapidapi-host'),
        'x-rapidapi-key': os.getenv('x-rapidapi-key')}
    try:
        response = requests.request("GET", url, headers=headers, params=querystring,
                                timeout=10)
    except Exception:
        return ["Что-то пошло не так"]
    if response.status_code == 200:
        result = json.loads(response.text)["suggestions"][0]["entities"]
        result = {elem["name"]: elem["destinationId"] for elem in result}
        return result
    else:
        return ["Что-то пошло не так"]


def get_search_hotels(destinationId:int, date_in, date_out, sort: str, price_min: int = 0,
                      price_max: int = 999999) -> dict:
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": f"{destinationId}",
                   "pageNumber": "1",
                   "pageSize": "25",
                   "checkIn": date_in,
                   "checkOut": date_out,
                   "adults1": "1",
                   "sortOrder": sort,
                   "locale": "ru_RU", "currency": "RUB",
                   "landmarkIds": "City center",
                   "priceMin": price_min, "priceMax": price_max}

    headers = {
        'x-rapidapi-host': os.getenv('x-rapidapi-host'),
        'x-rapidapi-key': os.getenv('x-rapidapi-key')
        }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring,
                                timeout=10)
    except Exception:
        return ["Что-то пошло не так"]
    if response.status_code == 200:
        if sort == "DISTANCE_FROM_LANDMARK":
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
        return json.loads(response.text)["data"]["body"]["searchResults"]\
        ["results"]

    else:
        return ["Что-то пошло не так"]


def get_photo(hotel_id: int) -> dict["URL"]:

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
    except Exception:
        return ["Что-то пошло не так"]
    if response.status_code == 200:
        response = json.loads(response.text)
        result = [photo["baseUrl"].replace("{size}", search_max(photo["sizes"]))
                  for photo in response["hotelImages"]]
        return result
    else:
        return ["Что-то пошло не так."]
