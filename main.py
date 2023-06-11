import glob
import os
import subprocess
import traceback
from time import sleep, time
from faster_whisper import download_model, WhisperModel
from DiscordWrapper import DiscordWrapper
from FasterWhisperTranslator import FasterWhisperTranslator

AUDIO_DIR = "audio"
FFMPEG_LOCATION_WINDOWS = "C:\\ffmpeg\\bin\\ffmpeg"
SEGMENT_TIME_SECONDS = 30

if __name__ == '__main__':
    # Setup discord
    print("Setting Up Discord")
    discord = DiscordWrapper()

    # Setup whisper model
    translator = FasterWhisperTranslator()

    try:
        current_translation_m3u8 = ""

        while True:
            if discord.video_m3u8 == "":
                sleep(1)  # Just loop idly if there's no URL
                continue

            # Start translating
            current_translation_m3u8 = discord.video_m3u8

            # Delete all temp files
            files = glob.glob(os.path.join(AUDIO_DIR, "*.aac"))
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
                                               os.path.join(AUDIO_DIR, "live%06d.aac")])

            print("Waiting for first segment")
            sleep(SEGMENT_TIME_SECONDS)

            prev_file = ""
            # This condition check handles users changing the translation URL
            while current_translation_m3u8 == discord.video_m3u8:
                # Look for 2nd latest file - The latest file is still in progress.
                files = glob.glob(os.path.join(AUDIO_DIR, "*.aac"))
                files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

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
                start_time = time()
                discord_message = translator.translate(audio_file)

                end_time = time()
                discord.send_message(f"{audio_file} - TL Delay: "
                                     f"{round(SEGMENT_TIME_SECONDS + end_time - start_time, 3)}\n"
                                     f"{discord_message}")

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
