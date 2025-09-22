# scripts/create_tables.py
import asyncio
import sys
import os

# Configurar paths correctamente
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
project_dir = os.path.dirname(src_dir)

# Agregar src al path para poder importar módulos
sys.path.insert(0, src_dir)

print("Current dir:", current_dir)
print("Src dir:", src_dir)
print("Project dir:", project_dir)
print("Database URL:", os.environ.get("DATABASE_URL"))
print("Importing database components...")

try:
    from modulos.alianzas.infrastructure.db import engine, Base
    print("✅ Database components imported successfully")
except Exception as e:
    print(f"❌ Error importing database components: {e}")
    sys.exit(1)

try:
    # 👇 IMPORTA tus modelos para que se registren en Base.metadata
    from modulos.alianzas.infrastructure import models as _
    print("✅ Alianzas models imported successfully")
except Exception as e:
    print(f"❌ Error importing alianzas models: {e}")

try:
    # 👇 IMPORTA los modelos de saga para registrarlos en Base.metadata
    from modulos.sagas.infraestructura import dto as saga_models
    print("✅ Saga models imported successfully")
    print(f"Saga models attributes: {dir(saga_models)}")
except Exception as e:
    print(f"❌ Error importing saga models: {e}")
    print("Continuing without saga models...")

async def main():
    print("\nStarting table creation...")
    async with engine.begin() as conn:
        # Útil para depurar: ver qué tablas conoce el metadata
        def _debug(_conn):
            tables = list(Base.metadata.tables.keys())
            print(f"Tablas registradas ({len(tables)}): {tables}")
            for table_name, table in Base.metadata.tables.items():
                print(f"  - {table_name}: {[col.name for col in table.columns]}")
        
        await conn.run_sync(_debug)
        
        print("\nCreating tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Error running script: {e}")
        import traceback
        traceback.print_exc()
