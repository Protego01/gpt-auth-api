from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import csv
import requests
import os

app = Flask(__name__)

# Enlace a tu hoja de Google Sheets (publicada como CSV)
URL_HOJA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRTLBQlz_iuj-A4om_MV6seXSbd6ZAJAMsBPzxwKDUyxvSFCNA0HvA6EiaXv098B51ws6GJYOzsAZ5u/pub?gid=0&single=true&output=csv"

# Tiempo límite por sesión (en minutos)
TIEMPO_EXPIRACION = timedelta(minutes=4)

# Sesiones activas en memoria
sesiones = {}

# Cargar usuarios desde la hoja (dinámicamente)
def cargar_usuarios():
    usuarios = {}
    try:
        response = requests.get(URL_HOJA)
        response.raise_for_status()
        decoded = response.content.decode("utf-8").splitlines()
        reader = csv.reader(decoded)
        next(reader, None)  # Saltar encabezado
        for row in reader:
            if len(row) >= 2:
                user_id = row[0].strip()
                clave = row[1].strip()
                usuarios[user_id] = clave
    except Exception as e:
        print("Error al cargar la hoja:", e)
    return usuarios

@app.route("/login", methods=["POST"])
def login():
    usuarios = cargar_usuarios()
    data = request.json
    user_id = data.get("id")
    clave = data.get("clave")
    ahora = datetime.utcnow()

    if user_id not in usuarios:
        return jsonify({"autorizado": False, "reason": "ID no autorizado"})

    if clave != usuarios[user_id]:
        return jsonify({"autorizado": False, "reason": "Clave incorrecta"})

    ultima = sesiones.get(user_id)
    if ultima and ahora - ultima < TIEMPO_EXPIRACION:
        return jsonify({
            "autorizado": False,
            "reason": "Ya hay una sesión activa para este usuario"
        })

    sesiones[user_id] = ahora
    return jsonify({"autorizado": True})

@app.route("/")
def index():
    return "API GPT lista"

# Iniciar Flask usando el puerto asignado por Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
