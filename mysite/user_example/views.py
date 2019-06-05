from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate, login
from django.views.generic import View
from .forms import UserForm, LoginForm, PasswordForm,BazaSkladnikowForm,PrzepisForm,SkladnikiFormSet,SkladnikiFormSet2,\
    SkladnikForm,SkladnikFormTest, PrzepisFormTest, SkladnikiFormSet2Test, WyswietlaniePrzepisuForm, \
    SkladnikiFormSet3Test, SkladnikiFormSet3, PrzepisFormPusty, PrzepisKomentarzForm
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from .models import Skladniki, Przepis, Skladniki_test, Przepis_test, Przepis_skladnik_test, Przepis_skladnik, \
    Przepis_komentarze
from django.views.generic.edit import CreateView
from . import views
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Q
from django.urls import reverse
import re, json



def listy_skladnikow(author):
    def createlist(grupa,author):
        lista = ["|"]
        obj = Skladniki.objects.filter(grupa=grupa).order_by('nazwa')
        if author != 'admin':
            obj = obj.exclude(~Q(author=author), aktywny=False)
        for to in obj:
            lista.append(str(to.id) + '|' + to.nazwa)
        return lista
    author = author
    for to in Skladniki.GRUPY:
        if to[0] == "Bakalie":
            lista_bakalie = createlist(to[0],author)
        elif to[0] == "Jaja":
            lista_jaja = createlist(to[0],author)
        elif to[0] == "Mieso":
            lista_mieso = createlist(to[0],author)
        elif to[0] == "Owoce":
            lista_owoce = createlist(to[0],author)
        elif to[0] == "Produkty cukiernicze":
            lista_p_cukiernicze = createlist(to[0],author)
        elif to[0] == "Produkty mleczne":
            lista_p_mleczne = createlist(to[0],author)
        elif to[0] == "Produkty zbozowe":
            lista_p_zbozowe = createlist(to[0],author)
        elif to[0] == "Przyprawy":
            lista_przyprawy = createlist(to[0],author)
        elif to[0] == "Ryby":
            lista_ryby = createlist(to[0],author)
        elif to[0] == "Suche nasiona straczkowe":
            lista_s_nasiona = createlist(to[0],author)
        elif to[0] == "Tluszcze":
            lista_tluszcze = createlist(to[0],author)
        elif to[0] == "Warzywa":
            lista_warzywa = createlist(to[0],author)
        elif to[0] == "Wedliny":
            lista_wedliny = createlist(to[0],author)

    arga = {
        'lista_Bakalie': lista_bakalie,
        'lista_Jaja': lista_jaja, 'lista_Mieso': lista_mieso,
        'lista_Owoce': lista_owoce, 'lista_p_cukiernicze': lista_p_cukiernicze,
        'lista_p_mleczne': lista_p_mleczne, 'lista_p_zbozowe': lista_p_zbozowe,
        'lista_Przyprawy': lista_przyprawy, 'lista_Ryby': lista_ryby,
        'lista_s_nasiona': lista_s_nasiona, 'lista_Tluszcze': lista_tluszcze,
        'lista_Warzywa': lista_warzywa, 'lista_Wedliny': lista_wedliny,
    }

    return arga

def index(request):
    return render(request, 'user_example/index.html')

def number(request):
    return render(request, 'user_example/number.html')

def like(request):
    test = get_object_or_404(Przepis_komentarze, id=request.POST.get('kom_id'))
    test.likes.add(request.user)
    print(test.likes.count())
    return HttpResponseRedirect(reverse('wyswietl_przepisy'))

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')
    else:
        form = UserCreationForm()

    context = {'form': form}
    return render(request, 'registration/register2.html', context)

class UserFormView(View):
    form_class = UserForm
    template_name = 'registration/register.html'

    # dispaly blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # process form data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # cleaned (normalized) data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                validate_password(password, user)
            except ValidationError as e:
                form.add_error('password', e)
                return render(request, self.template_name, {'form': form})

            user.set_password(password)
            user.save()

            # returns User objects if credentials are correct
            user = authenticate(username=username, password=password)

            if user is not None:

                if user.is_active:
                    login(request, user)
                    return render(request, 'user_example/index.html')
        return render(request, self.template_name, {'form': form})

def autorzy(request):
    return render(request, 'user_example/o_autorach.html')

def logout_view(request):
    logout(request)
    return redirect('index')

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
        return render(request, 'user_example/index.html')
    return render(request, 'registration/login.html', {'form': form})

def change_password(request):
    if request.method == 'POST':
        form = PasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Hasło zostało zmienione')
            return redirect('index')
        else:
            messages.error(request, 'to error')
    else:
        form = PasswordForm(request.user)
    return render(request, 'registration/change_password.html', {'form': form})

def email(request):
    subject = 'Dzieki za zarejestrowanie'
    message = 'oznacza swiat'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = ['plkulinarni@gmail.com']

    send_mail(subject, message, email_from, recipient_list)

    return redirect('index')

class UserFormView2(View):
    form_class = UserForm
    template_name = 'registration/register.html'

    # dispaly blank form
    def get(self, request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    # process form data
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            user = form.save(commit=False)
            user.is_active = False

            # cleaned (normalized) data
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            try:
                validate_password(password, user)
            except ValidationError as e:
                form.add_error('password', e)
                return render(request, self.template_name, {'form': form})

            user.set_password(password)
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Aktywacja konta'
            message = render_to_string('registration/active_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'registration/accept_email.html')
        return render(request, self.template_name, {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'registration/error_accept_email.html')

def accept(request):
    return render(request, 'registration/o_autorach.html')

class baza_skladnikow(View):
    form = BazaSkladnikowForm

    def get(self,request):
        return render(request, 'user_example/skladniki.html', {'form': self.form})

    def post(self,request):
        reguly = 'ężął'
        reguly_replacement = 'ezal'
        translator = str.maketrans(reguly, reguly_replacement)
        dane_request = request.POST.copy()
        dane_request['grupa'] = dane_request['grupa'].translate(translator)
        form = self.form(dane_request)
        if form.is_valid():
            grupa_wybor = form.cleaned_data['grupa']
            author = request.user
            nazwy = Skladniki.objects.filter(grupa=grupa_wybor).order_by('nazwa')
            if author.is_anonymous:
                nazwy = nazwy.exclude(aktywny=False)
            else:
                nazwy = nazwy.exclude(~Q(author=author), aktywny=False)
            ostatni = request.POST.get('grupa')
            args = {
                'form': self.form, 'nazwy': nazwy, 'ostatni': ostatni,
            }
            return render(request, 'user_example/skladniki.html', args)
        return render(request, 'user_example/skladniki.html', {'form': self.form})

class wyswietl_przepisy(View):
    form = WyswietlaniePrzepisuForm
    przepisy = Przepis.objects.all
    form_przepis = PrzepisFormTest
    form_przepis_glowny = PrzepisForm
    form_komentarze = PrzepisKomentarzForm
    def get(self,request):
        args = {
            'form': self.form, 'przepis': self.przepisy,
        }
        return render(request, 'user_example/wyswietl_przepisy.html', args)

    def post(self, request):
        action = request.POST.items()
        for item in action:
            if item[0] == 'przepis':
                obiekt = Przepis.objects.get(id=item[1])
                obiekt_skl = Przepis_skladnik.objects.filter(przepis_id=item[1])
                author = request.user
                dane_skladnik = []

                form_komentarze = self.form_komentarze(request.GET or None)
                obiekt_komentarze = Przepis_komentarze.objects.filter(przepis=item[1])
                if author.is_anonymous:
                    obiekt_komentarze = obiekt_komentarze.exclude(aktywny=False)
                else:
                    obiekt_komentarze = obiekt_komentarze.exclude(~Q(author=author), aktywny=False)
                dodatkowe_komentarze = obiekt_komentarze.exclude(podkomentarz=False)
                obiekt_komentarze = obiekt_komentarze.exclude(podkomentarz=True)
                czylike = []
                czydislike = []
                for a in obiekt_komentarze:
                    if (a.likes.filter(id=request.user.id).exists()):
                        czylike.append(a.id)
                    elif (a.dislikes.filter(id=request.user.id).exists()):
                        czydislike.append(a.id)
                for a in dodatkowe_komentarze:
                    if (a.likes.filter(id=request.user.id).exists()):
                        czylike.append(a.id)
                    elif (a.dislikes.filter(id=request.user.id).exists()):
                        czydislike.append(a.id)

                for a in obiekt_skl:
                    for b in Skladniki.objects.filter(id=a.skladnik_id):
                        if a.ilosc == None:
                            dane_skladnik.append(b.nazwa)
                        elif a.waga == None:
                            dane_skladnik.append(b.nazwa)
                        else:
                            dane_skladnik.append(str(a.ilosc) + " " + str(a.waga) + " " + b.nazwa)
                args = {
                    'przepis': obiekt, 'skladniki': dane_skladnik, 'author': author, 'komentarze': obiekt_komentarze,
                    'komentdodat': dodatkowe_komentarze, 'czylike': czylike, 'czydislike': czydislike
                }
                return render(request, 'user_example/wyswietl_przepis.html',args )
            elif item[0] == 'edit':
                obiekt = Przepis.objects.get(id=item[1])
                if obiekt.edycja == True:
                    obiekt2 = Przepis_test.objects.get(edycja=item[1])
                    lista_glowna, args = views.admin_panel.przepisy(request, obiekt2.id)
                else:
                    lista_glowna, args = views.moje_konto.przepisy(request,item[1],request.user)
                return render(request, 'user_example/testprzepisy.html', args)
            elif item[0] == 'acceptprzepis':
                views.moje_konto.post(self,request)
                obiekt2 = Przepis_test.objects.exclude(edycja=None)

                nowy = True
                for test in obiekt2:
                    if int(test.id) == int(item[1]):
                        nowy = False
                if nowy == True:
                    obiekt = Przepis.objects.get(id=item[1])
                    obiekt_skl = Przepis_skladnik.objects.filter(przepis_id=item[1])
                elif nowy == False:
                    obiekt2 = Przepis_test.objects.get(id=item[1])
                    obiekt = Przepis.objects.get(id=obiekt2.edycja)
                    obiekt_skl = Przepis_skladnik.objects.filter(przepis_id=obiekt2.edycja)
                author = request.user
                dane_skladnik = []
                for a in obiekt_skl:
                    for b in Skladniki.objects.filter(id=a.skladnik_id):
                        if a.ilosc == None:
                            dane_skladnik.append(b.nazwa)
                        elif a.waga == None:
                            dane_skladnik.append(b.nazwa)
                        else:
                            dane_skladnik.append(str(a.ilosc) + " " + str(a.waga) + " " + b.nazwa)
                return render(request, 'user_example/wyswietl_przepis.html',{'przepis': obiekt, 'skladniki': dane_skladnik, 'author': author}, )

        args = {
            'form': self.form, 'przepis': self.przepisy,
        }
        return render(request, 'user_example/wyswietl_przepisy.html', args)

class PrzepisCreate(CreateView):
    model = Przepis
    form_class = PrzepisForm
    def get_context_data(self, **kwargs):
        context = super(PrzepisCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            context['skladniki'] = SkladnikiFormSet(self.request.POST)
        else:
            context['skladniki'] = SkladnikiFormSet()
        return context

    def form_valid(self, form, skladniki):
        return render('user_example/przepis_list.html')

    def form_invalid(self, form, skladniki):
        return self.render_to_response(
            self.get_context_data(form=form, skladniki=skladniki)
        )

def ajaxkom(request):
    data = {
        'is_valid': False, }

    if request.is_ajax():
        kom_text = request.POST.get('koment')
        kom_author = str(request.user)
        kom_przepis = request.POST.get('przepis')
        obiekt = Przepis.objects.get(id=kom_przepis)
        obiekt_test = Przepis_komentarze.objects.filter(przepis=kom_przepis, aktywny=False, author=request.user)
        obiekt_test = obiekt_test.exclude(podkomentarz=True)
        print(obiekt_test)
        if(len(obiekt_test)<2):
            new_kom = Przepis_komentarze(przepis=obiekt,
                                         tresc=kom_text,
                                         author=request.user,
                                         aktywny=False
                                         )
            new_kom.save()
            data = {
                'is_valid': True,
                'koment': kom_text,
                'author': kom_author,
            }

    return JsonResponse(data)

def ajaxpodkom(request):
    data = {
        'is_valid': False, }

    if request.is_ajax():
        kom_text = request.POST.get('koment')
        kom_author = str(request.user)
        kom_przepis = request.POST.get('przepis')
        obiekt = Przepis.objects.get(id=kom_przepis)
        obiekt_test = Przepis_komentarze.objects.filter(przepis=kom_przepis, aktywny=False, author=request.user)
        obiekt_test = obiekt_test.exclude(podkomentarz=False)
        if (len(obiekt_test) < 2):
            new_kom = Przepis_komentarze(przepis=obiekt,
                                         tresc=kom_text,
                                         author=request.user,
                                         podkomentarz=True,
                                         idkomentarza=request.POST.get('komentarz'),
                                         aktywny=False
                                         )
            new_kom.save()
            data = {
                'is_valid': True,
                'koment': kom_text,
                'author': kom_author,
            }

    return JsonResponse(data)

def ajaxtest(request):
    def createlist(grupa):
        lista = ["|"]
        obj = Skladniki.objects.filter(grupa=grupa).order_by('nazwa')
        for to in obj:
            lista.append(str(to.id) + '|' + to.nazwa)
        return lista

    data = {
    'is_valid': False,}

    if request.is_ajax():
        nazwa_skl = request.POST.get('nazwa_skladnika')
        grupa_skl = request.POST.get('grupa_skladnika')
        obj_glowny = Skladniki.objects.filter(nazwa=nazwa_skl)
        obj_testowy = Skladniki_test.objects.filter(nazwa=nazwa_skl)
        reguly = 'ężął'
        reguly_replacement = 'ezal'
        translator = str.maketrans(reguly,reguly_replacement)
        grupa_skl = grupa_skl.translate(translator)

        if len(obj_glowny) == 0 and len(obj_testowy) == 0 and len(nazwa_skl) != 0:
            new_skl = Skladniki(nazwa=nazwa_skl,
                                grupa=grupa_skl,
                                aktywny=False,
                                author=request.user
                                )
            new_skl.save()
            data = {
                'is_valid': True,
                'lista': createlist(grupa_skl), }
            data.update(response=grupa_skl)
        elif len(obj_glowny) != 0:
            data.update(is_valid=False)
            data.update(response='Istnieje juz w glownej bazie skladnikow')
        elif len(obj_testowy) != 0:
            data.update(is_valid=False)
            data.update(response='Istnieje juz w testowej bazie skladnikow')
    print(data)

    return JsonResponse(data)

def ajaxkomlike(request):
    data = {
        'is_valid': False,
        'opcja': None,
        'liczbalike': None,
        'liczbadislike': None,}

    if request.is_ajax():
        kom_id = request.POST.get('id_koment')
        opcja = (request.POST.get('opcja'))
        test = get_object_or_404(Przepis_komentarze, id=kom_id)
        if opcja == 'like':
            if (test.likes.filter(id=request.user.id).exists()):
                test.likes.remove(request.user)
                data.update(opcja="removelike")
                data.update(liczbalike=test.likes.count())
            else:
                test.likes.add(request.user)
                data.update(opcja="addlike")
                data.update(liczbalike=test.likes.count())
                if (test.dislikes.filter(id=request.user.id).exists()):
                    test.dislikes.remove(request.user)
                    data.update(opcja="addlike_dislike")
                    data.update(liczbadislike=test.dislikes.count())
            data.update(is_valid=True)
        elif opcja == 'dislike':
            if (test.dislikes.filter(id=request.user.id).exists()):
                test.dislikes.remove(request.user)
                data.update(opcja="removedislike")
                data.update(liczbadislike=test.dislikes.count())
            else:
                test.dislikes.add(request.user)
                data.update(opcja="adddislike")
                data.update(liczbadislike=test.dislikes.count())
                if (test.likes.filter(id=request.user.id).exists()):
                    test.likes.remove(request.user)
                    data.update(opcja="adddislike_like")
                    data.update(liczbalike=test.likes.count())
            data.update(is_valid=True)
    return JsonResponse(data)

def dodaj_przepis(request):
    def createlist(grupa,author):
        lista = ["|"]
        obj = Skladniki.objects.filter(grupa=grupa).order_by('nazwa')
        obj = obj.exclude(~Q(author=author), aktywny=False)
        for to in obj:
            lista.append(str(to.id) + '|' + to.nazwa)
        return lista

    template_name = 'user_example/tworzenie_przepisow.html'
    form = BazaSkladnikowForm
    form_przepis = PrzepisForm
    if request.method == 'GET':
        przepis_form = form_przepis(request.GET or None)
        formset = SkladnikiFormSet2(queryset=Przepis.objects.none())
        form2 = form(request.GET or None)
    elif request.method == 'POST':
        przepis_form = form_przepis(request.POST,request.FILES)
        formset = SkladnikiFormSet2(request.POST)
        form2 = form(request.POST)
        print(request.POST)
        if przepis_form.is_valid() and formset.is_valid():
            przepis2 = przepis_form.save(commit=False)
            przepis2.author = request.user
            przep = przepis_form.save()
            for form in formset:
                # so that `book` instance can be attached.
                skladniki_form = form.save(commit=False)
                skladniki_form.przepis = przep
                skladniki_form.save()
            return redirect('wyswietl_przepisy')
    author = request.user
    for to in Skladniki.GRUPY:
        if to[0] == "Bakalie":
            lista_bakalie = createlist(to[0],author)
        elif to[0] == "Jaja":
            lista_jaja = createlist(to[0],author)
        elif to[0] == "Mieso":
            lista_mieso = createlist(to[0],author)
        elif to[0] == "Owoce":
            lista_owoce = createlist(to[0],author)
        elif to[0] == "Produkty cukiernicze":
            lista_p_cukiernicze = createlist(to[0],author)
        elif to[0] == "Produkty mleczne":
            lista_p_mleczne = createlist(to[0],author)
        elif to[0] == "Produkty zbozowe":
            lista_p_zbozowe = createlist(to[0],author)
        elif to[0] == "Przyprawy":
            lista_przyprawy = createlist(to[0],author)
        elif to[0] == "Ryby":
            lista_ryby = createlist(to[0],author)
        elif to[0] == "Suche nasiona straczkowe":
            lista_s_nasiona = createlist(to[0],author)
        elif to[0] == "Tluszcze":
            lista_tluszcze = createlist(to[0],author)
        elif to[0] == "Warzywa":
            lista_warzywa = createlist(to[0],author)
        elif to[0] == "Wedliny":
            lista_wedliny = createlist(to[0],author)

    return render(request, template_name, {
        'przepis_form': przepis_form,
        'form': form,
        'form2': form2,
        'formset': formset,
        'lista_Bakalie': lista_bakalie,
        'lista_Jaja': lista_jaja,
        'lista_Mieso': lista_mieso,
        'lista_Owoce': lista_owoce,
        'lista_p_cukiernicze': lista_p_cukiernicze,
        'lista_p_mleczne': lista_p_mleczne,
        'lista_p_zbozowe': lista_p_zbozowe,
        'lista_Przyprawy': lista_przyprawy,
        'lista_Ryby': lista_ryby,
        'lista_s_nasiona': lista_s_nasiona,
        'lista_Tluszcze': lista_tluszcze,
        'lista_Warzywa': lista_warzywa,
        'lista_Wedliny': lista_wedliny,
    })

def dodaj_przepis_test(request):
    def createlist(grupa):
        lista = ["|"]
        obj = Skladniki.objects.filter(grupa=grupa).order_by('nazwa')
        obj = obj.exclude(~Q(author=author), aktywny=False)
        for to in obj:
            lista.append(str(to.id) + '|' + to.nazwa)
        return lista

    template_name = 'user_example/tworzenie_przepisow.html'
    form = BazaSkladnikowForm
    form_przepis = PrzepisFormTest
    form_przepis_glowny = PrzepisForm
    if request.method == 'GET':
        przepis_form = form_przepis(request.GET or None)
        przepis_form_glowny = form_przepis_glowny(request.GET or None)
        formset = SkladnikiFormSet2Test(queryset=Przepis.objects.none())
        form2 = form(request.GET or None)
    elif request.method == 'POST':
        przepis_form = form_przepis(request.POST, request.FILES)
        przepis_form_glowny = form_przepis_glowny(request.POST, request.FILES)
        formset = SkladnikiFormSet2Test(request.POST)
        form2 = form(request.POST)
        if przepis_form.is_valid() and formset.is_valid() and przepis_form_glowny.is_valid():
            przepis2 = przepis_form.save(commit=False)
            przepis2.author = request.user
            przep = przepis_form.save()
            for form in formset:
                # so that `book` instance can be attached.
                skladniki_form = form.save(commit=False)
                skladniki_form.przepis = przep
                skladniki_form.save()
            return redirect('wyswietl_przepisy')
    author = request.user
    for to in Skladniki.GRUPY:
        if to[0] == "Bakalie":
            lista_bakalie = createlist(to[0],author)
        elif to[0] == "Jaja":
            lista_jaja = createlist(to[0],author)
        elif to[0] == "Mieso":
            lista_mieso = createlist(to[0],author)
        elif to[0] == "Owoce":
            lista_owoce = createlist(to[0],author)
        elif to[0] == "Produkty cukiernicze":
            lista_p_cukiernicze = createlist(to[0],author)
        elif to[0] == "Produkty mleczne":
            lista_p_mleczne = createlist(to[0],author)
        elif to[0] == "Produkty zbozowe":
            lista_p_zbozowe = createlist(to[0],author)
        elif to[0] == "Przyprawy":
            lista_przyprawy = createlist(to[0],author)
        elif to[0] == "Ryby":
            lista_ryby = createlist(to[0],author)
        elif to[0] == "Suche nasiona straczkowe":
            lista_s_nasiona = createlist(to[0],author)
        elif to[0] == "Tluszcze":
            lista_tluszcze = createlist(to[0],author)
        elif to[0] == "Warzywa":
            lista_warzywa = createlist(to[0],author)
        elif to[0] == "Wedliny":
            lista_wedliny = createlist(to[0],author)

    return render(request, template_name, {
        'przepis_form': przepis_form,
        'przepis_form_test': przepis_form_glowny,
        'form': form,
        'form2': form2,
        'formset': formset,
        'lista_Bakalie': lista_bakalie,
        'lista_Jaja': lista_jaja,
        'lista_Mieso': lista_mieso,
        'lista_Owoce': lista_owoce,
        'lista_p_cukiernicze': lista_p_cukiernicze,
        'lista_p_mleczne': lista_p_mleczne,
        'lista_p_zbozowe': lista_p_zbozowe,
        'lista_Przyprawy': lista_przyprawy,
        'lista_Ryby': lista_ryby,
        'lista_s_nasiona': lista_s_nasiona,
        'lista_Tluszcze': lista_tluszcze,
        'lista_Warzywa': lista_warzywa,
        'lista_Wedliny': lista_wedliny,
    })

class dodaj_skladnik(View):
    template_name = 'user_example/dodawanie_skladnikow.html'
    form = SkladnikForm

    def get(self, request):
        skladnik_form = self.form(request.GET or None)
        return render(request, self.template_name, {'form': skladnik_form})

    def post(self, request):
        skladnik_form = self.form(request.POST,request.FILES)

        if skladnik_form.is_valid():
            skladniki_form = skladnik_form.save(commit=False)
            skladniki_form.author = request.user
            skladniki_form.save()

            return render(request, 'user_example/dodawanie_skladnikow2.html')

        return render(request, self.template_name, {'form': skladnik_form})

class dodaj_skladnik_test(View):
    template_name = 'user_example/dodawanie_skladnikow.html'
    form = SkladnikFormTest
    form2 = SkladnikForm

    def get(self, request):
        skladnik_form = self.form2(request.GET or None)
        skladnik_test = self.form(request.GET or None)
        return render(request, self.template_name, {'form': skladnik_form, 'test': skladnik_test})

    def post(self, request):
        skladnik_form = self.form2(request.POST,request.FILES)
        skladnik_test = self.form(request.POST,request.FILES)

        if ((skladnik_form.is_valid()) and (skladnik_test.is_valid())):
            skladniki_form = skladnik_form.save(commit=False)
            skladniki_test = skladnik_test.save(commit=False)
            skladniki_test.nazwa = skladniki_form.nazwa
            skladniki_test.opis = skladniki_form.opis
            skladniki_test.zastosowanie = skladniki_form.zastosowanie
            skladniki_test.grupa = skladniki_form.grupa
            skladniki_test.data = skladniki_form.data
            skladniki_test.obraz = skladniki_form.obraz

            skladniki_form.author = request.user

            skladniki_test.author = skladniki_form.author
            skladniki_test.save()
            return render(request, 'user_example/dodawanie_skladnikow2.html')

        return render(request, self.template_name, {'form': skladnik_form, 'form2': skladnik_test})

class admin_panel(View):
    def przepisy(self, numer, author_skladnik):
        formset = SkladnikiFormSet2Test(queryset=Przepis.objects.none())
        obiekt = Przepis_test.objects.get(id=numer)
        obiekt2 = Przepis_test.objects.all()
        forma = PrzepisFormTest(instance=obiekt)
        obiekt3 = Przepis_skladnik_test.objects.filter(przepis_id=numer)
        form2 = BazaSkladnikowForm(None)
        lista_glowna = []

        fala = SkladnikiFormSet3Test(queryset=obiekt3)

        for a in obiekt3:
            for b in Skladniki.objects.filter(id=a.skladnik_id):
                if a.ilosc == None and a.waga == None:
                    lista_glowna.append(b.grupa + '|' + b.nazwa + '|' + "None" + '|' + "None")
                elif a.ilosc == None:
                        lista_glowna.append(b.grupa + '|' + b.nazwa + '|' + "None" + '|' + a.waga)
                elif a.waga == None:
                    lista_glowna.append(b.grupa + '|' + b.nazwa + '|' + str(a.ilosc) + '|' + "None")
                else:
                    lista_glowna.append(b.grupa + '|' + b.nazwa + '|' + str(a.ilosc) + '|' + a.waga)

        arga = {
            'przepis_form': forma,
            'formset': fala,
            'formseta': formset,
            'dane': obiekt,
            'form2': form2,
            'lista_glowna': lista_glowna,
        }
        if str(author_skladnik) == 'admin':
            arga.update(views.listy_skladnikow('admin'))
        else:
            arga.update(views.listy_skladnikow(author_skladnik))
        return lista_glowna, arga

    template_name = 'user_example/admin_accept.html'
    form = SkladnikForm
    form2 = SkladnikFormTest
    form_przepis = PrzepisFormTest
    form_przepis_glowny = PrzepisForm
    formbaza = BazaSkladnikowForm

    def get(self, request):
        skladniki = Skladniki_test.objects.all()
        przepisy = Przepis_test.objects.filter(edycja=None)
        przepisy_edycja = Przepis_test.objects.exclude(edycja=None)
        formset = SkladnikiFormSet2Test(queryset=Przepis.objects.none())
        return render(request, self.template_name, {'formset': formset,
                                                    'dane': skladniki,
                                                    'przepisy': przepisy,
                                                    'przepisy_edycja': przepisy_edycja,
                                                    })

    def post(self, request):
        skladnik = self.form(request.POST, request.FILES)
        skladnik_test = self.form2(request.POST, request.FILES)
        przepis_form = self.form_przepis(request.POST, request.FILES)
        przepis_form_glowny = self.form_przepis_glowny(request.POST, request.FILES)
        formsetform = SkladnikiFormSet3Test(request.POST)
        action = request.POST.items()

        for a in action:
            if a[0] == 'nazwa':
                break
            elif a[0] != 'csrfmiddlewaretoken':
                action = a
                if 'add' in action[0]:
                    if action[0] == 'add1':
                        obiekt = Skladniki_test.objects.get(id=action[1])
                        b = Skladniki(nazwa=obiekt.nazwa,
                                      opis=obiekt.opis,
                                      zastosowanie=obiekt.zastosowanie,
                                      grupa=obiekt.grupa,
                                      data=obiekt.data,
                                      obraz=obiekt.obraz,
                                      author=obiekt.author
                                      )
                        b.save()
                        Skladniki_test.objects.get(id=action[1]).delete()
                        return redirect('admin_panel')
                    elif action[0] == 'add2':
                        obiekt = Przepis_test.objects.get(id=action[1])
                        b = Przepis(nazwa=obiekt.nazwa,
                                    opis=obiekt.opis,
                                    obraz=obiekt.obraz,
                                    data=obiekt.data,
                                    author=obiekt.author
                                    )
                        b.save()
                        obiekt3 = Przepis_skladnik_test.objects.filter(przepis_id=action[1])
                        for test in obiekt3:
                            b_skladnik = Przepis_skladnik(przepis=b,
                                                          skladnik=test.skladnik,
                                                          ilosc=test.ilosc,
                                                          waga=test.waga,
                                                          )
                            b_skladnik.save()
                        Przepis_test.objects.get(id=action[1]).delete()
                        Przepis_skladnik_test.objects.filter(przepis_id=action[1]).delete()
                        return redirect('admin_panel')
                    elif action[0] == 'add3':
                        obiekt = Przepis_test.objects.get(id=action[1])
                        obiekt_glowny = Przepis.objects.get(id=obiekt.edycja)
                        obiekt_glowny.nazwa = obiekt.nazwa
                        obiekt_glowny.opis = obiekt.opis
                        obiekt_glowny.obraz = obiekt.obraz
                        obiekt_glowny.data = obiekt.data
                        obiekt_glowny.author = obiekt.author
                        obiekt_glowny.edycja = False
                        obiekt_glowny.save()

                        obiekt_skladniki = Przepis_skladnik_test.objects.filter(przepis_id=action[1])
                        Przepis_skladnik.objects.filter(przepis_id=obiekt.edycja).delete()
                        for test in obiekt_skladniki:
                            skladnik_obiekt = Przepis_skladnik(przepis=obiekt_glowny,
                                                               skladnik=test.skladnik,
                                                               ilosc=test.ilosc,
                                                               waga=test.waga
                                                               )
                            skladnik_obiekt.save()
                        Przepis_test.objects.get(id=action[1]).delete()
                        Przepis_skladnik_test.objects.filter(przepis_id=action[1]).delete()
                        return redirect('admin_panel')
                elif 'delete' in action[0]:
                    if action[0] == 'delete1':
                        obiekt = Skladniki_test.objects.get(id=action[1])
                        obiekt.obraz.delete()
                        Skladniki_test.objects.get(id=action[1]).delete()
                        return redirect('admin_panel')
                    elif action[0] == 'delete2':
                        obiekt = Przepis_test.objects.get(id=action[1])
                        obiekt.obraz.delete()
                        Przepis_skladnik_test.objects.filter(przepis_id=action[1]).delete()
                        Przepis_test.objects.get(id=action[1]).delete()
                        return redirect('admin_panel')
                    elif action[0] == 'delete3':
                        obiekt = Przepis_test.objects.get(id=action[1])
                        obiekt_glowny = Przepis.objects.get(id=obiekt.edycja)
                        obiekt_glowny.edycja = False
                        obiekt_glowny.save()
                        Przepis_test.objects.get(id=action[1]).delete()
                        Przepis_skladnik_test.objects.filter(przepis_id=action[1]).delete()
                        return redirect('admin_panel')
                elif 'edit' in action[0]:
                    if action[0] == 'edit1':
                        obiekt = Skladniki_test.objects.get(id=action[1])
                        forma = SkladnikFormTest(instance=obiekt)
                        return render(request, 'user_example/testadmin.html', {'form': forma, 'dane': obiekt})
                    elif action[0] == 'edit2':
                        lista_glowna, args = self.przepisy(action[1], request.user)
                        return render(request, 'user_example/testprzepisy.html', args)
                    elif action[0] == 'edit3':
                        lista_glowna, args = self.przepisy(action[1], request.user)
                        return render(request, 'user_example/testprzepisy.html', args)

        action = request.POST.items()
        for b in action:
            if b[0] == 'accept':
                dane_glowne = Skladniki_test.objects.get(id=b[1])
                if skladnik.is_valid():
                    obiekt = Skladniki_test.objects.get(id=b[1])
                    nowe_dane = skladnik.save(commit=False)

                    if obiekt.nazwa == nowe_dane.nazwa:
                        if nowe_dane.obraz != None:
                            obiekt.obraz = nowe_dane.obraz
                        obiekt.nazwa = nowe_dane.nazwa
                        obiekt.opis = nowe_dane.opis
                        obiekt.zastosowanie = nowe_dane.zastosowanie
                        obiekt.grupa = nowe_dane.grupa
                        obiekt.save()
                        return redirect('admin_panel')

                    if skladnik_test.is_valid():
                        if nowe_dane.obraz != None:
                            obiekt.obraz = nowe_dane.obraz
                        obiekt.nazwa = nowe_dane.nazwa
                        obiekt.opis = nowe_dane.opis
                        obiekt.zastosowanie = nowe_dane.zastosowanie
                        obiekt.grupa = nowe_dane.grupa
                        obiekt.save()
                        return redirect('admin_panel')
                return render(request, 'user_example/testadmin2.html', {'form': skladnik, 'form2': skladnik_test, 'dane': dane_glowne})
            elif b[0] == 'acceptprzepis':
                numer = b[1]
                form2 = BazaSkladnikowForm(request.POST)
                formsecik = SkladnikiFormSet2Test(queryset=Przepis.objects.none())
                wzor = 'form-\d*-skladnik'
                lista_glowna = []
                licznik = 0
                dane_glowne = Przepis_test.objects.get(id=numer)
                obiekt2 = Przepis_test.objects.exclude(edycja=None)
                nowy = True
                for test in obiekt2:
                    if int(test.id) == int(numer):
                        nowy = False

                if nowy == True:
                    if przepis_form_glowny.is_valid() and formsetform.is_valid():
                        nowe_dane = przepis_form_glowny.save(commit=False)
                        obiekt = Przepis_test.objects.get(id=numer)

                        if nowe_dane.nazwa == obiekt.nazwa:
                            obiekt.opis = nowe_dane.opis
                            if nowe_dane.obraz != None:
                                obiekt.obraz = nowe_dane.obraz
                            Przepis_skladnik_test.objects.filter(przepis_id=numer).delete()
                            obiekt.save()
                            for form in formsetform:
                                skladniki_form = form.save(commit=False)
                                skladniki_form.przepis = obiekt
                                skladniki_form.save()
                            return redirect('admin_panel')

                        if przepis_form.is_valid():
                            obiekt.opis = nowe_dane.opis
                            if nowe_dane.obraz != None:
                                obiekt.obraz = nowe_dane.obraz
                            Przepis_skladnik_test.objects.filter(przepis_id=numer).delete()
                            obiekt.nazwa = nowe_dane.nazwa
                            obiekt.save()
                            for form in formsetform:
                                skladniki_form = form.save(commit=False)
                                skladniki_form.przepis = obiekt
                                skladniki_form.save()
                            return redirect('admin_panel')
                else:
                    test = Przepis.objects.get(id=dane_glowne.edycja)
                    pustyform = PrzepisFormPusty(request.POST, request.FILES)
                    pustyform_dane = pustyform.save(commit=False)

                    if (request.POST[
                            'nazwa'] == test.nazwa or przepis_form_glowny.is_valid()) and formsetform.is_valid():
                        if request.POST['nazwa'] == test.nazwa:
                            pustyform_dane.nazwa = test.nazwa
                            nowe_dane = pustyform_dane
                        else:
                            nowe_dane = przepis_form_glowny.save(commit=False)

                        obiekt = Przepis_test.objects.get(id=numer)

                        if nowe_dane.nazwa == obiekt.nazwa:
                            obiekt.opis = nowe_dane.opis
                            if nowe_dane.obraz != None:
                                obiekt.obraz = nowe_dane.obraz
                            Przepis_skladnik_test.objects.filter(przepis_id=numer).delete()
                            obiekt.save()
                            for form in formsetform:
                                skladniki_form = form.save(commit=False)
                                skladniki_form.przepis = obiekt
                                skladniki_form.save()
                            return redirect('admin_panel')

                        if przepis_form.is_valid():
                            obiekt.opis = nowe_dane.opis
                            if nowe_dane.obraz != None:
                                obiekt.obraz = nowe_dane.obraz
                            Przepis_skladnik_test.objects.filter(przepis_id=numer).delete()
                            obiekt.nazwa = nowe_dane.nazwa
                            obiekt.save()
                            for form in formsetform:
                                skladniki_form = form.save(commit=False)
                                skladniki_form.przepis = obiekt
                                skladniki_form.save()
                            return redirect('admin_panel')

                for skladniki_post in request.POST:
                    if re.findall(wzor, skladniki_post):
                        skladnikid = "form-" + str(licznik) + "-skladnik"
                        iloscid = "form-" + str(licznik) + "-ilosc"
                        wagaid = "form-" + str(licznik) + "-waga"
                        for bb in Skladniki.objects.filter(id=request.POST[skladnikid]):
                            if wagaid in request.POST and iloscid in request.POST:
                                lista_glowna.append(
                                    bb.grupa + '|' + bb.nazwa + '|' + str(request.POST[iloscid]) + '|' + request.POST[
                                        wagaid])
                            elif iloscid in request.POST:
                                lista_glowna.append(
                                    bb.grupa + '|' + bb.nazwa + '|' + str(request.POST[iloscid]) + '|' + "None")
                            elif wagaid in request.POST:
                                lista_glowna.append(
                                    bb.grupa + '|' + bb.nazwa + '|' + "None" + '|' + request.POST[wagaid])
                            else:
                                lista_glowna.append(bb.grupa + '|' + bb.nazwa + '|' + "None" + '|' + "None")
                            licznik += 1
                args = {
                    'przepis_form': przepis_form,
                    'przepis_form_test': przepis_form_glowny,
                    'formset': formsetform,
                    'formseta': formsecik,
                    'dane': dane_glowne,
                    'form2': form2,
                    'lista_glowna': lista_glowna,
                }
                args.update(views.listy_skladnikow('admin'))
                return render(request, 'user_example/testprzepisy.html', args)
        return redirect('admin_panel')

class moje_konto(View):
    def przepisy(self, numer, author_skladnika):
        formset = SkladnikiFormSet2(queryset=Przepis.objects.none())
        obiekt = Przepis.objects.get(id=numer)
        obiekt2 = Przepis.objects.all()
        forma = PrzepisForm(instance=obiekt)
        obiekt3 = Przepis_skladnik.objects.filter(przepis_id=numer)
        form2 = BazaSkladnikowForm(None)
        lista_glowna = []
        author_skladnika = author_skladnika
        fala = SkladnikiFormSet3(queryset=obiekt3)

        for a in obiekt3:
            for b in Skladniki.objects.filter(id=a.skladnik_id):
                if a.ilosc == None and a.waga == None:
                    lista_glowna.append(b.grupa + '|' + b.nazwa + '|' + "None" + '|' + "None")
                elif a.ilosc == None:
                        lista_glowna.append(b.grupa + '|' + b.nazwa + '|' + "None" + '|' + a.waga)
                elif a.waga == None:
                    lista_glowna.append(b.grupa + '|' + b.nazwa + '|' + str(a.ilosc) + '|' + "None")
                else:
                    lista_glowna.append(b.grupa + '|' + b.nazwa + '|' + str(a.ilosc) + '|' + a.waga)

        arga = {
            'przepis_form': forma,
            'formset': fala,
            'formseta': formset,
            'dane': obiekt,
            'form2': form2,
            'lista_glowna': lista_glowna,
        }
        arga.update(views.listy_skladnikow(author_skladnika))

        return lista_glowna, arga

    template_name = 'user_example/moje_konto.html'
    form_przepis = PrzepisFormTest
    form_przepis_glowny = PrzepisForm

    def get(self, request):
        obiekt = Przepis.objects.filter(author=request.user)
        obiekt2 = Przepis_test.objects.filter(author=request.user)
        edity = obiekt2.exclude(edycja=None)
        testowe = obiekt2.filter(edycja=None)
        return render(request, self.template_name, {'dane': obiekt, 'edity': edity, 'testowe': testowe})

    def post(self, request):
        action = request.POST.items()

        for item in action:
            if item[0] == 'nazwa':
                break
            elif item[0] != 'csrfmiddlewaretoken':
                if item[0] == 'przycisk':
                    obiekt = Przepis.objects.get(id=item[1])
                    obiekt_skl = Przepis_skladnik.objects.filter(przepis_id=item[1])
                    dane_skladnik = []
                    for a in obiekt_skl:
                        for b in Skladniki.objects.filter(id=a.skladnik_id):
                            if a.ilosc == None:
                                dane_skladnik.append(b.nazwa)
                            elif a.waga == None:
                                dane_skladnik.append(b.nazwa)
                            else:
                                dane_skladnik.append(str(a.ilosc) + " " + str(a.waga) + " " + b.nazwa)

                    obiekt_komentarze = Przepis_komentarze.objects.filter(przepis=item[1])
                    author = request.user
                    obiekt_komentarze = obiekt_komentarze.exclude(~Q(author=author), aktywny=False)
                    dodatkowe_komentarze = obiekt_komentarze.exclude(podkomentarz=False)
                    obiekt_komentarze = obiekt_komentarze.exclude(podkomentarz=True)
                    return render(request, 'user_example/wyswietl_przepis.html', {'przepis': obiekt,
                                            'skladniki': dane_skladnik, 'komentarze': obiekt_komentarze,
                                            'komentdodat': dodatkowe_komentarze,}, )
                elif item[0] == 'przycisk_aktywne':
                    obiekt = Przepis_test.objects.get(id=item[1])
                    obiekt_skl = Przepis_skladnik_test.objects.filter(przepis_id=item[1])
                    dane_skladnik = []
                    for a in obiekt_skl:
                        for b in Skladniki.objects.filter(id=a.skladnik_id):
                            if a.ilosc==None:
                                dane_skladnik.append(b.nazwa)
                            elif a.waga==None:
                                dane_skladnik.append(b.nazwa)
                            else:
                                dane_skladnik.append(str(a.ilosc) + " " + str(a.waga) + " " + b.nazwa)
                    return render(request, 'user_example/wyswietl_przepis.html', {'przepis': obiekt, 'aktiv': 1, 'skladniki': dane_skladnik})
                elif item[0] == 'przycisk_testowe':
                    obiekt = Przepis_test.objects.get(id=item[1])
                    obiekt_skl = Przepis_skladnik_test.objects.filter(przepis_id=item[1])
                    dane_skladnik = []
                    for a in obiekt_skl:
                        for b in Skladniki.objects.filter(id=a.skladnik_id):
                            if a.ilosc==None:
                                dane_skladnik.append(b.nazwa)
                            elif a.waga==None:
                                dane_skladnik.append(b.nazwa)
                            else:
                                dane_skladnik.append(str(a.ilosc) + " " + str(a.waga) + " " + b.nazwa)
                    return render(request, 'user_example/wyswietl_przepis.html', {'przepis': obiekt, 'testowy': 1, 'skladniki': dane_skladnik})
                elif item[0] == 'edit':
                    obiekt = Przepis.objects.get(id=item[1])
                    if obiekt.edycja == True:
                        obiekt2 = Przepis_test.objects.get(edycja=item[1])
                        lista_glowna, args = views.admin_panel.przepisy(request, obiekt2.id, request.user)
                    else:
                        lista_glowna, args = self.przepisy(item[1],request.user)
                    return render(request, 'user_example/testprzepisy.html', args)
                elif item[0] == 'edit2':
                    lista_glowna, args = views.admin_panel.przepisy(request, item[1])
                    arc = {
                        "zmiana_nazwy": 1
                    }
                    args.update(arc)
                    return render(request, 'user_example/testprzepisy.html', args)
                elif item[0] == 'delete':
                    obiekt = Przepis_test.objects.get(id=item[1])
                    obiekt2 = Przepis.objects.get(id=obiekt.edycja)
                    obiekt2.edycja = False
                    obiekt2.save()
                    Przepis_test.objects.get(id=item[1]).delete()
                    return redirect('moje_konto')

        action = request.POST.items()
        for item in action:
            if item[0] == 'acceptprzepis':
                obiekt2 = Przepis_test.objects.exclude(edycja=None)

                nowy = True
                for test in obiekt2:
                    if int(test.id) == int(item[1]):
                        nowy = False
                wzor = 'form-\d*-skladnik'
                lista_glowna = []
                licznik = 0
                numer = item[1]
                # testowy
                przepis_form = self.form_przepis(request.POST, request.FILES)
                # glowny
                przepis_form_glowny = self.form_przepis_glowny(request.POST, request.FILES)

                if nowy == True:
                    formsetform = SkladnikiFormSet3(request.POST)
                    form2 = BazaSkladnikowForm(request.POST)
                    formsecik = SkladnikiFormSet2(queryset=Przepis.objects.none())
                    dane_glowne = Przepis.objects.get(id=numer)
                    arg = {
                        'przepis_form': przepis_form_glowny,
                        'przepis_form_test': przepis_form,
                    }

                    if przepis_form.is_valid() and formsetform.is_valid():
                        nowe_dane = przepis_form.save(commit=False)
                        obiekt = Przepis.objects.get(id=numer)
                        obiekt_testskl = Przepis_skladnik.objects.filter(przepis_id=numer)
                        zmiana = False
                        zmiana_formset = False

                        if obiekt.nazwa != nowe_dane.nazwa:
                            zmiana=True
                        elif obiekt.opis != nowe_dane.opis:
                            zmiana=True
                        elif obiekt.obraz != nowe_dane.obraz and nowe_dane.obraz != None:
                            zmiana = True

                        if len(formsetform) > len(obiekt_testskl):
                            zmiana = True
                            zmiana_formset = True
                        else:
                            n = len(obiekt_testskl)
                            macierz = [[0]*2 for i in range(n)]
                            licznik_macierzy = 0
                            for ob in obiekt_testskl:
                                macierz[licznik_macierzy][0] = ob.skladnik
                                macierz[licznik_macierzy][1] = False
                                licznik_macierzy +=1

                            for skl in formsetform:
                                skladniki_form = skl.save(commit=False)
                                for sklv2 in obiekt_testskl:
                                    if skladniki_form.skladnik == sklv2.skladnik and skladniki_form.ilosc == sklv2.ilosc \
                                            and skladniki_form.waga == sklv2.waga:
                                        for i in range(len(macierz)):
                                            if sklv2.skladnik == macierz[i][0]:
                                                macierz[i][1] = True

                            for i in range(len(macierz)):
                                if macierz[i][1] == False:
                                    zmiana_formset = True
                                    zmiana = True

                        if zmiana == True:
                            if nowe_dane.nazwa == obiekt.nazwa:
                                obiekt.opis = nowe_dane.opis
                                if nowe_dane.obraz != None:
                                    obiekt.obraz = nowe_dane.obraz
                                b = Przepis_test(nazwa=obiekt.nazwa,
                                                 opis=obiekt.opis,
                                                 obraz=obiekt.obraz,
                                                 data=obiekt.data,
                                                 author=obiekt.author,
                                                 edycja=numer
                                                 )
                                b.save()

                                if zmiana_formset == False:
                                    obiekt3 = Przepis_skladnik.objects.filter(przepis_id=numer)
                                    for test in obiekt3:
                                        b_skladnik = Przepis_skladnik_test(przepis=b,
                                                                           skladnik=test.skladnik,
                                                                           ilosc=test.ilosc,
                                                                           waga=test.waga,
                                                                           )
                                        b_skladnik.save()
                                else:
                                    for test in formsetform:
                                        obiekt3 = test.save(commit=False)
                                        b_skladnik = Przepis_skladnik_test(przepis=b,
                                                                           skladnik=obiekt3.skladnik,
                                                                           ilosc=obiekt3.ilosc,
                                                                           waga=obiekt3.waga,
                                                                           )
                                        b_skladnik.save()


                                obiekt = Przepis.objects.get(id=numer)
                                obiekt.edycja = True
                                obiekt.save()
                                return redirect('moje_konto')

                            if przepis_form_glowny.is_valid():
                                if nowe_dane.obraz != None:
                                    obiekt.obraz = nowe_dane.obraz
                                obiekt.opis = nowe_dane.opis
                                obiekt.nazwa = nowe_dane.nazwa
                                b = Przepis_test(nazwa=obiekt.nazwa,
                                                 opis=obiekt.opis,
                                                 obraz=obiekt.obraz,
                                                 data=obiekt.data,
                                                 author=obiekt.author,
                                                 edycja=numer
                                                 )
                                b.save()
                                obiekt3 = Przepis_skladnik.objects.filter(przepis_id=numer)
                                for test in obiekt3:
                                    b_skladnik = Przepis_skladnik_test(przepis=b,
                                                                       skladnik=test.skladnik,
                                                                       ilosc=test.ilosc,
                                                                       waga=test.waga,
                                                                       )
                                    b_skladnik.save()
                                return redirect('moje_konto')
                        else:
                            return redirect('moje_konto')
                else:
                    formsetform = SkladnikiFormSet3Test(request.POST)
                    form2 = BazaSkladnikowForm(request.POST)
                    formsecik = SkladnikiFormSet2Test(queryset=Przepis.objects.none())
                    dane_glowne = Przepis_test.objects.get(id=numer)
                    arg = {
                        'przepis_form': przepis_form,
                        'przepis_form_test': przepis_form_glowny,
                    }

                    test = Przepis.objects.get(id=dane_glowne.edycja)

                    pustyform = PrzepisFormPusty(request.POST, request.FILES)
                    pustyform_dane = pustyform.save(commit=False)

                    if (request.POST['nazwa'] == test.nazwa or przepis_form_glowny.is_valid()) and formsetform.is_valid():
                        if request.POST['nazwa'] == test.nazwa:
                            pustyform_dane.nazwa = test.nazwa
                            nowe_dane = pustyform_dane
                        else:
                            nowe_dane = przepis_form_glowny.save(commit=False)

                        obiekt = Przepis_test.objects.get(id=numer)

                        if nowe_dane.nazwa == obiekt.nazwa:
                            obiekt.opis = nowe_dane.opis
                            if nowe_dane.obraz != None:
                                obiekt.obraz = nowe_dane.obraz
                            Przepis_skladnik_test.objects.filter(przepis_id=numer).delete()
                            obiekt.save()
                            for form in formsetform:
                                skladniki_form = form.save(commit=False)
                                skladniki_form.przepis = obiekt
                                skladniki_form.save()
                            return redirect('moje_konto')

                        if przepis_form.is_valid():
                            obiekt.opis = nowe_dane.opis
                            if nowe_dane.obraz != None:
                                obiekt.obraz = nowe_dane.obraz
                            Przepis_skladnik_test.objects.filter(przepis_id=numer).delete()
                            obiekt.nazwa = nowe_dane.nazwa
                            obiekt.save()
                            for form in formsetform:
                                skladniki_form = form.save(commit=False)
                                skladniki_form.przepis = obiekt
                                skladniki_form.save()
                            return redirect('moje_konto')

                for skladniki_post in request.POST:
                    if re.findall(wzor, skladniki_post):
                        skladnikid = "form-" + str(licznik) + "-skladnik"
                        iloscid = "form-" + str(licznik) + "-ilosc"
                        wagaid = "form-" + str(licznik) + "-waga"
                        for bb in Skladniki.objects.filter(id=request.POST[skladnikid]):
                            if wagaid in request.POST and iloscid in request.POST:
                                lista_glowna.append(
                                    bb.grupa + '|' + bb.nazwa + '|' + str(request.POST[iloscid]) + '|' + request.POST[
                                        wagaid])
                            elif iloscid in request.POST:
                                lista_glowna.append(
                                    bb.grupa + '|' + bb.nazwa + '|' + str(request.POST[iloscid]) + '|' + "None")
                            elif wagaid in request.POST:
                                lista_glowna.append(
                                    bb.grupa + '|' + bb.nazwa + '|' + "None" + '|' + request.POST[wagaid])
                            else:
                                lista_glowna.append(bb.grupa + '|' + bb.nazwa + '|' + "None" + '|' + "None")

                            licznik += 1
                args = {
                    'formset': formsetform,
                    'formseta': formsecik,
                    'dane': dane_glowne,
                    'form2': form2,
                    'lista_glowna': lista_glowna,
                }
                args.update(arg)
                args.update(views.listy_skladnikow(request.user))
                return render(request, 'user_example/testprzepisy.html', args)
            elif item[0] == 'acceptprzepis_testowy':
                wzor = 'form-\d*-skladnik'
                lista_glowna = []
                licznik = 0
                numer = item[1]
                # testowy
                przepis_form = self.form_przepis(request.POST, request.FILES)
                # glowny
                przepis_form_glowny = self.form_przepis_glowny(request.POST, request.FILES)

                formsetform = SkladnikiFormSet3Test(request.POST)
                form2 = BazaSkladnikowForm(request.POST)
                formsecik = SkladnikiFormSet2Test(queryset=Przepis.objects.none())
                dane_glowne = Przepis_test.objects.get(id=numer)
                arg = {
                    'przepis_form': przepis_form,
                    'przepis_form_test': przepis_form_glowny,
                }

                test = dane_glowne

                pustyform = PrzepisFormPusty(request.POST, request.FILES)
                pustyform_dane = pustyform.save(commit=False)

                if (request.POST['nazwa'] == test.nazwa or przepis_form_glowny.is_valid()) and formsetform.is_valid():
                    if request.POST['nazwa'] == test.nazwa:
                        pustyform_dane.nazwa = test.nazwa
                        nowe_dane = pustyform_dane
                    else:
                        nowe_dane = przepis_form_glowny.save(commit=False)

                    obiekt = Przepis_test.objects.get(id=numer)

                    if nowe_dane.nazwa == obiekt.nazwa:
                        obiekt.opis = nowe_dane.opis
                        if nowe_dane.obraz != None:
                            obiekt.obraz = nowe_dane.obraz
                        Przepis_skladnik_test.objects.filter(przepis_id=numer).delete()
                        obiekt.save()
                        for form in formsetform:
                            skladniki_form = form.save(commit=False)
                            skladniki_form.przepis = obiekt
                            skladniki_form.save()

                    if przepis_form.is_valid():
                        obiekt.opis = nowe_dane.opis
                        if nowe_dane.obraz != None:
                            obiekt.obraz = nowe_dane.obraz
                        Przepis_skladnik_test.objects.filter(przepis_id=numer).delete()
                        obiekt.nazwa = nowe_dane.nazwa
                        obiekt.save()
                        for form in formsetform:
                            skladniki_form = form.save(commit=False)
                            skladniki_form.przepis = obiekt
                            skladniki_form.save()
                    return redirect('moje_konto')

                for skladniki_post in request.POST:
                    if re.findall(wzor, skladniki_post):
                        skladnikid = "form-" + str(licznik) + "-skladnik"
                        iloscid = "form-" + str(licznik) + "-ilosc"
                        wagaid = "form-" + str(licznik) + "-waga"
                        for bb in Skladniki.objects.filter(id=request.POST[skladnikid]):
                            if wagaid in request.POST and iloscid in request.POST:
                                lista_glowna.append(
                                    bb.grupa + '|' + bb.nazwa + '|' + str(request.POST[iloscid]) + '|' + request.POST[
                                        wagaid])
                            elif iloscid in request.POST:
                                lista_glowna.append(
                                    bb.grupa + '|' + bb.nazwa + '|' + str(request.POST[iloscid]) + '|' + "None")
                            elif wagaid in request.POST:
                                lista_glowna.append(
                                    bb.grupa + '|' + bb.nazwa + '|' + "None" + '|' + request.POST[wagaid])
                            else:
                                lista_glowna.append(bb.grupa + '|' + bb.nazwa + '|' + "None" + '|' + "None")

                            licznik += 1
                args = {
                    'formset': formsetform,
                    'formseta': formsecik,
                    'dane': dane_glowne,
                    'form2': form2,
                    'lista_glowna': lista_glowna,
                    'zmiana_nazwy': 1,
                }
                args.update(arg)
                args.update(views.listy_skladnikow(request.user))
                return render(request, 'user_example/testprzepisy.html', args)

        return  render(request, self.template_name )
