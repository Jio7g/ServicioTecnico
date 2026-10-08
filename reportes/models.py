from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.utils import timezone


class TipoProblema(models.TextChoices):
    EQUIPO = "equipo", "Equipo de cómputo"
    RED = "red", "Red o internet"
    IMPRESORA = "impresora", "Impresora"
    SOFTWARE = "software", "Sistema o software"
    ELECTRICA = "electrica", "Instalación eléctrica"
    OTRO = "otro", "Otro"


class Resultado(models.TextChoices):
    RESUELTO = "si", "Sí, quedó resuelto"
    PARCIAL = "parcial", "Parcialmente, queda pendiente"
    NO = "no", "No se pudo resolver"


class ReporteAtencion(models.Model):
    # 1. Datos generales y persona afectada
    numero = models.CharField("Reporte No.", max_length=20, unique=True, null=True, blank=True, editable=False)
    fecha = models.DateField("Fecha", default=timezone.localdate)
    oficina = models.CharField("Oficina o dependencia", max_length=150)
    hora_llegada = models.TimeField("Hora de llegada", null=True, blank=True)
    hora_salida = models.TimeField("Hora de salida", null=True, blank=True)
    persona_afectada = models.CharField("Persona afectada (nombre)", max_length=150)
    cargo = models.CharField("Cargo o puesto", max_length=100, blank=True)
    tecnico = models.CharField("Técnico responsable", max_length=150)
    telefono = models.CharField("Teléfono o extensión", max_length=30, blank=True)

    # 2. Problema reportado
    tipos_problema = models.JSONField("Tipo de problema", default=list, blank=True)
    otro_tipo = models.CharField("Otro (especifique)", max_length=100, blank=True)
    descripcion = models.TextField("Descripción")

    # 3 y 4
    resolucion = models.TextField("Qué se hizo para solucionarlo", blank=True)
    recomendaciones = models.TextField("Para evitar que el problema se repita", blank=True)

    # 5. Confirmación
    resultado = models.CharField("¿Se resolvió el problema?", max_length=10,
                                 choices=Resultado.choices, default=Resultado.RESUELTO)
    motivo_seguimiento = models.TextField("Motivo o seguimiento", blank=True)

    # 6. Compras
    hubo_compra = models.BooleanField("¿Fue necesario comprar algo?", default=False)
    no_factura = models.CharField("No. de factura o comprobante", max_length=50, blank=True)

    # 7-8. Firmas: nombre + firma dibujada (imagen PNG en base64)
    firma_tecnico = models.CharField("Nombre del técnico que apoyó", max_length=150, blank=True)
    firma_tecnico_img = models.TextField("Firma del técnico", blank=True)
    firma_encargado = models.CharField("Nombre del encargado de oficina", max_length=150, blank=True)
    firma_encargado_img = models.TextField("Firma del encargado", blank=True)

    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "-id"]
        verbose_name = "Reporte de atención técnica"
        verbose_name_plural = "Reportes de atención técnica"

    def __str__(self):
        return f"{self.numero} - {self.oficina}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.numero:
            self.numero = f"ATC-{self.fecha.year}-{self.pk:04d}"
            super().save(update_fields=["numero"])

    def get_absolute_url(self):
        return reverse("reportes:detalle", args=[self.pk])

    @property
    def tipos_display(self):
        etiquetas = dict(TipoProblema.choices)
        nombres = []
        for t in self.tipos_problema:
            if t == TipoProblema.OTRO and self.otro_tipo:
                nombres.append(f"Otro: {self.otro_tipo}")
            else:
                nombres.append(etiquetas.get(t, t))
        return nombres

    @property
    def total_compra(self):
        return sum((i.total for i in self.compras.all()), Decimal("0"))


class CompraItem(models.Model):
    reporte = models.ForeignKey(ReporteAtencion, on_delete=models.CASCADE, related_name="compras")
    articulo = models.CharField("Artículo comprado", max_length=150)
    cantidad = models.PositiveIntegerField("Cantidad", default=1)
    precio_unitario = models.DecimalField("Precio unit. (Q)", max_digits=10, decimal_places=2)

    @property
    def total(self):
        return (self.cantidad or 0) * (self.precio_unitario or Decimal("0"))

    def __str__(self):
        return self.articulo