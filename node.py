import asyncio, json, sys, time
import pygame

pygame.mixer.init()
offset = 0.0

async def play_at(path, start_at):
    pygame.mixer.music.load(path)
    await asyncio.sleep(max(start_at - offset - time.time(), 0))
    pygame.mixer.music.play()

async def handle(reader, writer):
    while line := await reader.readline():
        msg = json.loads(line)
        if msg["type"] == "PING":
            writer.write((json.dumps({"time": time.time()}) + "\n").encode())
            await writer.drain()
        elif msg["type"] == "PLAY":
            asyncio.create_task(play_at(msg["file"], msg["start_at"]))

async def send(host, port, msg):
    _, writer = await asyncio.open_connection(host, port)
    writer.write((json.dumps(msg) + "\n").encode())
    await writer.drain()

async def get_offset(host, port):
    reader, writer = await asyncio.open_connection(host, port)
    t0 = time.time()
    writer.write(b'{"type": "PING"}\n')
    await writer.drain()
    leader_time = json.loads(await reader.readline())["time"]
    t1 = time.time()
    return leader_time - (t0 + t1) / 2

async def main():
    global offset
    role, port = sys.argv[1], int(sys.argv[2])
    server = await asyncio.start_server(handle, "0.0.0.0", port)
    if role == "follow":
        host, leader_port = sys.argv[3].split(":")
        offset = await get_offset(host, int(leader_port))
        print(f"offset: {offset * 1000:.1f} ms")
    else:
        path, peers = sys.argv[3], sys.argv[4:]
        await asyncio.to_thread(input, "Press Enter to play... ")
        start_at = time.time() + 2
        for peer in peers:
            host, p = peer.split(":")
            await send(host, int(p), {"type": "PLAY", "file": path, "start_at": start_at})
        asyncio.create_task(play_at(path, start_at))
    async with server:
        await server.serve_forever()

asyncio.run(main())