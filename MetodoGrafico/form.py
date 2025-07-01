from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User



class ProblemaPLForm(forms.Form):
    OBJETIVO_CHOICES = [
        ("max", "Maximizar"),
        ("min", "Minimizar"),
    ]

    objetivo = forms.ChoiceField(
        choices=OBJETIVO_CHOICES, widget=forms.Select(attrs={"class": "form-select"})
    )
    coef_x1 = forms.FloatField(
        label="Coeficiente x1",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Coeficiente de x₁"}
        ),
    )
    coef_x2 = forms.FloatField(
        label="Coeficiente x2",
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Coeficiente de x₂"}
        ),
    )
    x1_min = forms.FloatField(
        label="Valor mínimo para x1",
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Mínimo permitido para x₁"}
        ),
    )
    x1_max = forms.FloatField(
        label="Valor máximo para x1",
        required=False,
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "placeholder": "Valor máximo permitido para x₁",
            }
        ),
    )
    x2_min = forms.FloatField(
        label="Valor mínimo para x2",
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Mínimo permitido para x₂"}
        ),
    )
    x2_max = forms.FloatField(
        label="Valor máximo para x2",
        required=False,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Máximo permitido para x₂"}
        ),
    )
    restricciones = forms.CharField(
        label="Restricciones (JSON)",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": '[{"coef_x1": 2, "coef_x2": 1, "operador": "<=", "valor": 18}]',
            }
        ),
    )

    def clean_restricciones(self):
        import json

        data = self.cleaned_data.get("restricciones")
        if not data:
            raise forms.ValidationError("Este campo es obligatorio")
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            raise forms.ValidationError("Formato de restricciones invalido")
        if not isinstance(parsed, list):
            raise forms.ValidationError("Las restricciones deben ser una lista")
        for res in parsed:
            try:
                float(res.get("coef_x1"))
                float(res.get("coef_x2"))
                float(res.get("valor"))
            except (TypeError, ValueError):
                raise forms.ValidationError("Coeficientes y valores deben ser numeros")
            if res.get("operador") not in ["<=", ">=", "="]:
                raise forms.ValidationError("Operador invalido")
        return parsed

    def clean(self):
        cleaned = super().clean()
        x1_min = cleaned.get("x1_min")
        x1_max = cleaned.get("x1_max")
        x2_min = cleaned.get("x2_min")
        x2_max = cleaned.get("x2_max")
        if x1_min is not None and x1_max is not None and x1_max < x1_min:
            self.add_error(
                "x1_max", "El límite superior debe ser mayor o igual al inferior"
            )
        if x2_min is not None and x2_max is not None and x2_max < x2_min:
            self.add_error(
                "x2_max", "El límite superior debe ser mayor o igual al inferior"
            )
        return cleaned


class SistemaLinealForm(forms.Form):
    """Formulario para resolver sistemas de dos ecuaciones."""

    ecuacion1 = forms.CharField(
        label="Ecuación 1",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "3 x1 + 5 x2 = 6"}
        ),
    )
    ecuacion2 = forms.CharField(
        label="Ecuación 2",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "4 x1 + 2 x2 = 5"}
        ),
    )
    metodo = forms.ChoiceField(
        choices=[("eliminacion", "Eliminación"), ("sustitucion", "Sustitución")],
        widget=forms.Select(attrs={"class": "form-select"}),
        initial="eliminacion",
    )
