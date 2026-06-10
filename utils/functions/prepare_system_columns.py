def prepare_system_dataframe(df, pk_hash: list[str]):
    '''
    Args: df: DataFrame
          pk_hash: list of primary key column names
    Returns: 
         DataFrame
    This function DataFrame and returns a processed DataFrame with the following modifications:
    - Renames all columns to uppercase.
    - Adds a "CREATED_AT" column with the current timestamp in UTC.
    - Adds an "UPDATED_AT" column with the current timestamp.
    - Adds "PK_HASH" column with hash of primary key columns.
    - Adds "R_HASH" column with hash of all remaining columns.
    '''
    from pyspark.sql.functions import col, current_timestamp, from_utc_timestamp, lit, md5, concat_ws

    processed_df = df
    for column in df.columns:
        processed_df = processed_df.withColumnRenamed(column, column.upper())
    
    # Get uppercase version of pk_hash columns
    pk_columns_upper = [col_name.upper() for col_name in pk_hash]
    
    # Get all other columns (excluding pk_hash columns)
    all_columns_upper = [col_name.upper() for col_name in df.columns]
    r_columns = [col_name for col_name in all_columns_upper if col_name not in pk_columns_upper]
    
    return (
        processed_df
        .withColumn("PK_HASH", md5(concat_ws("|", *[col(c) for c in pk_columns_upper])))
        .withColumn("R_HASH", md5(concat_ws("|", *[col(c) for c in r_columns])))
        .withColumn("CREATED_AT", from_utc_timestamp(current_timestamp(), "America/Argentina/Buenos_Aires"))
        .withColumn("UPDATED_AT", from_utc_timestamp(current_timestamp(), "America/Argentina/Buenos_Aires"))
        .withColumn("DELETED", lit(False).cast('boolean'))
        .withColumn("DELETED_AT", lit(None).cast('timestamp'))

    )