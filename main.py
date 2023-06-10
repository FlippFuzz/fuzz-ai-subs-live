import glob
import os
import subprocess
import traceback
from time import sleep
from faster_whisper import download_model, WhisperModel
from DiscordWrapper import DiscordWrapper

MODEL_SIZE = "medium"
COMPUTE_TYPE = "int8"
AUDIO_DIR = "audio"
FFMPEG_LOCATION_WINDOWS = "C:\\ffmpeg\\bin\\ffmpeg"
SEGMENT_TIME_SECONDS = 30

if __name__ == '__main__':
    # Setup discord
    print("Setting Up Discord")
    discord = DiscordWrapper()

    # Setup whisper model
    print("Setting Up Whisper")
    model_dir = download_model(MODEL_SIZE)
    model = WhisperModel(model_dir, compute_type=COMPUTE_TYPE)

    try:
        current_translation_m3u8 = ""

        while True:
            if discord.video_m3u8 == "":
                sleep(1)  # Just loop idly if there's no URL
                continue

            # Start translating
            current_translation_m3u8 = discord.video_m3u8

            # Delete all temp files
            files = glob.glob(f"{AUDIO_DIR}\\*.aac")
            for file in files:
                os.remove(file)

            ffmpeg_location = FFMPEG_LOCATION_WINDOWS
            if os.name != 'nt':
                ffmpeg_location = "ffmpeg"

            # Start downloading audio files
            ffmpeg_process = subprocess.Popen([ffmpeg_location,
                                               "-loglevel", "quiet",
                                               "-y", "-re",
                                               "-probesize", "32",
                                               "-i", current_translation_m3u8,
                                               "-f", "segment", "-segment_time", f"{SEGMENT_TIME_SECONDS}",
                                               "-c:a", "copy",
                                               f"{AUDIO_DIR}\\live%06d.aac"])

            print("Waiting for first segment")
            sleep(SEGMENT_TIME_SECONDS)

            prev_file = ""
            # This condition check handles users changing the translation URL
            while current_translation_m3u8 == discord.video_m3u8:
                # Look for 2nd latest file - The latest file is still in progress.
                files = glob.glob(f"{AUDIO_DIR}\\*.aac")
                files.sort(key=os.path.getctime)

                if len(files) < 2 or files[-2] == prev_file:
                    print(f"New {SEGMENT_TIME_SECONDS}s segment not ready yet")
                    sleep(1)
                    continue
                audio_file = files[-2]
                print(f"Working on {audio_file}")
                prev_file = audio_file

                # Delete old files
                i = 0
                while i < len(files) - 2:
                    os.remove(files[i])
                    i += 1

                # Translate current file
                segments, info = model.transcribe(audio_file, language="ja", task="translate",
                                                  beam_size=1, vad_filter=False)

                discord_message = f"{audio_file}\n"
                for segment in segments:
                    text = segment.text.strip()
                    print(text)
                    discord_message += text + "\n"

                discord.send_message(discord_message)

            ffmpeg_process.terminate()
            ffmpeg_process.wait()

    except KeyboardInterrupt as e:
        print("Caught KeyboardInterrupt")
        print(traceback.format_exc())
        discord.terminate_discord_client()
    except Exception as e:
        print("Caught Exception")
        print(traceback.format_exc())
        discord.terminate_discord_client()