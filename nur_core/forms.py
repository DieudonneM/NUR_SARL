from django import forms


class ContactForm(forms.Form):
    SERVICE_CHOICES = [
        ("", "Sélectionnez une expertise"),
        ("data", "Data & intelligence artificielle"),
        ("software", "Logiciels & solutions numériques"),
        ("network", "Réseaux & infrastructures"),
        ("other", "Autre besoin"),
    ]

    name = forms.CharField(max_length=120)
    email = forms.EmailField()
    organization = forms.CharField(max_length=160, required=False)
    phone = forms.CharField(max_length=40, required=False)
    service = forms.ChoiceField(choices=SERVICE_CHOICES)
    message = forms.CharField(max_length=3000, widget=forms.Textarea)