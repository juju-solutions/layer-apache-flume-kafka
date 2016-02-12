import jujuresources
from charms.reactive import when, when_not
from charms.reactive import set_state, remove_state
from charmhelpers.core import hookenv
from charms.flume import Flume
from charms.reactive.helpers import data_changed
from jujubigdata.utils import DistConfig

def dist_config():

    if not getattr(dist_config, 'value', None):
        flume_reqs = ['packages', 'groups', 'users', 'dirs']
        dist_config.value = DistConfig(filename='dist.yaml', required_keys=flume_reqs)
    return dist_config.value


@when_not('flume.installed')
def install_flume(*args):

    flume = Flume(dist_config())
    if flume.verify_resources():
        hookenv.status_set('maintenance', 'Installing Flume kafka agent')
        flume.install()
        set_state('flume.installed')


@when('flume.installed')
@when_not('flume-agent.connected')
def waiting_for_flume_connection():
    hookenv.status_set('blocked', 'Waiting for connection to Flume HDFS')


@when('flume.installed', 'flume-agent.connected')
@when_not('flume-agent.available')
def waiting_for_flume_available(flume):
    hookenv.status_set('waiting', 'Waiting for availability of Flume HDFS')


@when('flume.installed', 'flume-agent.available')
@when_not('flume.started')
def configure_flume(flumehdfs):
    try:
        port = flumehdfs.get_flume_port()
        ip = flumehdfs.get_flume_ip()
        protocol = flumehdfs.get_flume_protocol()
        flumehdfsinfo = {'port': port, 'private-address': ip, 'protocol': protocol}
        hookenv.log("Connecting to Flume HDFS")
        hookenv.status_set('maintenance', 'Setting up Flume')
        flume = Flume(dist_config())
        flume.configure_flume(flumehdfsinfo)
        config = hookenv.config()
        data_changed('configuration', config)
        flume.restart()
        hookenv.status_set('active', 'Ready')
        set_state('flume.started')
    except:
        hookenv.log("Relation with Flume sink not established correctly")        


@when('flume.started')
@when_not('flume-agent.available')
def agent_disconnected():
    remove_state('flume.started')
    hookenv.status_set('blocked', 'Waiting for a connection to Flume HDFS')
    flume = Flume(dist_config())
    flume.stop()


@when('flume.started', 'flume-agent.available')
def reconfigure(flumehdfs):
    config = hookenv.config()
    if not data_changed('configuration', config):
        return

    port = flumehdfs.get_flume_port()
    ip = flumehdfs.get_flume_ip()
    protocol = flumehdfs.get_flume_protocol()
    flumehdfsinfo = {'port': port, 'private-address': ip, 'protocol': protocol}
    flume = Flume(dist_config())
    flume.configure_flume(flumehdfsinfo)
    flume.restart()

    
@when('kafka.related')
@when_not('kafka.available')
def kafka_related(kafka):
    # TODO (kt): have kafka pass the zookeeper endpoints
    hookenv.status_set('waiting', 'Waiting for the connection to kafka.')


@when('kafka.available', 'flume.started')
def kafka_available(kafka):
    hookenv.status_set('active', 'Ready')

