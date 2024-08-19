import json
import time
from typing import Optional
from urllib.parse import parse_qs
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer, AsyncWebsocketConsumer
from channels.consumer import AsyncConsumer
import json
import asyncio
import psutil
from channels.exceptions import StopConsumer

class observations(WebsocketConsumer):
    def connect(self):
        ip = self.scope["url_route"]["kwargs"].get("ip_address", None)
        if ip:
            self.room_group_name = f"ip_{ip}"
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )
            self.accept()
            # self.accept(
            #     "Token"
            # )
            # https://github.com/django/channels/issues/1369#issuecomment-724299511

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from room group
    def send_observation(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps(message))


# class LoggerConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.room_name = "logger"
#         self.room_group_name = f"logger_{self.room_name}"

#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)

#         await self.accept()

#         # Start sending status updates
#         asyncio.create_task(self.send_status())

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def send_status(self):
#         while True:
#             try:
#                 state = {
#                     "type": "resource",
#                     "cpu": f"{psutil.cpu_percent(interval=1.0):.2f}",
#                     "memory": f"{psutil.virtual_memory().percent:.2f}",
#                     "uptime": psutil.boot_time(),
#                     "load": f"{psutil.getloadavg()[1]:.2f}",
#                 }
#                 print(f"Sending data: {state}")  # Debug log
#                 await self.send(text_data=json.dumps(state))
#                 await asyncio.sleep(1)
#             except Exception as e:
#                 print(f"Error in send_status: {e}")
#                 break


class LoggerConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        self.connected = True

        await self.send({"type": "websocket.accept"})

        while self.connected:
            await asyncio.sleep(2)
            uptime = (time.time() - psutil.boot_time()) * 1000
            state = {
                "type": "RESOURCE",
                "cpu": f"{psutil.cpu_percent(interval=1.0):.2f}",
                "memory": f"{psutil.virtual_memory().percent:.2f}",
                "uptime": uptime,
                "load": f"{psutil.getloadavg()[1]:.2f}",
            }

            await self.send({"type": "websocket.send", "text": json.dumps(state)})

    async def disconnect(self, event):
        self.connected = False
        raise StopConsumer()
