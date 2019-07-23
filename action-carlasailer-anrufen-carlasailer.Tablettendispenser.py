#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import configparser
from hermes_python.hermes import Hermes
from hermes_python.ffi.utils import MqttOptions
from hermes_python.ontology import *
import io

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(configparser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, configparser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    conf = read_configuration_file(CONFIG_INI)
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intent_message, conf):
    print('[Received] intent: {}'.format(intent_message.intent.intent_name))
    
    #define message to be sent to the speech synthesis engine
    slot_items = [str(item.value) for item in intent_message.slots.anrufen.all()]
    
    if 'hilfe' in slot_items:
        message_to_tts = "Du brauchst Hilfe. Ich rufe sofort einen Notarzt."
    
    elif intent_message.slots.Notfallkontakt.first() is not None:
        #extract slot from message
        slot_person = str(intent_message.slots.Notfallkontakt.first().value)
        message_to_tts = "Ich werde folgende Person anrufen: {}".format(slot_person)
    
    elif intent_message.slots.Angehoerige.first() is not None:
        slot_person = str(intent_message.slots.Angehoerige.first().value)
        message_to_tts = "Ich werde folgende Person anrufen: {}".format(slot_person)
    
    else: 
        message_to_tts = "Leider konnte ich keine Person ermitteln"
    
    # terminate the session by sending message to tts
    hermes.publish_end_session(intent_message.session_id, message_to_tts)
    


if __name__ == "__main__":
    mqtt_opts = MqttOptions()
    with Hermes(mqtt_options=mqtt_opts) as h:
        h.subscribe_intent("carlasailer:anrufen", subscribe_intent_callback).start()
