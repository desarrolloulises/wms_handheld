# WMS Handheld

Sistema web para terminales handheld Intermec CK3X, desarrollado en Flask y pensado para ejecutarse en el navegador Internet Explorer 6 del dispositivo. Se despliega en IIS mediante FastCGI.

## Tecnologías

| Componente | Versión |
|------------|---------|
| Flask      | 3.1.3   |
| requests   | 2.33.1  |
| wfastcgi   | 3.0.0   |

## Estructura del proyecto

```
wms_handheld/
├── app.py                      # Configuración de rutas y lógica del login
├── config.py                   # Constantes (URLs) y mapa de rutas
├── auth.py                     # login_required, obtener_accesos
├── menu.py                     # Lógica del menú jerárquico
├── web.config                  # Configuración para IIS
├── templates/
│   ├── layout_base.html        # Estructura base del HTML (cabecera, dimensiones del viewport)
│   ├── login.html              # Formulario de inicio de sesión
│   ├── menu_principal.html     # Menú dinámico
│   ├── vista_provisional.html  # Vista informativa para rutas sin HTML vinculado
│   └── reasignaciones.html     # Módulo de reasignaciones de cajas
└── static/
    ├── error.wav               # Sonido de error
    └── succes.wav              # Sonido de éxito
```

## Descripción de los archivos

- **app.py**: define las rutas de Flask y la lógica del inicio de sesión.
- **config.py**: contiene las constantes (URLs) y el mapa de rutas `MAPA_RUTAS`.
- **auth.py**: incluye el decorador `login_required` y la función `obtener_accesos`.
- **menu.py**: construye el menú jerárquico según los accesos del usuario.
- **web.config**: configuración del sitio para IIS con FastCGI.

## Cómo agregar una nueva ruta

Las rutas se vinculan a una pantalla en `config.py`, dentro del diccionario `MAPA_RUTAS`. La llave se forma con el nivel, un guion y el subnivel, y el valor es el HTML que se mostrará:

```python
MAPA_RUTAS = {
    "2999-1": "reasignaciones.html",
}
```

Pasos:

1. Crear el archivo HTML en la carpeta `templates/`.
2. Agregar la entrada `"nivel-subnivel": "archivo.html"` en `MAPA_RUTAS`.

Si una ruta del menú aún no tiene un HTML vinculado, el sistema muestra `vista_provisional.html`.

## Despliegue en IIS

El sistema se sirve a través de IIS usando `wfastcgi`, por lo que es necesario el archivo `web.config` en la raíz del proyecto:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonFastCGI"
           path="*"
           verb="*"
           modules="FastCgiModule"
           scriptProcessor="C:\dev_sites\wms_handheld\env\Scripts\python.exe|C:\dev_sites\wms_handheld\env\Lib\site-packages\wfastcgi.py"
           resourceType="Unspecified"
           requireAccess="Script" />
    </handlers>
  </system.webServer>
  <appSettings>
    <add key="WSGI_HANDLER" value="app.app" />
    <!-- Ruta ABSOLUTA a la carpeta del proyecto -->
    <add key="PYTHONPATH" value="C:\dev_sites\wms_handheld" />
    <add key="FLASK_ENV" value="production" />
  </appSettings>
</configuration>
```

Notas:

- Ajustar las rutas de `scriptProcessor` y `PYTHONPATH` según la ubicación real del proyecto y del entorno virtual.
- `WSGI_HANDLER` apunta a `app.app` (el objeto Flask `app` dentro de `app.py`).

## Consideraciones para IE6

- Usar HTML y CSS simples, sin características modernas.
- Mantener el viewport definido en `layout_base.html` para el tamaño de pantalla de la CK3X.
- Los sonidos de éxito y error se encuentran en `static/`.