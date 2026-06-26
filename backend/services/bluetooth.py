class BluetoothService:
    def __init__(self):
        self.connected = True
        self.device = "iPhone de Teste"

    def get_status(self):
        return {
            "connected": self.connected,
            "device": self.device
        }