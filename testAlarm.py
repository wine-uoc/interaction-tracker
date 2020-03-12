import os
import time
duration = 0.15  # seconds
freq = 440  # Hz
os.system('play -nq -t alsa synth {} sine {}'.format(duration, 760))
time.sleep(0.5)
os.system('play -nq -t alsa synth {} sine {}'.format(duration, 440))