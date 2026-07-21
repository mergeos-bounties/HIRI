import asyncio

class WebRTCStreamProxy:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.clients = []

    async def start(self):
        print(f"Starting WebRTC proxy for RTSP stream: {self.rtsp_url}")
        # Dummy loop simulating stream translation
        while True:
            await asyncio.sleep(1)
            self._broadcast_frame()

    def _broadcast_frame(self):
        if self.clients:
            print(f"Broadcasting WebRTC frame to {len(self.clients)} clients.")

    def add_client(self, client_id):
        self.clients.append(client_id)
        print(f"Added client {client_id}")

    def remove_client(self, client_id):
        if client_id in self.clients:
            self.clients.remove(client_id)
            print(f"Removed client {client_id}")

async def main():
    proxy = WebRTCStreamProxy("rtsp://admin:admin@192.168.1.100:554/stream")
    proxy.add_client("client_1")
    await proxy.start()

if __name__ == "__main__":
    asyncio.run(main())