from django.db import models
from django.utils import timezone


class Demande(models.Model):
    nom = models.CharField(max_length=255)

    def __str__(self):
        return self.nom

class Question(models.Model):
    demande = models.ForeignKey(Demande, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=200)

    def __str__(self):
        return self.question_text



class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    next_question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='next_question', null=True, blank=True)
    demande_suivante = models.ForeignKey(Demande, on_delete=models.CASCADE, null=True, blank=True)
    is_text_field = models.BooleanField(default=False)  # Ajoutez ceci

    def __str__(self):
        return self.choice_text



class Personnelles(models.Model):
    email = models.EmailField(max_length=100, null=True, unique=True)
    nom = models.CharField(max_length=25, null=True)
    prenom = models.CharField(max_length=25, null=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)
    mot_de_passe = models.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Parcours(models.Model):
    personnel = models.ForeignKey(Personnelles, on_delete=models.CASCADE)  # La personne qui a effectué le parcours
    demande_nom = models.CharField(max_length=255)  # Le nom de la demande traitée
    parcours_text = models.TextField()  # Le texte décrivant le parcours
    date_time = models.DateTimeField(default=timezone.now)  # La date et l'heure du parcours

    def __str__(self):
        return f"{self.demande_nom} par {self.personnel.nom} {self.personnel.prenom} le {self.date_time}"