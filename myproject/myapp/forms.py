from django import forms
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import CustomTable, TableAccess


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields.pop('usable_password', None)


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
        ('add', 'Добавить данные в таблицу'),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, required=False)  # Сделали поле необязательным
    table = forms.ChoiceField(choices=[], required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Извлекаем пользователя из переданных аргументов
        super().__init__(*args, **kwargs)

        # Инициализируем поле `table` пустыми значениями
        self.fields['table'].choices = []

        if user:
            # Фильтруем таблицы в зависимости от прав доступа пользователя
            if user.is_superuser:
                # Суперпользователь видит все таблицы
                accessible_tables = CustomTable.objects.all()
                self.fields['table'].choices = [(table.name, table.name) for table in accessible_tables]
            else:
                # Обычные пользователи видят только таблицы, которые они создали
                accessible_tables = []
                for i in TableAccess.objects.filter(user=user):
                    accessible_tables.append(str(i).split()[-1])
                self.fields['table'].choices = [(table, table) for table in accessible_tables]

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        table = cleaned_data.get('table')

        if action == 'add' and not table:
            self.add_error('table', 'Это поле обязательно для добавления данных в существующую таблицу.')
        elif not action:
            action = 'add'  # Добавили проверку, если action не задано
