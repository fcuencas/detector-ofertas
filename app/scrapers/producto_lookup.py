import httpx
from datetime import datetime

HEADERS = {
    "User-Agent": "DetectorOfertasFalsas/1.0 (contacto@detectorofertas.mx)"
}

async def buscar_por_barcode(barcode: str) -> dict:
    resultado = {
        "barcode": barcode,
        "encontrado": False,
        "fuentes": [],
        "timestamp": datetime.utcnow().isoformat()
    }
    async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
        try:
            r = await client.get(
                f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
            )
            data = r.json()
            if data.get("status") == 1:
                p = data["product"]
                resultado["nombre"] = (
                    p.get("product_name_es") or
                    p.get("product_name_en") or
                    p.get("product_name")
                )
                resultado["marca"] = p.get("brands")
                resultado["categoria"] = p.get("categories")
                resultado["imagen"] = p.get("image_url")
                resultado["cantidad"] = p.get("quantity")
                resultado["nutriscore"] = p.get("nutriscore_grade")
                resultado["encontrado"] = True
                resultado["fuentes"].append("open_food_facts")
        except Exception as e:
            resultado["error"] = str(e)
    return resultado


async def buscar_por_nombre(nombre: str) -> dict:
    async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
        try:
            r = await client.get(
                "https://world.openfoodfacts.org/api/v2/search",
                params={
                    "search_terms": nombre,
                    "page_size": 10,
                    "fields": "code,product_name,product_name_es,brands,image_small_url,nutriscore_grade"
                }
            )
            data = r.json()
            productos = data.get("products", [])
            return {
                "query": nombre,
                "total": data.get("count", 0),
                "resultados": [
                    {
                        "barcode": p.get("code"),
                        "nombre": (
                            p.get("product_name_es") or
                            p.get("product_name")
                        ),
                        "marca": p.get("brands"),
                        "imagen": p.get("image_small_url"),
                        "nutriscore": p.get("nutriscore_grade"),
                        "fuente": "open_food_facts"
                    }
                    for p in productos
                    if p.get("product_name") or p.get("product_name_es")
                ],
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": str(e), "query": nombre}