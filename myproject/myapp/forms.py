from django import forms


class TableChoiceForm(forms.Form):
    TABLE_CHOICES = [
        ('Person', 'Person'),
        ('Team', 'Team'),
    ]
    table = forms.ChoiceField(choices=TABLE_CHOICES)
    file = forms.FileField()
