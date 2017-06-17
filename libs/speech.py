#!/usr/bin/env python3

# NOTE: this example requires PyAudio because it uses the Microphone class
import subprocess
import time

import speech_recognition as sr
from gtts import gTTS
import pygame

from libs import utils

log = utils.get_logger(__name__)
r = sr.Recognizer()

pygame.mixer.init()


def speech_to_text(timeout=15, phrase_time_limit=10):
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError as e:
            log.info('Timed out')
            return False

        try:
            return r.recognize_google(audio)

        except sr.UnknownValueError:
            log.info("Google Speech Recognition could not understand audio")
            return False

        except sr.RequestError as e:
            log.info("Could not request results from Google Speech Recognition service; {0}".format(e))
            return False


def play_text(text, wait_to_finish=True):
    try:
        tts = gTTS(text=text, lang='en')
        filename = '/tmp/temp.mp3'
        tts.save(filename)
        # music = pyglet.media.load(filename, streaming=False)
        # music.play()
        log.info("Speaking: %s" % (text,))
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()

        if wait_to_finish:
            while pygame.mixer.music.get_busy():
                time.sleep(1)

    except BaseException as e:
        log.info(e)
