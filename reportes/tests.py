from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ReporteAtencion


def datos_base(**extra):
    d = {
        "fecha": "2026-10-08", "oficina": "Tesorería", "persona_afectada": "Ana López",
        "cargo": "Cajera", "tecnico": "Juan Pérez", "telefono": "7942-0000",
        "hora_llegada": "09:00", "hora_salida": "10:15",
        "tipos_problema": ["red", "otro"], "otro_tipo": "Cámara",
        "descripcion": "Sin internet", "resolucion": "Se cambió cable", "recomendaciones": "",
        "resultado": "si", "motivo_seguimiento": "", "hubo_compra": "True", "no_factura": "F-123",
        "firma_tecnico": "Juan Pérez", "firma_encargado": "", "firma_jefe": "",
        "compras-TOTAL_FORMS": "2", "compras-INITIAL_FORMS": "0",
        "compras-MIN_NUM_FORMS": "0", "compras-MAX_NUM_FORMS": "1000",
        "compras-0-articulo": "Cable UTP", "compras-0-cantidad": "2", "compras-0-precio_unitario": "15.50",
        "compras-1-articulo": "", "compras-1-cantidad": "", "compras-1-precio_unitario": "",
    }
    d.update(extra)
    return d


class FlujoTest(TestCase):
    def setUp(self):
        get_user_model().objects.create_user("tec", password="x12345678")
        self.client.login(username="tec", password="x12345678")

    def test_requiere_login(self):
        self.client.logout()
        self.assertEqual(self.client.get(reverse("reportes:lista")).status_code, 302)

    def test_crear_con_compra(self):
        r = self.client.post(reverse("reportes:nuevo"), datos_base())
        self.assertEqual(r.status_code, 302, getattr(r, "context", None) and r.context["form"].errors)
        rep = ReporteAtencion.objects.get()
        self.assertEqual(rep.numero, "ATC-2026-0001")
        self.assertEqual(rep.total_compra, Decimal("31.00"))
        self.assertEqual(rep.tipos_display, ["Red o internet", "Otro: Cámara"])

    def test_sin_compra_no_guarda_filas(self):
        self.client.post(reverse("reportes:nuevo"), datos_base(hubo_compra="False"))
        rep = ReporteAtencion.objects.get()
        self.assertFalse(rep.hubo_compra)
        self.assertEqual(rep.compras.count(), 0)

    def test_pantallas(self):
        self.client.post(reverse("reportes:nuevo"), datos_base())
        rep = ReporteAtencion.objects.get()
        for name, args in [("lista", []), ("nuevo", []), ("detalle", [rep.pk]),
                           ("editar", [rep.pk]), ("eliminar", [rep.pk])]:
            self.assertEqual(self.client.get(reverse(f"reportes:{name}", args=args)).status_code, 200, name)
        self.assertContains(self.client.get(reverse("reportes:lista"), {"q": "Tesor"}), "ATC-2026-0001")
        self.client.post(reverse("reportes:eliminar", args=[rep.pk]))
        self.assertEqual(ReporteAtencion.objects.count(), 0)

    def test_validacion_otro_y_horas(self):
        r = self.client.post(reverse("reportes:nuevo"), datos_base(otro_tipo="", hora_salida="08:00"))
        self.assertEqual(r.status_code, 200)
        self.assertIn("otro_tipo", r.context["form"].errors)
        self.assertIn("hora_salida", r.context["form"].errors)
