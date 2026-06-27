# Product Requirement Document (PRD) · E-Commerce MVP Final

## 1. Propósito del Producto
El propósito de este proyecto es consolidar un e-commerce totalmente funcional y estable que sirva como pieza clave para el portafolio profesional. La aplicación web permitirá a los usuarios autenticados navegar por un catálogo de productos, gestionar un carrito de compras interactivo (agregar, modificar cantidades, eliminar) y finalizar un pedido con su respectivo registro histórico. Asimismo, ofrecerá a los usuarios administradores una interfaz limpia para la gestión del inventario (CRUD). El sistema estará optimizado para una ejecución local rápida y preparado para su despliegue en la plataforma Render.

## 2. Tecnologías Core
* **Backend:** Django 5.x (Python)
* **Base de Datos:** SQLite3 (Configurada para persistencia local y en la nube)
* **Frontend:** HTML5, Tailwind CSS (v3 o v4 implementado mediante CDN o empaquetador básico)
* **Despliegue:** Render (Capa gratuita)

---

## 3. Alcance del MVP (Flujos y Funcionalidades)

### 3.1 Autenticación y Roles
El sistema contará con dos tipos de accesos diferenciados y protegidos por el sistema de autenticación nativo de Django:

| Rol | Permisos y Acceso |
| :--- | :--- |
| **Cliente (User)** | Iniciar sesión, cerrar sesión, visualizar el catálogo, acceder al detalle de productos, operar el carrito de compras y confirmar pedidos. |
| **Administrador (Staff)** | Iniciar sesión, cerrar sesión, acceder al panel de administración y realizar operaciones CRUD completas sobre el inventario de productos. |

> **Nota de UX:** Si un usuario no autenticado intenta agregar un producto al carrito o proceder al pago, el sistema lo redireccionará automáticamente a la vista de Login mediante un decorador (`@login_required`), mostrando un mensaje informativo.

### 3.2 Catálogo y Persistencia (Modelo de Datos)
La persistencia de la información se manejará mediante el ORM de Django con SQLite3. Se estructuran tres relaciones principales:

* **Producto (`Product`):** `id`, `nombre`, `descripcion`, `precio` (Decimal, max_digits=10, decimal_places=2), `stock` (Integer), `imagen` (URL o campo de archivo).
* **Carrito / Ítem de Carrito (`Cart` / `CartItem`):** Relación que asocia al usuario autenticado con los productos seleccionados y sus respectivas cantidades.
* **Orden / Ítem de Orden (`Order` / `OrderItem`):** Registro histórico inmutable de la compra. Almacena la referencia del usuario, fecha de creación, total y el desglose de productos con el precio congelado al momento de la transacción.

### 3.3 Carrito y Compra (Flujo Completo)
El flujo principal "Catálogo → Carrito → Confirmación" debe operar de forma estable y sin errores de cálculo matemático:
1. **Agregar/Quitar:** Botones directos con peticiones POST en las vistas de catálogo y detalle.
2. **Actualizar Cantidades:** Campos numéricos o botones (+ / -) dentro de la vista del carrito que validen en tiempo real el stock disponible en la base de datos antes de guardar.
3. **Cálculos:** Operaciones automatizadas en los métodos del modelo o en las vistas para devolver Subtotales ($\text{Precio} \times \text{Cantidad}$) y el Total General ($\sum \text{Subtotales}$).
4. **Confirmación de Compra:** Al presionar "Confirmar Compra", el sistema debe vaciar de forma atómica el carrito del usuario, descontar las unidades correspondientes del stock de cada producto y generar un registro único en la tabla `Orden`.

### 3.4 Interfaz de Usuario y Navegación (Tailwind CSS)
La interfaz gráfica se construirá con HTML5 semántico y Tailwind CSS para asegurar un diseño responsivo, limpio y profesional. Se requiere una barra de navegación (Navbar) global con comportamiento dinámico:
* **Enlaces Públicos/Clientes:** Logo/Inicio (Catálogo), Carrito (con un badge indicador del conteo de ítems) y Login/Logout.
* **Enlaces de Administración:** Botón de acceso al Panel de Gestión de Productos visible *únicamente* si `user.is_staff` es verdadero.

---

## 4. Validaciones y Mensajes de Feedback
Para garantizar una experiencia de usuario robusta y mitigar errores en la base de datos se implementarán de forma obligatoria:
* **Validación en Formularios (Django Forms):** Los campos de precio y cantidad deben ser estrictamente superiores a cero (`precio > 0` y `cantidad > 0`). Todos los campos obligatorios deben estar controlados del lado del cliente y del servidor.
* **Mensajes de Usuario (Django Messages Framework):**
    * *Éxito (Success):* "Producto añadido al carrito", "Cantidad actualizada", "Compra confirmada con éxito. ¡Gracias por tu pedido!".
    * *Error/Alerta (Error/Warning):* "No hay suficiente stock disponible para este producto", "Por favor, inicia sesión para gestionar tu carrito".

---

## 5. Estrategia de Despliegue en Render (Con SQLite3)

Para desplegar el proyecto en la capa gratuita de Render utilizando **SQLite3** sin perder los datos en cada reinicio del servidor, se debe hacer uso de la característica **Persistent Disk** de Render desde su panel web, junto con las siguientes configuraciones de software:

### 5.1 Configuración de la Base de Datos (`settings.py`)
Modificar el diccionario `DATABASES` para que Django detecte el entorno de producción y guarde el archivo `.sqlite3` en el volumen persistente:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Detectar la variable de entorno que Render asigna automáticamente
IS_RENDER = os.environ.get('RENDER')

if IS_RENDER:
    # Ruta apuntando al directorio del disco persistente configurado en Render
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/data/db.sqlite3',
        }
    }
else:
    # Configuración estándar para desarrollo local
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```
