import bluetooth
import time
import struct
from hub import port

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
            print('.', end='')
            
            if name == '':
                return
            
            for n in self.names:
                if name in n:
                    return
            
            self.names.append(name)
            print(name)
            self.handle_name(name)

        elif event == IRQ_SCAN_DONE:
            self.scanning = False
            
    def handle_name(self, name):
        if name.startswith('Message:'):
            message = name.split(':', 1)[1]
            print('Received Message:', message)

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

    def scan(self, duration=2000):
        self.scanning = True
        self._ble.gap_scan(duration, 30000, 30000)

    def stop_scan(self):
        self._ble.gap_scan(None)
        self.scanning = False


c = Sniff()
d = 3000

while True:
    c.scan(d)
    time.sleep(d / 1000)
    c.stop_scan()
    print(c.names)
    c.names.clear()
