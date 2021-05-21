import requests
from ha_token import ha_token

ha_auth = "Bearer " + ha_token
url_todo = "http://homeassistant.fritz.box:8123/states/input_boolean.stromverbrauch_todo"
headers = {
    "Authorization": ha_auth,
    "content-type": "application/json",
}

response = requests.get(url_todo, headers=headers)
print(response.text)
