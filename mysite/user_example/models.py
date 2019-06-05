from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

class Przepis(models.Model):
    nazwa = models.CharField(verbose_name="Przepis", max_length=50, unique=True)
    opis = models.TextField(blank=True, help_text="Opis Przepisu")
    obraz = models.ImageField(null=True, blank=True, upload_to="static/images/przepisy")
    data = models.DateField('dodano', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    edycja = models.BooleanField(default=False)

    def __str__(self):
        return self.nazwa

class Skladniki(models.Model):
    GRUPY = (
        ('Bakalie', 'Bakalie'),
        ('Jaja', 'Jaja'),
        ('Mieso', 'Mięso'),
        ('Owoce', 'Owoce'),
        ('Produkty cukiernicze', 'Produkty cukiernicze'),
        ('Produkty mleczne', 'Produkty mleczne'),
        ('Produkty zbozowe', 'Produkty zbożowe'),
        ('Przyprawy', 'Przyprawy'),
        ('Ryby', 'Ryby'),
        ('Suche nasiona straczkowe', 'Suche nasiona strączkowe'),
        ('Tluszcze', 'Tłuszcze'),
        ('Warzywa', 'Warzywa'),
        ('Wedliny', 'Wędliny'),
    )

    nazwa = models.CharField(max_length=50, unique=True)
    opis = models.TextField(blank=True, help_text="Opis składnika")
    zastosowanie = models.TextField(blank=True, help_text="Zastosowanie składnika")
    grupa = models.CharField(max_length=20, choices=GRUPY)
    data = models.DateField('dodano', auto_now_add=True)
    obraz = models.ImageField(null=True, blank=True, upload_to="static/images/baza_skladnikow")
    aktywny = models.BooleanField(default=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.grupa +':' + self.nazwa



class Przepis_skladnik(models.Model):
    wag = (
        ('kg', 'kg'),
        ('dag', 'dag'),
        ('g', 'g'),
    )

    przepis = models.ForeignKey(Przepis, on_delete=models.CASCADE)
    skladnik = models.ForeignKey(Skladniki, verbose_name='Składniki', on_delete=models.CASCADE)
    ilosc = models.FloatField(max_length=5, blank=True, null=True)
    waga = models.CharField(max_length=3, choices=wag, blank=True, null=True)

class Przepis_komentarze(models.Model):
    przepis = models.ForeignKey(Przepis, on_delete=models.CASCADE)
    tresc = models.TextField(blank=True)
    aktywny = models.BooleanField(default=True)
    czykomentarze = models.BooleanField(default=False)
    podkomentarz = models.BooleanField(default=False)
    idkomentarza = models.IntegerField(blank=True, null=True)
    likes = models.ManyToManyField(User, related_name="likes", blank=True)
    dislikes = models.ManyToManyField(User, related_name="dislikes", blank=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    data = models.DateField('dodano', auto_now_add=True)

class Skladniki_test(models.Model):
    GRUPY = (
        ('Bakalie', 'Bakalie'),
        ('Jaja', 'Jaja'),
        ('Mieso', 'Mięso'),
        ('Owoce', 'Owoce'),
        ('Produkty cukiernicze', 'Produkty cukiernicze'),
        ('Produkty mleczne', 'Produkty mleczne'),
        ('Produkty zbozowe', 'Produkty zbożowe'),
        ('Przyprawy', 'Przyprawy'),
        ('Ryby', 'Ryby'),
        ('Suche nasiona straczkowe', 'Suche nasiona strączkowe'),
        ('Tluszcze', 'Tłuszcze'),
        ('Warzywa', 'Warzywa'),
        ('Wedliny', 'Wędliny'),
    )

    nazwa = models.CharField(max_length=50, unique=True)
    opis = models.TextField(blank=True, help_text="Opis składnika")
    zastosowanie = models.TextField(blank=True, help_text="Zastosowanie składnika")
    grupa = models.CharField(max_length=20, choices=GRUPY)
    data = models.DateField('dodano', auto_now_add=True)
    obraz = models.ImageField(null=True, blank=True, upload_to="static/images/baza_skladnikow")
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.grupa +':' + self.nazwa

class Przepis_test(models.Model):
    nazwa = models.CharField(verbose_name="Przepis", max_length=50, unique=True)
    opis = models.TextField(blank=True, help_text="Opis Przepisu")
    obraz = models.ImageField(null=True, blank=True, upload_to="static/images/przepisy")
    data = models.DateField('dodano', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    edycja = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return self.nazwa

class Przepis_skladnik_test(models.Model):
    wag = (
        ('kg', 'kg'),
        ('dag', 'dag'),
        ('g', 'g'),
    )

    przepis = models.ForeignKey(Przepis_test, on_delete=models.CASCADE)
    skladnik = models.ForeignKey(Skladniki, verbose_name='Składniki', on_delete=models.CASCADE)
    ilosc = models.FloatField(max_length=5, blank=True, null=True)
    waga = models.CharField(max_length=3, choices=wag, blank=True, null=True)
