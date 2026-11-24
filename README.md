# Sync Music Player

Distributed synchronized music player built with Python, `grpcio`, and `pygame`. Consensus mechanism between nodes is on the pipeline. 

## Setup

```bash
uv sync
```

Ensure the same audio file is available on every node (for example `blinkmoth.mp3`).

## Project Structure

```text
proto/node.proto       # gRPC service and message definitions
scripts/
└── generate_proto.py  # Compiles node.proto into src/sync_music_player/rpc/generated/
src/sync_music_player/
├── cli.py             # CLI flags and interactive command loop
├── node.py            # MusicSyncNode orchestrator
├── clock.py           # Ping-based clock offset synchronization
├── audio.py           # Scheduled playback via pygame.mixer
└── rpc/
    ├── client.py      # Persistent gRPC channels and RPC calls
    ├── server.py      # NodeService gRPC handlers and server lifecycle
    └── generated/     # Generated protobuf/gRPC modules
```

## Usage

```bash
# Terminal 1 (Leader)
uv run sync-music-player --id node-1 --listen 127.0.0.1:6000 --role leader --peers node-2=127.0.0.1:6001

# Terminal 2 (Follower)
uv run sync-music-player --id node-2 --listen 127.0.0.1:6001 --role follower --peers node-1=127.0.0.1:6000
```

Add `--no-audio` to run without initializing `pygame.mixer`.

### Interactive Commands

- `play <track_path>` — Broadcast synchronized playback from the leader.
  - `play blinkmoth.mp3` for the default test file.
- `status` — Show node state, active peer connections, and peer health.
- `quit` / `exit` — Shut down the node gracefully.

Followers synchronize their clock automatically every 30 seconds. Logs are written to `logs/<node_id>.log`.

## Regenerating gRPC Stubs

If `proto/node.proto` changes, regenerate the stubs with:

```bash
uv run python scripts/generate_proto.py
```
