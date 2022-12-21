from traceback import format_exception
from typing import Dict
from util.modules.midb import Database
import datetime
import pydash as _
import asyncio

allowed_events = ['on_expires', 'on_create', 'on_remove', 'on_check']

class Timeouts:
    def __init__(self, db: Database) -> None:
        self.db = db
        self._callbacks: Dict[str, callable] = {}
    
    async def add(self, *, time: float, id: str, data: any):
        v = await self.get_timeouts()
        expires = self.get_timestamp() + time
        item = { 'time': time, 'expires': expires, 'id': id, 'data': data }
        v.append(item)
        self.db.set('timeouts', v, 'Main')
        await self.emit('on_create', item)
        await self.check()
    
    async def remove(self, *, id: str):
        timeouts=await self.get_timeouts()
        without = [item for item in timeouts if item["expires"] != id]
        await self.update_timeouts(without)
        await self.emit('on_remove', without)
    
    def event(self, func):
        if func.__name__ not in allowed_events:
            raise SyntaxWarning('Not a valid event')
        self._callbacks[func.__name__] = self._callbacks.get(func.__name__, []) + [func]
        return func
    
    def get_timestamp(self):
        return datetime.datetime.now().timestamp()
    
    async def emit(self, event: str, *args, **kwargs):
        try:
            [await function(*args, **kwargs) for function in self._callbacks.get(event, [])]
        except Exception as err:
            print("".join(format_exception(err, err, err.__traceback__)))
    
    async def out(self, *, item):
        v = await self.get_timeouts()
        if item in v:
            v.remove(item)
            await self.update_timeouts(v)
            await self.emit('on_expires', item)
        else:
            pass
    
    async def expire(self, item, time):
        await asyncio.sleep(time)
        await self.out(item=item)
    
    async def get_timeouts(self):
        return self.db.get('timeouts', 'Main') or []
    
    async def update_timeouts(self, value):
        self.db.set('timeouts', value, 'Main')
    
    async def check(self):
        await self.emit('on_check')
        items = await self.get_timeouts()
        for item in items:
            if self.get_timestamp() >= item['expires']:
                await self.out(item=item)
            else:
                now = self.get_timestamp()
                time_left = round(item['expires'] - now)
                asyncio.create_task(self.expire(item, time_left))