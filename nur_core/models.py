from django.core.exceptions import ValidationError
from django.db import models


class PortfolioItem(models.Model):
    MAX_IMAGES = 3

    POLE_CHOICES = [
        ("data", "Data & intelligence artificielle"),
        ("software", "Logiciels & solutions numériques"),
        ("network", "Réseaux & infrastructures"),
        ("other", "Autre activité"),
    ]

    title = models.CharField("Titre / Activité", max_length=160)
    pole = models.CharField(
        "Pôle d'expertise",
        max_length=20,
        choices=POLE_CHOICES,
        default="software",
    )
    summary = models.TextField(
        "Texte de présentation",
        max_length=600,
        help_text="Texte affiché avec la ou les images dans le bandeau défilant.",
    )
    location_or_client = models.CharField(
        "Lieu ou contexte (optionnel)",
        max_length=140,
        blank=True,
    )
    is_published = models.BooleanField("Publié sur l'accueil", default=True)
    display_order = models.PositiveIntegerField("Ordre d'affichage", default=0)
    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Mis à jour le", auto_now=True)

    class Meta:
        verbose_name = "Élément portfolio"
        verbose_name_plural = "Éléments portfolio"
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title


class PortfolioImage(models.Model):
    portfolio_item = models.ForeignKey(
        PortfolioItem,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Activité / Texte",
    )
    image = models.ImageField("Image", upload_to="portfolio/%Y/%m/")
    caption = models.CharField("Légende courte (optionnel)", max_length=160, blank=True)
    order = models.PositiveSmallIntegerField("Ordre de défilement", default=1)

    class Meta:
        verbose_name = "Image du portfolio"
        verbose_name_plural = "Images du portfolio"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.portfolio_item.title} — Image #{self.order}"

    def clean(self):
        super().clean()
        if not self.portfolio_item_id:
            return

        siblings = PortfolioImage.objects.filter(portfolio_item_id=self.portfolio_item_id)
        if self.pk:
            siblings = siblings.exclude(pk=self.pk)

        if siblings.count() >= PortfolioItem.MAX_IMAGES:
            raise ValidationError(
                f"Un même texte peut contenir au maximum {PortfolioItem.MAX_IMAGES} images."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)