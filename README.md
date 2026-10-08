# Sistema de Reportes de Atención Técnica
Municipalidad de Chiquimula · Django + Tailwind CSS

## Puesta en marcha (Windows / Linux / Mac)

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser   # usuario para ingresar
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ e ingresar con el usuario creado.
Panel de administración: http://127.0.0.1:8000/admin/

## Pruebas
```bash
python manage.py test
```

## Estructura
- `reportes/models.py`  → `ReporteAtencion` (secciones 1-9) y `CompraItem` (tabla de compras)
- `reportes/forms.py`   → formulario + formset de compras
- `reportes/views.py`   → lista con búsqueda/filtro, crear, editar, detalle/impresión, eliminar
- `templates/`, `reportes/templates/reportes/` → pantallas con Tailwind

## Notas
- Tailwind se carga por CDN (necesita internet). Para producción, compilarlo localmente
  (Tailwind CLI o `django-tailwind`) y cambiar `DEBUG`, `SECRET_KEY` y `ALLOWED_HOSTS` en `config/settings.py`.
- El No. de reporte se genera solo: `ATC-AAAA-0001`.
