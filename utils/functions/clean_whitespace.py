from pyspark.sql import DataFrame
from pyspark.sql.functions import col, trim
from pyspark.sql.types import StringType


def clean_whitespace(
    df: DataFrame,
    clean_names: bool = True,
    clean_string_values: bool = True,
) -> DataFrame:
    """
    Elimina espacios en blanco sobrantes de un DataFrame.

    Args:
        df                  : DataFrame de entrada.
        clean_names         : Si True, elimina espacios al inicio/final de los
                              nombres de columna y colapsa espacios internos
                              multiples en uno solo.
                              Ej: 'PRECIO '  -> 'PRECIO'
                                  'Precio  Unitario' -> 'Precio Unitario'
        clean_string_values : Si True, aplica trim() a los valores de todas las
                              columnas de tipo string para eliminar espacios al
                              inicio y final de cada celda.

    Returns:
        DataFrame con columnas y/o valores limpios.
    """
    if clean_names:
        new_cols = [" ".join(c.split()) for c in df.columns]
        df = df.toDF(*new_cols)

    if clean_string_values:
        string_cols = [f.name for f in df.schema.fields if f.dataType == StringType()]
        for c in string_cols:
            df = df.withColumn(c, trim(col(c)))

    return df
