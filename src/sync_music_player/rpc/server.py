import logging
import time

import grpc

from sync_music_player.rpc.generated.node_pb2 import HealthResponse, PingResponse, PlayResponse
from sync_music_player.rpc.generated import node_pb2_grpc


class RpcServer(node_pb2_grpc.NodeServiceServicer):
    def __init__(self, node_id, role, listen_address, on_play):
        self.node_id = node_id
        self.role = role
        self.listen_address = listen_address
        self._on_play = on_play
        self._server = None

    async def Ping(self, request, context):
        logging.info(f"Received Ping: from={request.sender_id or 'unknown'}")
        return PingResponse(responder_id=self.node_id, server_time=time.time())

    async def Play(self, request, context):
        logging.info(f"Received Play command: from={request.sender_id or 'unknown'} track={request.track_path} start_at={request.start_at_unix:.3f}")
        if not request.track_path.strip() or request.start_at_unix <= 0:
            await context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid PlayRequest.")
        accepted, message = await self._on_play(request.track_path, request.start_at_unix)
        return PlayResponse(accepted=accepted, message=message)

    async def Health(self, request, context):
        logging.info(f"Received Health check: from={request.sender_id or 'unknown'}")
        return HealthResponse(node_id=self.node_id, role=self.role, healthy=True, server_time=time.time())

    async def start(self):
        if self._server is not None:
            return
        server = grpc.aio.server()
        node_pb2_grpc.add_NodeServiceServicer_to_server(self, server)
        if server.add_insecure_port(self.listen_address) == 0:
            raise RuntimeError(f"Failed to bind gRPC server on '{self.listen_address}'.")
        await server.start()
        self._server = server
        logging.info(f"gRPC server listening on {self.listen_address}")

    async def stop(self, grace=3.0):
        if self._server is None:
            return
        server = self._server
        self._server = None
        await server.stop(grace=grace)
        logging.info("gRPC server stopped")
