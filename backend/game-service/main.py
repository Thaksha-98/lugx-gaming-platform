from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List
from starlette_prometheus import PrometheusMiddleware, metrics
from datetime import date


app = FastAPI()
# Add Prometheus middleware for metrics
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

# DB Config
DB_CONFIG = {
    "host": "postgres.lugx.svc.cluster.local",
    "database": "lugx_db",
    "user": "admin",
    "password": "securepassword123"
}

class Game(BaseModel):
    name: str
    category: str
    released_date: date
    price: float

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.on_event("startup")
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id SERIAL PRIMARY KEY,
            name TEXT,
            category TEXT,
            released_date DATE,
            price DECIMAL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.get("/games", response_model=List[Game])
def get_games():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT name, category, released_date, price FROM games")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"name": r[0], "category": r[1], "released_date": str(r[2]), "price": r[3]} for r in rows]

@app.post("/games")
def create_game(game: Game):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO games (name, category, released_date, price) VALUES (%s, %s, %s, %s)",
        (game.name, game.category, game.released_date, game.price)
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "Game created"}
