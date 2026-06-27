from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from django.db import transaction
from cart.models import Cart
from .models import Order


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.error(request, "Tu carrito está vacío.")
        return redirect('cart:detail')

    if request.method == 'POST':
        with transaction.atomic():
            order = Order.objects.create(user=request.user)
            for cart_item in cart.items.select_related('product').all():
                product = cart_item.product
                if cart_item.quantity > product.stock:
                    messages.error(
                        request,
                        f"No hay suficiente stock para {product.name}."
                    )
                    return redirect('cart:detail')
                order.items.create(
                    product=product,
                    product_name=product.name,
                    quantity=cart_item.quantity,
                    price=product.price,
                )
                product.stock -= cart_item.quantity
                product.save(update_fields=['stock'])
            order.calculate_total()
            cart.items.all().delete()
        messages.success(request, "Compra confirmada con éxito. ¡Gracias por tu pedido!")
        return redirect('orders:history')

    return render(request, 'orders/order_confirm.html', {'cart': cart})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items').all()
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})
