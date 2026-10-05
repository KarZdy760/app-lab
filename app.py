import os
import psycopg
from flask import Flask, jsonify

app = Flask(__name__)

def connect():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        connect_timeout=3,
        application_name="app-lab",
        options="-c statement_timeout=5000",
    )

@app.get("/")
def index():
    try:
        with connect() as conn:
            row = conn.execute(
                "UPDATE public.counter SET visits = visits + 1 "
                "WHERE id = 1 RETURNING visits"
            ).fetchone()
            if row is None:
                raise RuntimeError("Brak rekordu licznika")
        return jsonify(
            application="app-lab",
            version=os.getenv("APP_VERSION", "2.0"),
            visits=row[0],
        )
    except Exception:
        app.logger.exception("Nie udalo sie obsluzyc zadania")
        return jsonify(error="Nie mozna wykonac operacji w bazie"), 503

@app.get("/live")
def live():
    return jsonify(status="alive"), 200

@app.get("/ready")
def ready():
    try:
        with connect() as conn:
            row = conn.execute(
                "SELECT visits FROM public.counter WHERE id = 1"
            ).fetchone()
            if row is None:
                raise RuntimeError("Brak rekordu licznika")
        return jsonify(status="ready"), 200
    except Exception:
        app.logger.exception("Sprawdzenie gotowosci nie powiodlo sie")
        return jsonify(status="not ready"), 503
