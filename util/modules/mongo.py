import motor.motor_asyncio
import os
import pydash as _

class MongoDB:
    def __init__(self, uri: str) -> None:
        self.client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self.client['dim']
    
    async def set(self, *, table: str, id: str, path: str, value: any):
        item = await self.db[table].find_one({ "id": id }) or {}
        if item:
            updated = _.set_(item, path, value)
            await self.db[table].replace_one({ "id": id }, updated)
        else:
            data = _.set_({"id": id}, path, value)
            await self.db[table].insert_one(data)
    
    async def get(self, *, table: str, id: str, path: str = None):
        item = await self.db[table].find_one({"id": id})
        if not item:
            return None
        else:
            return _.get(item, path) if path else item
    
    async def delete(self, *, table: str, id: str, path: str = None):
        item = await self.db[table].find_one({"id": id})
        if not item:
            return
        else:
            if path:
                _.unset(item, path)
                await self.db[table].replace_one({"id": id}, item)
            else:
                await self.db[table].delete_one({"id": id})
    
    async def get_collection(self, *, table: str):
        item = await self.db[table].find_one()
        return item