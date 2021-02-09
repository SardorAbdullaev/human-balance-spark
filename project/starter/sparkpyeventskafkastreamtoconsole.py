from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, unbase64, base64, split
from pyspark.sql.types import StructField, StructType, StringType, BooleanType, ArrayType, DateType

stediSchema = StructType([
    StructField("customer", StringType()),
    StructField("score", StringType()),
    StructField("riskDate", StringType())
])

# TO-DO: using the spark application object, read a streaming dataframe from the Kafka topic stedi-events as the source
# Be sure to specify the option that reads all the events from the topic including those that were published before you started the spark stream

spark = SparkSession.builder.appName("STEDI_parser").getOrCreate()
spark.sparkContext.setLogLevel('WARN')
stediDf = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:19092") \
    .option("subscribe", "stedi-events") \
    .option("startingOffsets", "earliest") \
    .load()
# TO-DO: cast the value column in the streaming dataframe as a STRING
stediValuesDf = stediDf.selectExpr("cast(value as string) value")

# TO-DO: parse the JSON from the single column "value" with a json object in it, like this:
# +------------+
# | value      |
# +------------+
# |{"custom"...|
# +------------+
#
# and create separated fields like this:
# +------------+-----+-----------+
# |    customer|score| riskDate  |
# +------------+-----+-----------+
# |"sam@tes"...| -1.4| 2020-09...|
# +------------+-----+-----------+
#
# storing them in a temporary view called CustomerRisk
stediValuesDf.withColumn("value", from_json("value", stediSchema)).select(col("value.*")).createOrReplaceTempView(
    "CustomerRisk")

# # TO-DO: execute a sql statement against a temporary view, selecting the customer and the score from the temporary view, creating a dataframe called customerRiskStreamingDF
customerRiskStreamingDF = spark.sql("select customer, score from CustomerRisk")
customerRiskStreamingDF.writeStream.outputMode("append").format("console").start().awaitTermination()
