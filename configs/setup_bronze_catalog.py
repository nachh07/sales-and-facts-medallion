# Databricks notebook source
# MAGIC %md
# MAGIC ## Setup Bronze Catalog — Unity Catalog
# MAGIC
# MAGIC Este script verifica y crea la infraestructura necesaria para la capa **Bronze** del proyecto.
# MAGIC
# MAGIC ### ¿Qué crea este script?
# MAGIC - **Catálogo `bronze`**: Catálogo para almacenar las tablas Delta en estado raw pero con
# MAGIC   columnas de sistema (PK_HASH, R_HASH, CREATED_AT, UPDATED_AT, DELETED, DELETED_AT).
# MAGIC - **Schema `origin_system`**: Schema que mapea 1:1 con el sistema de origen.
# MAGIC
# MAGIC ### Tablas que el pipeline creará en Bronze
# MAGIC | Tabla Delta                         | Descripción                        | PK                |
# MAGIC |-------------------------------------|------------------------------------|-------------------|
# MAGIC | `bronze.origin_system.venta`        | Transacciones de ventas            | `IdVenta`         |
# MAGIC | `bronze.origin_system.clientes`     | Maestro de clientes                | `ID`              |
# MAGIC | `bronze.origin_system.productos`    | Maestro de productos               | `ID_PRODUCTO`     |
# MAGIC | `bronze.origin_system.sucursales`   | Maestro de sucursales              | `ID`              |
# MAGIC | `bronze.origin_system.empleados`    | Maestro de empleados               | `ID_EMPLEADO`     |
# MAGIC | `bronze.origin_system.compra`       | Transacciones de compras           | `IdCompra`        |
# MAGIC | `bronze.origin_system.gasto`        | Registros de gastos                | `IdGasto`         |
# MAGIC | `bronze.origin_system.tipos_gasto`  | Maestro de tipos de gasto          | `IdTipoGasto`     |
# MAGIC | `bronze.origin_system.canal_venta`  | Maestro de canales de venta        | `IdCanal`         |
# MAGIC | `bronze.origin_system.proveedores`  | Maestro de proveedores             | `IdProveedor`     |
# MAGIC | `bronze.origin_system.calendario`   | Dimensión de calendario            | `Fecha`           |

# COMMAND ----------

# MAGIC %md
# MAGIC ### 1. Parámetros de configuración

# COMMAND ----------

BRONZE_CATALOG = "bronze"
ORIGIN_SCHEMA  = "origin_system"

print(f"Catálogo destino : {BRONZE_CATALOG}")
print(f"Schema destino   : {ORIGIN_SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 2. Crear catálogo `bronze` (si no existe)

# COMMAND ----------

spark.sql(f"""
    CREATE CATALOG IF NOT EXISTS {BRONZE_CATALOG}
    COMMENT 'Capa Bronze de la arquitectura Medallion. Almacena datos crudos en formato Delta con columnas de sistema.'
""")

print(f"✅ Catálogo '{BRONZE_CATALOG}' listo.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 3. Crear schema `origin_system` dentro de `bronze`

# COMMAND ----------

spark.sql(f"""
    CREATE SCHEMA IF NOT EXISTS {BRONZE_CATALOG}.{ORIGIN_SCHEMA}
    COMMENT 'Schema que representa las entidades del sistema de origen de ventas y hechos.'
""")

print(f"✅ Schema '{BRONZE_CATALOG}.{ORIGIN_SCHEMA}' listo.")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 4. Verificar schemas y tablas existentes en bronze

# COMMAND ----------

print("Schemas en bronze:")
spark.sql(f"SHOW SCHEMAS IN {BRONZE_CATALOG}").show()

print("Tablas en bronze.origin_system (si ya existen):")
try:
    spark.sql(f"SHOW TABLES IN {BRONZE_CATALOG}.{ORIGIN_SCHEMA}").show()
except Exception as e:
    print(f"  (Sin tablas aún — se crearán al ejecutar el pipeline landing_to_bronze)")

# COMMAND ----------

# MAGIC %md
# MAGIC ### 5. Resumen final

# COMMAND ----------

print("=" * 60)
print("  BRONZE CATALOG — SETUP COMPLETO")
print("=" * 60)
print(f"  Catálogo : {BRONZE_CATALOG}")
print(f"  Schema   : {ORIGIN_SCHEMA}")
print("=" * 60)
print()
print("Próximos pasos:")
print("  1. Asegurarse de que setup_landing_zone.py fue ejecutado")
print("  2. Subir los CSVs al volume /Volumes/landing/origin_system/raw_data/")
print("  3. Ejecutar el pipeline: pipelines/landing_to_bronze")
