import logging
from typing import Dict, List, Tuple
from pyspark.sql import DataFrame
from pyspark.sql.utils import AnalysisException


def validate_natural_key_df(dataframe_and_key: Dict[str, Tuple[DataFrame, List[str]]]) -> None:
    """
    Valida que la clave natural de cada DataFrame sea única y no nula.

    Args:
        dataframe_and_key: diccionario con la forma:
            {
                'nombre_tabla': (df, ['col_pk1', 'col_pk2', ...]),
                ...
            }

    Raises:
        ValueError       : si alguna clave tiene nulos o duplicados.
        AnalysisException: si ocurre un error al consultar el DataFrame.
    """
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    validated_keys = []

    for table_name, (df, key_columns) in dataframe_and_key.items():
        try:
            null_condition   = ' OR '.join([f"{col_name} IS NULL" for col_name in key_columns])
            null_count       = df.filter(null_condition).count()
            duplicated_count = df.groupBy(*key_columns).count().filter("count > 1").count()

            if null_count > 0 or duplicated_count > 0:
                raise ValueError(
                    f"[{table_name}] Hay {null_count} registros nulos y "
                    f"{duplicated_count} duplicados para la clave {key_columns}."
                )
            else:
                logger.info(f"[{table_name}] La clave {key_columns} es válida.")
                validated_keys.append(table_name)

        except AnalysisException as err:
            logger.error(f"[{table_name}] Error al validar clave {key_columns}: {err}")
            raise err

    logger.info(f"Todas las claves validadas: {validated_keys}")
