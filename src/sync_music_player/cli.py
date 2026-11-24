from argparse import ArgumentParser
import asyncio
import logging
from pathlib import Path
import sys

from sync_music_player.node import MusicSyncNode


def parse_peers(specs):
    peers = {}
    for spec in specs:
        peer_id, peer_addr = spec.split("=", 1) if "=" in spec else (spec, spec)
        if not peer_id.strip() or not peer_addr.strip():
            raise ValueError(f"Invalid peer '{spec}': expected 'node_id=host:port'.")
        peers[peer_id.strip()] = peer_addr.strip()
    return peers


async def run(node):
    await node.start()
    print("Commands: play <file>, status, quit")
    try:
        while True:
            try:
                # Read user input without blocking the event loop
                line = (await asyncio.to_thread(input, f"[{node.node_id}]> ")).strip()
            except EOFError:
                await asyncio.Future()  # In case of ctrl + D or uninteractive terminal, wait for a signal to exit gracefully

            parts = line.split()
            if not parts:
                continue
            cmd = parts[0].lower()

            if cmd in ("quit", "exit"):
                break
            if cmd == "status":
                print(f"Node '{node.node_id}' | role={node.role} offset={node.clock.offset_s * 1000:.2f}ms peers={node.client.active_peers()}")
                for peer_id, res in (await node.check_health()).items(): # check_health request for each peer
                    print(f"  - {peer_id}: {res}")
            elif cmd == "play" and len(parts) >= 2:
                try:
                    for peer_id, (ok, msg) in (await node.broadcast_play(parts[1])).items():
                        print(f"  - {peer_id}: [{'OK' if ok else 'FAIL'}] {msg}")
                except Exception as exc:
                    print(f"Play failed: {exc}")
            else:
                print("Commands: play <file>, status, quit")
    finally:
        await node.shutdown()


def main(argv=None):
    parser = ArgumentParser(prog="sync-music-player", description="Synchronized distributed music player over gRPC.")
    parser.add_argument("--id", required=True, help="Unique node ID (e.g., node-1).")
    parser.add_argument("--listen", required=True, help="Listen address (e.g., 0.0.0.0:6000).")
    parser.add_argument("--peers", nargs="*", default=[], help="Peers in 'id=host:port' form.")
    parser.add_argument("--role", choices=["leader", "follower"], default="follower", help="Node role (default: follower).")
    parser.add_argument("--no-audio", action="store_true", help="Disable pygame audio initialization.")
    args = parser.parse_args(argv)

    try:
        peers = parse_peers(args.peers)
    except ValueError as exc:
        parser.error(str(exc))

    Path("logs").mkdir(exist_ok=True)
    log_path = Path("logs") / f"{args.id}.log"
    logging.basicConfig(filename=log_path, level=logging.INFO, format="%(levelname)s: %(message)s")
    print(f"Logging to {log_path}")

    node = MusicSyncNode(args.id, args.listen, args.role, peers, no_audio=args.no_audio)
    try:
        asyncio.run(run(node))
    except KeyboardInterrupt:
        sys.exit(0)
