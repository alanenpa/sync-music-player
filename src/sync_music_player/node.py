import asyncio
import logging
import time

from sync_music_player.audio import AudioPlayer
from sync_music_player.clock import ClockSync
from sync_music_player.rpc import RpcClient, RpcServer

# This file connects all components of a node
class MusicSyncNode:
    def __init__(self, node_id, listen_address, role, peers, no_audio=False, lead_time=2.0, sync_interval=30.0):
        self.node_id = node_id
        self.listen_address = listen_address
        self.role = role
        self.peers = dict(peers)
        self.lead_time = lead_time
        self.sync_interval = sync_interval
        self.client = RpcClient()
        self.clock = ClockSync()
        self.audio = AudioPlayer(no_audio=no_audio)
        self.server = RpcServer(node_id, role, listen_address, self.handle_play)
        self._sync_task = None

    async def start(self):
        logging.info(f"Starting node: id={self.node_id} role={self.role} listen={self.listen_address} peers={len(self.peers)}")
        self.audio.setup_audio()
        await self.server.start()
        if self.role == "follower" and self.peers:
            self._sync_task = asyncio.create_task(self._sync_time_to_leader_loop())

    async def _sync_time_to_leader_loop(self):
        peer_id, peer_addr = next(iter(self.peers.items()))
        while True:
            try:
                await self.clock.sync(self.client, peer_id, peer_addr, self.node_id)
            except Exception as exc:
                logging.error(f"Clock sync failed: {exc}")
            await asyncio.sleep(self.sync_interval)

    async def handle_play(self, track_path, start_at):
        """For follower. Handle a Play command received from the leader node."""
        delay_s = self.clock.delay_until(start_at)
        try:
            await self.audio.schedule_play(track_path, delay_s)
        except FileNotFoundError as exc:
            return (False, str(exc))
        return (True, f"Scheduled in {delay_s * 1000.0:.1f} ms")

    async def broadcast_play(self, track_path):
        """For Leader. Broadcast a Play command to all peers and schedule local playback."""
        if self.role != "leader":
            raise PermissionError(f"Node '{self.node_id}' is not the leader.")

        start_at = time.time() + self.lead_time
        # Schedule leader playback with "lead_time" delay
        await self.audio.schedule_play(track_path, self.clock.delay_until(start_at))
        logging.info(f"Broadcasting Play: track={track_path} start_at={start_at:.3f} peers={len(self.peers)}")

        # Send Play command to all peers in "self.peers" dictionary
        tasks = {
            peer_id: asyncio.create_task(self.client.play(peer_id, peer_addr, self.node_id, track_path, start_at))
            for peer_id, peer_addr in self.peers.items()
        }
        outcomes = {}
        # Wait for tasks to complete and log the results
        for peer_id, task in tasks.items():
            try:
                outcomes[peer_id] = await task
            except Exception as exc:
                outcomes[peer_id] = (False, str(exc))

        accepted = sum(1 for ok, _ in outcomes.values() if ok)
        logging.info(f"Broadcast Play summary: track={track_path} accepted={accepted}/{len(tasks)}")
        return outcomes

    async def check_health(self):
        # Send Health check to all peers in "self.peers" dictionary
        tasks = {
            peer_id: asyncio.create_task(self.client.health(peer_id, peer_addr, self.node_id))
            for peer_id, peer_addr in self.peers.items()
        }
        results = {}
        for peer_id, task in tasks.items():
            try:
                results[peer_id] = await task
            except Exception as exc:
                results[peer_id] = exc
        return results

    async def shutdown(self):
        logging.info(f"Shutting down node: id={self.node_id}")
        if self._sync_task is not None:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass
        await self.server.stop()
        await self.audio.close_audio()
        await self.client.close_all()
        logging.info(f"Node shutdown complete: id={self.node_id}")
