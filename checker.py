import subprocess
from sys import platform
import os
from threading import Thread

default_adresses = ["1.1.1.1", "2.2.4.4", "8.8.8.8"]
maximum_failed_share = 0.75

class Pinger:
    def __init__(self, address, count):
        self.address = address
        self.count = count
        self.connected = False

    def _ping_windows(self):
        process = subprocess.run(["ping", default_adresses[0], "-n", str(self.count)], capture_output=True)
        packet_array = process.stdout.decode("utf-8").split("\r\n")
        packet_string = ""
        i = len(packet_array) - 1
        while i >= 0:
            if packet_array[i].__contains__("Packets"):
                packet_string = packet_array[i]
                break
            i -= 1
        start_index = packet_string.index("Lost = ")
        end_index = packet_string[start_index+7:].index(" (")
        lost_packets = int(packet_string[start_index+7:start_index+7+end_index])
        if lost_packets / (1.0 * self.count) > maximum_failed_share:
            self.connected = False
        else:
            self.connected = True

    def _ping_linux(self):
        process = subprocess.run(["ping", "-c", str(self.count), default_adresses[0], "-q"], capture_output=True)
        packet_array = process.stdout.decode("utf-8").split("\n")
        summary_line = ""
        for line in packet_array:
            if "packets transmitted" in line:
                summary_line = line
                break
        split_summary = summary_line.split(",")
        received = int(split_summary[1].strip().split(" ")[0])
        lost_packets = self.count - received
        if lost_packets / (1.0 * self.count) > maximum_failed_share:
            self.connected = False
        else:
            self.connected = True

    def ping(self):
        if platform == "win32":
            self._ping_windows()
        else:
            self._ping_linux()

    def is_connected(self):
        return self.connected


def play_alarm_sound():
    if platform == "win32":
        import winsound
        winsound.PlaySound("alarm.wav", winsound.SND_FILENAME)
    elif platform == "linux":
        os.system('aplay alarm.wav')

pingers = []
for address in default_adresses:
    pingers.append(Pinger(address, 4))

done = False
while not done:
    done = True
    for pinger in pingers:
        pinger.ping()
        if not pinger.is_connected():
            done = False


play_sound_thread = Thread(target=play_alarm_sound, daemon=True)
play_sound_thread.start()
input("Press any key to exit")
exit(0)

