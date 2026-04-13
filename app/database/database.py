import aiosqlite
from datetime import datetime

DB_PATH = "detector_ofertas.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT UNIQUE NOT NULL,
                nombre TEXT,
                marca TEXT,
                categoria TEXT,
                imagen TEXT,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS historial_precios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode TEXT NOT NULL,
                tienda TEXT NOT NULL,
                precio REAL NOT NULL,
                precio_original REAL,
                descuento_pct REAL,
                url TEXT,
                fuente TEXT,
                registrado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_historial_barcode 
            ON historial_precios(barcode, registrado_en DESC)
        """)
        await db.commit()

async def guardar_producto(barcode: str, nombre: str, marca: str,
                           categoria: str, imagen: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT OR IGNORE INTO productos 
            (barcode, nombre, marca, categoria, imagen)
            VALUES (?, ?, ?, ?, ?)
        """, (barcode, nombre, marca, categoria, imagen))
        await db.commit()

async def guardar_precio(barcode: str, tienda: str, precio: float,
                         precio_original: float = None,
                         descuento_pct: float = None,
                         url: str = None, fuente: str = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO historial_precios 
            (barcode, tienda, precio, precio_original, descuento_pct, url, fuente)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (barcode, tienda, precio, precio_original, descuento_pct, url, fuente))
        await db.commit()

async def obtener_historial(barcode: str, dias: int = 90) -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("""
            SELECT tienda, precio, precio_original, descuento_pct,
                   url, fuente, registrado_en
            FROM historial_precios
            WHERE barcode = ?
            AND registrado_en >= datetime('now', ? || ' days')
            ORDER BY registrado_en DESC
        """, (barcode, f"-{dias}"))
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]