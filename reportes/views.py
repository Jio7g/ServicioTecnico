from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import CompraFormSet, ReporteForm
from .models import ReporteAtencion, Resultado


class ReporteListView(LoginRequiredMixin, ListView):
    model = ReporteAtencion
    template_name = "reportes/lista.html"
    context_object_name = "reportes"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        estado = self.request.GET.get("estado", "")
        if q:
            qs = qs.filter(
                Q(numero__icontains=q) | Q(oficina__icontains=q)
                | Q(persona_afectada__icontains=q) | Q(tecnico__icontains=q)
            )
        if estado in Resultado.values:
            qs = qs.filter(resultado=estado)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["estado"] = self.request.GET.get("estado", "")
        ctx["resultados"] = Resultado.choices
        total = ReporteAtencion.objects
        ctx["stats"] = {
            "total": total.count(),
            "resueltos": total.filter(resultado=Resultado.RESUELTO).count(),
            "pendientes": total.exclude(resultado=Resultado.RESUELTO).count(),
        }
        return ctx


class ReporteFormMixin(LoginRequiredMixin):
    model = ReporteAtencion
    form_class = ReporteForm
    template_name = "reportes/form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["formset"] = CompraFormSet(self.request.POST, instance=self.object)
        else:
            ctx["formset"] = CompraFormSet(instance=self.object)
        return ctx

    def form_valid(self, form):
        ctx = self.get_context_data()
        formset = ctx["formset"]
        if not formset.is_valid():
            return self.render_to_response(self.get_context_data(form=form))
        with transaction.atomic():
            self.object = form.save()
            formset.instance = self.object
            if self.object.hubo_compra:
                formset.save()
            else:  # si marcó "No", no se guardan filas de compra
                self.object.compras.all().delete()
        messages.success(self.request, f"Reporte {self.object.numero} guardado correctamente.")
        return HttpResponseRedirect(self.object.get_absolute_url())


class ReporteCreateView(ReporteFormMixin, CreateView):
    pass


class ReporteUpdateView(ReporteFormMixin, UpdateView):
    pass


class ReporteDetailView(LoginRequiredMixin, DetailView):
    model = ReporteAtencion
    template_name = "reportes/detalle.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        r = self.object
        ctx["firmas"] = [
            ("7. Firma — Técnico que apoyó", r.firma_tecnico, r.firma_tecnico_img),
            ("8. Firma — Encargado de oficina", r.firma_encargado, r.firma_encargado_img),
        ]
        return ctx


class ReporteDeleteView(LoginRequiredMixin, DeleteView):
    model = ReporteAtencion
    template_name = "reportes/confirmar_eliminar.html"
    success_url = reverse_lazy("reportes:lista")

    def form_valid(self, form):
        messages.success(self.request, "Reporte eliminado.")
        return super().form_valid(form)