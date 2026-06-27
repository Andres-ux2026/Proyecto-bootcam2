from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from products.models import Category, Product


PRODUCTS_BY_CATEGORY = {
    "Electrónica": [
        {"name": "Smartphone X10", "price": 299.99, "stock": 25,
         "description": "Smartphone con pantalla AMOLED de 6.5\", 128GB de almacenamiento y cámara de 48MP.",
         "image": "https://picsum.photos/seed/smartphone/400/300"},
        {"name": "Laptop Pro 15", "price": 899.99, "stock": 15,
         "description": "Laptop con procesador Intel i7, 16GB RAM, SSD 512GB y pantalla Full HD 15.6\".",
         "image": "https://picsum.photos/seed/laptop/400/300"},
        {"name": "Auriculares Bluetooth", "price": 79.99, "stock": 40,
         "description": "Auriculares inalámbricos con cancelación de ruido activa y 30h de batería.",
         "image": "https://picsum.photos/seed/auriculares/400/300"},
        {"name": "Cargador USB-C 65W", "price": 39.99, "stock": 60,
         "description": "Cargador GaN compacto de 65W con puerto USB-C compatible con laptops y smartphones.",
         "image": "https://picsum.photos/seed/cargador/400/300"},
        {"name": "Tablet Mini 8", "price": 199.99, "stock": 30,
         "description": "Tablet de 8.4\" con 64GB, ideal para lectura y entretenimiento portátil.",
         "image": "https://picsum.photos/seed/tablet/400/300"},
    ],
    "Ropa": [
        {"name": "Camiseta Algodón", "price": 19.99, "stock": 100,
         "description": "Camiseta de algodón orgánico 100%, corte regular, disponible en varios colores.",
         "image": "https://picsum.photos/seed/camiseta/400/300"},
        {"name": "Chaqueta Invierno", "price": 89.99, "stock": 20,
         "description": "Chaqueta térmica con relleno de pluma sintética, resistente al agua y al viento.",
         "image": "https://picsum.photos/seed/chaqueta/400/300"},
        {"name": "Zapatillas Runner", "price": 129.99, "stock": 35,
         "description": "Zapatillas deportivas con amortiguación avanzada y suela de goma antideslizante.",
         "image": "https://picsum.photos/seed/zapatillas/400/300"},
        {"name": "Gorra Clásica", "price": 14.99, "stock": 80,
         "description": "Gorra ajustable de algodón con visera curva y diseño clásico.",
         "image": "https://picsum.photos/seed/gorra/400/300"},
        {"name": "Mochila Urbana", "price": 49.99, "stock": 45,
         "description": "Mochila de 25L con compartimento para laptop, impermeable y con puerto USB.",
         "image": "https://picsum.photos/seed/mochila/400/300"},
    ],
    "Libros": [
        {"name": "Python 101", "price": 34.99, "stock": 50,
         "description": "Guía completa para principiantes en programación con Python. Ejercicios prácticos incluidos.",
         "image": "https://picsum.photos/seed/python/400/300"},
        {"name": "Django Avanzado", "price": 44.99, "stock": 30,
         "description": "Técnicas avanzadas de desarrollo web con Django: APIs, testing y despliegue.",
         "image": "https://picsum.photos/seed/django/400/300"},
        {"name": "Algoritmos y Estructuras", "price": 39.99, "stock": 25,
         "description": "Fundamentos de algoritmos, estructuras de datos y optimización con ejemplos en Python.",
         "image": "https://picsum.photos/seed/algoritmos/400/300"},
        {"name": "Data Science Esencial", "price": 49.99, "stock": 20,
         "description": "Introducción al análisis de datos con pandas, numpy y visualización con matplotlib.",
         "image": "https://picsum.photos/seed/datascience/400/300"},
        {"name": "Clean Code", "price": 29.99, "stock": 40,
         "description": "Principios de código limpio, refactorización y buenas prácticas de programación.",
         "image": "https://picsum.photos/seed/cleancode/400/300"},
    ],
    "Hogar": [
        {"name": "Lámpara LED Escritorio", "price": 59.99, "stock": 30,
         "description": "Lámpara LED regulable con temperatura de color ajustable y puerto USB de carga.",
         "image": "https://picsum.photos/seed/lampara/400/300"},
        {"name": "Set de Sartenes", "price": 79.99, "stock": 20,
         "description": "Set de 3 sartenes antiadherentes con recubrimiento cerámico, aptos para inducción.",
         "image": "https://picsum.photos/seed/sartenes/400/300"},
        {"name": "Organizador Escritorio", "price": 24.99, "stock": 50,
         "description": "Organizador modular de bambú con compartimentos para accesorios de oficina.",
         "image": "https://picsum.photos/seed/organizador/400/300"},
        {"name": "Marco de Fotos 8x10", "price": 12.99, "stock": 70,
         "description": "Marco de fotos clásico de madera con respaldo plegable y vidrio protector.",
         "image": "https://picsum.photos/seed/marco/400/300"},
    ],
    "Deportes": [
        {"name": "Pesas 5kg (Par)", "price": 34.99, "stock": 25,
         "description": "Par de pesas con recubrimiento de neopreno, agarre ergonómico y diseño compacto.",
         "image": "https://picsum.photos/seed/pesas/400/300"},
        {"name": "Yoga Mat Premium", "price": 29.99, "stock": 40,
         "description": "Esterilla de yoga de 6mm, antideslizante, con alineación guiada y bolsa de transporte.",
         "image": "https://picsum.photos/seed/yoga/400/300"},
        {"name": "Cuerda Saltar Speed", "price": 15.99, "stock": 60,
         "description": "Cuerda de saltar profesional con rodamientos de bolas y cables de acero ajustables.",
         "image": "https://picsum.photos/seed/cuerda/400/300"},
        {"name": "Botella Deporte 750ml", "price": 18.99, "stock": 80,
         "description": "Botella térmica de acero inoxidable con aislamiento al vacío, mantiene 24h frío.",
         "image": "https://picsum.photos/seed/botella/400/300"},
    ],
}


class Command(BaseCommand):
    help = "Siembra la base de datos con categorías, 20 productos y 2 usuarios de prueba"

    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_true', help='Skip confirmation')

    def handle(self, *args, **options):
        self.stdout.write("Creando usuarios...")
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={"is_staff": True, "is_superuser": True},
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Admin creado (admin / admin123)"))
        else:
            self.stdout.write("  - Admin ya existe")

        cliente, created = User.objects.get_or_create(
            username="cliente",
            defaults={"is_staff": False, "is_superuser": False},
        )
        if created:
            cliente.set_password("cliente123")
            cliente.save()
            self.stdout.write(self.style.SUCCESS("  ✓ Cliente creado (cliente / cliente123)"))
        else:
            self.stdout.write("  - Cliente ya existe")

        self.stdout.write("Creando categorías y productos...")
        total_products = 0
        for cat_name, products_data in PRODUCTS_BY_CATEGORY.items():
            cat_slug = cat_name.lower().replace(" ", "-").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
            category, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={"slug": cat_slug},
            )
            if created:
                self.stdout.write(f"  ✓ Categoría '{cat_name}' creada")
            else:
                self.stdout.write(f"  - Categoría '{cat_name}' ya existe")

            for prod_data in products_data:
                name = prod_data["name"]
                slug = name.lower().replace(" ", "-")
                Product.objects.get_or_create(
                    slug=slug,
                    defaults={
                        "category": category,
                        "name": name,
                        "description": prod_data["description"],
                        "price": prod_data["price"],
                        "stock": prod_data["stock"],
                        "image": prod_data["image"],
                    }
                )
                total_products += 1

        self.stdout.write(self.style.SUCCESS(f"  ✓ {total_products} productos creados"))
        self.stdout.write(self.style.SUCCESS("¡Seed completado exitosamente!"))
