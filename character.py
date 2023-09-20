import requests, requests_cache, datetime


requests_cache.install_cache(cache_name='rio_cache', expire_after=120)

class Character():
    name = ""
    realm = ""
    region = ""

    def __init__(self, name, realm, region):
        self.name = name
        self.realm = realm
        self.region = region

    def get_mythic_plus_data(self):
        best_runs = requests.get(f"https://raider.io/api/v1/characters/profile?region={self.region}&realm={self.realm}&name={self.name}&fields=mythic_plus_best_runs")
        alternate_runs = requests.get(f"https://raider.io/api/v1/characters/profile?region={self.region}&realm={self.realm}&name={self.name}&fields=mythic_plus_alternate_runs")
        time = datetime.datetime.now().strftime("%d.%b %Y %H:%M:%S")
        print(f"{time} : UPDATED {self.name}")
        return best_runs.json() and alternate_runs.json()

