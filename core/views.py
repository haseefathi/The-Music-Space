from re import template
from django.shortcuts import render, get_list_or_404, redirect, get_object_or_404
from .models import Item, OrderItem, Order, BillingAddress
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
import stripe
# Create your views here.


class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = "home-page.html"


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)

    order_item, created = OrderItem.objects.get_or_create(
        item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug):
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect('core:order-summary')
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect('core:order-summary')
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")

        return redirect('core:order-summary')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug):
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False)[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect('core:order-summary')
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect('core:product', slug=slug)

    else:
        messages.info(request, "You do not have an active order.")
        return redirect('core:product', slug=slug)


def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug):
            order_item = OrderItem.objects.filter(
                item=item, user=request.user, ordered=False)[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect('core:order-summary')
        else:
            messages.info(request, "This item was not in your cart.")
            return redirect('core:product', slug=slug)

    else:
        messages.info(request, "You do not have an active order.")
        return redirect('core:product', slug=slug)


class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request, "payment.html")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, "checkout-page.html", context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            print(self.request.POST)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zipcode = form.cleaned_data.get('zipcode')
                # same_shipping_address = form.cleaned_data.get(
                #     'same_shipping_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zipcode=zipcode
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                return redirect('core:checkout')
            messages.warning(self.request, 'Failed checkout')
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order.")
            return redirect('core:order-summary')


def products_view(request):
    context = {

    }
    return render(request, 'product-page.html', context)


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order.")
            return redirect('/')
