from .compiler import Compiler
from .interpreter_funcs import Data, FUNCS
from discord.ext import commands

class Interpreter:
    def __init__(self, util):
        self.compiler = Compiler("")
        self.compiler.set_funcs(list(FUNCS.keys()))
        self.funcs = FUNCS.items()
        self.util = util

    async def resolve_overloads(self, d: Data):
        if not d or not len(d.func["fields"]):
            return
        for i in range(0, len(d.func["fields"])):
            d.func = await self.resolve_overload(d, i)
        return d
    
    async def resolve_overload(self, d: Data, index: int):
        if len(d.func["fields"]) and len(d.func["fields"]) >= index:
            for over in d.func["fields"][index]["overs"]:
                found = next((x for x in d.interpreter.funcs if x[0] == over["name"].lower()), None)
                if found:
                    NEWDATA = Data()
                    NEWDATA.embed = d.embed
                    NEWDATA.buttons = d.buttons
                    NEWDATA.interpreter = d.interpreter
                    NEWDATA.metadata = d.metadata
                    NEWDATA.ctx = d.ctx
                    NEWDATA.func = over
                    NEWDATA.code = d.func["fields"][index]["value"]
                    reject = await found[1](NEWDATA, self.util)
                    if reject and isinstance(reject, str) and d.func["inside"] and len(d.func["fields"]):
                        d.func["fields"][index]["value"] = reject
                        d.func["inside"] = ";".join(list(map(lambda f: f["value"], d.func["fields"])))
                        d.func["total"] = f"{d.func['name']}[{d.func['inside']}]"
        return d.func

    async def run_function(self, fn, d: Data):
        found = next((x for x in d.interpreter.funcs if x[0] == fn["name"].lower()), None)
        if found:
            d.func = fn
            reject = await found[1](d, self.util)
            if reject and isinstance(reject, str):
                d.code = reject.strip() or ""
    
    async def read(self, text: str, ctx: commands.Context):
        if not text:
            return {}
        await self.compiler.set_code(text)
        await self.compiler.magic()
        data = Data()
        data.code = self.compiler.result or text
        data.interpreter = self
        data.ctx = ctx
        entries = list(self.compiler.matched.copy().items()) if self.compiler.matched else None
        if entries:
            for fn in entries[::-1]:
                await self.run_function(fn[1], data)
        if data.embed and not data.embed.title and not data.embed.description and not data.embed.author.name and not data.embed.footer.text and not data.embed.image.url and not data.embed.thumbnail.url:
            data.embed = None
        return data