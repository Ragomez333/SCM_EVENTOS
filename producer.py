import pika
import json

def enviar_evento(tipo: str, horario: str):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='eventos')
        channel.basic_publish(
            exchange='',
            routing_key='eventos',
            body=json.dumps({"tipo": tipo, "horario": horario})
        )
        connection.close()
    except Exception as e:
        print(f"[Producer] Error: {e}")