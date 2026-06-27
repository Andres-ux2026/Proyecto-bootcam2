from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db import transaction
from products.models import Product
from .models import Cart, CartItem
from .forms import CartItemForm


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product,
        defaults={'quantity': 1},
    )
    if not created:
        if cart_item.quantity >= product.stock:
            messages.error(request, "No hay suficiente stock disponible para este producto.")
            return redirect('products:detail', pk=pk)
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"Producto añadido al carrito.")
    return redirect('products:list')


@login_required
def update_cart_item(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            if quantity > cart_item.product.stock:
                messages.error(request, "No hay suficiente stock disponible.")
                return redirect('cart:detail')
            form.save()
            messages.success(request, "Cantidad actualizada.")
        else:
            for error in form.errors.values():
                messages.error(request, error)
    return redirect('cart:detail')


@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Producto eliminado del carrito.")
    return redirect('cart:detail')


@login_required
def cart_detail(request):
    cart = Cart.objects.filter(user=request.user).first()
    return render(request, 'cart/cart_detail.html', {'cart': cart})
