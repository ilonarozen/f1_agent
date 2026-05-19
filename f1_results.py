import requests

def get_f1_drivers():
    try:
        response = requests.get("https://api.openf1.org/v1/drivers?session_key=9158")
        response.raise_for_status()
        data = response.json()
        
        print(f"🏎️  Pilotes F1 2024 — {len(data)} pilotes\n")
        print("-" * 40)
        
        for i, driver in enumerate(data, 1):
            print(f"{i:2}. {driver['full_name']} — {driver['team_name']} ({driver['country_code']})")
            
    except requests.exceptions.ConnectionError:
        print("❌ Pas de connexion internet")
    except requests.exceptions.HTTPError as e:
        print(f"❌ Erreur HTTP : {e}")
    except Exception as e:
        print(f"❌ Erreur : {e}")

get_f1_drivers()