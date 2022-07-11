from dataclasses import dataclass
import time


@dataclass(slots=True)
class Hertz:
    rollover: int = 100
    count: int = 0
    start: float = time.monotonic()
    hz: float = 0

    def increment(self):
        """
        Update count and if count == rollover, then print
        hertz using the format. Also at rollover, it resets
        """
        self.count += 1

        if (self.count % self.rollover) == 0:
            now = time.monotonic()
            self.hz = self.count/(now - self.start)
            self.count = 0
            self.start = now

    def reset(self):
        """
        Resets count to 0 and start to current time
        """
        self.start = time.monotonic()
        self.count = 0
