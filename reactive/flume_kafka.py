from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state, is_state
from charmhelpers.core import hookenv
from charms.flume import Flume
from charms.reactive.helpers import any_file_changed
from jujubigdata.utils import DistConfig


@when('flume-base.installed')
@when_not('flume-kafka.started')
def report_status():
    kafka_joined = is_state('kafka.connected')
    kafka_ready = is_state('kafka.available')
    sink_joined = is_state('flume-sink.ready')
    sink_ready = is_state('flume-sink.joined')
    if not kafka_joined and not sink_joined:
        hookenv.status_set('blocked', 'Waiting for connection to Kafka and Flume sink')
    elif not kafka_joined:
        hookenv.status_set('blocked', 'Waiting for connection to Kafka')
    elif not sink_joined:
        hookenv.status_set('blocked', 'Waiting for connection to Flume sink')
    elif not kafka_ready and not sink_ready:
        hookenv.status_set('waiting', 'Waiting for Kafka and Flume sink')
    elif not kafka_ready:
        hookenv.status_set('waiting', 'Waiting for Kafka')
    elif not sink_ready:
        hookenv.status_set('waiting', 'Waiting for Flume sink')


@when('flume-base.installed')
@when('flume-sink.ready', 'kafka.available')
def configure_flume(sink, kafka):
    hookenv.status_set('maintenance', 'Configuring Flume')
    flume = Flume(DistConfig())
    flume.configure_flume({
        'agents': sink.agents(),
        'zookeepers': kafka.zookeepers(),
    })
    if any_file_changed(flume.config_file):
        flume.restart()
    hookenv.status_set('active', 'Ready')
    set_state('flume-kafka.started')


@when('flume-kafka.started')
@when_not('flume-sink.ready')
def stop_flume():
    flume = Flume(DistConfig())
    flume.stop()
    remove_state('flume-kafka.started')


@when('flume-kafka.started')
@when_not('kafka.available')
def kafka_lost():
    stop_flume()
