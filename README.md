## Overview

Flume is a distributed, reliable, and available service for efficiently
collecting, aggregating, and moving large amounts of log data. It has a simple
and flexible architecture based on streaming data flows. It is robust and fault
tolerant with tunable reliability mechanisms and many fail over and recovery
mechanisms. It uses a simple extensible data model that allows for online
analytic application. Learn more at [flume.apache.org](http://flume.apache.org).

This charm provides a Flume agent designed to ingest messages published to
a Kafka topic and send them to the `apache-flume-hdfs` agent for storage in
the shared filesystem (HDFS) of a connected Hadoop cluster. This leverages the
KafkaSource jar packaged with Flume. Learn more about the
[Flume Kafka Source](https://flume.apache.org/FlumeUserGuide.html#kafka-source).


## Usage

This charm is intended to be deployed via the
[apache-ingestion-kafka](https://jujucharms.com/apache-ingestion-kafka) bundle:

    juju quickstart apache-ingestion-kafka

This will deploy the Apache Hadoop platform with Apache Flume and Apache Kafka
communicating with the cluster via the `apache-hadoop-plugin` charm.


## Configuration

The default Kafka topic where messages are published is unset. Set this to
an existing Kafka topic as follows:

    juju set flume-kafka kafka_topic='<topic_name>'

If you don't have a Kafka topic, you may create one (and verify successful
creation) with:

    juju action do kafka/0 create-topic topic=<topic_name> \
     partitions=1 replication=1
    juju action fetch <id>  # <-- id from above command

Once the Flume agents start, messages will start flowing into
HDFS in year-month-day directories here: `/user/flume/flume-kafka/%y-%m-%d`.


## Testing

A Kafka topic is required for this test. Topic creation is covered in the
**Configuration** section above. Generate Kafka messages with the `write-topic`
action:

    juju action do kafka/0 write-topic topic=<topic_name> data="This is a test"

To verify these messages are being stored into HDFS, SSH to the `flume-hdfs`
unit, locate an event, and cat it:

    juju ssh flume-hdfs/0
    hdfs dfs -ls /user/flume/flume-kafka  # <-- find a date
    hdfs dfs -ls /user/flume/flume-kafka/yyyy-mm-dd  # <-- find an event
    hdfs dfs -cat /user/flume/flume-kafka/yyyy-mm-dd/FlumeData.[id]


## Contact Information

- <bigdata@lists.ubuntu.com>


## Help

- [Apache Flume home page](http://flume.apache.org/)
- [Apache Flume bug tracker](https://issues.apache.org/jira/browse/flume)
- [Apache Flume mailing lists](https://flume.apache.org/mailinglists.html)
- `#juju` on `irc.freenode.net`
