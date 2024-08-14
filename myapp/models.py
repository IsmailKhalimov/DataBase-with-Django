from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=100)
    left_near = models.IntegerField()
    left_far = models.IntegerField()
    right_near = models.IntegerField()
    right_far = models.IntegerField()
    free_throw = models.IntegerField()

    def __str__(self):
        return self.name
