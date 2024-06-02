import json
from typing import Optional
from urllib.parse import parse_qs
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


class mock_request_consumer(WebsocketConsumer):
    room_name="mock_req"
    def connect(self):
        self.room_group_name = f"send_{self.room_name}"
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "accept_mock_req", "message": message}
        )

    # Receive message from room group
    def send_mock_req(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))

    def accept_mock_req(self, event):
        message = event["message"]
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))


class observations(WebsocketConsumer):
    def connect(self):
        ip = self.scope["url_route"]["kwargs"].get("ip_address", None)
        if ip:
            self.room_group_name = f"ip_{ip}"
            print(self.room_group_name)
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )
            self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    # # Receive message from WebSocket
    # def receive(self, text_data):
    #     text_data_json = json.loads(text_data)
    #     message = text_data_json["message"]
    #     # Send message to room group
    #     async_to_sync(self.channel_layer.group_send)(
    #         self.room_group_name, {"type": "accept_mock_req", "message": message}
    #     )

    # Receive message from room group
    def send_observation(self, event):
        message = event["message"]

        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))
