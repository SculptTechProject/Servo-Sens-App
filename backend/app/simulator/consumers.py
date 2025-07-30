from channels.generic.websocket import AsyncJsonWebsocketConsumer


class WorkspaceConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.ws_id = self.scope["url_route"]["kwargs"]["ws_id"]
        self.group = f"ws_{self.ws_id}"
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group, self.channel_name)

    async def ws_message(self, event):
        await self.send_json(event["data"])
