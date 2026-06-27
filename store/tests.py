from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from products.models import Category, Product
from cart.models import Cart
from orders.models import Order
from decimal import Decimal


class E2ETest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cat = Category.objects.create(name="Electrónica", slug="electronica")
        cls.cat = cat
        cls.prod_a = Product.objects.create(
            category=cat, name="Smartphone", slug="smartphone",
            description="Teléfono inteligente", price=299990, stock=10,
            image="https://picsum.photos/seed/smartphone/400/300",
        )
        cls.prod_b = Product.objects.create(
            category=cat, name="Laptop", slug="laptop",
            description="Laptop potente", price=899990, stock=5,
        )
        cls.prod_low = Product.objects.create(
            category=cat, name="Audífonos", slug="audifonos",
            description="Audífonos", price=49990, stock=1,
        )
        cls.admin = User.objects.create_user("admin", password="admin123", is_staff=True, is_superuser=True)
        cls.client_user = User.objects.create_user("cliente", password="cliente123")

    # ============ 1. CATÁLOGO ============

    def test_catalogo_carga_sin_auth(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Smartphone")
        self.assertContains(r, "Laptop")

    def test_detalle_producto(self):
        r = self.client.get(f'/product/{self.prod_a.pk}/')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Smartphone")
        self.assertContains(r, "299990,00")
        self.assertContains(r, "Stock disponible: 10")

    def test_filtro_categoria(self):
        r = self.client.get('/?category=electronica')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Smartphone")

    # ============ 2. AUTENTICACIÓN ============

    def test_login_cliente(self):
        r = self.client.post('/accounts/login/', {'username': 'cliente', 'password': 'cliente123'}, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['user'].is_authenticated)

    def test_login_admin(self):
        r = self.client.post('/accounts/login/', {'username': 'admin', 'password': 'admin123'}, follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.context['user'].is_authenticated)

    def test_login_fallido_muestra_error(self):
        r = self.client.post('/accounts/login/', {'username': 'cliente', 'password': 'mala'}, follow=True)
        self.assertContains(r, "incorrectos")

    def test_logout(self):
        self.client.login(username='cliente', password='cliente123')
        r = self.client.post('/accounts/logout/', follow=True)
        self.assertFalse(r.context['user'].is_authenticated)

    def test_ruta_protegida_redirige(self):
        r = self.client.get('/cart/')
        self.assertRedirects(r, '/accounts/login/?next=/cart/')

    # ============ 3. CARRITO ============

    def test_agregar_al_carrito(self):
        self.client.login(username='cliente', password='cliente123')
        r = self.client.post(f'/cart/add/{self.prod_a.pk}/', follow=True)
        msgs = [str(m) for m in get_messages(r.wsgi_request)]
        self.assertTrue(any("añadido" in m for m in msgs))
        self.assertEqual(Cart.objects.get(user__username='cliente').items.count(), 1)

    def test_agregar_repetido_incrementa(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_a.pk}/')
        self.client.post(f'/cart/add/{self.prod_a.pk}/')
        item = Cart.objects.get(user__username='cliente').items.first()
        self.assertEqual(item.quantity, 2)

    def test_agregar_sin_stock_muestra_error(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_low.pk}/')
        self.client.post(f'/cart/add/{self.prod_low.pk}/')
        r = self.client.post(f'/cart/add/{self.prod_low.pk}/', follow=True)
        msgs = [str(m) for m in get_messages(r.wsgi_request)]
        self.assertTrue(any("stock" in m.lower() for m in msgs))

    def test_carrito_muestra_items(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_a.pk}/')
        self.client.post(f'/cart/add/{self.prod_b.pk}/')
        r = self.client.get('/cart/')
        self.assertContains(r, "Smartphone")
        self.assertContains(r, "Laptop")
        self.assertContains(r, "1199980,00")

    def test_actualizar_cantidad(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_a.pk}/')
        item = Cart.objects.get(user__username='cliente').items.first()
        self.client.post(f'/cart/update/{item.pk}/', {'quantity': 5}, follow=True)
        item.refresh_from_db()
        self.assertEqual(item.quantity, 5)

    def test_actualizar_excede_stock(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_a.pk}/')
        item = Cart.objects.get(user__username='cliente').items.first()
        r = self.client.post(f'/cart/update/{item.pk}/', {'quantity': 999}, follow=True)
        msgs = [str(m) for m in get_messages(r.wsgi_request)]
        self.assertTrue(any("stock" in m.lower() for m in msgs))
        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_eliminar_del_carrito(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_a.pk}/')
        item = Cart.objects.get(user__username='cliente').items.first()
        self.client.post(f'/cart/remove/{item.pk}/', follow=True)
        self.assertEqual(Cart.objects.get(user__username='cliente').items.count(), 0)

    # ============ 4. CHECKOUT ============

    def test_checkout_exitoso(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_a.pk}/')
        self.client.post(f'/cart/add/{self.prod_b.pk}/')
        old_a = Product.objects.get(pk=self.prod_a.pk).stock
        old_b = Product.objects.get(pk=self.prod_b.pk).stock
        r = self.client.post('/orders/checkout/', {'confirm': 'on'}, follow=True)
        msgs = [str(m) for m in get_messages(r.wsgi_request)]
        self.assertTrue(any("Gracias" in m for m in msgs))
        self.assertEqual(Cart.objects.get(user__username='cliente').items.count(), 0)
        self.assertEqual(Product.objects.get(pk=self.prod_a.pk).stock, old_a - 1)
        self.assertEqual(Product.objects.get(pk=self.prod_b.pk).stock, old_b - 1)
        self.assertTrue(Order.objects.filter(user__username='cliente').exists())

    def test_checkout_carrito_vacio(self):
        self.client.login(username='cliente', password='cliente123')
        r = self.client.post('/orders/checkout/', {'confirm': 'on'}, follow=True)
        msgs = [str(m) for m in get_messages(r.wsgi_request)]
        self.assertTrue(any("vacío" in m for m in msgs))

    def test_checkout_stock_insuficiente(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_low.pk}/')
        Product.objects.filter(pk=self.prod_low.pk).update(stock=0)
        r = self.client.post('/orders/checkout/', {'confirm': 'on'}, follow=True)
        msgs = [str(m) for m in get_messages(r.wsgi_request)]
        self.assertTrue(any("stock" in m.lower() for m in msgs))

    def test_historial_ordenes(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_a.pk}/')
        self.client.post('/orders/checkout/', {'confirm': 'on'}, follow=True)
        r = self.client.get('/orders/')
        self.assertContains(r, "Smartphone")

    # ============ 5. CRUD ADMIN ============

    def test_admin_crea_producto(self):
        self.client.login(username='admin', password='admin123')
        self.client.post('/product/create/', {
            'category': self.cat.pk, 'name': 'Tablet',
            'description': 'Nueva', 'price': 199.99, 'stock': 20,
        }, follow=True)
        self.assertTrue(Product.objects.filter(name='Tablet').exists())

    def test_admin_edita_producto(self):
        self.client.login(username='admin', password='admin123')
        self.client.post(f'/product/{self.prod_a.pk}/update/', {
            'category': self.cat.pk, 'name': 'Smartphone Pro',
            'description': 'Upd', 'price': 399990, 'stock': 15,
        }, follow=True)
        self.prod_a.refresh_from_db()
        self.assertEqual(self.prod_a.name, 'Smartphone Pro')
        self.assertEqual(self.prod_a.price, Decimal('399990'))

    def test_admin_elimina_producto(self):
        self.client.login(username='admin', password='admin123')
        self.client.post(f'/product/{self.prod_b.pk}/delete/', follow=True)
        self.assertFalse(Product.objects.filter(pk=self.prod_b.pk).exists())

    def test_cliente_no_accede_crud(self):
        self.client.login(username='cliente', password='cliente123')
        r = self.client.get('/product/create/')
        self.assertEqual(r.status_code, 403)

    # ============ 6. VALIDACIONES ============

    def test_precio_cero_rechazado(self):
        self.client.login(username='admin', password='admin123')
        r = self.client.post('/product/create/', {
            'category': self.cat.pk, 'name': 'X',
            'description': '', 'price': 0, 'stock': 10,
        })
        self.assertContains(r, "mayor a cero")

    def test_stock_negativo_rechazado(self):
        self.client.login(username='admin', password='admin123')
        r = self.client.post('/product/create/', {
            'category': self.cat.pk, 'name': 'X',
            'description': '', 'price': 10, 'stock': -5,
        })
        self.assertContains(r, "no puede ser negativo")

    def test_cantidad_cero_rechazada(self):
        self.client.login(username='cliente', password='cliente123')
        self.client.post(f'/cart/add/{self.prod_a.pk}/')
        item = Cart.objects.get(user__username='cliente').items.first()
        r = self.client.post(f'/cart/update/{item.pk}/', {'quantity': 0}, follow=True)
        msgs = [str(m) for m in get_messages(r.wsgi_request)]
        self.assertTrue(any("mayor a cero" in m for m in msgs))

    # ============ 7. NAVBAR ============

    def test_navbar_muestra_login_sin_auth(self):
        r = self.client.get('/')
        self.assertContains(r, "Iniciar Sesión")
        self.assertNotContains(r, "Cerrar Sesión")

    def test_navbar_muestra_gestion_para_admin(self):
        self.client.login(username='admin', password='admin123')
        r = self.client.get('/')
        self.assertContains(r, "Gestión")

    def test_navbar_oculta_gestion_para_cliente(self):
        self.client.login(username='cliente', password='cliente123')
        r = self.client.get('/')
        self.assertNotContains(r, "Gestión")
