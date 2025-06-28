from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ProblemaPL(models.Model):
    OBJETIVO_CHOICES = [
        ('max', 'Maximizar'),
        ('min', 'Minimizar'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='problemas_pl',
        null=True,
        blank=True
    )
    objetivo = models.CharField(max_length=3, choices=OBJETIVO_CHOICES)
    coef_x1 = models.FloatField()
    coef_x2 = models.FloatField()
    restricciones = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PL {self.get_objetivo_display()}"


class HistoryEntry(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='history_entries'
    )
    problem_description = models.TextField()
    result = models.CharField(max_length=255)
    graph_image = models.ImageField(upload_to='graphs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at:%Y-%m-%d %H:%M}"
