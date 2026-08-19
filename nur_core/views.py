from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from .forms import ContactForm


def contact(request, sent=False):
    form = ContactForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        service = dict(ContactForm.SERVICE_CHOICES)[data["service"]]
        body = (
            f"Nom : {data['name']}\n"
            f"E-mail : {data['email']}\n"
            f"Organisation : {data['organization'] or 'Non renseignée'}\n"
            f"Téléphone : {data['phone'] or 'Non renseigné'}\n"
            f"Expertise : {service}\n\n"
            f"Message :\n{data['message']}"
        )
        EmailMessage(
            subject=f"Nouvelle demande NUR - {service}",
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],
            reply_to=[data["email"]],
        ).send()
        return redirect("contact-sent")

    return render(request, "contact.html", {"form": form, "sent": sent})