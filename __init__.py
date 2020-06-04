from datetime import datetime
from mycroft import MycroftSkill, intent_handler
import os
from yeelight import *


class Yeelight(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.bulb = Bulb("192.168.1.60")
        self.log.info("Yeelight Bulb initilized")
        self.state = self.bulb.last_properties
        self.log.debug(f"Bulb properties: {self.state}")
        transitions = [
            RGBTransition(255, 0, 0),
            SleepTransition(400),
            RGBTransition(0, 255, 0),
            SleepTransition(400),
            RGBTransition(0, 0, 255),
            SleepTransition(400),
        ]
        self.flow = Flow(0, Flow.actions.recover, transitions)
        self.populate_colors_dict()
        self.bulb.get_properties()
        if self.bulb.last_properties["power"] == "on":
            self.turned_on_time = datetime.now()

    def populate_colors_dict(self):
        self.colors = {}
        with open(
            os.path.dirname(os.path.abspath(__file__)) + "/colors.csv", "r"
        ) as csv:
            for line in csv.readlines():
                line = line.strip("\n")
                values = line.split(",")
                name = values[0].replace("(", "")
                name = name.replace(")", "")
                name = name.replace("/", "")
                name = name.replace("-", " ")
                name = name.replace("'", "")
                name = name.lower()
                red = int(values[1])
                green = int(values[2])
                blue = int(values[3])
                self.colors[name] = (red, green, blue)

    @intent_handler("on.intent")
    def handle_bulb_on(self, message):
        self.bulb.get_properties()
        self.log.info("Turning bulb on")
        self.speak_dialog("in.progress")
        self.bulb.turn_on()
        self.turned_on_time = datetime.now()

    @intent_handler("off.intent")
    def handle_bulb_off(self, message):
        self.bulb.get_properties()
        self.log.info("Turning bulb off")
        self.speak_dialog("in.progress")
        self.bulb.turn_off()

    @intent_handler("change.color.intent")
    def handle_change_color(self, message):
        self.bulb.get_properties()
        color = message.data.get("color")
        self.log.info(f"Changing color to {color}")
        try:
            rgb = self.colors[color]
            self.speak(f"Changing color to {color}")
            self.bulb.set_rgb(rgb[0], rgb[1], rgb[2])
            self.color = color
        except KeyError as e:
            self.speak(f"Color {color} does not exist!")

    @intent_handler("change.intensity.intent")
    def handle_change_intensity(self, message):
        self.bulb.get_properties()
        percent = int(message.data.get("percent").rstrip("%"))
        self.log.info(f"Changing intensity to {percent} percent")
        self.speak(f"Changing intensity to {percent} percent")
        if percent == 0:
            self.bulb.turn_off()
        else:
            if self.bulb.last_properties["power"] == "off":
                self.bulb.turn_on()
                self.turned_on_time = datetime.now()
            self.bulb.set_brightness(percent)

    @intent_handler("flow.mode.intent")
    def handle_activate_flow(self, message):
        self.bulb.get_properties()
        self.log.info("Activating flow mode")
        self.speak("Activating flow mode")
        if self.bulb.last_properties["power"] == "off":
            self.bulb.turn_on()
            self.turned_on_time = datetime.now()
        self.bulb.start_flow(self.flow)
        self.color = 'flowing'

    @intent_handler("normal.mode.intent")
    def handle_activate_normal(self, message):
        self.bulb.get_properties()
        self.log.info("Activating normal mode")
        self.speak("Activating normal mode")
        self.bulb.set_rgb(255, 255, 255)
        self.bulb.set_power_mode(PowerMode.NORMAL)
        self.color = 'white'

    @intent_handler("intensity.state.intent")
    def handle_state_intensity(self, message):
        self.bulb.get_properties()
        self.log.info("Getting bulb intensity")
        if self.bulb.last_properties["power"] == "off":
            self.speak(f"The bulb intensity is at 0 percent")
        self.speak(
            f'The bulb intensity is at {self.bulb.last_properties["bright"]} percent'
        )

    @intent_handler("mode.state.intent")
    def handle_state_mode(self, message):
        self.bulb.get_properties()
        self.log.info("Getting bulb mode")
        is_flowing = True if self.bulb.last_properties["flowing"] == "1" else False
        is_color = False if self.bulb.last_properties["rgb"] == "16777215" else True
        if is_flowing:
            self.speak("The bulb is in flow mode")
        elif is_color:
            self.speak("The bulb is in color mode")
        else:
            self.speak("The bulb is in normal mode")

    @intent_handler("color.state.intent")
    def handle_state_color(self, message):
        self.bulb.get_properties()
        self.log.info("Getting bulb color")
        try:
            self.speak(f"The color of the bulb is {self.color}")
        except AttributeError:
            self.speak(f"The color of the bulb is white")

    @intent_handler("state.intent")
    def handle_state(self, message):
        self.bulb.get_properties()
        self.log.info("Getting bulb general state")
        self.handle_turned_on(message)
        self.handle_state_color(message)
        self.handle_state_mode(message)
        self.handle_state_intensity(message)

    @intent_handler("time.turned.on.intent")
    def handle_turned_on(self, message):
        self.bulb.get_properties()
        self.log.info("Getting bulb general state")
        now = datetime.now()
        timedelta = now - self.turned_on_time
        seconds = int(timedelta.total_seconds())
        minutes = int(seconds / 60)
        suffix = 's' if minutes > 1 else ''
        if seconds < 60:
            self.speak(f'The bulb has been on for {seconds} seconds')
        else:
            self.speak(f'The bulb has been on for {minutes} minute{suffix} and {seconds % 60} seconds')



def create_skill():
    return Yeelight()
