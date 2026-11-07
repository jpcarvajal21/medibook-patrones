"""
BACKEND: servidor web con Flask.
Solo recibe las peticiones del frontend y llama a la lógica de negocio (carpeta dominio).
Ejecutar:  python app.py   y abrir  http://127.0.0.1:5000
"""
from datetime import datetime

from flask import Flask, jsonify, request, send_from_directory

from dominio.datos import T0, Sistema
from dominio.estados import AccionNoPermitida

app = Flask(__name__, static_folder="static")
sistema = Sistema()


def leer_reloj() -> datetime:
    """El frontend envía la fecha y hora simulada; fsi no llega, se usa T0 de la Etapa 3."""
    texto = (request.get_json(silent=True) or {}).get("ahora")
    return datetime.fromisoformat(texto) if texto else T0


@app.get("/")
def inicio():
    return send_from_directory("static", "index.html")


@app.get("/api/citas")
def listar_citas():
    return jsonify({
        "citas": [c.a_dict() for c in sistema.citas.values()],
        "avisos": sistema.bandeja.mensajes,
        "historial": sistema.historial.registros,
        "t0": T0.isoformat(timespec="minutes"),
    })


@app.post("/api/citas/<id_cita>/cancelar")
def cancelar(id_cita):
    cita = sistema.citas.get(id_cita)
    if cita is None:
        return jsonify({"ok": False, "mensaje": "La cita no existe."}), 404
    avisos_antes = len(sistema.bandeja.mensajes)
    try:
        mensaje = cita.cancelar(leer_reloj())          # STATE decide; OBSERVER avisa
        ok, codigo = True, 200
    except AccionNoPermitida as error:
        mensaje, ok, codigo = str(error), False, 409
    return jsonify({"ok": ok, "mensaje": mensaje, "estado": cita.estado.nombre,
                    "avisos_nuevos": sistema.bandeja.mensajes[avisos_antes:]}), codigo


@app.post("/api/citas/<id_cita>/atender")
def atender(id_cita):
    cita = sistema.citas.get(id_cita)
    if cita is None:
        return jsonify({"ok": False, "mensaje": "La cita no existe."}), 404
    try:
        mensaje = cita.atender()
        ok, codigo = True, 200
    except AccionNoPermitida as error:
        mensaje, ok, codigo = str(error), False, 409
    return jsonify({"ok": ok, "mensaje": mensaje, "estado": cita.estado.nombre, "avisos_nuevos": []}), codigo


@app.post("/api/reiniciar")
def reiniciar():
    sistema.reiniciar()
    return jsonify({"ok": True, "mensaje": "Datos reiniciados al estado inicial."})


if __name__ == "__main__":
    app.run(debug=True)
