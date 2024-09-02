from django.contrib import admin
from .models import CustomTable, TableAccess


class TableAccessInline(admin.TabularInline):
    model = TableAccess
    extra = 1


class CustomTableAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'created_by')
    inlines = [TableAccessInline]


admin.site.register(CustomTable, CustomTableAdmin)
admin.site.register(TableAccess)
