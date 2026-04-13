from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.scrapers.producto_lookup import buscar_por_barcode, buscar_por_nombre
from app.database.database import init_db, guardar_producto, guardar_precio, obtener_historial
from app.detector import analizar_oferta

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Detector de Ofertas Falsas API",
    description="API para analizar historial de precios en Mexico",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "mensaje": "Detector de Ofertas Falsas API",
        "version": "0.1.0",
        "status": "funcionando"
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/producto/barcode/{barcode}")
async def get_producto_por_barcode(barcode: str):
    return await buscar_por_barcode(barcode)

@app.get("/producto/buscar")
async def get_buscar_producto(q: str):
    return await buscar_por_nombre(q)

@app.post("/precio/registrar")
async def registrar_precio(
    barcode: str,
    tienda: str,
    precio: float,
    precio_original: float = None,
    url: str = None
):
    descuento = None
    if precio_original and precio_original > 0:
        descuento = round((1 - precio / precio_original) * 100, 2)

    await guardar_precio(
        barcode=barcode,
        tienda=tienda,
        precio=precio,
        precio_original=precio_original,
        descuento_pct=descuento,
        url=url,
        fuente="manual"
    )
    return {"mensaje": "Precio registrado correctamente", "barcode": barcode}

@app.get("/precio/historial/{barcode}")
async def get_historial(barcode: str, dias: int = 90):
    historial = await obtener_historial(barcode, dias)
    return {
        "barcode": barcode,
        "dias": dias,
        "total_registros": len(historial),
        "historial": historial
    }

@app.get("/analizar/{barcode}")
async def analizar_producto(barcode: str, precio_actual: float):
    historial = await obtener_historial(barcode, dias=90)
    analisis = analizar_oferta(historial, precio_actual)
    return {
        "barcode": barcode,
        "analisis": analisis,
        "historial_disponible": len(historial)
    }