import bluetooth
import time
import struct

NAME_FLAG = 0x09
IRQ_SCAN_RESULT = 5
IRQ_SCAN_DONE = 6

class Sniff:
    def __init__(self):
        self._ble = bluetooth.BLE()
        self._ble.active(True)
        self._ble.irq(self._irq)
        self.scanning = False
        self.names = []

    def _irq(self, event, data):
        if event == IRQ_SCAN_RESULT:
            addr_type, addr, adv_type, rssi, adv_data = data
            name = self.decode_name(adv_data)
            if name and name not in self.names:
                self.names.append(name)
                print(f"Received: {name}")
        elif event == IRQ_SCAN_DONE:
            self.scanning = False

    def decode_field(self, payload, adv_type):
        i = 0
        result = []
        while i + 1 < len(payload):
            if payload[i + 1] == adv_type:
                result.append(payload[i + 2 : i + payload[i] + 1])
            i += 1 + payload[i]
        return result

    def decode_name(self, payload):
        n = self.decode_field(payload, NAME_FLAG)
        return str(n[0], "utf-8") if n else ""

    def scan(self, duration=1000):
        self.scanning = True
        self._ble.gap_scan(duration, 30000, 30000)
        while self.scanning:
            time.sleep(0.1)  # Short sleep to allow for event processing

    def stop_scan(self):
        self._ble.gap_scan(None)
        self.scanning = False

c = Sniff()

while True:
    c.scan(1000)  # Scan for 1 second
    c.stop_scan()
    c.names.clear()
    time.sleep(0.1)  # Short delay between scans