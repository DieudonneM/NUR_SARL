from django.contrib import admin, messages
from django.utils.html import format_html

from .models import PortfolioImage, PortfolioItem


class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1
    min_num = 0
    max_num = PortfolioItem.MAX_IMAGES
    validate_max = True
    fields = ("image", "caption", "order", "preview")
    readonly_fields = ("preview",)
    ordering = ("order", "id")

    @admin.display(description="Aperçu")
    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:52px;width:84px;object-fit:cover;border-radius:6px;" />',
                obj.image.url,
            )
        return "—"


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "pole",
        "images_count",
        "is_published",
        "display_order",
        "updated_at",
    )
    list_filter = ("pole", "is_published", "created_at")
    search_fields = ("title", "summary", "location_or_client")
    list_editable = ("is_published", "display_order")
    list_per_page = 20
    inlines = [PortfolioImageInline]
    actions = ("publish_items", "unpublish_items")

    fieldsets = (
        (
            "Contenu éditorial",
            {
                "fields": ("title", "pole", "summary", "location_or_client"),
            },
        ),
        (
            "Publication & ordre",
            {
                "fields": ("is_published", "display_order"),
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related("images")

    @admin.display(description="Images (max 3)")
    def images_count(self, obj):
        count = obj.images.count()
        color = "#b45309" if count > PortfolioItem.MAX_IMAGES else "#15803d"
        return format_html(
            '<span style="font-weight:600;color:{};">{} / {}</span>',
            color,
            count,
            PortfolioItem.MAX_IMAGES,
        )

    @admin.action(description="Publier les éléments sélectionnés")
    def publish_items(self, request, queryset):
        updated = queryset.update(is_published=True)
        self.message_user(
            request,
            f"{updated} élément(s) publié(s) sur la page d'accueil.",
            messages.SUCCESS,
        )

    @admin.action(description="Retirer de l'accueil (brouillon)")
    def unpublish_items(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(
            request,
            f"{updated} élément(s) passé(s) en brouillon.",
            messages.INFO,
        )


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ("portfolio_item", "order", "caption", "thumb")
    list_filter = ("portfolio_item__pole",)
    search_fields = ("portfolio_item__title", "caption")
    list_editable = ("order",)

    @admin.display(description="Aperçu")
    def thumb(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="height:44px;width:72px;object-fit:cover;border-radius:4px;" />',
                obj.image.url,
            )
        return "—"