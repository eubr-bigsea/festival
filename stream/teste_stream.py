# -*- coding: utf-8 -*-
# !/usr/bin/env python
from pyspark.ml import Pipeline
from pyspark.ml.classification import DecisionTreeClassificationModel, \
    LogisticRegressionModel, NaiveBayesModel
from pyspark.ml.feature import *
from pyspark.ml.pipeline import PipelineModel
from pyspark.mllib.linalg import VectorUDT
from pyspark.sql import SparkSession
from pyspark.sql import functions, types
from pyspark.sql.types import StructType, StructField, StringType, LongType, \
    TimestampType, FloatType, IntegerType

import numpy as np
import re
from util import remove_punctuation, strip_accents

REMOVE_URL_EXPR = re.compile(r"(\w+://\S+)")


def format_text_udf(text):
    return functions.udf(
        lambda t: remove_punctuation(
            REMOVE_URL_EXPR.sub("", strip_accents(
                t.lower().replace('\t', ' ').replace('\n', ' ')))),
        types.StringType())(text)


def feature_index(tweets):
    # Feature indexer
    model_path = 'hdfs://spark01.ctweb.inweb.org.br:9000/limonero/models/' \
                 'Sentiment_Analysis_-_Indexer.sentiment_inx.0000'

    string_indexer_model = StringIndexerModel.load(model_path)
    return string_indexer_model.transform(
        tweets), string_indexer_model.labels


def generate_n_grams(tweets):
    # Generate N-Grams
    n_gramers = NGram(inputCol='words_stops_removed', outputCol='n_grams')
    return n_gramers.transform(tweets)


def words_to_vector(tweets):
    model_path = 'hdfs://spark01.ctweb.inweb.org.br:9000/limonero/models/' \
                 'word_vector.0000'

    model = PipelineModel.load(model_path)
    return model.transform(tweets)


def remove_stop_words(ss, tweets):
    # Remove stop words
    url = 'hdfs://spark01.ctweb.inweb.org.br:9000' \
          '/lemonade/samples/portugues.txt'
    schema = types.StructType()
    schema.add('stop_word', types.StringType(), False,
               {'sources': ['11/stop_word']})
    stops = ss.read.option('nullValue', '').option(
        'treatEmptyValuesAsNulls', 'true').option(
        'wholeFile', True).option('multiLine', True).option(
        'escape', '"').csv(
        url, schema=schema,
        quote=None,
        header=False, sep=',',
        inferSchema=False,
        mode='PERMISSIVE')
    sw = [stop[0].strip() for stop in stops.collect() if stop and stop[0]]
    col_alias = [["words", "words_stops_removed"]]
    case_sensitive = False
    removers = [StopWordsRemover(inputCol=col, outputCol=alias,
                                 stopWords=sw, caseSensitive=case_sensitive)
                for col, alias in col_alias]
    pipeline = Pipeline(stages=removers)
    tweets = pipeline.fit(tweets).transform(tweets)
    return tweets


def tokenize(tweets):
    # Tokenizer
    col_alias = [["text_cleaned", "words"]]
    pattern_exp = r'\s+'
    min_token_length = 2
    tokenizers = [RegexTokenizer(inputCol=col, outputCol=alias,
                                 pattern=pattern_exp,
                                 minTokenLength=min_token_length)
                  for col, alias in col_alias]
    pipeline = Pipeline(stages=tokenizers)
    tweets = pipeline.fit(tweets).transform(tweets)
    return tweets


def remove_accents_punctuation(tweets):
    # Remove accents and punctuation from text
    tweets = tweets.withColumn(
        'text_cleaned', format_text_udf(tweets['text']))
    return tweets


def apply_decision_tree_classifier(tweets):
    model_path = 'hdfs://spark01.ctweb.inweb.org.br:9000/limonero/models/' \
                 'Sentiment_Analysis_-_Decision_tree.0000'
    model = DecisionTreeClassificationModel.load(model_path)
    return model.transform(tweets)


def apply_logistic_regression_classifier(tweets):
    model_path = 'hdfs://spark01.ctweb.inweb.org.br:9000/limonero/models/' \
                 'Sentiment_Analysis_-_Logistic_Regression.0000'
    model = LogisticRegressionModel.load(model_path)
    return model.transform(tweets)


def apply_naive_bayes_classifier(tweets):
    model_path = 'hdfs://spark01.ctweb.inweb.org.br:9000/limonero/models/' \
                 'Sentiment_Analysis_-_Naive_Bayes.0000'
    model = NaiveBayesModel.load(model_path)
    return model.transform(tweets)


def average_probabilities(*args):
    return sum(args) / len(args)


def get_at_pos(inx):
    def _get_at_pos(value):
        return float(value[inx])

    return _get_at_pos


def f4():
    spark_builder = SparkSession.builder.appName(
        'PythonStreamingReceiverKafkaWordCount')
    spark_builder.config(
        'spark.jars.packages',
        ','.join(['org.apache.spark:spark-streaming-kafka-0-8_2.11:2.3.0',
                  'org.apache.spark:spark-sql-kafka-0-10_2.11:2.3.0',
                  'mysql:mysql-connector-java:5.1.38']))

    spark_builder.config('spark.master', 'local[*]')

    url = "jdbc:mysql://oxumare.ctweb.inweb.org.br:33060/festival"
    properties = {
        "user": "root",
        "password": "s3cur3@3019."
    }

    ss = spark_builder.getOrCreate()

    kafka_server = "oxumare:9092"
    topic_name = "tweets_ctb"

    stream = ss.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", kafka_server) \
        .option("subscribe", topic_name) \
        .load()

    json_schema = StructType([StructField("_id", LongType()),
                              StructField("created_at", TimestampType()),
                              StructField("latitude", FloatType()),
                              StructField("longitude", FloatType()),
                              StructField("cell", IntegerType()),
                              StructField("text", StringType()),
                              StructField("user", StringType())])

    tweets = stream.select(
        functions.from_json(stream.value.cast(StringType()), json_schema).alias(
            'json')).select(functions.col('json.user').alias('user'),
                            functions.col('json.text').alias('text'),
                            functions.col('json.cell').alias('cell'),
                            functions.col('json.latitude').alias('latitude'),
                            functions.col('json.longitude').alias('longitude'),
                            functions.col('json.created_at').alias('date'))

    tweets = remove_accents_punctuation(tweets)
    tweets = tokenize(tweets)
    tweets = remove_stop_words(ss, tweets)
    tweets = generate_n_grams(tweets)
    tweets = words_to_vector(tweets)
    tweets = tweets.drop('text_cleaned', 'words', 'words_stops_removed',
                         'n_grams')
    tweets, labels = feature_index(tweets)

    # tweets = tweets.select(['latitude', 'longitude', 'cell'])
    tweets.printSchema()

    actions = [apply_decision_tree_classifier,
               apply_logistic_regression_classifier,
               apply_naive_bayes_classifier]

    for i, action in enumerate(actions):
        tweets = action(tweets) \
            .withColumnRenamed('probability', 'probability{}'.format(i)) \
            .drop('rawPrediction', 'prediction')

    tweets.printSchema()

    tweets = tweets.withColumn(
        'final_probability', functions.udf(average_probabilities, VectorUDT())(
            tweets['probability0'], tweets['probability1'],
            tweets['probability2'])).withColumn('result', functions.udf(
        lambda x: labels[np.argmax(x)])('final_probability'))

    cols = [functions.udf(get_at_pos(i), FloatType())(
        tweets['final_probability']).alias(labels[i]) for i in range(3)]

    tweets = tweets.select(
        ['date', 'text', 'cell', 'latitude', 'longitude', 'result'] + cols)

    tweets = tweets.groupBy(
        functions.window(
            functions.col('date'), "60 minutes", "30 minutes"),
        functions.col('cell')).agg(functions.avg('positive').alias('score'),
                                   functions.count('cell').alias('count')) \
        .orderBy('window')

    tweets = tweets.select(functions.to_json(
        functions.struct([tweets[x] for x in tweets.columns])).alias(
        "value"))

    # query = tweets.writeStream \
    #     .outputMode('complete') \
    #     .option("truncate", False) \
    #     .format('console') \
    #     .start()
    # query = tweets.writeStream \
    #     .outputMode('complete') \
    #     .option("truncate", False) \
    #     .format('console') \
    #     .trigger(processingTime='60 seconds') \
    #     .start()
    query = tweets.writeStream \
        .format("kafka").option("kafka.bootstrap.servers", kafka_server) \
        .outputMode('complete') \
        .option("topic", topic_name + "_result") \
        .option("checkpointLocation", "/data/checkpoint/1").start()

    query.awaitTermination()


if __name__ == '__main__':
    f4()
