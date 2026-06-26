from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "F1 Agent API is running"}

@app.get("/drivers")
def get_drivers():
    response = requests.get("https://api.openf1.org/v1/drivers?session_key=9158")
    return response.json()

@app.get("/race/{year}")
def get_race(year: int):
    response = requests.get(f"https://api.openf1.org/v1/sessions?year={year}&session_type=Race")
    return response.json()
