import asyncio

from hikari import RESTApp, TokenType

from config import env


class RESTAppClient:
    def __init__(self):
        self.bot: RESTApp = RESTApp()

        self.loop = asyncio.new_event_loop()
        self.loop.run_until_complete(self.bot.start())

    async def _fetch_message(self, channel_id: int, message_id: int):
        async with self.bot.acquire(env["TOKEN"], TokenType.BOT) as client:
            message = await client.fetch_message(channel_id, message_id)
        return message

    def fetch_message(self, channel_id: int, message_id: int):
        return self.loop.run_until_complete(self._fetch_message(channel_id, message_id))

    async def _edit_message(self, message, content: str):
        async with self.bot.acquire(env["TOKEN"], TokenType.BOT) as client:
            await client.edit_message(message.channel_id, message.id, content)

    def edit_message(self, message, content: str):
        self.loop.run_until_complete(self._edit_message(message, content))

    async def _fetch_user(self, user_id: int):
        async with self.bot.acquire(env["TOKEN"], TokenType.BOT) as client:
            user = await client.fetch_user(user_id)
        return user

    def fetch_user(self, user_id: int):
        return self.loop.run_until_complete(self._fetch_user(user_id))

    async def _get_all_bot_guilds(self):
        async with self.bot.acquire(env["TOKEN"], TokenType.BOT) as client:
            guilds = await client.fetch_my_guilds()
        return guilds

    def get_all_bot_guilds(self):
        return self.loop.run_until_complete(self._get_all_bot_guilds())
