from django.db import models
from django.contrib.auth import get_user_model

class ProblemaPL(models.Model):
    OBJETIVO_CHOICES = [
        ('max', 'Maximizar'),
        ('min', 'Minimizar'),
    ]

    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name='problemas_pl',
        null=True, blank=True
    )
    objetivo = models.CharField(max_length=3, choices=OBJETIVO_CHOICES)
    coef_x1 = models.FloatField()
    coef_x2 = models.FloatField()
    restricciones = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PL {self.get_objetivo_display()}"