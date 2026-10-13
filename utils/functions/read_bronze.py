import logging
from pyspark.sql import DataFrame

try:
    from utils.functions.get_spark import get_spark
except ImportError:
    from get_spark import get_spark



def read_bronze(input_catalog: str, input_schema: str, table: str) -> DataFrame:
    """Lee una tabla de bronze y descarta las columnas de sistema (se regeneran en silver)."""
    logger = logging.getLogger(__name__)
    BRONZE_CATALOG = "bronze"

    SYSTEM_COLUMNS = ["PK_HASH", "R_HASH", "CREATED_AT", "UPDATED_AT", "DELETED", "DELETED_AT"]

    if input_catalog != BRONZE_CATALOG:
        raise ValueError(
            f"Catálogo inválido: '{input_catalog}'. "
            f"read_bronze solo puede leer del catálogo '{BRONZE_CATALOG}'."
        )

    full_table = f"{input_catalog}.{input_schema}.{table}"
    try:
        logger.info(f"Leyendo tabla de bronze: {full_table}")
        return get_spark().table(full_table).drop(*SYSTEM_COLUMNS)
    except Exception as e:
        logger.error(f"Error al leer la tabla {full_table}: {e}")
        raise
