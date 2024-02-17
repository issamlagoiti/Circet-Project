
from django.shortcuts import render, redirect, get_object_or_404
from .models import Demande, Question, Choice, Personnelles, Parcours
from django.http import HttpResponse
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .forms import ParcoursForm, SignUpForm
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.urls import reverse
from functools import wraps
from django.contrib.auth import update_session_auth_hash
from .forms import PasswordChangeForm
from .forms import CustomPasswordChangeForm
from .forms import DemandeForm, QuestionForm, ChoiceForm
from django.db.models import Count
import datetime


def demande_details_view(request): 
    if 'user_email' not in request.session:
        # redirect to login page if not logged in
        return redirect('sign_in')
    user_email = request.session['user_email']
    demandes = Demande.objects.all()
    personnel = Personnelles.objects.get(email=user_email)
    if request.method == 'POST':
        selected_demande_id = request.POST.get('demande')
        selected_demande = Demande.objects.get(id=selected_demande_id)
        first_question = selected_demande.question_set.first()
        

        if first_question:
            return redirect('question_details', question_id=first_question.id)
        else:
            return redirect('fin_questionnaire')

    context = {
        'demandes': demandes,
        'personnel': personnel,
    }

    return render(request, 'demande_details.html', context)


def question_details_view(request, question_id):
    if 'user_email' not in request.session:
        # redirect to login page if not logged in
        return redirect('sign_in')
    user_email = request.session['user_email']
    question = Question.objects.get(id=question_id)
    choices = question.choice_set.all()
    demande = question.demande
    personnel = Personnelles.objects.get(email=user_email)

    if request.method == 'POST':
        selected_choice_id = request.POST.get('choice')
        selected_choice = Choice.objects.get(id=selected_choice_id)
        next_question = selected_choice.next_question
        demande_suivante = selected_choice.demande_suivante

        if selected_choice.is_text_field:
            selected_choice_text = request.POST.get('choice_text')
        else:
            selected_choice_text = selected_choice.choice_text

        # Store the demande_id, question_id, and choice_text in the session
        request.session.setdefault('parcours', []).append((demande.id, question.id, selected_choice_text))
        request.session.modified = True

        if next_question:
            return redirect('question_details', question_id=next_question.id)
        elif demande_suivante:
            first_question = demande_suivante.question_set.first()
            return redirect('question_details', question_id=first_question.id)
        else:
            return redirect('fin_questionnaire')

    context = {
        'question': question,
        'choices': choices,
        'demande': demande,
        'personnel': personnel,
    }

    return render(request, 'question_details.html', context)

def fin_questionnaire_view(request):
    if 'user_email' not in request.session:
        # redirect to login page if not logged in
        return redirect('sign_in')
    user_email = request.session['user_email']
    derniere_demande_text_list = []  # Liste pour stocker le texte de la dernière demande
    last_demande_id = None

    # Trouvez l'ID de la dernière demande
    for demande_id, question_id, choice_text in reversed(request.session.get('parcours', [])):
        last_demande_id = demande_id
        break  # quittez la boucle dès que vous trouvez la dernière demande

    # Remplissez la liste de texte de la dernière demande
    demande_nom = ''  # Initialisez le nom de la demande
    for demande_id, question_id, choice_text in request.session.get('parcours', []):
        if demande_id == last_demande_id:
            demande = Demande.objects.get(id=demande_id)
            question = Question.objects.get(id=question_id)

            # Si le nom de la demande n'a pas encore été ajouté, ajoutez-le maintenant
            if demande.nom != demande_nom:
                derniere_demande_text_list.append(f"Demande: {demande.nom}")
                demande_nom = demande.nom  # Mettez à jour le nom de la demande

            # Convertir les informations de parcours en texte
            derniere_demande_text_list.append(
                f"{question.question_text} {choice_text}"
                #f"Question: {question.question_text}, Choix: {choice_text}"
            )

    # Joindre le texte du parcours en une seule chaîne
    parcours_text = "\n".join(derniere_demande_text_list)

    # Obtenez l'objet Personnelles associé à l'email de l'utilisateur
    personnel = Personnelles.objects.get(email=user_email)

    # Obtenez le nom de la dernière demande traitée
    demande_nom = Demande.objects.get(id=last_demande_id).nom if last_demande_id is not None else ''
   # print(f'demande_nom: {demande_nom}')  # Ajoutez cette ligne pour déboguer

    del request.session['parcours']  # Supprimez le parcours de la session
    form = ParcoursForm(initial={'parcours_text': parcours_text, 'demande_nom': demande_nom})
    context = {
        'parcours_text': parcours_text,
        'form': form,
        'demande_nom': demande_nom,  # Assurez-vous que cela est inclus
        'personnel': personnel
    }

    return render(request, 'fin_questionnaire.html', context)


@csrf_exempt
def enregistrer_parcours_view(request):
    if request.method == 'POST':

        form = ParcoursForm(request.POST)
        if form.is_valid():
            parcours_text = form.cleaned_data['parcours_text']
            demande_nom = form.cleaned_data['demande_nom']
            user_email = request.session.get('user_email')
            personnel = Personnelles.objects.get(email=user_email)

            Parcours.objects.create(
                parcours_text=parcours_text,
                demande_nom=demande_nom,
                personnel=personnel,
                date_time=timezone.now()
            )
            
            # Ajoutez un message de succès
            messages.success(request, 'Parcours enregistré avec succès')
            
            # Redirigez vers la page fin_questionnaire_view
            return redirect('demande_details')
        else:
            # Le formulaire n'est pas valide ou les champ contient des des caracteristique qui n'est pas defini sur la base de donne
            messages.error(request, 'Erreur lors de l\'enregistrement du parcours')
            return redirect('demande_details')
    else:
        # Ce n'est pas une requête POST 
        messages.error(request, 'Méthode non autorisée')
        return redirect('demande_details')


def sign_in(request):
    error = None
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['mot_de_passe']
        try:
            user = Personnelles.objects.get(email=email)
        except Personnelles.DoesNotExist:
            user = None

        if user is not None and user.mot_de_passe == password:
            request.session['user_email'] = user.email
            return redirect('demande_details')
        else:
            error = "email ou mot de passe invalide."
    return render(request, 'sign_in.html', {'error': error})


def signout(request):
    if 'user_email' in request.session:
        del request.session['user_email']

    logout(request)
    
    return redirect('sign_in')


def sign_up_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            # le formulaire est valide, sauvegardez l'objet et redirigez vert  sign_in pour ce conneter 
            form.save()
            return redirect('sign_in')
    else:
        form = SignUpForm()

    return render(request, 'sign_up.html', {'form': form})



@csrf_exempt
def parcours_view(request):
        # Vérifier si l'utilisateur est connecté
    if 'user_email' not in request.session:
        return redirect('sign_in')

    
    user_email = request.session.get('user_email')
    personnel = Personnelles.objects.get(email=user_email)
    parcours_list = Parcours.objects.filter(personnel=personnel)

    if request.method == 'POST':
        if 'delete' in request.POST:
            parcours_id = request.POST.get('parcours_id')
            parcours = get_object_or_404(Parcours, id=parcours_id)
            parcours.delete()
            return HttpResponseRedirect(reverse('parcours_view'))

        elif 'edit' in request.POST:
            parcours_id = request.POST.get('parcours_id')
            parcours = get_object_or_404(Parcours, id=parcours_id)
            form = ParcoursForm(instance=parcours)
            return render(request, 'edit_parcours.html', {'form': form, 'parcours': parcours, 'personnel': personnel})

        elif 'update' in request.POST:
            parcours_id = request.POST.get('parcours_id')
            parcours = get_object_or_404(Parcours, id=parcours_id)
            form = ParcoursForm(request.POST, instance=parcours)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('parcours_view'))
        
    context = {
        'personnel': personnel,
    }

    return render(request, 'parcours.html', {'parcours_list': parcours_list, 'personnel': personnel})



def profile_view(request):
    if 'user_email' not in request.session:
        return redirect('sign_in')

    user_email = request.session['user_email']

    try:
        personnel = Personnelles.objects.get(email=user_email)
    except Personnelles.DoesNotExist:
        return redirect('sign_in')
    
    # Compter le nombre total de parcours
    total_parcours = Parcours.objects.filter(personnel=personnel).count()

   

    # Calculating parcours for today, this week and this month
    start_of_today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = start_of_today - datetime.timedelta(days=start_of_today.weekday())
    start_of_month = start_of_today.replace(day=1)

    parcours_today = Parcours.objects.filter(personnel=personnel, date_time__gte=start_of_today).count()
    parcours_this_week = Parcours.objects.filter(personnel=personnel, date_time__gte=start_of_week).count()
    parcours_this_month = Parcours.objects.filter(personnel=personnel, date_time__gte=start_of_month).count()

    today = timezone.now().date()
    parcours_per_month = []
    for i in range(30):  # loop over the last 30 days
        day = today - datetime.timedelta(days=i)
        count = Parcours.objects.filter(personnel=personnel, date_time__date=day).count()
        parcours_per_month.append((day, count))
    parcours_per_month.reverse()  # to have days in ascending order
    

    context = {
        'personnel': personnel,
        'total_parcours': total_parcours,
        'parcours_per_month': parcours_per_month,
        'parcours_today': parcours_today,
        'parcours_this_week': parcours_this_week,
        'parcours_this_month': parcours_this_month,
    }

    return render(request, 'profile.html', context)

def change_password_view(request):
    # Vérifier si l'utilisateur est connecté
    if 'user_email' not in request.session:
        return redirect('sign_in')

    user_email = request.session['user_email']

    # Obtenez l'objet Personnelles associé à l'e-mail de l'utilisateur
    try:
        personnel = Personnelles.objects.get(email=user_email)
    except Personnelles.DoesNotExist:
        return redirect('sign_in')

    # Si le formulaire est soumis
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.POST)

        # Vérifiez si le formulaire est valide
        if form.is_valid():
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            # Vérifiez si l'ancien mot de passe est correct
            if personnel.mot_de_passe != old_password:
                messages.error(request, 'L\'ancien mot de passe est incorrect.')
            # Vérifiez si les nouveaux mots de passe correspondent
            elif new_password != confirm_password:
                messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
            else:
                # Mettez à jour le mot de passe et redirigez l'utilisateur
                personnel.mot_de_passe = new_password  # Vous pouvez ajouter un hachage ici
                personnel.save()
                messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
                return redirect('profile_view')

    else:
        form = CustomPasswordChangeForm()
 
    return render(request, 'change_password.html', {'form': form, 'personnel': personnel})



def add_demande(request):
    if request.method == 'POST':
        form = DemandeForm(request.POST)
        question_form = QuestionForm(request.POST, prefix='question')
        choice_form = ChoiceForm(request.POST, prefix='choice')

        if form.is_valid() and question_form.is_valid() and choice_form.is_valid():
            demande = form.save()
            question = question_form.save(commit=False)
            question.demande = demande
            question.save()
            choice = choice_form.save(commit=False)
            choice.question = question
            choice.save()
            return redirect('success_page')
    else:
        form = DemandeForm()
        question_form = QuestionForm(prefix='question')
        choice_form = ChoiceForm(prefix='choice')
        
    return render(request, 'add_demande.html', {'form': form, 'question_form': question_form, 'choice_form': choice_form})



def calendrier(request):
    # Vérifier si l'utilisateur est connecté
    if 'user_email' not in request.session:
        return redirect('sign_in')

    user_email = request.session['user_email']


    # Obtenez l'objet Personnelles associé à l'email de l'utilisateur
    personnel = Personnelles.objects.get(email=user_email)

    context = {
        'personnel': personnel,
    }
    return render(request, 'calendrier.html', context)

def contacts(request):
    # Vérifier si l'utilisateur est connecté
    if 'user_email' not in request.session:
        return redirect('sign_in')

    user_email = request.session['user_email']


    # Obtenez l'objet Personnelles associé à l'email de l'utilisateur
    personnel = Personnelles.objects.get(email=user_email)

    context = {
        'personnel': personnel,
    }
    return render(request, 'contacts.html', context)



def search_demandes(request):
    query = request.GET.get('query', '')
    if query:
        demandes = Demande.objects.filter(nom__icontains=query)
    else:
        demandes = Demande.objects.all()

    return render(request, 'demande_details.html', {'demandes': demandes})