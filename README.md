# LOUD // Backend para Venta de Entradas

¡Hola! Este repositorio contiene el backend para la plataforma de eventos "LOUD". El objetivo de este proyecto fue crear un sistema rápido, ordenado y preparado para el mundo real, usando buenas prácticas de programación, caché para que cargue súper rápido y protección contra bots.

## 🚀 Cómo funciona nuestra Infraestructura (Docker Compose)

Todo el proyecto se levanta con un solo comando gracias a Docker. Usamos 5 piezas clave que trabajan en equipo:

1. **Nginx:** Es nuestro guardia de tráfico. Recibe todas las peticiones y decide a dónde enviarlas (el panel admin, la API o el frontend).
2. **PostgreSQL:** Nuestra base de datos principal donde guardamos todos los eventos y entradas.
3. **Redis:** Una memoria súper rápida que usamos para dos cosas: bloquear bots y guardar datos temporalmente (caché) para responder más rápido.
4. **Django (Admin):** Lo usamos exclusivamente como un panel de administración visual y fácil de usar para gestionar los eventos.
5. **FastAPI:** El corazón del proyecto. Una API súper rápida que se comunica con el frontend para mostrar los eventos y procesar las cosas.

## 📊 Modelo de Datos (Opción A)

Elegimos trabajar con el dominio de **Venta de Entradas para Conciertos y Eventos**. 

## 🏛 Arquitectura C4

### ¿Cómo organizamos la base de datos?

* **Lugares y Eventos separados:** El lugar del evento (`Venue`) está separado del evento en sí (`Event`). Así no repetimos la misma dirección cien veces y las búsquedas son más rápidas.
* **Entradas inteligentes:** Creamos un modelo `TicketTier` (ej. General, VIP) que controla cuántas entradas hay en total y cuántas quedan disponibles en tiempo real.
* **UUIDs:** En lugar de usar IDs normales (1, 2, 3...), usamos códigos únicos largos (UUID). Esto hace que el sistema sea más seguro y difícil de predecir.

## 🗄 Modelo de Base de Datos (Diagrama ER)

![Diagrama Entidad-Relación](imagenes/diagrama.png)

## 🛠 Buenas Prácticas y Código Limpio (SOLID)

En la parte de FastAPI nos aseguramos de no mezclar todo el código en un solo archivo. Aplicamos principios de diseño para mantenerlo limpio:

* **Cada cosa en su lugar (SRP):** Las rutas solo reciben peticiones, y los servicios manejan la lógica. No mezclamos cosas.
* **Patrón Repositorio:** Sacamos todas las consultas de la base de datos (SQL) y las pusimos en su propia capa.
* **Inyección de Dependencias:** Usamos `Depends` en FastAPI para conectar nuestras diferentes partes (como la base de datos o el caché) sin "amarrar" el código.
* **Pydantic:** Usamos esquemas para asegurarnos de que los datos que entran y salen tienen el formato exacto que necesitamos, ni más ni menos.

## 💾 Creación de Datos de Prueba (Seed)

Para no tener que registrar eventos a mano, creamos un script (`seed_data.py`).

* En lugar de guardar los datos uno por uno (lo cual tomaría horas), usamos `bulk_create` para guardar todo de golpe.
* Con un solo comando generamos **300 eventos** y **150,000 reservas**, dejando el sistema listo para hacer pruebas de carga.

## 🛡 Lógica y Seguridad

### Evitando sobreventas (Race Conditions)

¿Qué pasa si dos personas intentan comprar la última entrada al mismo tiempo? Lo resolvimos directamente en la base de datos poniendo una regla (`CHECK constraint`) que prohíbe que el número de entradas disponibles baje de cero. Si pasa, la base de datos bloquea la segunda compra.

### Caché a prueba de fallos

Guardamos las respuestas de la API en Redis por 30 segundos para que todo cargue al instante. Pero si Redis se llega a caer o fallar, la API no se muere; simplemente se da cuenta y va a buscar los datos directo a PostgreSQL.

### Bloqueo de Bots (Rate Limiting)

Para evitar ataques o bots, configuramos Redis para que cuente cuántas veces entra una IP. Si alguien hace más de 20 peticiones por minuto, le bloqueamos el acceso y le mandamos un error `429 Too Many Requests`.

## 🌍 Zonas Horarias y Seguridad Extra

* **Fechas:** Guardamos todas las fechas en formato universal (UTC) y nos aseguramos de que el sistema sepa exactamente qué zona horaria usar al devolver los datos, evitando desfases.
* **Nginx:** Apagamos la opción que muestra la versión de Nginx (`server_tokens off;`). Así, si alguien intenta buscar vulnerabilidades en nuestro servidor, no sabrá qué versión exacta estamos usando.

## 🧪 Pruebas Automatizadas

Escribimos tests con `pytest` para asegurarnos de que no rompemos nada por accidente. Las pruebas verifican:

* Que la API esté viva.
* Que los eventos se devuelvan en el formato correcto y con la paginación bien hecha.
* Que el sistema devuelva un error 404 si buscas un evento que no existe.
* Que nuestro escudo anti-bots realmente bloquee a quien haga demasiadas peticiones.

---

## 🚀 Cómo ejecutar el proyecto

**1. Configurar variables de entorno:**
```bash
cp .env.example .env

```

**2. Levantar los contenedores:**

```bash
docker-compose up -d --build

```

*(Espera unos 30 segundos para que la base de datos inicie por completo).*

**3. Poblar la base de datos (Seed):**

```bash
docker exec -it django_admin python manage.py seed_data

```

**4. Ejecutar pruebas automatizadas:**

```bash
docker exec -it fastapi_backend pytest tests/

```

**5. Enlaces de acceso rápido:**

* 🎟️ **Frontend:** [http://localhost/](https://www.google.com/search?q=http://localhost/)
* ⚙️ **Panel Admin:** [http://localhost/admin/](https://www.google.com/search?q=http://localhost/admin/) *(User: `admin` | Pass: `admin123`)*
* 📡 **API Pública:** [http://localhost/api/v1/events/](https://www.google.com/search?q=http://localhost/api/v1/events/)
* 📖 **Docs API (Swagger):** [http://localhost/api/openapi.json](https://www.google.com/search?q=http://localhost/api/openapi.json)

**6. Detener el proyecto:**

```bash
docker-compose down

```
---

## 📝 Retrospectiva del Proyecto

**De lo que me siento más orgullosa:**
Me enorgullece muchísimo haber logrado que el panel de administración funcione correctamente. Anteriormente pasé semanas intentando hacer tareas similares sin éxito, así que ver que esta vez, a pesar de todos los errores que cometí en el proceso, logré sacarlo adelante y hacerlo funcionar, es un gran logro personal para mí.

**De lo que me siento menos conforme:**
Definitivamente, de la cantidad de errores que fui cometiendo a lo largo del desarrollo. Muchas veces lograba que una parte del código funcionara, y al intentar mejorar o tocar otra cosa, lo anterior dejaba de dar el resultado esperado. Es un proceso frustrante, pero entiendo que es parte del aprendizaje.
