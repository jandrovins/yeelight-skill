from mycroft import MycroftSkill, intent_file_handler


class Yeelight(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('yeelight.intent')
    def handle_yeelight(self, message):
        self.speak_dialog('yeelight')


def create_skill():
    return Yeelight()

