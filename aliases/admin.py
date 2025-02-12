from django import forms
from django.contrib import admin

from aliases.models import Alias, AliasRecipient


class AliasRecipientForm(forms.ModelForm):
    class Meta:
        model = AliasRecipient
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        if email_address := cleaned_data.get("email_address"):
            if AliasRecipient.objects.exclude(id=self.instance.id).filter(
                alias=self.instance.alias, email_address=email_address
            ):
                self.add_error(
                    "email_address",
                    (
                        "This recipient already exists for "
                        f"{self.instance.alias.alias}@{self.instance.alias.domain}."
                    ),
                )
        return cleaned_data


class AliasRecipientInline(admin.TabularInline):
    model = AliasRecipient
    form = AliasRecipientForm
    extra = 0


class AliasAdmin(admin.ModelAdmin):
    list_display = ("get_alias_display", "recip_display", "ready")
    inlines = [AliasRecipientInline]
    readonly_fields = ("domain", "mailgun_id", "ready")

    fieldsets = [
        ("ALIAS CONFIGURATION", {"fields": ("alias", "domain")}),
        ("Status", {"fields": ("ready",)}),
    ]

    def recip_display(self, obj=None):
        if obj is None:
            return None
        return ", ".join([r.email_address for r in obj.recipients.all()])

    def ready(self, obj=None):
        if obj is None:
            return False
        return (
            (obj.mailgun_id is not None)
            and (obj.mailgun_updated_at is not None)
            and (obj.mailgun_updated_at > obj.updated_at)
        )

    ready.boolean = True

    def get_alias_display(self, obj=None):
        if obj is None:
            return None
        return f"{obj.alias}@bikeaction.org"

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Alias, AliasAdmin)
