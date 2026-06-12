import logging
from typing import Dict, List
from pyspark.sql import DataFrame
from pyspark.sql.utils import AnalysisException
from pyspark.sql.functions import col, concat_ws

def validate_natural_key_df(dataframe_and_key: Dict[DataFrame, List[str]]) -> None:
 
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    
    validated_keys = []
    
    for df, key_columns in dataframe_and_key.items():
        try:
            null_condition = ' OR '.join([f"{col_name} IS NULL" for col_name in key_columns])
            null_count = df.filter(null_condition).count()
            duplicated_count = df.groupBy(*key_columns).count().filter("count > 1").count()
            
            if null_count > 0 or duplicated_count > 0:
                raise ValueError(
                    f"Hay {null_count} registros nulos y {duplicated_count} duplicados "
                    f"para la clave {key_columns}."
                )
            else:
                logger.info(f"La clave {key_columns} es válida.")
                validated_keys.append(key_columns)
                
        except AnalysisException as err:
            logger.error(f"Error al validar clave {key_columns}: {err}")
            raise err
    
    logger.info(f"Todas las claves validadas: {validated_keys}")

