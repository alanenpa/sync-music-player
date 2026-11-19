# Sync Music Player

## Requirements
 
- [uv](https://docs.astral.sh/uv/)
- Python 3.13 (uv installs it automatically)
- pygame (installed by `uv sync`)
 
## Setup
 
```
uv sync
```
 
Put the same audio file in the project folder on every machine (or use blinkmoth.mp3 already in repo).
 
## Usage
 
Start the leader first, then the followers, then press Enter in the leader's terminal.
 
Leader:
 
```
uv run node.py lead <port> <audio-file> <follower-ip:port> ...
```
 
Follower:
 
```
uv run node.py follow <port> <leader-ip:port>
```
 
Example on one machine, with each command in its own terminal:
 
```
uv run node.py lead 6000 song.mp3 127.0.0.1:6001 127.0.0.1:6002
uv run node.py follow 6001 127.0.0.1:6000
uv run node.py follow 6002 127.0.0.1:6000
```
 