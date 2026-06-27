from django.db import migrations


def update_prices(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    updates = {
        'smartphone-x10': 299990,
        'laptop-pro-15': 899990,
        'auriculares-bluetooth': 79990,
        'cargador-usb-c-65w': 39990,
        'tablet-mini-8': 199990,
        'camiseta-algodon': 19990,
        'chaqueta-invierno': 89990,
        'zapatillas-runner': 129990,
        'gorra-clasica': 14990,
        'mochila-urbana': 49990,
        'python-101': 34990,
        'django-avanzado': 44990,
        'algoritmos-y-estructuras': 39990,
        'data-science-esencial': 49990,
        'clean-code': 29990,
        'lampara-led-escritorio': 59990,
        'set-de-sartenes': 79990,
        'organizador-escritorio': 24990,
        'marco-de-fotos-8x10': 12990,
        'pesas-5kg-par': 34990,
        'yoga-mat-premium': 29990,
        'cuerda-saltar-speed': 15990,
        'botella-deporte-750ml': 18990,
    }
    for slug, price in updates.items():
        Product.objects.filter(slug=slug).update(price=price)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_prices),
    ]
