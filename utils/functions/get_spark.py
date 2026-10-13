import os


def get_spark():
    """
    Devuelve una sesion de Spark que funciona tanto dentro como fuera de Databricks.

      - Dentro de un notebook/job de Databricks: reutiliza la sesion activa.
      - Fuera de Databricks (VS Code, terminal): abre una sesion remota con
        Databricks Connect usando el perfil de ~/.databrickscfg (o las variables
        de entorno DATABRICKS_*). Por defecto usa compute serverless; si se
        define DATABRICKS_CLUSTER_ID se conecta a ese cluster.
    """
    if "DATABRICKS_RUNTIME_VERSION" in os.environ:
        from pyspark.sql import SparkSession
        return SparkSession.builder.getOrCreate()

    from databricks.connect import DatabricksSession
    builder = DatabricksSession.builder
    if not os.environ.get("DATABRICKS_CLUSTER_ID"):
        builder = builder.serverless(True)
    return builder.getOrCreate()
