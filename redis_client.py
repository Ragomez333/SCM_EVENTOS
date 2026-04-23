import redis

# Conexión a Redis (coordinador)
r = redis.Redis(host='localhost', port=6379, decode_responses=True)