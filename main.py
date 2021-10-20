import requests
import json
import datetime
from types import GeneratorType


def get_location_id(location: str) -> int:
    url = "https://hotels4.p.rapidapi.com/locations/search"
    querystring = {"query": location,
                   "locale": "ru_RU"
                   }
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "beb5153422msh10d86b9d8d66b69p1d0b86jsn2dffe442b880"
        }
    response = requests.request("GET", url, headers=headers, params=querystring)
    result = json.loads(response.text)["suggestions"][0]["entities"]
    for elem in result:
        if elem["name"] == location:
            return elem["destinationId"]
    else:
        return None


def get_search_hotels(destinationId:int, sort: str, price_min: int = 0,
                      price_max: int = 999999) -> dict:
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": f"{destinationId}",
                   "pageNumber": "1",
                   "pageSize": "25",
                   "checkIn": str(datetime.datetime.now().date()),
                   "checkOut": str(datetime.datetime.now().date() +
                                   datetime.timedelta(1)),
                   "adults1": "1",
                   "sortOrder": sort,
                   "locale": "ru_RU", "currency": "RUB",
                   "landmarkIds": "City center",
                   "priceMin": price_min, "priceMax": price_max}

    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "beb5153422msh10d86b9d8d66b69p1d0b86jsn2dffe442b880"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)
    if sort == "DISTANCE_FROM_LANDMARK":
        hotels = json.loads(response.text)["data"]["body"]["searchResults"]\
            ["results"]
        hotels = sorted(
            hotels, key=lambda x: (0, float(str(x["landmarks"][0]
                                            ["distance"]).replace(
                " км", "").replace(",", ".")),
                               float(x["ratePlan"]["price"]["current"].repalace(
                                   ",", ".")))
            if str(x["landmarks"][0]["label"]) == "" else
            (1, float(str(x["landmarks"][0]["distance"]).replace(
                " км", "").replace(",", ".")),
             float(x["ratePlan"]["price"]["current"].replace(",", ".")))
        )
        """
        Добавить сортировку на одинаковую дальность от центра города
        ["ratePlan"]["price"]
        ["landmarks"][0]["distance"]
        ["landmarks"][0]["label"]
        """
    return json.loads(response.text)["data"]["body"]["searchResults"]["results"]


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
    response = requests.request("GET", url, headers=headers, params=querystring)
    response = json.loads(response.text)

    result = [photo["baseUrl"].replace("{size}", search_max(photo["sizes"]))
              for photo in response["hotelImages"]]
    return result


class Log:
    @classmethod
    def write(cls, chat_id: int, text: str) -> None:
        with open("history.txt", "a+", encoding="UTF-8") as file:
            now = datetime.datetime.now()
            now = now.strftime("%H:%M:%S, %d.%B.%Y")
            file.write(str(chat_id) + "(SPLIT_SYMBOL)" + now + " " + text + "\n")

    @classmethod
    def read(cls, chat_id: int) -> GeneratorType:
        with open("history.txt", "r", encoding="UTF-8") as file:
            for row in file:
                chat_id_row, message = row.split("(SPLIT_SYMBOL)", 1)
                if str(chat_id) == chat_id_row:
                    yield message


if __name__ == "__main__":
    print(get_photo(938109376))
