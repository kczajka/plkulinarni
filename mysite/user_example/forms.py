from django.contrib.auth.models import User
from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.utils.translation import ugettext as _
from django.core.validators import validate_email
from .models import Skladniki, Przepis, Przepis_skladnik, Skladniki_test, Przepis_test, Przepis_skladnik_test, \
    Przepis_komentarze
from django.forms.models import inlineformset_factory
from django.forms import modelformset_factory, formset_factory
from django.db import models


class LoginForm(forms.Form):
    username = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        try:
            user = authenticate(username=User.objects.get(email=username), password=password)
            print(user)
        except:
            user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise forms.ValidationError("Wprowadź poprawną nazwę konta i hasło.")
        return self.cleaned_data

    def login(self, request):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        try:
            user = authenticate(username=User.objects.get(email=username), password=password)
        except:
            user = authenticate(username=username, password=password)
        return user



class UserForm(forms.ModelForm):
    username = forms.CharField(
        label=('Nazwa'),
        max_length=25,
        error_messages={
            'unique': _("Użytkownik o tej nazwie już istnieje"),
            'invalid': _("Wprowadź prawidłową nazwę użytkownika. Ta wartość może zawierać tylko litery, cyfry i znaki @ /. / + / - / _"),
        },
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nazwa'
            }
        )
    )
    password = forms.CharField(
        label=('Hasło'),
        max_length=25,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Hasło'
            }
        )
    )
    password_confirm = forms.CharField(
        label=('Haslo2'),
        max_length=25,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Powtórz hasło'
            }
        )
    )
    email = forms.CharField(
        label='Adres email',
        validators=[validate_email],
        error_messages={
            'unique': _("Podany email jest już zarejestrowany."),
        },
        max_length=25,
        widget=forms.EmailInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Adres email'
            }
        )
    )

    class Meta:
        model = User
        User._meta.get_field('email')._unique = True
        fields = ['username', 'email', 'password', 'password_confirm']
    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            self.add_error('password_confirm', "Hasła nie są zgodne.")
        return cleaned_data


class PasswordForm(PasswordChangeForm):
    error_messages = {
        'password_mismatch': _("Hasła nie są zgodne!"),
        'password_incorrect': _("Twoje stare hasło jest niepoprawne!"),
    }

    old_password = forms.CharField(
        label=('Stare hasło'),
        validators=[],
        max_length=25,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Stare hasło'
            }
        )
    )
    new_password1 = forms.CharField(
        label=('Nowe hasło'),
        max_length=25,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Nowe hasło'
            }
        )
    )
    new_password2 = forms.CharField(
        label=('Nowe hasło2'),
        max_length=25,
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Powtórz nowe hasło'
            }
        )
    )

class BazaSkladnikowForm(forms.ModelForm):
    class Meta:
        model = Skladniki
        fields = ['grupa',]

class WyswietlaniePrzepisuForm(forms.ModelForm):
    class Meta:
        model = Przepis
        fields = ['nazwa','opis','obraz',]

class SkladnikForm(forms.ModelForm):
    class Meta:
        model = Skladniki
        exclude = ('data','author',)
        widgets = {
            'nazwa': forms.TextInput(attrs={
                'placeholder': 'Nazwa składnika',
            }),
            'grupa': forms.Select(attrs={
                'class': 'browser-default custom-select',
            }),
            'opis': forms.Textarea(attrs={
                'cols': 80,
                'rows': 5,
                'placeholder': 'Opis',
            }),
            'zastosowanie': forms.Textarea(attrs={
                'cols': 80,
                'rows': 5,
                'placeholder': 'Zastosowanie',
            })
        }

class SkladnikFormTest(forms.ModelForm):
    class Meta:
        model = Skladniki_test
        exclude = ('data','author',)
        widgets = {
            'nazwa': forms.TextInput(attrs={
                'placeholder': 'Nazwa składnika',
            }),
            'grupa': forms.Select(attrs={
                'class': 'browser-default custom-select',
            }),
            'opis': forms.Textarea(attrs={
                'cols': 80,
                'rows': 5,
                'placeholder': 'Opis',
            }),
            'zastosowanie': forms.Textarea(attrs={
                'cols': 80,
                'rows': 5,
                'placeholder': 'Zastosowanie',
            })
        }

class PrzepisForm(forms.ModelForm):
    class Meta:
        model = Przepis
        exclude = ('data','author',)
        widgets = {
            'nazwa': forms.TextInput(attrs={
                'placeholder': 'Nazwa przepisu',
            }),
            'opis': forms.Textarea(attrs={
                'rows': 10,
                'cols': 100
            }
            ),
        }

SkladnikiFormSet = inlineformset_factory(
    parent_model=Przepis,
    model=Przepis_skladnik,
    max_num=30,
    extra=1,
    fields=('skladnik','ilosc','waga')
)

SkladnikiFormSet2 = modelformset_factory(
    Przepis_skladnik,
    fields=('skladnik','ilosc','waga'),
    extra=1,
)

class PrzepisFormTest(forms.ModelForm):
    class Meta:
        model = Przepis_test
        exclude = ('data','author',)
        widgets = {
            'opis': forms.Textarea(attrs={
                'rows': 10,
                'cols': 100
            }
            ),
        }

SkladnikiFormSet2Test = modelformset_factory(
    Przepis_skladnik_test,
    fields=('skladnik','ilosc','waga'),
    extra=1,
)
SkladnikiFormSet3Test = modelformset_factory(
    Przepis_skladnik_test,
    fields=('skladnik','ilosc','waga'),
    extra=0,
)
SkladnikiFormSet3 = modelformset_factory(
    Przepis_skladnik,
    fields=('skladnik','ilosc','waga'),
    extra=0,
)


class PrzepisFormPusty(forms.ModelForm):
    class Meta:
        model = Przepis
        exclude = ('data','author','nazwa')
        widgets = {
            'opis': forms.Textarea(attrs={
                'rows': 10,
                'cols': 100
            }),
        }

class PrzepisKomentarzForm(forms.ModelForm):
    class Meta:
        model = Przepis_komentarze
        fields = ['tresc',]
        widgets ={
            'tresc': forms.Textarea(attrs={
                'rows': 5,
                'cols': 108
            })
        }
