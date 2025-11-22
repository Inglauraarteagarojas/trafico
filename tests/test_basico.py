import os
import re

RUTA_ARCHIVO = "index.html"


def leer_html():
    assert os.path.exists(RUTA_ARCHIVO), "No se encontró index.html en la raíz del proyecto"
    with open(RUTA_ARCHIVO, "r", encoding="utf-8") as f:
        return f.read()


def test_index_existe():
    """Prueba de humo: el archivo index.html debe existir."""
    assert os.path.exists(RUTA_ARCHIVO), "index.html no existe"


def test_index_tiene_titulo():
    """Validar que el HTML tenga etiqueta <title> con algún texto."""
    html = leer_html()
    match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
    assert match is not None, "No se encontró la etiqueta <title> en index.html"
    assert match.group(1).strip() != "", "La etiqueta <title> está vacía"


def test_index_tiene_header_principal():
    """Validar que exista al menos un encabezado principal <h1>."""
    html = leer_html()
    tiene_h1 = re.search(r"<h1[^>]*>.*?</h1>", html, re.IGNORECASE | re.DOTALL)
    assert tiene_h1 is not None, "No se encontró ningún <h1> en index.html"