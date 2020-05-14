from mycroft import MycroftSkill, intent_handler
from yeelight import *


class Yeelight(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_handler('bulb.on.intent')
    def handle_bulb_on(self, message):
        self.log.info("Turning bulb on")
        self.speak_dialog('in.progress')
        self.bulb.turn_on()

    @intent_handler('bulb.off.intent')
    def handle_bulb_on(self, message):
        self.log.info("Turning bulb off")
        self.speak_dialog('in.progress')
        self.bulb.turn_off()

    def initialize(self):
        self.bulb = Bulb("192.168.1.60")
        self.log.info("Yeelight Bulb initilized")
        self.get_properties()
        self.state = bulb.last_properties
        self.log.debug(f'Bulb properties: {self.state}')



def create_skill():
    return Yeelight()

