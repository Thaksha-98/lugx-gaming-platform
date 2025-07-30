from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import psycopg2
from starlette_prometheus import PrometheusMiddleware, metrics

app = FastAPI()

# Add Prometheus middleware for metrics
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", metrics)

DB_CONFIG = {
    "host": "postgres.lugx.svc.cluster.local",
    "database": "lugx_db",
    "user": "admin",
    "password": "securepassword123"
}

class OrderItem(BaseModel):
    game_id: int
    quantity: int
    price: float

class Order(BaseModel):
    user_id: str
    items: List[OrderItem]
    total_price: float

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

@app.on_event("startup")
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            total_price DECIMAL,
            created_at TIMESTAMP DEFAULT NOW()
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id SERIAL PRIMARY KEY,
            order_id INTEGER,
            game_id INTEGER,
            quantity INTEGER,
            price DECIMAL
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

@app.post("/orders")
def create_order(order: Order):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO orders (user_id, total_price) VALUES (%s, %s) RETURNING id",
        (order.user_id, order.total_price)
    )
    order_id = cur.fetchone()[0]
    for item in order.items:
        cur.execute(
            "INSERT INTO order_items (order_id, game_id, quantity, price) VALUES (%s, %s, %s, %s)",
            (order_id, item.game_id, item.quantity, item.price)
        )
    conn.commit()
    cur.close()
    conn.close()
    return {"order_id": order_id, "status": "Order created"}
@app.get("/orders")
def list_orders():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, total_price, created_at FROM orders")
    orders_data = cur.fetchall()

    orders = []
    for order_row in orders_data:
        order_id, user_id, total_price, created_at = order_row
        cur.execute("SELECT game_id, quantity, price FROM order_items WHERE order_id = %s", (order_id,))
        items_data = cur.fetchall()
        items = [{"game_id": game_id, "quantity": quantity, "price": float(price)} for game_id, quantity, price in items_data]
        orders.append({
            "order_id": order_id,
            "user_id": user_id,
            "total_price": float(total_price),
            "created_at": created_at,
            "items": items
        })

    cur.close()
    conn.close()
    return orders
