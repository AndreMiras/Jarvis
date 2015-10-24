import re
import webbrowser
import thread
import yaml

from src.wikipedia import wikipedia
from src import network
from src.some_functions import words_to_nums, play_music
from src import common


with open('config.yml', 'r') as f:
    config = yaml.load(f)


class Brain():

    '''
    This class will load core things in Jarvis' brain
    '''

    def __init__(self, speak_engine):
        self.speak_engine = speak_engine

    def talking_to_me(self, text):
        """
        Returns True if talking to me, otherwise returns False.
        """
        return 'jarvis' in text.lower()

    def _preprocess(self, text):
        """
        Pre-processes the text.

        1) Changes to lower-case.
        So we don't have to look for "Word" as well as "word".

        2) Removes the first "Jarvis" occurence in the text.
        This avoids to leads to some weirdness like:
        "Jarvis, what's your name?"
        Or like that:
        "Jarvis, your name is Jarvis."
        """
        # 1)
        text = text.lower()
        # 2)
        text = text.replace("jarvis", "", 1)
        print "text:", text
        return text

    def process(self, text):
        speak_engine = self.speak_engine
        if not self.talking_to_me(text):
            print("Not talking to me.")
            return True
        text = self._preprocess(text)
        words = text.split(' ')
        if 'open' in words:
            speak_engine.say("I'm on it. Stand By.")
            websites = config["config"]["websites"]
            website_to_open = text[text.index('open') + 5:]
            if website_to_open in websites:
                url = websites[website_to_open]
                webbrowser.open_new_tab(url)
        if 'search' in words:
            speak_engine.say("I'm looking for it. Please stand by!")
            term_to_search = text[text.index('search') + 7:]
            summary = wikipedia.summary(term_to_search)
            summary = " ".join(re.findall('\w+.', summary))
            summary = summary[:99]
            speak_engine.say(summary)
            return True
        if 'where' in words and ('are' in words or 'am' in words) and ('we' in words or 'i' in words) or 'location' in words:
            speak_engine.say("I am tracking the location. Stand by.")
            speak_engine.say(network.currentLocation())
            return True
        if 'play' in words:
            if 'a' in words and 'song' in words:
                speak_engine.say("I'm looking for it. Please stand by!")
                thread.start_new_thread(play_music, ())
            return True
        if 'current' in words and 'time' in words:
            time = common.getCurrentTime()
            speak_engine.say(time)
            return True
        '''Handling Mathematical/Computational queries'''
        if 'add' in words or 'subtract' in words or 'multiply' in words or 'divide' in words:
            try:
                nums = re.findall('\d+', text)
                if len(nums) < 2:
                    mod_text = words_to_nums(text)
                    nums += re.findall('\d+', mod_text)
                    print nums
                nums = map(int, nums)
                if 'add' in words:
                    speak_engine.say("It is " + str(sum(nums)))
                if 'subtract' in words:
                    speak_engine.say("It is " + str(nums[1] - nums[0]))
                if 'multiply' in words:
                    speak_engine.say("It is " + str(nums[0] * nums[1]))
                if 'divide' in words:
                    speak_engine.say("It is " + str(nums[0] / nums[1]))
            except:
                speak_engine.say(
                    "Perhaps my Mathematical part of brain is malfunctioning.")
            return True
        if self.process_lights(text):
            return True
        return False

    def process_lights(self, text):
        """
        Handles light commands with Philips Hue.
        """
        speak_engine = self.speak_engine
        words = text.split(' ')
        # looks in text so 'light' and 'lights' would match
        if 'light' in text:
            if 'dim' in words or 'full' in words or 'turn' in words or 'switch' in words:
                if 'full' in words or 'on' in words:
                    brightness = 255
                    on = True
                    speak_engine.say("OK, I'll switch the lights on for you.")
                elif 'dim' in words:
                    brightness = 127
                    on = True
                    speak_engine.say("OK, I'll dim the lights for you.")
                elif 'off' in words:
                    brightness = 0
                    on = False
                    speak_engine.say("OK, I'll switch the lights off for you.")
                from phue import Bridge
                # will guess the IP if none is given
                ip_address = None
                bridge = Bridge(ip_address)
                lights_dict = bridge.get_light_objects('name')
                for name, light in lights_dict.items():
                    light.brightness = brightness
                    light.on = on
                return True
