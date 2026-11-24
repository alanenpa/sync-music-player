import asyncio
import logging
from pathlib import Path

import pygame


class AudioPlayer:
    def __init__(self, no_audio=False):
        self._no_audio = no_audio           # --no-audio flag disables audio playback
        self._mixer_initialized = False  
        self._pending_task = None

    def setup_audio(self):
        """Tries to initialize mixer if audio is enabled and not already initialized."""
        if self._no_audio or self._mixer_initialized:
            return
        try:
            pygame.mixer.init()
            self._mixer_initialized = True
            logging.info("Initialized pygame.mixer")
        except pygame.error as exc:
            logging.error(f"Failed to initialize pygame.mixer; continuing without audio: {exc}")

    async def _cancel_scheduled_play(self):
        """Helper function to cancel and await any pending scheduled playback task."""
        if self._pending_task is not None and not self._pending_task.done():
            self._pending_task.cancel()
            try:
                await self._pending_task
            except asyncio.CancelledError:
                pass
        self._pending_task = None

    async def schedule_play(self, track_path, delay_s):
        resolved = Path(track_path)
        if not resolved.is_file():
            raise FileNotFoundError(f"Audio file not found: '{track_path}'")
        await self._cancel_scheduled_play()
        logging.info(f"Scheduled playback: track={track_path} delay_ms={delay_s * 1000.0:.1f}")
        self._pending_task = asyncio.create_task(self._play_after_delay(str(resolved), delay_s))

    async def _play_after_delay(self, track_path, delay_s):
        try:
            if self._mixer_initialized:
                pygame.mixer.music.load(track_path)
            if delay_s > 0:
                await asyncio.sleep(delay_s)
            if self._mixer_initialized:
                pygame.mixer.music.play()
            logging.info(f"Playback started: track={track_path}")
        except asyncio.CancelledError:
            logging.info(f"Scheduled playback cancelled: track={track_path}")
            raise
        except pygame.error as exc:
            logging.error(f"Audio playback failed: track={track_path} error={exc}")

    async def close_audio(self):
        await self._cancel_scheduled_play()
        if self._mixer_initialized:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            except pygame.error as exc:
                logging.error(f"Error closing pygame.mixer: {exc}")
            finally:
                self._mixer_initialized = False
