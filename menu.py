# ============================================================
# LOGICA DEL MENU JERARQUICO
# ============================================================

from flask import render_template, request

from auth import obtener_accesos


# ============================================================
# FUNCION CENTRAL DEL MENU
# ============================================================
#
# Renderiza menu_principal.html con el contexto adecuado:
#
#   nivel_id=None, subnivel_id=None  -> menu principal (niveles)
#   nivel_id=X,    subnivel_id=None  -> subniveles del nivel X
#   nivel_id=X,    subnivel_id=Y     -> subaccesos del subnivel Y
#
# ============================================================

def render_menu(nivel_id=None, subnivel_id=None):
    usuario = request.cookies.get("usuario")
    accesos = obtener_accesos(usuario)

    nivel_actual = None
    subnivel_actual = None

    # ---------- Buscar nivel actual ----------
    for nivel in accesos:
        if nivel.get("id") == nivel_id:
            nivel_actual = nivel
            for sub in nivel.get("subNiveles", []):
                if sub.get("id") == subnivel_id:
                    subnivel_actual = sub
                    break
            break

    return render_template(
        "menu_principal.html",
        usuario=usuario,
        accesos=accesos,
        nivel_actual=nivel_actual,
        subnivel_actual=subnivel_actual
    )