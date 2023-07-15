import asyncio
from dotenv import load_dotenv
from structures.bot import TBot

bot = TBot()

async def main():
    load_dotenv()
    async with bot:
        await bot.start()

if __name__ == "__main__":
    asyncio.run(main())