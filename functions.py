import requests
from config import dbValorant

class SyncApi(): # PERMET DE SYNC LE BOT AVEC L'API VALORANT ET DE METTRE A JOUR LES DONNEES DANS LA BASE DE DONNEES
    
    def __init__(self):
        self.agentDict = {}
        self.skinDict = {}
        self.mapDict = {}
        self.bundleDict = {}
    
    def get_all_agents(self):
        
        url = "https://valorant-api.com/v1/agents"
        params ={"language": "fr-FR","isPlayableCharacter": "true"}
        response = requests.get(url = url, params=params)

        if response.status_code == 200:
            data = response.json()
            for agent in data["data"]:
                
                self.agentDict = {}
                self.agentDict["uuid"] = agent["uuid"]
                self.agentDict["displayName"] = agent["displayName"]
                self.agentDict["description"] = agent["description"]
                self.agentDict["role"] = agent["role"]
                self.agentDict["characterTags"] = agent["characterTags"]
                self.agentDict["abilities"] = agent["abilities"]
                self.agentDict["background"] = agent["background"]
                self.agentDict["fullPortrait"] = agent["fullPortrait"]
                self.agentDict["fullPotraitV2"] = agent["fullPortraitV2"]
                self.agentDict["bustPortrait"] = agent["bustPortrait"]
                self.agentDict["displayIcon"] = agent["displayIcon"]
                self.agentDict["voiceLine"] = agent["voiceLine"]
                
                print(self.agentDict)
                dbValorant.agents.update_one({"uuid": agent["uuid"]}, {"$set": self.agentDict}, upsert=True)
 
            return data
        
        else:
            print("Failed to retrieve agents. Status code:", response.status_code)
            return None

    def get_all_skins(self):
        url = "https://valorant-api.com/v1/weapons/skins"
        params = {"language": "fr-FR"}
        response = requests.get(url=url, params=params)

        if response.status_code == 200:
            data = response.json()
            for skin in data["data"]:
                self.skinDict = {}
                self.skinDict["uuid"] = skin["uuid"]
                self.skinDict["displayName"] = skin["displayName"]
                self.skinDict["levels"] = skin["levels"]
                self.skinDict["contentTierUuid"] = skin["contentTierUuid"]
                self.skinDict["wallpaper"] = skin["wallpaper"]  
                self.skinDict["displayIcon"] = skin["displayIcon"]
                self.skinDict["chromas"] = skin["chromas"]

                print(self.skinDict)
                dbValorant.skins.update_one({"uuid": skin["uuid"]}, {"$set": self.skinDict}, upsert=True)

            return data

        else:
            print("Failed to retrieve skins. Status code:", response.status_code)
            return None
        
        
    def get_all_maps(self):
        url = "https://valorant-api.com/v1/maps"
        params = {"language": "fr-FR"}
        response = requests.get(url=url, params=params)

        if response.status_code == 200:
            data = response.json()
            for map in data["data"]:
                self.mapDict = {}
                self.mapDict["uuid"] = map["uuid"]
                self.mapDict["displayName"] = map["displayName"]
                self.mapDict["tacticalDescription"] = map["tacticalDescription"]
                self.mapDict["narrativeDescription"] = map["narrativeDescription"]
                self.mapDict["coordinates"] = map["coordinates"]
                self.mapDict["displayIcon"] = map["displayIcon"]
                self.mapDict["premierBackgroundImage"] = map["premierBackgroundImage"]
                self.mapDict["stylizedBackgroundImage"] = map["stylizedBackgroundImage"]
                self.mapDict["splash"] = map["splash"]

                print(self.mapDict)
                dbValorant.maps.update_one({"uuid": map["uuid"]}, {"$set": self.mapDict}, upsert=True)

            return data

        else:
            print("Failed to retrieve maps. Status code:", response.status_code)
            return None

    def get_all_bundles(self):
        url = "https://valorant-api.com/v1/bundles"
        params = {"language": "fr-FR"}
        response = requests.get(url=url, params=params)

        if response.status_code == 200:
            data = response.json()
            for bundle in data["data"]:
                self.bundleDict = {}
                self.bundleDict["uuid"] = bundle["uuid"]
                self.bundleDict["displayName"] = bundle["displayName"]
                self.bundleDict["description"] = bundle["description"]
                self.bundleDict["promoDescription"] = bundle["promoDescription"]
                self.bundleDict["extraDescription"] = bundle["extraDescription"]  
                self.bundleDict["displayIcon"] = bundle["displayIcon"]
                self.bundleDict["displayIcon2"] = bundle["displayIcon2"]
                self.bundleDict["logoIcon"] = bundle["logoIcon"]
                self.bundleDict["verticalPromoImage"] = bundle["verticalPromoImage"]

                print(self.bundleDict)
                dbValorant.bundles.update_one({"uuid": bundle["uuid"]}, {"$set": self.bundleDict}, upsert=True)

            return data

        else:
            print("Failed to retrieve skins. Status code:", response.status_code)
            return None
        
        
        

# valorantSync =  SyncApi()

# valorantSync.get_all_agents()
# valorantSync.get_all_skins()
# valorantSync.get_all_maps()
# valorantSync.get_all_bundles()