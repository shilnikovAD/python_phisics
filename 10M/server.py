from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
import uvicorn
import os
import uuid

from ising_model import (
    IsingModel2D,
    get_model,
    scan_temperature_ferromagnetic,
    find_critical_temperature,
)


app = FastAPI(title="Ising Model 2D Simulation")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)


# Pydantic модели для API
class InitRequest(BaseModel):
    size: int = Field(30, ge=10, le=100)
    T: float = Field(1.0, ge=0.1, le=5.0)
    J: float = Field(1.0, ge=-2.0, le=2.0)
    B: float = Field(0.0, ge=-1.0, le=1.0)
    spins: Optional[List[List[int]]] = None


class StepRequest(BaseModel):
    session_id: str
    n_steps: int = Field(1, ge=1, le=10000)


class FlipRequest(BaseModel):
    session_id: str
    i: int
    j: int


class UpdateParamsRequest(BaseModel):
    session_id: str
    T: Optional[float] = None
    J: Optional[float] = None
    B: Optional[float] = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Интерактивная 2D симуляция модели Изинга"""
    return FileResponse(os.path.join(STATIC_DIR, "ising2d.html"))


@app.post("/api/init")
async def init_model(req: InitRequest):
    """
    Инициализировать новую модель или обновить существующую
    """
    try:
        session_id = str(uuid.uuid4())
        model = IsingModel2D(size=req.size, T=req.T, J=req.J, B=req.B)

        if req.spins:
            model.set_spins(req.spins)

        # Сохраняем в глобальное хранилище
        from ising_model import _models

        _models[session_id] = model

        return JSONResponse(
            content={
                "success": True,
                "session_id": session_id,
                "state": model.get_state(),
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/step")
async def run_steps(req: StepRequest):
    """
    Выполнить n шагов Монте-Карло
    """
    try:
        model = get_model(req.session_id)
        accepted, spins = model.run_steps(req.n_steps)

        return JSONResponse(
            content={
                "success": True,
                "accepted": accepted,
                "state": model.get_state(),
            }
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/flip")
async def flip_spin(req: FlipRequest):
    """
    Перевернуть спин в позиции (i, j)
    """
    try:
        model = get_model(req.session_id)
        model.flip_spin(req.i, req.j)

        return JSONResponse(content={"success": True, "state": model.get_state()})
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/update_params")
async def update_params(req: UpdateParamsRequest):
    """
    Обновить параметры модели (T, J, B)
    """
    try:
        model = get_model(req.session_id)

        if req.T is not None:
            model.T = req.T
        if req.J is not None:
            model.J = req.J
        if req.B is not None:
            model.B = req.B

        return JSONResponse(content={"success": True, "state": model.get_state()})
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# М10Б: Ферромагнетизм - API endpoints
# ============================================================================


class FerromagneticScanRequest(BaseModel):
    size: int = Field(20, ge=10, le=50, description="Размер решетки")
    J: float = Field(1.0, ge=0.1, le=2.0, description="Обменное взаимодействие")
    B: float = Field(0.0, ge=-1.0, le=1.0, description="Внешнее поле")
    T_min: float = Field(0.5, ge=0.1, le=2.0)
    T_max: float = Field(4.0, ge=2.0, le=6.0)
    T_steps: int = Field(25, ge=10, le=50)
    equilibration_steps: int = Field(2000, ge=500, le=10000)
    measurement_steps: int = Field(1000, ge=500, le=5000)


class CriticalTemperatureRequest(BaseModel):
    size: int = Field(20, ge=10, le=50)
    J: float = Field(1.0, ge=0.1, le=2.0)
    T_min: float = Field(1.5, ge=0.5, le=2.0)
    T_max: float = Field(3.5, ge=2.5, le=5.0)
    T_steps: int = Field(30, ge=15, le=50)


@app.post("/api/ferromagnetic_scan")
async def ferromagnetic_scan(req: FerromagneticScanRequest):
    """
    М10Б: Сканирование ферромагнетика по температурам

    Возвращает:
    - ⟨M⟩(T) - функция намагниченности
    - χ(T) - восприимчивость
    - ⟨E⟩(T) - энергия
    """
    try:
        result = scan_temperature_ferromagnetic(
            size=req.size,
            J=req.J,
            B=req.B,
            T_min=req.T_min,
            T_max=req.T_max,
            T_steps=req.T_steps,
            equilibration_steps=req.equilibration_steps,
            measurement_steps=req.measurement_steps,
        )
        return JSONResponse(content={"success": True, "data": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/find_critical_temperature")
async def find_tc(req: CriticalTemperatureRequest):
    """
    М10Б: Определение температуры фазового перехода T₀ (T_c)

    Методы:
    1. Максимум восприимчивости χ
    2. Пересечение ⟨|M|⟩ с порогом

    Теория для 2D: T_c ≈ 2.269 * J
    """
    try:
        result = find_critical_temperature(
            size=req.size,
            J=req.J,
            T_min=req.T_min,
            T_max=req.T_max,
            T_steps=req.T_steps,
        )
        return JSONResponse(content={"success": True, "data": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Монтируем статические файлы
try:
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
except Exception:
    pass


if __name__ == "__main__":
    print("Запуск сервера симуляции спиновых систем...")
    print("Откройте браузер: http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
