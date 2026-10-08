from django.contrib import admin

from .models import CompraItem, ReporteAtencion


class CompraInline(admin.TabularInline):
    model = CompraItem
    extra = 0


@admin.register(ReporteAtencion)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ("numero", "fecha", "oficina", "persona_afectada", "tecnico", "resultado")
    list_filter = ("resultado", "fecha")
    search_fields = ("numero", "oficina", "persona_afectada", "tecnico")
    inlines = [CompraInline]