from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import os

app = Flask(__name__)

# Usuarios autorizados
usuarios = {
    "123456789": {"clave": "gato44", "ultima_sesion": None},
    "987654321": {"clave": "peras18", "ultima_sesion": None}
}

# Tiempo límite por sesión (en minutos)
TIEMPO_EXPIRACION = timedelta(minutes=10)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user_id = data.get("user_id")
    clave = data.get("clave")
    ahora = datetime.utcnow()

    if user_id not in usuarios:
        return jsonify({ "access": False, "reason": "ID no autorizado" })

    usuario = usuarios[user_id]

    if clave != usuario["clave"]:
        return jsonify({ "access": False, "reason": "Clave incorrecta" })

    ultima = usuario["ultima_sesion"]
    if ultima and ahora - ultima < TIEMPO_EXPIRACION:
        return jsonify({
            "access": False,
            "reason": "Ya hay una sesión activa para este usuario"
        })

    usuario["ultima_sesion"] = ahora
    return jsonify({ "access": True })

@app.route("/")
def index():
    return "API GPT lista"

# Iniciar Flask usando el puerto asignado por Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
