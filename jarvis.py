import aiml
import sys
import traceback

import speech_recognition

from src import google_tts
from src import microphone
from src import commonsense
from src import brain
from excp.exception import NotUnderstoodException

exit_flag = 0
tts_engine = google_tts.Pyttsx()
jarvis_brain = brain.Brain(tts_engine)
# mic = microphone.Microphone()
k = aiml.Kernel()
recognizer = speech_recognition.Recognizer()


def check_sleep(words):
    if 'sleep' in words or 'hibernate' in words:
        commonsense.sleepy()
        sleep()
    if ('shut' in words and 'down' in words) or 'bye' in words or 'goodbye' in words:
        tts_engine.say("I am shutting down")
        exit_flag = 1
        return True


def sleep():
    while not exit_flag:
        try:
            with speech_recognition.Microphone() as source:
                print("Say something!")
                audio = recognizer.listen(source)
            stt_response = recognizer.recognize_google(audio)
            words_stt_response = stt_response.split(' ')
            if 'wake' in words_stt_response or 'jarvis' in words_stt_response or 'wakeup' in words_stt_response:
                tts_engine.say("Hello Sir, I am back once again.")
                wakeup()
        except Exception:
            pass


def wakeup():
    with speech_recognition.Microphone() as source:
        tts_engine.say("A moment of silence, please.")
        # listens for 1 second to calibrate the energy threshold for ambient noise levels
        recognizer.adjust_for_ambient_noise(source)
    while not exit_flag:
        # _, s_data = mic.listen()
        # if mic.is_silent(s_data):
        #     commonsense.sleepy()
        #     sleep()
        with speech_recognition.Microphone() as source:
            print("Say something!")
            audio = recognizer.listen(source)
        try:
            stt_response = recognizer.recognize_google(audio)
            print("Heard: %r" % stt_response)
            if(jarvis_brain.process(stt_response)):
                pass
            else:
                if check_sleep(stt_response.split(' ')):
                    break
                response = k.respond(stt_response)
                print(response)
                tts_engine.say(response)
        except NotUnderstoodException:
            commonsense.sorry()
        except Exception:
            print("Error in processing loop:")
            traceback.print_exc()
            commonsense.uhoh()

k.loadBrain('data/jarvis.brn')
try:
    f = open('data/jarvis.cred')
except IOError:
    sys.exit(1)

bot_predicates = f.readlines()
f.close()
for bot_predicate in bot_predicates:
    key_value = bot_predicate.split('::')
    if len(key_value) == 2:
        k.setBotPredicate(key_value[0], key_value[1].rstrip('\n'))
wakeup()
