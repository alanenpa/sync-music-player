import logging
import time


class ClockSync:
    def __init__(self):
        self.offset_s = 0.0
        self.last_rtt_s = None

    async def sync(self, client, peer_id, peer_addr, sender_id):
        t0, server_time, t1 = await client.ping(peer_id, peer_addr, sender_id)
        rtt = max(t1 - t0, 0.0)
        self.offset_s = server_time - (t0 + rtt / 2.0)
        self.last_rtt_s = rtt
        logging.info(f"Clock synchronized: peer={peer_id} offset_ms={self.offset_s * 1000.0:.2f} rtt_ms={rtt * 1000.0:.2f}")
        return (self.offset_s, rtt)

    def delay_until(self, target_unix):
        return max((target_unix - self.offset_s) - time.time(), 0.0)
