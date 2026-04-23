from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import asyncio

from redis_client import r
from producer import enviar_evento
from database import init_db, guardar_cita, cancelar_cita_db, listar_citas

app = FastAPI()
init_db()

class CitaRequest(BaseModel):
    horarios: List[str]

@app.post("/crear_cita")
async def crear_cita(request: CitaRequest):
    resultados = []
    for horario in request.horarios:
        lock = r.set(f"cita:{horario}", "ocupado", nx=True, ex=3600)
        if not lock:
            resultados.append({"horario": horario, "estado": "rechazado", "motivo": "Horario ocupado"})
            continue
        guardar_cita(horario)
        enviar_evento("CITA_CREADA", horario)
        await asyncio.sleep(0.1)
        resultados.append({"horario": horario, "estado": "creada"})
    return {"resultados": resultados}

@app.delete("/cancelar_cita")
async def cancelar_cita(request: CitaRequest):
    resultados = []
    for horario in request.horarios:
        if not r.exists(f"cita:{horario}"):
            resultados.append({"horario": horario, "estado": "rechazado", "motivo": "Horario no encontrado"})
            continue
        r.delete(f"cita:{horario}")
        if not cancelar_cita_db(horario):
            resultados.append({"horario": horario, "estado": "rechazado", "motivo": "No se pudo cancelar en BD"})
            continue
        enviar_evento("CITA_CANCELADA", horario)
        await asyncio.sleep(0.1)
        resultados.append({"horario": horario, "estado": "cancelada"})
    return {"resultados": resultados}

@app.get("/citas")
async def obtener_citas():
    return {"citas": listar_citas()}