import smtplib

from django.conf import settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from .forms import ContactForm
from .models import PortfolioItem


def home(request):
    portfolio_items = list(
        PortfolioItem.objects.filter(is_published=True).prefetch_related("images")
    )
    for item in portfolio_items:
        item.carousel_images = list(item.images.all())[: PortfolioItem.MAX_IMAGES]

    return render(
        request,
        "home.html",
        {
            "portfolio_items": portfolio_items,
        },
    )


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
        recipients = getattr(settings, "CONTACT_EMAILS", None)
        if not recipients:
            recipients = getattr(settings, "CONTACT_EMAIL", None)
        if isinstance(recipients, str):
            recipients = [email.strip() for email in recipients.split(",") if email.strip()]
        else:
            recipients = [email.strip() for email in recipients if email.strip()]

        try:
            sent_count = EmailMessage(
                subject=f"Nouvelle demande NUR - {service}",
                body=body,
                #from_email=settings.DEFAULT_FROM_EMAIL,
                from_email=settings.EMAIL_HOST_USER,
                to=recipients,
                reply_to=[data["email"]],
            ).send()
            if sent_count:
                return redirect("contact-sent")
        except (smtplib.SMTPException, OSError):
            pass

        form.add_error(
            None,
            "Votre demande n'a pas pu être envoyée. Veuillez réessayer ou nous écrire directement.",
        )

    return render(request, "contact.html", {"form": form, "sent": sent})