import json
from EdgeGPT import Chatbot, ConversationStyle

class BingChat:
    """ContextManager for Bing Chatbot

    Usage:
        ``\`
        async with BingChat("path/to/cookies.json") as bot:
            response = await bot.ask(prompt="Tell me a joke", conversation_style=ConversationStyle.precise)

        print(response)
        `\``
    """

    def __init__(self, cookies_path: str):
        self.cookies = self.load_cookies(cookies_path)
   
    def load_cookies(self, cookies_path: str):
        with open('./cookies.json', 'r') as f:
            return json.load(f)
        
    async def __aenter__(self):
        self.bot = await Chatbot.create(cookies=self.cookies)
        return self

    async def ask(
        self,
        prompt: str,
        wss_link: str = "wss://sydney.bing.com/sydney/ChatHub",
        conversation_style = None,
        options: dict = None,
        webpage_context: str | None = None,
        search_result: bool = False,
    ):
        """Ask a question to the bot and return its response"""
        response = await self.bot.ask(prompt, wss_link, conversation_style, options, webpage_context, search_result)
        return response["item"]["messages"][1]["text"].replace('Bing', 'Tokyo').replace('bing', 'tokyo')

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.bot.close()