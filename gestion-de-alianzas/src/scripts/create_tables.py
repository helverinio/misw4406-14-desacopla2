# scripts/create_tables.py
import asyncio
from src.modulos.alianzas.infrastructure.db import engine, Base

# 👇 IMPORTA tus modelos para que se registren en Base.metadata
from src.modulos.alianzas.infrastructure import models as _  # noqa: F401

async def main():
    async with engine.begin() as conn:
        # Útil para depurar: ver qué tablas conoce el metadata
        def _debug(_conn):
            print("Tablas registradas:", list(Base.metadata.tables.keys()))
        await conn.run_sync(_debug)

        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(main())
