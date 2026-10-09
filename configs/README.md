# Configuración de Infraestructura — Unity Catalog

Esta carpeta contiene scripts de configuración para la infraestructura de datos en Databricks Unity Catalog.

## Estructura

```
configs/
├── README.md                  ← Este archivo
├── setup_landing_zone.py      ← Crea catálogos, schemas y volúmenes para la landing zone
└── setup_bronze_catalog.py    ← Crea el catálogo y schema de bronze (destino del pipeline)
```

## Conceptos clave

### ¿Qué es un Volumen en Unity Catalog?
Un **Volume** es una entidad de Unity Catalog que representa una ubicación física de almacenamiento (cloud storage / DBFS) accesible a través de una ruta `/Volumes/<catalog>/<schema>/<volume>/`. Simulan un "blob storage" o "bucket S3" con gobernanza de Unity Catalog.

### Landing Zone
La **landing zone** es la primera capa de ingesta donde se depositan los archivos **tal como llegan** desde el sistema fuente (CSV, JSON, Parquet, etc.), sin ninguna transformación. En este proyecto, los archivos CSV del sistema de ventas se depositan aquí antes de ser procesados hacia Bronze.

### Arquitectura Medallion utilizada
```
Landing Zone (Volumes)
       ↓  [landing_to_bronze.ipynb]
    Bronze  (Delta Tables — raw, con system columns)
       ↓  [sales_pipeline_silver.ipynb]
    Silver  (Delta Tables — curada y enriquecida)
       ↓  [customer_segmentation_gold / segment_summary_gold]
    Gold    (Delta Tables — agregada para consumo)
```

## Cómo usarlos

1. Abrir cada script en un notebook de Databricks (o ejecutar como script Python en un cluster)
2. Ejecutar `setup_landing_zone.py` primero — crea el catálogo `landing`, schema `origin_system` y el volume `raw_data`
3. Ejecutar `setup_bronze_catalog.py` segundo — verifica/crea el catálogo `bronze` y schema `origin_system`
4. Subir los CSVs al volume `/Volumes/landing/origin_system/raw_data/` (manualmente o via DBFS CLI)

> Requisito: El usuario que ejecute los scripts debe tener permisos de CREATE CATALOG y CREATE SCHEMA en Unity Catalog.
