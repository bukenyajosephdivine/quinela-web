import asyncio
import edge_tts
import sounddevice as sd
import soundfile as sf
import tempfile
import os

VOICE = "en-US-JennyNeural"   # female, natural voice

async def speak(text: str):
    if not text.strip():
        return

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        audio_path = f.name

    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(audio_path)

    data, samplerate = sf.read(audio_path, dtype="float32")
    sd.play(data, samplerate)
    sd.wait()

    os.remove(audio_path)