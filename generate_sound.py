import wave
import math
import struct

filename = "sonar_beep.wav"

duration = 0.15
frequency = 880.0
sample_rate = 44100

print(f"Generating {filename}")

with wave.open(filename, 'w') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)

    for i in range(int(duration * sample_rate)):
        envelope = 1.0 - (i/(duration * sample_rate))
        value = int(32767.0 * envelope * 0.5 * math.sin(2.0 * math.pi * frequency * i/sample_rate))
        data = struct.pack('<h', value)
        wav_file.writeframesraw(data)
print("Done! File sonar_beep.wav was created!")

