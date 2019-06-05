from django.contrib import admin
from . import models
from django.forms import Textarea
from django.db.models.fields import TextField


admin.site.register(models.Skladniki)
admin.site.register(models.Skladniki_test)
admin.site.register(models.Przepis_komentarze)

class Przepis_skladnikINLINE(admin.TabularInline):
    model = models.Przepis_skladnik
    max_num = 30
    extra = 0
class Przepis_skladnikINLINETest(admin.TabularInline):
    model = models.Przepis_skladnik_test
    max_num = 30
    extra = 0

@admin.register(models.Przepis)
class PrzepisAdmin(admin.ModelAdmin):
    exclude = ('autor',)
    inlines = [Przepis_skladnikINLINE]
    list_per_page = 10
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }

    def save_model(self, request, obj, form, change):
        if not change:
            obj.autor = request.user
        obj.save()

@admin.register(models.Przepis_test)
class PrzepisAdminTest(admin.ModelAdmin):
    exclude = ('autor',)
    inlines = [Przepis_skladnikINLINETest]
    list_per_page = 10
    formfield_overrides = {
        TextField: {'widget': Textarea(attrs={'rows': 2, 'cols': 100})},
    }

    def save_model(self, request, obj, form, change):
        if not change:
            obj.autor = request.user
        obj.save()
