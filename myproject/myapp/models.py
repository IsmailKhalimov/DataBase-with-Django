from django.db import models
from django.contrib.auth.models import User


# Новая модель для хранения динамически созданных таблиц
class CustomTable(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tables')

    def __str__(self):
        return self.name


class TableAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='table_accesses')
    table = models.ForeignKey(CustomTable, on_delete=models.CASCADE, related_name='user_access')
    can_access = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} access to {self.table.name}"
