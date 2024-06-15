import paho.mqtt.client as mqtt
import os, time, datetime, json, re, signal
from kef import Kef
from gpio import Gpio
from logger import log

# MQTT connection variables
localBroker = "localhost"
localPort = 1883
localTopic = "device/#"
localTimeOut = 120

gpio = Gpio()
kef = Kef()

def on_log(client, userdata, level, buff):
    log.log(level, buff)

def on_connect(client, userdata, flags, rc):
    log.info("connected with result code: '%s'" % mqtt.connack_string(rc))
    client.subscribe(localTopic)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        log.error("unexpected disconnection: '%s'" % mqtt.error_string(rc))

def on_message(client, userdata, msg):
    try:
        data = msg.payload.decode("utf-8")
        log.info("received message for topic=%s, data='%s'" % (msg.topic, data))

        match = re.match(r'device/(.*?)/(.*)', msg.topic.lower())
        device = match.group(1)
        command = match.group(2)

        if command == 'state' or command == 'info':
            return

        if device == "computer":
            state = gpio.execute(device, command, json.loads(data))
            publish(device, state)
        elif device == "leopard" or device == "speaker":
            state = kef.execute(command, json.loads(data))
            publish(device, state)
        else:
            log.error("unknown device: '%s'" % device)

    except Exception as e:
        log.error("failure", exc_info=e)

def publish(device, state):
    topic = "device/%s/state" % device
    result = client.publish(topic, json.dumps(state))
    log.info("publish message to topic=%s, data='%s', result=%s" % (topic, state, result))


def exit_gracefully(signum, frame):
    log.info("stopping hives")
    gpio.cleanup()
    quit()

########################
# Main
########################
if "__main__" == __name__:
    log.info("starting hives")

    signal.signal(signal.SIGTERM, exit_gracefully)
    signal.signal(signal.SIGINT, exit_gracefully)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_message = on_message
    client.on_log = on_log

    client.connect(localBroker, localPort, localTimeOut)

    # Blocking call that processes network traffic, dispatches callbacks and
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    # handles reconnecting.
    client.loop_forever()
