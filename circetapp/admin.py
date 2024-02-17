from django.contrib import admin
from .models import Question, Choice, Demande, Personnelles, Parcours
from django.http import HttpResponse
import csv
import datetime
from django.utils.encoding import smart_str
import codecs
from import_export import resources
from import_export.admin import ImportExportModelAdmin


def get_model_fields(model):
    return [field.name for field in model._meta.fields]


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f"{opts.model_name}_{date_str}.csv"
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    response.write(codecs.BOM_UTF8)

    writer = csv.writer(response, delimiter=';', quoting=csv.QUOTE_ALL, quotechar='"', escapechar='\\', lineterminator='\n')

    fields_to_exclude = ['id']
    fields = [field for field in opts.get_fields() if field.name not in fields_to_exclude and not field.many_to_many and not field.one_to_many]

    writer.writerow([field.verbose_name for field in fields])

    for obj in queryset:
        row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, str):
                value = value.strip()
            elif isinstance(value, datetime.datetime):
                value = value.strftime('%d %B %Y %H:%M')
            row.append(value)
    
        writer.writerow(row)

    return response

export_to_csv.short_description = 'Exporter vers CSV'


class ParcoursResource(resources.ModelResource):
    class Meta:
        model = Parcours

class QuestionResource(resources.ModelResource):
    class Meta:
        model = Question

class ChoiceResource(resources.ModelResource):
    class Meta:
        model = Choice

class DemandeResource(resources.ModelResource):
    class Meta:
        model = Demande

class PersonnellesResource(resources.ModelResource):
    class Meta:
        model = Personnelles

@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    resource_class = QuestionResource
    list_display = get_model_fields(Question)
    actions = [export_to_csv]

@admin.register(Choice)
class ChoiceAdmin(ImportExportModelAdmin):
    resource_class = ChoiceResource
    list_display = get_model_fields(Choice)
    actions = [export_to_csv]

@admin.register(Demande)
class DemandeAdmin(ImportExportModelAdmin):  # Nom de classe unique
    resource_class = DemandeResource
    list_display = get_model_fields(Demande)
    actions = [export_to_csv]

@admin.register(Personnelles)
class PersonnellesAdmin(ImportExportModelAdmin):  # Nom de classe unique
    resource_class = PersonnellesResource
    list_display = get_model_fields(Personnelles)
    actions = [export_to_csv]

@admin.register(Parcours)
class ParcoursAdmin(ImportExportModelAdmin):  # Nom de classe unique
    resource_class = ParcoursResource
    actions = [export_to_csv]  # Ceci permettra l'option d'exportation dans le menu déroulant
    list_display = get_model_fields(Parcours)
    
    search_fields = ['parcours_text', 'demande_nom', 'personnel__nom', 'personnel__prenom', 'date_time']  # vous pouvez ajouter d'autres champs pertinents ici

    list_filter = (
        ('date_time', admin.DateFieldListFilter),  # ceci ajoute un filtre de date dans la barre latérale
    )