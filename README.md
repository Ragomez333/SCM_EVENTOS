# SCM Eventos — API de citas con Redis, RabbitMQ y workers

API REST con **FastAPI** para crear y cancelar citas por horario. Usa **Redis** como bloqueo distribuido (evitar doble reserva), **SQLite** para persistencia y **RabbitMQ** para publicar eventos que consumen uno o más **workers** (notificación simulada y registro en log).

## Requisitos

- Python 3.10+
- [Redis](https://redis.io/) en `localhost:6379`
- [RabbitMQ](https://www.rabbitmq.com/) en `localhost` (AMQP por defecto)

## Instalación

```bash
cd SCM_EVENTOS
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install fastapi uvicorn redis pika
```

## Servicios externos

Arranca Redis y RabbitMQ antes de la API y los workers. Ejemplos con Docker:

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management-alpine
```

## Uso

### 1. API

```bash
uvicorn main:app --reload
```

Documentación interactiva: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Workers (uno o varios terminales)

```bash
python worker.py 1
python worker.py 2
```

Cada worker escribe en `worker_<id>.log` según el identificador pasado por argumento.

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/crear_cita` | Body: `{"horarios": ["09:00", "10:00"]}`. Reserva con lock en Redis; si el horario ya está ocupado, responde rechazado. |
| `DELETE` | `/cancelar_cita` | Mismo body. Libera Redis y marca la cita como cancelada en SQLite. |
| `GET` | `/citas` | Lista todas las citas almacenadas. |

## Flujo de eventos

1. Al crear o cancelar una cita válida, la API publica un mensaje JSON en la cola `eventos` de RabbitMQ (`CITA_CREADA` / `CITA_CANCELADA`).
2. Los workers consumen la cola, simulan notificación (`asyncio.sleep`) y añaden una línea al log local.

## Base de datos

Se crea automáticamente el archivo `citas.db` (SQLite) con la tabla `citas` al iniciar la aplicación (`init_db()` en `main.py`).

## Estructura del proyecto

| Archivo | Rol |
|---------|-----|
| `main.py` | FastAPI: rutas y orquestación Redis + BD + producer |
| `database.py` | SQLite: inicialización, insert, update, listado |
| `redis_client.py` | Cliente Redis compartido |
| `producer.py` | Publicación a RabbitMQ (pika) |
| `worker.py` | Consumidor de la cola `eventos` |

## Notas

- El producer y los workers usan `localhost` para RabbitMQ; ajusta `ConnectionParameters` si usas otro host.
- Los workers usan `auto_ack=True`; en producción suele preferirse confirmación manual tras procesar correctamente el mensaje.
