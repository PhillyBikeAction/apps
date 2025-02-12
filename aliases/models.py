from django.db import models


class Alias(models.Model):
    # User Supplied
    alias = models.CharField(
        max_length=64, null=False, blank=False, help_text="The alias name, the part before the @"
    )
    domain = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        default="bikeaction.org",
        help_text="The domain, the part after the @",
    )
    description = models.CharField(
        max_length=128, null=True, blank=True, help_text="A description for humans."
    )

    # Internal
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Mailgun
    mailgun_id = models.CharField(max_length=64, null=True, blank=True)
    mailgun_updated_at = models.DateTimeField(null=True)

    class Meta:
        verbose_name_plural = "aliases"

    def __str__(self):
        return f"{self.alias}@{self.domain} alias"


class AliasRecipient(models.Model):
    alias = models.ForeignKey(Alias, on_delete=models.CASCADE, related_name="recipients")
    email_address = models.EmailField(max_length=254)

    class Meta:
        constraints = [
            models.UniqueConstraint("alias", "email_address", name="unique_emails_per_alias")
        ]

    def __str__(self):
        return f"{self.email_address} - {self.alias.alias}@{self.alias.domain}"
