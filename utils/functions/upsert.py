import logging
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
from pyspark.errors import AnalysisException
from delta.tables import *


def upsert_data(df: DataFrame, table_name: str) -> None:
    """
    Realiza un UPSERT de un DataFrame hacia una tabla Delta.

    Estrategia:
      - Si la tabla NO existe → crea la tabla con saveAsTable (primera carga).
      - Si la tabla YA existe → ejecuta MERGE por PK_HASH:
          · WHEN MATCHED     → actualiza todas las columnas excepto CREATED_AT y R_HASH.
          · WHEN NOT MATCHED → inserta la fila nueva completa.

    Args:
        df         : DataFrame con columnas de sistema ya aplicadas
                     (PK_HASH, R_HASH, CREATED_AT, UPDATED_AT, DELETED, DELETED_AT).
        table_name : Nombre completo de la tabla destino
                     (ej: 'bronze.origin_system.venta').
    """
    logger = logging.getLogger(__name__)

    # Columnas que NO se actualizan en WHEN MATCHED:
    #   - CREATED_AT : timestamp de creación, es inmutable.
    #   - R_HASH     : hash de fila — se recalcula en cada ejecución desde la fuente;
    #                  conservar el original permite detectar cambios futuros.
    exclude_on_update = {'CREATED_AT', 'R_HASH'}

    try:
        df.write.format("delta").saveAsTable(table_name)
        logger.info(f"[{table_name}] Tabla creada por primera vez.")

    except AnalysisException as err:
        if "TABLE_OR_VIEW_ALREADY_EXISTS" in err.getErrorClass():
            logger.info(f"[{table_name}] Tabla existente — ejecutando MERGE (upsert)...")

            target_delta_table = DeltaTable.forName(SparkSession.builder.getActiveSession(), table_name)

            update_cols = {
                f"target.{col}": f"source.{col}"
                for col in df.columns
                if col not in exclude_on_update
            }

            (
                target_delta_table.alias("target")
                .merge(
                    df.alias("source"),
                    "target.PK_HASH = source.PK_HASH"
                )
                .whenMatchedUpdate(set=update_cols)
                .whenNotMatchedInsertAll()
                .execute()
            )

            logger.info(f"[{table_name}] MERGE completado.")
        else:
            raise err