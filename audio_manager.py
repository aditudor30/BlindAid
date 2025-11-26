import pyttsx3
import threading
import queue
import pygame
import time
import os


class AudioEngine():
    def __init__(self):
        self.engine = pyttsx3.init()
        self.queue = queue.Queue()

        pygame.mixer.init()

        if os.path.exists("sonar_beep.wav"):
            self.beep_sound = pygame.mixer.Sound("sonar_beep.wav")
            self.beep_sound.set_volume(0.6)
        else:
            print("Sound is missing!")
            self.beep_sound = None

        self.is_running = True

        self.thread = threading.Thread(target = self._worker, daemon = True)
        self.thread.start()

    def _worker(self):
        while self.is_running:
            try:
                text, priority = self.queue.get(timeout = 0.05)

                if priority == 'HIGH':
                    self.engine.stop()
                
                self.engine.say(text)
                self.engine.runAndWait()
                self.queue.task_done()
            except queue.Empty:
                pass
    
    def speak(self, text, priority="LOW"):

        if priority == "HIGH":
            with self.queue.mutex:
                self.queue.queue.clear()
        self.queue.put((text, priority))

    def play_sonar_beep(self):
        if self.beep_sound:
            self.beep_sound.play()
            
