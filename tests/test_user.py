import requests
from faker import Faker
faker = Faker()

prod_url = "https://api.stand.qastart.ru/signup"
local_url = "http://127.0.0.1:7000//signup"

def test_populate_users():
    for _ in range(40):
       res = requests.post(local_url, json={
                "name": faker.name(),
                "email": faker.email(),
                "password": "1234hhhAAA",
                "personal_data_access": True
        }
    )
       assert res.json()["uuid"]
