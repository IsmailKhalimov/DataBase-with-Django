from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=255)
    left_near = models.IntegerField()
    left_far = models.IntegerField()
    right_near = models.IntegerField()
    right_far = models.IntegerField()
    free_throw = models.IntegerField()


class Team(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    championships_won = models.IntegerField()


# Новая модель для хранения динамически созданных таблиц
class CustomTable(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Название таблицы
    created_at = models.DateTimeField(auto_now_add=True)  # Дата создания
