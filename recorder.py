import sounddevice as sd
import soundfile as sf

SAMPLE_RATE = 24000

def record_audio(duration=10, filename="live_record.wav"):

    print("Recording...")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1
    )

    sd.wait()

    sf.write(filename, audio, SAMPLE_RATE)

    print("Recording saved:", filename)

    return filename