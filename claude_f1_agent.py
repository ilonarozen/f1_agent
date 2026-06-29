from anthropic import Anthropic
from dotenv import load_dotenv
import os
import requests

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# On définit l'outil que Claude peut utiliser
tools = [
    {
        "name": "get_race_results",
        "description": "Récupère les sessions de courses F1 pour une année donnée",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {
                    "type": "integer",
                    "description": "L'année de la saison F1"
                }
            },
            "required": ["year"]
        }
    }
]

# La fonction qui exécute réellement l'appel API
def get_race_results(year):
    response = requests.get(f"https://api.openf1.org/v1/sessions?year={year}&session_type=Race")
    return response.json()

# On envoie la question à Claude avec l'outil disponible
message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "Quelles courses ont eu lieu en 2024 ?"}
    ]
)

# Si Claude veut utiliser l'outil, on l'exécute et on lui renvoie le résultat
if message.stop_reason == "tool_use":
    tool_use = next(block for block in message.content if block.type == "tool_use")
    year = tool_use.input["year"]
    result = get_race_results(year)

    # On renvoie le résultat à Claude pour qu'il formule sa réponse finale
    final_message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=tools,
        messages=[
            {"role": "user", "content": "Quelles courses ont eu lieu en 2024 ?"},
            {"role": "assistant", "content": message.content},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tool_use.id, "content": str(result)}
            ]}
        ]
    )
    print(final_message.content[0].text)
else:
    print(message.content[0].text)
