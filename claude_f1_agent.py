from anthropic import Anthropic
from dotenv import load_dotenv
import os
import requests

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# On définit les outils que Claude peut utiliser
tools = [
    {
        "name": "get_race_results",
        "description": "Récupère toutes les sessions de courses F1 pour une année donnée",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "L'année"}
            },
            "required": ["year"]
        }
    },
    {
        "name": "get_race_winner",
        "description": "Récupère le classement d'une course F1 spécifique par année et circuit",
        "input_schema": {
            "type": "object",
            "properties": {
                "year": {"type": "integer", "description": "L'année"},
                "circuit_short_name": {"type": "string", "description": "Le nom court du circuit tel qu'utilisé par l'API OpenF1 (ex: 'Monte Carlo' pour Monaco, pas 'Monaco')"}
            },
            "required": ["year", "circuit_short_name"]
        }
    }
]

def get_race_results(year):
    response = requests.get(f"https://api.openf1.org/v1/sessions?year={year}&session_type=Race")
    return response.json()

def get_race_winner(year, circuit_short_name):
    sessions = requests.get(f"https://api.openf1.org/v1/sessions?year={year}&session_type=Race&circuit_short_name={circuit_short_name}").json()
    print(f"DEBUG - sessions trouvées: {sessions}")  # ligne ajoutée pour debugger
    if not sessions:
        return {"error": "Course non trouvée"}
    session_key = sessions[0]["session_key"]
    positions = requests.get(f"https://api.openf1.org/v1/position?session_key={session_key}").json()
    return positions

question = "Qui a gagné le Grand Prix de Monaco en 2024 ?"

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": question}]
)

if message.stop_reason == "tool_use":
    tool_use = next(block for block in message.content if block.type == "tool_use")

    # On exécute la BONNE fonction selon ce que Claude a demandé
    if tool_use.name == "get_race_results":
        result = get_race_results(tool_use.input["year"])
    elif tool_use.name == "get_race_winner":
        result = get_race_winner(tool_use.input["year"], tool_use.input["circuit_short_name"])

    final_message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        tools=tools,
        messages=[
            {"role": "user", "content": question},
            {"role": "assistant", "content": message.content},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tool_use.id, "content": str(result)}
            ]}
        ]
    )
    print(final_message.content[0].text)
else:
    print(message.content[0].text)