from django.shortcuts import render,redirect
from django.contrib.auth import login as auth_login,logout,authenticate
from .forms import UserForm,UserchangeForm,UserprofilechangeForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.utils.encoding import force_bytes, force_text
import requests,json
from django.core.mail import EmailMessage
from .models import *
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import views as auth_views
import datetime
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)






class MovieListView(ListView):
    model = movie
    template_name = 'index.html'
    context_object_name = 'movie'

class MovieDetailView(DetailView):
    model = movie
    template_name = 'Movie_page.html'
    context_object_name = 'movie'

#------------------------------------------------------------------------------------------------------------------------


def city(request):
    x=theatre.objects.all().values('city').distinct()

    cities_l=[];
    for i in range(len(x)):
        cities_l.append(x[i]['city'])
    context={'cities':cities_l}
    return render(request,"city.html",context)


def main_page(request,city):
    context={'city':city,}

    top_10=10
    movies_by_rating=movie.objects.order_by('-imdb_movie_rating')
    high_rated_movies=[]
    for i in range(top_10):
        try:
            high_rated_movies.append({'movie_id': movies_by_rating[i].id,'movie_rating':movies_by_rating[i].imdb_movie_rating,
                                 'movie_name': movies_by_rating[i].movie_name+' ('+movies_by_rating[i].movie_age_rating+')'})
        except:
            break
    context['high_rated_movies']=high_rated_movies


    top_5=5
    theatres_in_city=theatre.objects.filter(city=city).values('id')
    screens_in_city=[]
    for i in range(len(theatres_in_city)):
        screens_in_city+=screen.objects.filter(theatre_id=theatres_in_city[i]['id']).values('id')
    movies_in_city=[]
    tickets_in_city=[]
    for i in range(len(screens_in_city)):
        movies_in_city+=ticket_price_and_time.objects.filter(screen_id=screens_in_city[i]['id']).values('movie_id').distinct()
        tickets_in_city+=ticket_price_and_time.objects.filter(screen_id=screens_in_city[i]['id'])

    instant_booking={}
    for i in range(len(movies_in_city)):
        try:
            instant_booking[movie.objects.get(id=movies_in_city[i]['movie_id']).movie_name]=[]
            for j in range(len(tickets_in_city)):
                if (movies_in_city[i]['movie_id']==tickets_in_city[j].movie_id.id):
                    instant_booking[tickets_in_city[j].movie_id.movie_name].append({'ticket_id':tickets_in_city[j].id,'movie_show_time':(str(tickets_in_city[j].show_timings)+' '+str(tickets_in_city[j].date))})
        except:
            break

    context['instant_booking']=instant_booking

    in_city_movie_list=[]
    for i in range(len(movies_in_city)):
        in_city_movie_list.append({'movie_id': movie.objects.get(id=movies_in_city[i]['movie_id']).id,
                                   'movie_name': movie.objects.get(id=movies_in_city[i]['movie_id']).movie_name,
                                   'movie_poster': movie.objects.get(id=movies_in_city[i]['movie_id']).movie_poster_1,
                                   'movie_details': '('+movie.objects.get(
                                       id=movies_in_city[i]['movie_id']).movie_age_rating + ') ' + movie.objects.get(
                                       id=movies_in_city[i]['movie_id']).movie_genre,'movie_release_date':movie.objects.get(
                                       id=movies_in_city[i]['movie_id']).movie_release_date})


    context['in_city_movie_list']=in_city_movie_list


    new_releases = []
    movies_by_release_date = movie.objects.all().order_by('-movie_release_date')

    for i in range(top_5):
        try:
            for j in range(len(movies_in_city)):
                if movies_in_city[j]['movie_id']==movies_by_release_date[i].id:
                    new_releases.append({'movie_id': movies_by_release_date[i].id,
                                         'movie_poster': movies_by_release_date[i].movie_poster_2})
                    break
                else:
                    continue
        except:
            break
    context['new_releases']=new_releases

    top_3=3
    now_playing_in_city=[]
    #up_coming_in_city = []
    count_now_playing_in_city=0
    now_playing_by_release_date=movie.objects.filter(movie_release_date__lte=datetime.date.today()).order_by('movie_release_date')
    for i in range(len(movies_in_city)):
        try:
            if count_now_playing_in_city > top_3:
                break
            for j in range(len(now_playing_by_release_date)):

                if movies_in_city[i]['movie_id']==now_playing_by_release_date[j].id:
                    now_playing_in_city.append({'movie_id': now_playing_by_release_date[j].id,
                                   'movie_name': now_playing_by_release_date[j].movie_name,
                                   'movie_poster': now_playing_by_release_date[j].movie_poster_1,
                                   'movie_details': '('+now_playing_by_release_date[j].movie_age_rating + ') ' + now_playing_by_release_date[j].movie_genre})
                    count_now_playing_in_city+=1
                    break
        except:
            break
        context['now_playing_in_city']=now_playing_in_city


    up_coming_in_city = []
    count_up_coming_in_city = 0
    up_coming_by_release_date = movie.objects.filter(movie_release_date__gt=datetime.date.today()).order_by(
        '-movie_release_date')
    for i in range(len(movies_in_city)):
        try:
            if count_up_coming_in_city > top_3:
                break
            for j in range(len(up_coming_by_release_date)):

                if movies_in_city[i]['movie_id'] == up_coming_by_release_date[j].id:
                    up_coming_in_city.append({'movie_id': up_coming_by_release_date[j].id,
                                                'movie_name': up_coming_by_release_date[j].movie_name,
                                                'movie_poster': up_coming_by_release_date[j].movie_poster_1,
                                                'movie_details': '(' + up_coming_by_release_date[
                                                    j].movie_age_rating + ') ' + up_coming_by_release_date[
                                                                     j].movie_genre})
                    count_up_coming_in_city += 1
                    break
        except:
            break
        context['up_coming_in_city'] = up_coming_in_city

    top_6=6
    featured=[]
    count_featured=0
    for i in range(len(movies_in_city)):
        try:
            if count_featured > top_6:
                break
            for j in range(len(movies_by_rating)):
                if movies_in_city[i]['movie_id']==movies_by_rating[j].id:
                    featured.append({'movie_id': movies_by_rating[j].id,
                                   'movie_name': movies_by_rating[j].movie_name,
                                   'movie_poster': movies_by_rating[j].movie_poster_1,'movie_rating':movies_by_rating[j].imdb_movie_rating,
                                   'movie_details': '('+movies_by_rating[j].movie_age_rating + ') ' + movies_by_rating[j].movie_genre})
                    count_featured+=1
                    break
                else:
                    continue

        except:
            break

    context['featured']=featured

    if request.user.is_authenticated:
        return render(request, 'index.html',context)
    return render(request, 'index.html',context)

#------------------------------------------------------------------------------------------------------------------------

def about_page(request):
    return render(request, 'about.html')


def movies_events(request):
    return render(request, 'movies_events.html')

def contact(request):
    return render(request, 'contact.html')


def user_logout(request):
    logout(request)
    return redirect(reverse('main_page'))


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                auth_login(request, user)
                return redirect(reverse('home'))
            else:
                return HttpResponse("Your account was inactive.")
        else:
            messages.error(request, 'username or password is not correct')
            return render(request, 'login.html', {})
    else:
        return render(request, 'index.html', {})


def signup(request):
    registered=False
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        if user_form.is_valid()and user_form.cleaned_data['password'] == user_form.cleaned_data['confirm_password']:
            user = user_form.save(commit=False)
            user.is_active = False
            user.set_password(user.password)
            user.save()
            registered=True
            current_site = get_current_site(request)
            domain = current_site.domain
            print(domain)
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = user_form.cleaned_data.get('email')
            name = user_form.cleaned_data.get('username')
            password = user_form.cleaned_data.get('password')
            print(name)
            print(password)
            response = requests.get(
                "http://api.quickemailverification.com/v1/verify?email=" + to_email + "&apikey=15aef1e3ebf4f0e3357b6aab94bb77833e639fc261b2d32903e1895bd330")
            result = response.json()

            if (result['did_you_mean'] == '' and result['result'] == "valid"):

                mail_subject = 'Activate your blog account.'
                to_email = user_form.cleaned_data.get('email')
                email = EmailMessage(mail_subject, message, to=[to_email])
                email.send()
                return render(request, 'emailsent.html', {})

            else:
                try:
                    u = User.objects.get(username=name)
                    u.delete()
                except User.DoesNotExist:
                    return HttpResponse('The email given is invalid please check it ')
                except Exception as e:
                    return render(request, 'signup.html', {'user_form': user_form})
                return HttpResponse('The email given is invalid please check it ')
        elif user_form.data['password'] != user_form.data['confirm_password']:
            user_form.add_error('confirm_password', 'The passwords do not match')

    else:
        user_form = UserForm()
    return render(request, 'signup.html', {'user_form': user_form, 'registered': registered})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        auth_login(request,user)
        return HttpResponseRedirect(reverse('home'))

    else:
        return HttpResponse('Activation link is invalid!')

#------------------------------------------------------------------------------------------------------------------------


@csrf_exempt
class IndexView(DetailView):
    model = User
    template_name = 'LoginHome.html'


@login_required
def home(request):
    user = request.user
    context = {'user': user}
    return render(request, 'LoginHome.html', context=context)




@login_required
def viewprofile(request):
    args = {'user': request.user}
    return render(request, 'viewprofile.html', args)


@login_required
def edit_profile(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        user_form = UserchangeForm(request.POST, instance=request.user)
        user_profile_form=UserprofilechangeForm(request.POST,instance=profile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()

            messages.success(
                request, ('Your profile was successfully updated!'))

            return redirect('viewprofile')
        else:
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserchangeForm(instance=request.user)
        user_profile_form=UserprofilechangeForm(instance=profile)

    return render(request, 'edit_profile.html', {
        'user_form': user_form,'user_profile_form':user_profile_form

    })


@login_required
def change_password(request):

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Imp
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('viewprofile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {
        'form': form
    })

