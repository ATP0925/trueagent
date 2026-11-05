"""
VoxCore Full-Duplex Live Voice Engine & Barge-In Coordinator for TrueAgent
Enables real-time bidirectional multimodal audio streaming with instant interruption.
"""

import sys
import queue
import threading
import numpy as np
from typing import Optional, Callable

try:
    import sounddevice as sd
    SOUNDDEVICE_AVAILABLE = True
except ImportError:
    SOUNDDEVICE_AVAILABLE = False


class VoxBargeInCoordinator:
    """Manages audio queue flushing and turn-taking state transitions."""
    def __init__(self, on_interruption: Optional[Callable[[], None]] = None):
        self.state = "IDLE"
        self.on_interruption = on_interruption
        self.interruption_count = 0
        self.turns_count = 0

    def trigger_interruption(self):
        self.interruption_count += 1
        self.state = "INTERRUPTED"
        if self.on_interruption:
            self.on_interruption()

    def set_speaking(self):
        self.turns_count += 1
        self.state = "SPEAKING"

    def set_idle(self):
        self.state = "IDLE"


class VoxAudioStreamManager:
    """Handles sound card input (16kHz) and output (24kHz) streaming."""
    def __init__(
        self,
        input_rate: int = 16000,
        output_rate: int = 24000,
        chunk_size: int = 1024,
        vad_threshold: float = 0.015,
        on_interruption: Optional[Callable[[], None]] = None
    ):
        self.input_rate = input_rate
        self.output_rate = output_rate
        self.chunk_size = chunk_size
        self.vad_threshold = vad_threshold
        self.on_interruption = on_interruption

        self.input_queue: queue.Queue = queue.Queue()
        self.output_queue: queue.Queue = queue.Queue()
        self.is_playing = False
        self.running = False
        self.input_stream = None
        self.output_stream = None

    def _input_callback(self, indata, frames, time_info, status):
        pcm = indata.copy()
        raw_bytes = (pcm * 32767).astype(np.int16).tobytes()
        self.input_queue.put(raw_bytes)

        rms = np.sqrt(np.mean(pcm**2)) if len(pcm) > 0 else 0.0
        if self.is_playing and rms > self.vad_threshold:
            self.flush()
            if self.on_interruption:
                self.on_interruption()

    def _output_callback(self, outdata, frames, time_info, status):
        needed = frames * 2
        buf = bytearray()
        while len(buf) < needed:
            try:
                chunk = self.output_queue.get_nowait()
                if chunk is None:
                    break
                buf.extend(chunk)
            except queue.Empty:
                break

        if len(buf) >= needed:
            to_play = buf[:needed]
            rem = buf[needed:]
            if rem:
                self.output_queue.queue.appendleft(bytes(rem))
            outdata[:, 0] = np.frombuffer(to_play, dtype=np.int16).astype(np.float32) / 32767.0
            self.is_playing = True
        elif len(buf) > 0:
            to_play = bytes(buf)
            audio = np.frombuffer(to_play, dtype=np.int16).astype(np.float32) / 32767.0
            outdata[:len(audio), 0] = audio
            outdata[len(audio):, 0] = 0.0
            self.is_playing = True
        else:
            outdata.fill(0.0)
            self.is_playing = False

    def start(self):
        if not SOUNDDEVICE_AVAILABLE or self.running:
            return
        self.running = True
        self.input_stream = sd.InputStream(
            samplerate=self.input_rate,
            channels=1,
            dtype="float32",
            blocksize=self.chunk_size,
            callback=self._input_callback
        )
        self.output_stream = sd.OutputStream(
            samplerate=self.output_rate,
            channels=1,
            dtype="float32",
            blocksize=self.chunk_size,
            callback=self._output_callback
        )
        self.input_stream.start()
        self.output_stream.start()

    def flush(self):
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break
        self.is_playing = False

    def stop(self):
        self.running = False
        self.flush()
        if self.input_stream:
            try:
                self.input_stream.stop()
                self.input_stream.close()
            except Exception:
                pass
        if self.output_stream:
            try:
                self.output_stream.stop()
                self.output_stream.close()
            except Exception:
                pass
