import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from djstripe.models import Customer, Price

from profiles.forms import ProfileUpdateForm
from profiles.models import Profile, ShirtOrder


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = Profile

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileDistrictAndRCOPartial(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profiles/_rcos_partial.html"

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfileDonationsPartial(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = "profiles/_donations_partial.html"

    def get_object(self, queryset=None):
        try:
            customer = Customer.objects.filter(subscriber=self.request.user).first()
            if customer:
                customer.api_retrieve()
                customer._sync_subscriptions()
                customer._sync_charges()
        except Exception:
            pass
        return self.request.user.profile


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm

    def get_success_url(self):
        return reverse("profile")

    def get_object(self):
        return Profile.objects.get(user=self.request.user)


class ShirtsAreDoneMixin:

    def dispatch(self, request, *args, **kwargs):
        messages.add_message(self.request, messages.INFO, "T-Shirt orders are closed")
        return HttpResponseRedirect(reverse("profile"))


class ShirtOrderView(LoginRequiredMixin, ShirtsAreDoneMixin, CreateView):
    model = ShirtOrder
    fields = ["fit", "print_color", "size"]

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        messages.add_message(
            self.request, messages.INFO, "T-Shirt order recorded! Complete payment to finalize."
        )
        self.obj = obj
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse("shirt_pay", kwargs={"shirt_id": self.obj.id})


class ShirtOrderDeleteView(LoginRequiredMixin, ShirtsAreDoneMixin, DeleteView):
    model = ShirtOrder

    def get_success_url(self):
        messages.add_message(self.request, messages.INFO, "T-Shirt order deleted.")
        return reverse("profile")


@csrf_exempt
def create_tshirt_checkout_session(request, shirt_id):
    # Close t-shirt orders
    messages.add_message(request, messages.INFO, "Sorry, shirt orders are closed!")
    return HttpResponseRedirect(reverse("profile"))

    stripe.api_key = settings.STRIPE_SECRET_KEY
    stripe_product_search = stripe.Product.search(
        query="active:'true' AND name:'T-Shirt Pre-Order 2025-02'"
    )
    price_search = [
        p
        for p in stripe.Price.search(query=f"product:'{stripe_product_search['data'][0]['id']}'")[
            "data"
        ]
    ]
    price = Price()._get_or_retrieve(price_search[0]["id"])

    if request.method == "POST":
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.create(
            ui_mode="embedded",
            mode="payment",
            currency="USD",
            line_items=[{"price": price.id, "quantity": 1}],
            return_url=request.build_absolute_uri(
                reverse("shirt_pay_complete", kwargs={"shirt_id": shirt_id})
            ),
            shipping_address_collection={"allowed_countries": ["US"]},
            customer=(
                request.user.djstripe_customers.first().id
                if request.user.is_authenticated and request.user.djstripe_customers.first()
                else None
            ),
        )
        request.session["_stripe_checkout_session_id"] = session.id
        return JsonResponse({"clientSecret": session.client_secret})
    else:
        shirt = ShirtOrder.objects.get(id=shirt_id)
        context = {"stripe_public_key": settings.STRIPE_PUBLIC_KEY, "shirt": shirt}
        return TemplateResponse(request, "tshirt_checkout_session.html", context)


def complete_tshirt_checkout_session(request, shirt_id):
    checkout_session_id = request.session.pop("_stripe_checkout_session_id", default=None)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    if session["status"] == "complete":
        s = ShirtOrder.objects.get(id=shirt_id)
        s.billing_details = session["customer_details"]
        s.shipping_details = session["shipping_details"]
        s.paid = True
        s.save()
        messages.add_message(request, messages.INFO, "T-Shirt paid!")
        return HttpResponseRedirect(reverse("profile"))
    messages.add_message(request, messages.ERROR, "T-Shirt payment incomoplete!")
    return HttpResponseRedirect(reverse("profile"))
