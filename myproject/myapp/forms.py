from django import forms
from django.db import connection


def get_table_choices():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname='public' AND tablename NOT LIKE 'django_%' AND tablename NOT LIKE 'auth_%'
        """)
        tables = cursor.fetchall()
    return [(table[0], table[0]) for table in tables]


class ActionChoiceForm(forms.Form):
    ACTION_CHOICES = [
        ('create', 'Создать новую таблицу'),
        ('add', 'Добавить данные в существующую таблицу'),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, required=False)  # Сделали поле необязательным

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['table'].choices = get_table_choices()

    table = forms.ChoiceField(choices=[], required=False)
    file = forms.FileField()

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        table = cleaned_data.get('table')

        if action == 'add' and not table:
            self.add_error('table', 'Это поле обязательно для добавления данных в существующую таблицу.')
        elif not action:
            action = 'add'  # Добавили проверку, если action не задано
