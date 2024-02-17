from django import forms
from .models import Parcours, Personnelles
from django.contrib.auth.forms import SetPasswordForm
from .models import Demande, Question, Choice
from django.contrib.auth.forms import PasswordChangeForm



class ParcoursForm(forms.ModelForm):
    class Meta:
        model = Parcours
        fields = ['parcours_text', 'demande_nom']

    def clean_parcours_text(self):
        data = self.cleaned_data['parcours_text']
        # Vous pouvez ajouter ici des vérifications supplémentaires si nécessaire
        return data  # Assurez-vous que les sauts de ligne sont conservés

class SignUpForm(forms.ModelForm):
    class Meta:
        model = Personnelles
        fields = ['nom', 'prenom', 'email', 'photo', 'mot_de_passe']
        widgets = {
            'mot_de_passe': forms.PasswordInput(),
        }        


class CustomPasswordChangeForm(forms.Form):
    old_password = forms.CharField(label='Ancien mot de passe', widget=forms.PasswordInput)
    new_password = forms.CharField(label='Nouveau mot de passe', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirmer le mot de passe', widget=forms.PasswordInput)





class DemandeForm(forms.ModelForm):
    class Meta:
        model = Demande
        fields = ['nom']

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['question_text']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'next_question', 'demande_suivante', 'is_text_field']