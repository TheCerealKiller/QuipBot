from discord.ext import tasks, commands


class Timer(commands.Cog):
    def __init__(self, duration: int, callback, never_stop=True):
        """A timer. Duration is in seconds. Callback is called every second with the current time (counting down)."""
        super().__init__()
        self.duration = duration
        self.time = duration
        self.callback = callback
        self.never_stop = never_stop

        self.count_down = tasks.loop(
            seconds=1.0, count=duration)(self.counter)

    def start(self, duration_override=None):
        duration = self.duration
        if (duration_override is not None):
            duration = duration_override

        self.time = duration
        self.count_down.start()

    def stop(self):
        self.count_down.cancel()

    async def counter(self):
        self.time -= 1
        await self.callback(self.time, self)
