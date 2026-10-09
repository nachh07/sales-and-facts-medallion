# Databricks notebook source
# MAGIC %md
# MAGIC ## Setup Landing Zone — Unity Catalog
# MAGIC
# MAGIC Este script crea la infraestructura necesaria para la **landing zone** del proyecto.
# MAGIC
# MAGIC ### ¿Qué crea este script?
# MAGIC - **Catálogo `landing`**: Catálogo dedicado para recibir archivos crudos desde el sistema fuente.
# MAGIC - **Schema `origin_system`**: Schema que agrupa los datos del sistema de origen (ventas/facts).
# MAGIC - **Volume `raw_data`**: Volumen donde se depositan los archivos CSV tal como llegan.
# MAGIC
# MAGIC ### Ruta resultante
# MAGIC ```
# MAGIC /Volumes/landing/origin_system/raw_data/
# MAGIC     ├── Venta.csv
# MAGIC     ├── Clientes.csv
# MAGIC     ├── Productos.csv
# MAGIC     ├── Sucursales.csv
# MAGIC     ├── Empleados.csv
# MAGIC     ├── Compra.csv
# MAGIC     ├── Gasto.csv
# MAGIC     ├── TiposDeGasto.csv
# MAGIC     ├── CanalDeVenta.csv
# MAGIC     ├── Proveedores.csv
# MAGIC     └── Calendario.csv
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1. Parámetros de configuración

# COMMAND ----------

# Parámetros — modificar según el entorno
LANDING_CATALOG  = "landing"
ORIGIN_SCHEMA    = "origin_system"
RAW_VOLUME       = "raw_data"

print(f"Catálogo destino  : {LANDING_CATALOG}")
print(f"Schema destino    : {ORIGIN_SCHEMA}")
print(f"Volume a crear    : {RAW_VOLUME}")
print(f"Ruta resultante   : /Volumes/{LANDING_CATALOG}/{ORIGIN_SCHEMA}/{RAW_VOLUME}/")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2. Crear catálogo `landing` (si no existe)

# COMMAND ----------

spark.sql(f"""
    CREATE CATALOG IF NOT EXISTS {LANDING_CATALOG}
    COMMENT 'Catálogo para la landing zone — archivos crudos del sistema fuente.'
""")

print(f"✅ Catálogo '{LANDING_CATALOG}' listo.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3. Crear schema `origin_system` dentro de `landing`

# COMMAND ----------

spark.sql(f"""
    CREATE SCHEMA IF NOT EXISTS {LANDING_CATALOG}.{ORIGIN_SCHEMA}
    COMMENT 'Schema que representa el sistema de origen de ventas y hechos.'
""")

print(f"✅ Schema '{LANDING_CATALOG}.{ORIGIN_SCHEMA}' listo.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4. Crear volume `raw_data`
# MAGIC
# MAGIC > **Nota**: En Databricks Free Edition (Community Edition) los volúmenes son **managed**,
# MAGIC > lo que significa que Databricks gestiona la ubicación de almacenamiento.
# MAGIC > En ediciones de pago podés crear **external volumes** apuntando a tu propio bucket/blob.

# COMMAND ----------

spark.sql(f"""
    CREATE VOLUME IF NOT EXISTS {LANDING_CATALOG}.{ORIGIN_SCHEMA}.{RAW_VOLUME}
    COMMENT 'Volume para archivos CSV crudos del sistema de ventas. Simula una landing zone en cloud storage.'
""")

print(f"✅ Volume '{LANDING_CATALOG}.{ORIGIN_SCHEMA}.{RAW_VOLUME}' listo.")
print(f"📁 Ruta de acceso: /Volumes/{LANDING_CATALOG}/{ORIGIN_SCHEMA}/{RAW_VOLUME}/")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 5. Verificar la creación — listado del volume

# COMMAND ----------

volume_path = f"/Volumes/{LANDING_CATALOG}/{ORIGIN_SCHEMA}/{RAW_VOLUME}"

try:
    files = dbutils.fs.ls(volume_path)
    if files:
        print(f"📂 Contenido actual de {volume_path}:")
        for f in files:
            print(f"   {f.name}  ({f.size:,} bytes)")
    else:
        print(f"📂 El volume {volume_path} está vacío.")
        print("👉 Próximo paso: subir los archivos CSV al volume usando 'Upload to Volume' en la UI de Databricks.")
except Exception as e:
    print(f"⚠️  Error al listar el volume: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 6. Instrucciones para subir archivos al Volume
# MAGIC
# MAGIC **Opción A — Desde la UI de Databricks (recomendado para Free Edition):**
# MAGIC 1. Ir a **Catalog** → `landing` → `origin_system` → `raw_data`
# MAGIC 2. Hacer clic en **"Upload to this volume"**
# MAGIC 3. Seleccionar todos los archivos CSV del directorio de datos
# MAGIC
# MAGIC **Opción B — Desde este notebook (si los archivos están en DBFS):**
# MAGIC ```python
# MAGIC # Ejemplo para copiar desde DBFS a un volume
# MAGIC archivos = ["Venta.csv", "Clientes.csv", "Productos.csv", "Sucursales.csv",
# MAGIC             "Empleados.csv", "Compra.csv", "Gasto.csv", "TiposDeGasto.csv",
# MAGIC             "CanalDeVenta.csv", "Proveedores.csv", "Calendario.csv"]
# MAGIC
# MAGIC origen_dbfs = "dbfs:/FileStore/raw_data"  # ajustar según tu ruta en DBFS
# MAGIC destino    = f"/Volumes/{LANDING_CATALOG}/{ORIGIN_SCHEMA}/{RAW_VOLUME}"
# MAGIC
# MAGIC for archivo in archivos:
# MAGIC     dbutils.fs.cp(f"{origen_dbfs}/{archivo}", f"{destino}/{archivo}")
# MAGIC     print(f"  Copiado: {archivo}")
# MAGIC ```
# MAGIC
# MAGIC **Opción C — Databricks CLI:**
# MAGIC ```bash
# MAGIC databricks fs cp ./data/Venta.csv dbfs:/Volumes/landing/origin_system/raw_data/Venta.csv
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ### 7. Resumen final

# COMMAND ----------

print("=" * 60)
print("  LANDING ZONE — SETUP COMPLETO")
print("=" * 60)
print(f"  Catálogo : {LANDING_CATALOG}")
print(f"  Schema   : {ORIGIN_SCHEMA}")
print(f"  Volume   : {RAW_VOLUME}")
print(f"  Ruta     : /Volumes/{LANDING_CATALOG}/{ORIGIN_SCHEMA}/{RAW_VOLUME}/")
print("=" * 60)
print()
print("Próximos pasos:")
print("  1. Subir los CSVs al volume (ver Instrucciones arriba)")
print("  2. Ejecutar configs/setup_bronze_catalog.py")
print("  3. Ejecutar el pipeline: pipelines/landing_to_bronze")
