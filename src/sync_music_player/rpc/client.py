import logging
import time
import grpc

from sync_music_player.rpc.generated.node_pb2 import PingRequest, PlayRequest, HealthRequest
from sync_music_player.rpc.generated import node_pb2_grpc

class RpcClient:
    def __init__(self, timeout=5.0):
        self.timeout = timeout
        self._channels = {}
        self._stubs = {}

    def _get_stub(self, peer_id, peer_addr):
        channel = self._channels.get(peer_id)
        if channel is not None and channel.get_state(try_to_connect=False) != grpc.ChannelConnectivity.SHUTDOWN:
            return self._stubs[peer_id]
        # If there was no existing channel or it was closed, create a new one
        channel = grpc.aio.insecure_channel(peer_addr)
        stub = node_pb2_grpc.NodeServiceStub(channel)
        self._channels[peer_id] = channel
        self._stubs[peer_id] = stub
        logging.info(f"Opened gRPC channel: peer={peer_id} address={peer_addr}")
        return stub

    async def _call(self, peer_id, peer_addr, method, request):
        """Send a gRPC request to a peer over its persistent channel and wrap any RPC errors."""
        stub = self._get_stub(peer_id, peer_addr)
        try:
            return await getattr(stub, method)(request, timeout=self.timeout)
        except grpc.aio.AioRpcError as exc:
            logging.error(f"{method} to {peer_id} failed: {exc.details()}")
            raise RuntimeError(f"{method} to {peer_id} failed: {exc.details()}") from exc

    async def ping(self, peer_id, peer_addr, sender_id):
        t0 = time.time()
        logging.info(f"Sending Ping: peer={peer_id}")
        resp = await self._call(peer_id, peer_addr, "Ping", PingRequest(sender_id=sender_id, client_send_time=t0))
        return (t0, resp.server_time, time.time())

    async def play(self, peer_id, peer_addr, sender_id, track_path, start_at):
        logging.info(f"Sending Play command: peer={peer_id} track={track_path} start_at={start_at:.3f}")
        resp = await self._call(peer_id, peer_addr, "Play", PlayRequest(sender_id=sender_id, track_path=track_path, start_at_unix=start_at))
        logging.info(f"Play response: peer={peer_id} accepted={resp.accepted} message={resp.message}")
        return (resp.accepted, resp.message)

    async def health(self, peer_id, peer_addr, sender_id):
        logging.info(f"Sending Health check: peer={peer_id}")
        t0 = time.time()
        resp = await self._call(peer_id, peer_addr, "Health", HealthRequest(sender_id=sender_id))
        rtt_ms = (time.time() - t0) * 1000.0
        logging.info(f"Health response: peer={resp.node_id} role={resp.role} healthy={resp.healthy} rtt_ms={rtt_ms:.2f}")
        return {"node_id": resp.node_id, "role": resp.role, "healthy": resp.healthy, "rtt_ms": rtt_ms}

    def active_peers(self):
        return list(self._channels)

    async def close_all(self):
        for peer_id, channel in list(self._channels.items()):
            try:
                await channel.close()
                logging.info(f"Closed gRPC channel: peer={peer_id}")
            except Exception as exc:
                logging.error(f"Error closing gRPC channel: peer={peer_id} error={exc}")
        self._channels.clear()
        self._stubs.clear()
