import aiohttp
from aiohttp.client_exceptions import ClientResponseError
from loguru import logger


class MatrixWebhook:
    def __init__(self, config):
        self.room = config['matrix_room']
        self.token = config['matrix_token']
        self.url = config['matrix_url']
        logger.info(f"sending to {self.room}")

    async def sendmsg(self, text):
        for _ in range(5):
            try:
                return await self._sendmsg(text)
            except ClientResponseError as e:
                logger.warning(e)
        else:
            logger.error("could not send webhook")

    async def _sendmsg(self, text):
        data = {
            'room': self.room,
            'token': self.token,
            'text': text
        }
        async with aiohttp.ClientSession(raise_for_status=True) as sess:
            async with sess.post(self.url, json=data) as r:
                j = await r.json()
                return j
