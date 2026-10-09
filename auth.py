# ============================================================
# AUTENTICACION Y CONTROL DE ACCESOS
# ============================================================

from functools import wraps
from flask import request, redirect, url_for
import requests

from config import BASE_URL_ACCESOS


# ============================================================
# DECORADOR: PROTECCION DE RUTAS
# ============================================================

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        usuario = request.cookies.get("usuario")

        if not usuario:
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


# ============================================================
# HELPER: OBTENER ACCESOS
# ============================================================

def obtener_accesos(usuario):
    try:
        response = requests.post(
            BASE_URL_ACCESOS,
            json={"usuario": usuario},
            headers={
                "accept": "*/*",
                "Content-Type": "application/json"
            },
            timeout=10
        )

        if response.status_code == 200:
            datos = response.json()
            if isinstance(datos, list):
                return datos

    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.ConnectionError:
        pass
    except Exception:
        pass

    return []