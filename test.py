import requests

def get_all_agents():
    url = "https://valorant-api.com/v1/agents"
    params ={"language": "fr-FR"}
    response = requests.get(url = url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to retrieve buddies. Status code:", response.status_code)
        return None

# Appel de la fonction pour obtenir tous les Buddys
agents_data = get_all_agents()

if agents_data:
    print("Liste de tous les agents :")
    for agent in agents_data["data"]:
        print("- Nom :", agent["displayName"])
        print("  Description :", agent["description"])
        print("  ID :", agent["uuid"])
        print("  Image URL :", agent["displayIcon"])
else:
    print("Impossible de récupérer les données des Buddys.")