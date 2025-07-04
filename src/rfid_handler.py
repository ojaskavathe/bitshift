import threading
import time
import board
import busio
from adafruit_pn532.i2c import PN532_I2C
from adafruit_pn532.adafruit_pn532 import MIFARE_CMD_AUTH_B

class RFIDHandler:
    def __init__(self, block_num=4):
        self.block_num = block_num
        self.default_key = [0xFF] * 6
        self.scanning = False
        self.scanned_data = None
        self.scanned_uid = None
        self.thread = None
        self.lock = threading.Lock()
        self.connected = False  # Track connection status

        # Attempt to initialize the PN532
        self._initialize_pn532()

    def _initialize_pn532(self):
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.pn532 = PN532_I2C(self.i2c, debug=False)
            self.pn532.SAM_configuration()
            self.connected = True
            print("PN532 successfully initialized.")
        except Exception as e:
            self.connected = False
            print(f"Error initializing PN532: {e}")

    def start_scanning(self):
        if self.connected and not self.scanning:
            self.scanning = True
            self.thread = threading.Thread(target=self.scan_loop)
            print("i2c: ", self.i2c)
            self.thread.start()
            print("Started scanning thread.")

    def stop_scanning(self):
        if self.scanning:
            self.scanning = False
            if self.thread is not None:
                self.thread.join()
                print("Stopped scanning thread.")

    def scan_loop(self):
        while self.scanning:
            try:
                uid = self.pn532.read_passive_target(timeout=1)
                if uid:
                    print(f"Card detected with UID: {[hex(i) for i in uid]}")
                    data = self.authenticate_and_read(uid, self.block_num)
                    if data:
                        with self.lock:
                            self.scanned_data = data
                            self.scanned_uid = uid
            except Exception as e:
                print(f"Error in scanning loop: {e}")
                self.scanning = False
            time.sleep(0.5)

    def authenticate_and_read(self, uid, block_num):
        if self.pn532.mifare_classic_authenticate_block(uid, block_num, MIFARE_CMD_AUTH_B, self.default_key):
            data = self.pn532.mifare_classic_read_block(block_num)
            if data:
                print(f"Block {block_num} data: {data}")
                return data.hex()
        print(f"Failed to read block {block_num}.")
        return None

    def authenticate_and_write(self, data_hex, block_num=4):
        uid = self.pn532.read_passive_target(timeout=1)
        if not uid:
            return "No card detected."

        if len(data_hex) != 32:
            return "Data must be 32 hex characters (16 bytes)."

        try:
            data_bytes = bytes.fromhex(data_hex)
        except ValueError:
            return "Invalid hex data."

        if self.pn532.mifare_classic_authenticate_block(uid, block_num, MIFARE_CMD_AUTH_B, self.default_key):
            if self.pn532.mifare_classic_write_block(block_num, data_bytes):
                print(f"Successfully wrote to block {block_num}.")
                return "Data written successfully."
        print(f"Failed to write to block {block_num}.")
        return "Failed to write data to card."

    def get_latest_scan(self):
        with self.lock:
            if self.scanned_data and self.scanned_uid:
                return {
                    "uid": [hex(i) for i in self.scanned_uid],
                    "data": self.scanned_data
                }
            else:
                return None

    def is_connected(self):
        return self.connected

# global RFIDHandler (idk if this is a good idea but eh)
rfid_handler = RFIDHandler()
