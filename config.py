# ============================================================
# CONFIGURACION GENERAL
# ============================================================

BASE_URL = "http://192.168.101.10:82/cedis/LOGIN"
BASE_URL_ACCESOS = "http://192.168.102.81:5242/cedis/auth/obtener-accesos"
BASE_URL_REASIGNACION = "http://192.168.102.81:5242/cedis/reasignacion-caja"

# ============================================================
# MAPA DE RUTAS DE NIVELES/SUBNIVELES
# ============================================================
# Aqui iras agregando las rutas conforme vincules HTMLs.
#
#   Clave "nivel-subnivel"               -> subnivel sin subaccesos
#   Clave "nivel-subnivel-subacceso"     -> subacceso especifico
#
# Ejemplo cuando tengas listo el HTML del nivel 2999 subnivel 1:
#   "2999-1": "prueba_desarrollo.html",
# ============================================================

MAPA_RUTAS = {
    "2999-1": "reasignaciones.html",
}