import statistics
from datetime import datetime, timedelta

def analizar_oferta(historial: list, precio_actual: float) -> dict:
    if len(historial) < 7:
        return {
            "veredicto": "SIN_DATOS",
            "emoji": "⚪",
            "mensaje": "No tenemos suficiente historial para analizar esta oferta.",
            "confianza": "baja",
            "precio_actual": precio_actual
        }

    hace_7_dias = datetime.utcnow() - timedelta(days=7)
    precios_referencia = [
        r["precio"] for r in historial
        if datetime.fromisoformat(r["registrado_en"]) < hace_7_dias
    ]

    if not precios_referencia:
        return {
            "veredicto": "SIN_DATOS",
            "emoji": "⚪",
            "mensaje": "Historial muy reciente, no podemos comparar precios.",
            "confianza": "baja",
            "precio_actual": precio_actual
        }

    precio_referencia = statistics.median(precios_referencia)

    hace_30_dias = datetime.utcnow() - timedelta(days=30)
    precios_30_dias = [
        r["precio"] for r in historial
        if datetime.fromisoformat(r["registrado_en"]) >= hace_30_dias
    ]
    precio_maximo_30d = max(precios_30_dias) if precios_30_dias else precio_actual

    ratio_actual = precio_actual / precio_referencia
    ratio_inflacion = precio_maximo_30d / precio_referencia

    if ratio_inflacion > 1.10 and ratio_actual < 1.05:
        pct_inflacion = round((ratio_inflacion - 1) * 100)
        return {
            "veredicto": "SOSPECHOSA",
            "emoji": "🔴",
            "mensaje": f"El precio subió {pct_inflacion}% en los últimos 30 días y ahora muestra ese nivel anterior como 'oferta'. Precio típico: ${precio_referencia:.2f}",
            "confianza": "alta" if len(precios_referencia) >= 30 else "media",
            "precio_actual": precio_actual,
            "precio_referencia": round(precio_referencia, 2),
            "observaciones": len(historial)
        }
    elif ratio_actual < 0.90:
        pct_descuento = round((1 - ratio_actual) * 100)
        return {
            "veredicto": "BUENA_OFERTA",
            "emoji": "🟢",
            "mensaje": f"El precio actual está {pct_descuento}% por debajo de su precio típico. Precio típico: ${precio_referencia:.2f}",
            "confianza": "alta" if len(precios_referencia) >= 30 else "media",
            "precio_actual": precio_actual,
            "precio_referencia": round(precio_referencia, 2),
            "observaciones": len(historial)
        }
    elif ratio_actual < 1.05:
        return {
            "veredicto": "PRECIO_NORMAL",
            "emoji": "🟡",
            "mensaje": f"Este es el precio habitual. No hay descuento real. Precio típico: ${precio_referencia:.2f}",
            "confianza": "alta" if len(precios_referencia) >= 30 else "media",
            "precio_actual": precio_actual,
            "precio_referencia": round(precio_referencia, 2),
            "observaciones": len(historial)
        }
    else:
        pct_alto = round((ratio_actual - 1) * 100)
        return {
            "veredicto": "PRECIO_ALTO",
            "emoji": "🔴",
            "mensaje": f"El precio actual está {pct_alto}% por encima de su precio típico. Precio típico: ${precio_referencia:.2f}",
            "confianza": "alta" if len(precios_referencia) >= 30 else "media",
            "precio_actual": precio_actual,
            "precio_referencia": round(precio_referencia, 2),
            "observaciones": len(historial)
        }