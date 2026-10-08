from django import forms
from django.forms import inlineformset_factory

from .models import CompraItem, ReporteAtencion, TipoProblema

# Clases Tailwind reutilizables para que todos los campos se vean igual
BASE = ("block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm "
        "text-slate-900 shadow-sm placeholder:text-slate-400 "
        "focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-200")


class ReporteForm(forms.ModelForm):
    tipos_problema = forms.MultipleChoiceField(
        label="Tipo de problema",
        choices=TipoProblema.choices,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = ReporteAtencion
        exclude = ["numero", "creado", "actualizado"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "hora_llegada": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "hora_salida": forms.TimeInput(attrs={"type": "time"}, format="%H:%M"),
            "descripcion": forms.Textarea(attrs={"rows": 6, "placeholder": "Describa qué falla reportó el usuario..."}),
            "resolucion": forms.Textarea(attrs={"rows": 6, "placeholder": "Pasos realizados para solucionarlo..."}),
            "recomendaciones": forms.Textarea(attrs={"rows": 6, "placeholder": "Recomendaciones para el usuario..."}),
            "motivo_seguimiento": forms.Textarea(attrs={"rows": 3}),
            "firma_tecnico_img": forms.HiddenInput,
            "firma_encargado_img": forms.HiddenInput,
            "resultado": forms.RadioSelect,
            "hubo_compra": forms.RadioSelect(choices=[(False, "No"), (True, "Sí (llenar tabla)")]),
            "oficina": forms.TextInput(attrs={"placeholder": "Ej. Tesorería municipal"}),
            "telefono": forms.TextInput(attrs={"placeholder": "Ej. 7942-0000 / ext. 12"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["hubo_compra"].required = False
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.HiddenInput):
                continue
            if isinstance(w, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                w.attrs["class"] = "h-4 w-4 accent-sky-600"
            else:
                w.attrs["class"] = BASE

    def _clean_firma(self, campo):
        v = (self.cleaned_data.get(campo) or "").strip()
        if v and (not v.startswith("data:image/png;base64,") or len(v) > 400_000):
            raise forms.ValidationError("La firma no es válida. Vuelva a dibujarla.")
        return v

    def clean_firma_tecnico_img(self):
        return self._clean_firma("firma_tecnico_img")

    def clean_firma_encargado_img(self):
        return self._clean_firma("firma_encargado_img")

    def clean(self):
        data = super().clean()
        if data.get("hora_llegada") and data.get("hora_salida") and data["hora_salida"] < data["hora_llegada"]:
            self.add_error("hora_salida", "La hora de salida no puede ser anterior a la de llegada.")
        if "otro" in (data.get("tipos_problema") or []) and not data.get("otro_tipo"):
            self.add_error("otro_tipo", "Especifique el tipo de problema.")
        return data


class CompraItemForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sin valor inicial: así una fila vacía se ignora al guardar
        self.fields["cantidad"].initial = None
        self.fields["cantidad"].widget.attrs["placeholder"] = "Cant."
        self.fields["precio_unitario"].widget.attrs["placeholder"] = "0.00"

    class Meta:
        model = CompraItem
        fields = ["articulo", "cantidad", "precio_unitario"]
        widgets = {
            "articulo": forms.TextInput(attrs={"placeholder": "Artículo", "class": BASE}),
            "cantidad": forms.NumberInput(attrs={"min": 1, "class": BASE + " js-cant"}),
            "precio_unitario": forms.NumberInput(attrs={"min": 0, "step": "0.01", "class": BASE + " js-precio"}),
        }


CompraFormSet = inlineformset_factory(
    ReporteAtencion, CompraItem, form=CompraItemForm, extra=2, can_delete=True,
)