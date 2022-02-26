from django.urls import path
from .views import products_view, HomeView, ItemDetailView, add_to_cart, remove_from_cart, OrderSummaryView, remove_single_item_from_cart, CheckoutView, PaymentView

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='item-list'),
    path('checkout', CheckoutView.as_view(), name='checkout'),
    path('product/<slug>/', ItemDetailView.as_view(), name="product"),
    path('add-to-cart/<slug>', add_to_cart, name="add-to-cart"),
    path('remove-from-cart/<slug>', remove_from_cart, name="remove-from-cart"),
    path('remove-item-from-cart/<slug>',
         remove_single_item_from_cart, name="remove-item-from-cart"),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('payment/<payment_option>', PaymentView.as_view(), name='payment'),
]
