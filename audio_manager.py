import threading
import queue
import pygame
import time
import os
import glob
import comtypes.client 

class AudioEngine():
    def __init__(self):

        self._cleanup_old_files()

        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(8)
        except Exception as e:
            print(f"Audio Error: {e}")
        
        self.beep_sound = None
        if os.path.exists("sonar_beep.wav"):
            try:
                self.beep_sound = pygame.mixer.Sound("sonar_beep.wav")
                self.beep_sound.set_volume(0.4) 
            except: pass
        
        self.speech_queue = queue.Queue()
        self.is_running = True
        self.last_played_file = None

        self.thread = threading.Thread(target = self._speech_worker, daemon = True)
        self.thread.start()

    def _cleanup_old_files(self):
        for f in glob.glob("temp_voice_*.wav"):
            try: os.remove(f)
            except: pass

    def _generate_speech_file(self, text, filename):

        try:
            
            abs_path = os.path.abspath(filename)
            
            
            speak = comtypes.client.CreateObject("SAPI.SpVoice")
            filestream = comtypes.client.CreateObject("SAPI.SpFileStream")
            
        
            filestream.Open(abs_path, 3, False) 
            speak.AudioOutputStream = filestream
            
            
            speak.Rate = 2 
            
            
            speak.Speak(text)
            
            
            filestream.Close()
            return True
        except Exception as e:
            print(f"SAPI Error: {e}")
            return False

    def _speech_worker(self):
        
        comtypes.CoInitialize()

        while self.is_running:
            try:
                text = self.speech_queue.get(timeout = 0.5)
                
                timestamp = int(time.time() * 1000)
                filename = f"temp_voice_{timestamp}.wav"
                
                
                success = self._generate_speech_file(text, filename)

                if success:
                    
                    attempts = 0
                    while (not os.path.exists(filename) or os.path.getsize(filename) == 0) and attempts < 10:
                        time.sleep(0.05)
                        attempts += 1
                    
                    
                    if os.path.exists(filename) and os.path.getsize(filename) > 0:
                        try:
                            voice_sfx = pygame.mixer.Sound(os.path.abspath(filename))
                            channel_voice = pygame.mixer.Channel(1)
                            
                            if channel_voice.get_busy():
                                channel_voice.stop()
                            
                            channel_voice.play(voice_sfx)

                            
                            if self.last_played_file and os.path.exists(self.last_played_file):
                                try: os.remove(self.last_played_file)
                                except: pass
                            self.last_played_file = filename

                        except Exception as e:
                            print(f"PyGame Error: {e}")
                
                self.speech_queue.task_done()

            except queue.Empty:
                pass
            except Exception as e:
                print(f"Worker Error: {e}")

    def speak(self, text, priority="LOW"):
        if priority == "HIGH":
            with self.speech_queue.mutex:
                self.speech_queue.queue.clear()
        self.speech_queue.put(text)

    def play_sonar_beep(self):
        if self.beep_sound:
            try:
                pygame.mixer.Channel(0).play(self.beep_sound)
            except: pass
            
    def stop_all(self):
        self.is_running = False
        pygame.mixer.stop()
        self._cleanup_old_files()