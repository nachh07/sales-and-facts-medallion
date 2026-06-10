from pyspark.sql.dataframe import DataFrame
from pyspark.errors import AnalysisException
from delta.tables import *

def upsert_data(df: DataFrame, table_name: str) -> None:
    try: 
        df.write.format("delta").saveAsTable(f"{table_name}")
    except AnalysisException as err:
        if "TABLE_OR_VIEW_ALREADY_EXISTS" in err.getErrorClass():
            exclude_update = ['CREATED_AT', 'UPDATED_AT','R_HASH']
            target_delta_table = DeltaTable.forName(spark, f"{table_name}")
            target_df = target_delta_table.toDF()
            source_df = df
            delta_merge_builder = (
                    target_delta_table.alias('target')
                    .merge(
                        source_df.alias('source'), 
                        "target.PK_HASH = source.PK_HASH"
                    )
                    .whenMatchedUpdate(
                        set = {f"target.{col}" : f"source.{col}" for col in source_df.columns if col != exclude_update}
                    )
                    .whenNotMatchedInsertAll()
                )
            delta_merge_builder.execute()
        else:
            raise err