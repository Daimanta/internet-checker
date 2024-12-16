import subprocess
import winsound
from threading import Thread

default_adresses = ["1.1.1.1", "2.2.4.4", "8.8.8.8"]
maximum_failed_share = 0.75

class Pinger:
    def __init__(self, address, count):
        self.address = address
        self.count = count
        self.connected = False

    def ping(self):
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

    def is_connected(self):
        return self.connected


def play_alarm_sound():
    winsound.PlaySound("alarm.wav", winsound.SND_FILENAME)

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

