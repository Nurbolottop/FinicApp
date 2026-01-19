import re

from rest_framework.throttling import ScopedRateThrottle


class ScopedRateThrottleWithPeriods(ScopedRateThrottle):
    duration_re = re.compile(r"^(?P<count>\d+)\/(?P<period>\d+)(?P<unit>sec|min|hour|day)$")

    def parse_rate(self, rate):
        if rate is None:
            return (None, None)

        rate = rate.strip()

        try:
            return super().parse_rate(rate)
        except Exception:
            match = self.duration_re.match(rate)
            if not match:
                raise

            num_requests = int(match.group("count"))
            period = int(match.group("period"))
            unit = match.group("unit")

            duration = {
                "sec": 1,
                "min": 60,
                "hour": 60 * 60,
                "day": 60 * 60 * 24,
            }[unit] * period

            return (num_requests, duration)
