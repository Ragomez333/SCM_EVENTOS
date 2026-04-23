import pika
import asyncio
import json
import sys

WORKER_ID = sys.argv[1] if len(sys.argv) > 1 else "1"

async def notificar(tipo: str, horario: str):
    await asyncio.sleep(0.5)
    print(f"[Worker-{WORKER_ID}][Notificación] {tipo} - {horario}")

async def registrar_log(tipo: str, horario: str):
    await asyncio.sleep(0.5)
    with open(f"worker_{WORKER_ID}.log", "a") as f:
        f.write(f"{tipo} | horario={horario}\n")
    print(f"[Worker-{WORKER_ID}][Log] {tipo} | {horario}")

async def procesar_evento(tipo: str, horario: str):
    await asyncio.gather(notificar(tipo, horario), registrar_log(tipo, horario))

def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode())
        asyncio.run(procesar_evento(data.get("tipo", "DESCONOCIDO"), data.get("horario", "N/A")))
    except Exception as e:
        print(f"[Worker-{WORKER_ID}] Error: {e}")

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='eventos')
channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='eventos', on_message_callback=callback, auto_ack=True)

print(f"[Worker-{WORKER_ID}] Escuchando...")
channel.start_consuming()