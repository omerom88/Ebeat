import mido
import time

ports = ("IAC Driver Melody 1", "IAC Driver Melody 2")
for port in ports:
    output_port = mido.open_output(port)
    output_port.send(mido.Message("note_on", note=60))
    time.sleep(0.5)
    output_port.send(mido.Message("note_off", note=60))
    time.sleep(1)
