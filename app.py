# ============================================================
# CEDIS - APLICACION PRINCIPAL
# ============================================================
# Este archivo SOLO contiene rutas HTTP.
# La logica vive en: config.py, auth.py, menu.py
# ============================================================

from flask import (
    Flask, request, render_template, redirect,
    url_for, make_response, jsonify
)
import requests

from config import BASE_URL, BASE_URL_REASIGNACION, MAPA_RUTAS
from auth import login_required
from menu import render_menu

app = Flask(__name__)


# ============================================================
# LOGIN
# ============================================================

@app.route("/", methods=["GET", "POST"])
def login():
    error = False
    mensaje = ""
    usuario = ""
    
    # ============================================================
    # Si ya existe cookie de sesion, redirigir directo al menu
    # ============================================================
    usuario_cookie = request.cookies.get("usuario")
    if usuario_cookie:
        return redirect(url_for("principal"))

    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        # ----------------------------------------------------
        # Validar campos
        # ----------------------------------------------------
        if usuario == "":
            error = True
            mensaje = "Ingrese el usuario."

        elif password == "":
            error = True
            mensaje = "Ingrese la contraseña."

        else:
            try:
                # ====================================================
                # PROCESO 1
                # ====================================================
                parametros = {
                    "proceso": 1,
                    "usuario": usuario,
                    "password": password
                }

                response = requests.get(
                    BASE_URL,
                    params=parametros,
                    timeout=10
                )
                datos = response.json()

                if not datos:
                    error = True
                    mensaje = "El sistema no devolvio informacion."

                else:
                    resultado = datos[0]
                    err_id = resultado.get("err_id", -1)
                    err_msg = resultado.get("err_msg", "")

                    # ====================================================
                    # USUARIO NO EXISTE
                    # ====================================================
                    if err_id == 10:
                        error = True
                        mensaje = "Usuario no existe."

                    # ====================================================
                    # USUARIO CORRECTO -> PROCESO 2
                    # ====================================================
                    elif err_id == 0:
                        parametros = {
                            "proceso": 2,
                            "usuario": usuario,
                            "password": password
                        }

                        response = requests.get(
                            BASE_URL,
                            params=parametros,
                            timeout=10
                        )
                        datos = response.json()

                        if not datos:
                            error = True
                            mensaje = "El sistema no devolvio informacion."

                        else:
                            resultado = datos[0]
                            err_id = resultado.get("err_id", -1)
                            err_msg = resultado.get("err_msg", "")

                            # ==========================================
                            # PASSWORD INCORRECTO
                            # ==========================================
                            if err_id == 20:
                                error = True
                                mensaje = "Password incorrecto."

                            # ==========================================
                            # LOGIN CORRECTO
                            # ==========================================
                            elif err_id == 0:
                                response = make_response(
                                    redirect(url_for("principal"))
                                )
                                response.set_cookie(
                                    "usuario",
                                    usuario,
                                    max_age=60 * 60 * 24 * 30
                                )
                                return response

                            # ==========================================
                            # OTRO ERROR
                            # ==========================================
                            else:
                                error = True
                                mensaje = err_msg or "Error al validar la contraseña."

                    # ====================================================
                    # OTRO ERROR DEL PROCESO 1
                    # ====================================================
                    else:
                        error = True
                        mensaje = err_msg or "Error al validar el usuario."

            except requests.exceptions.Timeout:
                error = True
                mensaje = "Tiempo de espera agotado."

            except requests.exceptions.ConnectionError:
                error = True
                mensaje = "No se pudo conectar con el servidor."

            except Exception:
                error = True
                mensaje = "Error de comunicacion con el servidor."

    return render_template(
        "login.html",
        error=error,
        mensaje=mensaje,
        usuario=usuario
    )


# ============================================================
# PRINCIPAL (menu jerarquico)
# ============================================================

@app.route("/principal")
@login_required
def principal():
    return render_menu(nivel_id=None, subnivel_id=None)


# ============================================================
# MENU - NIVELES
# ============================================================

@app.route("/menu/nivel/<int:nivel_id>")
@login_required
def menu_nivel(nivel_id):
    return render_menu(nivel_id=nivel_id, subnivel_id=None)


# ============================================================
# MENU - SUBNIVELES (muestra subaccesos)
# ============================================================

@app.route("/menu/nivel/<int:nivel_id>/subnivel/<int:subnivel_id>")
@login_required
def menu_subnivel(nivel_id, subnivel_id):
    return render_menu(nivel_id=nivel_id, subnivel_id=subnivel_id)


# ============================================================
# NIVEL / SUBNIVEL
# ============================================================

@app.route("/nivel/<int:nivel_id>/subnivel/<int:subnivel_id>")
@login_required
def ir_a_subnivel(nivel_id, subnivel_id):
    clave = "%d-%d" % (nivel_id, subnivel_id)

    if clave in MAPA_RUTAS:
        return render_template(MAPA_RUTAS[clave])

    return render_template(
        "vista_provisional.html",
        usuario=request.cookies.get("usuario"),
        nivel_id=nivel_id,
        subnivel_id=subnivel_id,
        subacceso_id=None
    )


# ============================================================
# NIVEL / SUBNIVEL / SUBACCESO
# ============================================================

@app.route("/nivel/<int:nivel_id>/subnivel/<int:subnivel_id>/subacceso/<int:subacceso_id>")
@login_required
def ir_a_subacceso(nivel_id, subnivel_id, subacceso_id):
    clave = "%d-%d-%d" % (nivel_id, subnivel_id, subacceso_id)

    if clave in MAPA_RUTAS:
        return render_template(MAPA_RUTAS[clave])

    return render_template(
        "vista_provisional.html",
        usuario=request.cookies.get("usuario"),
        nivel_id=nivel_id,
        subnivel_id=subnivel_id,
        subacceso_id=subacceso_id
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():
    response = make_response(redirect(url_for("login")))
    response.delete_cookie("usuario")
    return response


# ============================================================
# PROXY REASIGNACION DE CAJAS
# ============================================================
# El navegador IE de la CK3X no maneja bien CORS y no queremos
# exponer la IP interna del API en el HTML. Flask actua como
# proxy: recibe del cliente, reenvia al API y devuelve JSON.
# ============================================================

def _proxy_reasignacion(endpoint, payload):
    """Helper para reenviar un POST al API de reasignacion."""
    try:
        response = requests.post(
            "%s/%s" % (BASE_URL_REASIGNACION, endpoint),
            json=payload,
            headers={
                "accept": "*/*",
                "Content-Type": "application/json"
            },
            timeout=15
        )

        if response.status_code == 200:
            return jsonify(response.json())

        return jsonify({
            "errId": -1,
            "errMsg": "Error HTTP %d" % response.status_code,
            "titulo": "", "subtitulo": "",
            "ln3": "", "ln4": "", "ln5": "", "ln6": "", "ln7": "",
            "statusCaja": 0
        })

    except requests.exceptions.Timeout:
        return jsonify({
            "errId": -2,
            "errMsg": "Tiempo de espera agotado",
            "titulo": "", "subtitulo": "",
            "ln3": "", "ln4": "", "ln5": "", "ln6": "", "ln7": "",
            "statusCaja": 0
        })

    except requests.exceptions.ConnectionError:
        return jsonify({
            "errId": -3,
            "errMsg": "No se pudo conectar con el servidor",
            "titulo": "", "subtitulo": "",
            "ln3": "", "ln4": "", "ln5": "", "ln6": "", "ln7": "",
            "statusCaja": 0
        })

    except Exception:
        return jsonify({
            "errId": -4,
            "errMsg": "Error de comunicacion con el servidor",
            "titulo": "", "subtitulo": "",
            "ln3": "", "ln4": "", "ln5": "", "ln6": "", "ln7": "",
            "statusCaja": 0
        })


@app.route("/api/reasignacion/obtener-interfaz", methods=["POST"])
@login_required
def api_obtener_interfaz():
    data = request.get_json(silent=True) or {}
    usuario = request.cookies.get("usuario")
    return _proxy_reasignacion("obtener-interfaz", {
        "usuario": usuario
    })


@app.route("/api/reasignacion/consultar-caja-nueva", methods=["POST"])
@login_required
def api_consultar_caja_nueva():
    data = request.get_json(silent=True) or {}
    usuario = request.cookies.get("usuario")
    return _proxy_reasignacion("consultar-caja-nueva", {
        "idCajaNueva": data.get("idCajaNueva", ""),
        "usuario": usuario
    })


@app.route("/api/reasignacion/reasignar-caja", methods=["POST"])
@login_required
def api_reasignar_caja():
    data = request.get_json(silent=True) or {}
    usuario = request.cookies.get("usuario")
    return _proxy_reasignacion("reasignar-caja", {
        "idCajaNueva": data.get("idCajaNueva", ""),
        "idCajaAReasignar": data.get("idCajaAReasignar", ""),
        "usuario": usuario
    })

# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )