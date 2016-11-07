# Overview

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


# Deploying

A working Juju installation is assumed to be present. If Juju is not yet set
up, please follow the [getting-started][] instructions prior to deploying this
charm.

This charm is intended to be deployed via the [hadoop-kafka][] bundle:

    juju deploy hadoop-kafka

> **Note**: The above assumes Juju 2.0 or greater. If using an earlier version
of Juju, use [juju-quickstart][] with the following syntax: `juju quickstart
hadoop-kafka`.

This will deploy an Apache Bigtop Hadoop cluster with Apache Flume and Apache
Kafka. More information about this deployment can be found in the
[bundle readme](https://jujucharms.com/hadoop-kafka/).

## Network-Restricted Environments
Charms can be deployed in environments with limited network access. To deploy
in this environment, configure a Juju model with appropriate proxy and/or
mirror options. See [Configuring Models][] for more information.

[getting-started]: https://jujucharms.com/docs/stable/getting-started
[hadoop-kafka]: https://jujucharms.com/hadoop-kafka
[juju-quickstart]: https://launchpad.net/juju-quickstart
[Configuring Models]: https://jujucharms.com/docs/stable/models-config


# Configuring

The default Kafka topic where messages are published is unset. Set this to
an existing Kafka topic as follows:

    juju config flume-kafka kafka_topic='<topic_name>'

> **Note**: The above assumes Juju 2.0 or greater. If using an earlier version
of Juju, the syntax is `juju set flume-kafka kafka_topic='<topic_name>`.

If you don't have a Kafka topic, you may create one (and configure this charm
to use it) with:

    juju run-action kafka/0 create-topic topic=<topic_name> \
      partitions=1 replication=1
    juju show-action-output <id>  # <-- id from above command
    juju config flume-kafka kafka_topic='<topic_name>'

> **Note**: The above assumes Juju 2.0 or greater. If using an earlier version
of Juju, the syntax is:
`juju action do kafka/0 create-topic <action_args>;`
`juju action fetch <id>;`
`juju set flume-kafka kafka_topic=<topic_name>`.

Once the Flume agents start, messages will start flowing into
HDFS in year-month-day directories here: `/user/flume/flume-kafka/%y-%m-%d`.


# Testing

A Kafka topic is required for this test. Topic creation is covered in the
**Configuration** section above. Generate Kafka messages with the `write-topic`
action:

    juju run-action kafka/0 write-topic topic=<topic_name> data="This is a test"

> **Note**: The above assumes Juju 2.0 or greater. If using an earlier version
of Juju, the syntax is `juju action do kafka/0 write-topic <action-args>`.

To verify these messages are being stored into HDFS, SSH to the `flume-hdfs`
unit, locate an event, and cat it:

    juju ssh flume-hdfs/0
    hdfs dfs -ls /user/flume/flume-kafka  # <-- find a date
    hdfs dfs -ls /user/flume/flume-kafka/yyyy-mm-dd  # <-- find an event
    hdfs dfs -cat /user/flume/flume-kafka/yyyy-mm-dd/FlumeData.[id]


# Contact Information

- <bigdata@lists.ubuntu.com>


# Help

- [Apache Flume home page](http://flume.apache.org/)
- [Apache Flume bug tracker](https://issues.apache.org/jira/browse/flume)
- [Apache Flume mailing lists](https://flume.apache.org/mailinglists.html)
- [Juju mailing list](https://lists.ubuntu.com/mailman/listinfo/juju)
- [Juju community](https://jujucharms.com/community)
