import glob
import os
import subprocess
import traceback
from time import sleep, time
from DiscordWrapper import DiscordWrapper
from FasterWhisperTranslator import FasterWhisperTranslator
from Settings import Settings

# from WhisperCppTranslator import WhisperCppTranslator

AUDIO_DIR = "audio"
FFMPEG_LOCATION_WINDOWS = "C:\\ffmpeg\\bin\\ffmpeg"

if __name__ == '__main__':
    # Settings
    settings = Settings()

    # Setup discord
    print("Setting Up Discord")
    discord = DiscordWrapper(settings)

    # Setup whisper model
    translator = FasterWhisperTranslator(settings)
    # translator = WhisperCppTranslator()

    try:
        current_translation_m3u8 = ""

        while not settings.must_exit:
            if settings.video_m3u8 == "":
                sleep(1)  # Just loop idly if there's no URL
                continue

            # Start translating
            settings.must_restart = False
            current_translation_m3u8 = settings.video_m3u8

            # Delete all temp files
            files = glob.glob(os.path.join(AUDIO_DIR, "*.wav"))
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
                                               "-f", "segment", "-segment_time", f"{settings.buffer_time_seconds}",
                                               "-c:a", "pcm_s16le", "-ar", "16000", "-ac", "1",
                                               os.path.join(AUDIO_DIR, "%06d.wav")])

            print("Waiting for first segment")
            discord.send_message(f"Buffering. Please wait for at least {2*settings.buffer_time_seconds}s")
            sleep(settings.buffer_time_seconds)

            prev_file = ""
            # This condition check handles users changing the translation URL
            while settings.must_restart is False:
                # Look for 2nd latest file - The latest file is still in progress.
                files = glob.glob(os.path.join(AUDIO_DIR, "*.wav"))
                files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

                if len(files) < 2 or files[-2] == prev_file:
                    # print(f"New {settings.segment_time_seconds}s segment not ready yet")
                    sleep(0.1)
                    continue
                audio_file = files[-2]
                print(f"Working on {audio_file}")
                prev_file = audio_file

                # Delete old files
                i = 0
                while i < len(files) - 2:
                    try:
                        os.remove(files[i])
                    except PermissionError as e:
                        print("Caught PermissionError but continuing - Hopefully it's temporary")
                        print(traceback.format_exc())
                    i += 1

                # Translate current file
                start_time = time()
                lines = translator.translate(audio_file)

                discord_message = ""
                for line in lines:
                    discord_message += line + "\n"

                end_time = time()
                discord.send_message(f"{settings.channel} - {os.path.splitext(os.path.basename(audio_file))[0]} "
                                     f"- TL Delay: {round(settings.buffer_time_seconds + end_time - start_time, 3)}\n"
                                     f"{discord_message}")

            ffmpeg_process.terminate()
            ffmpeg_process.wait()

    except KeyboardInterrupt as e:
        print("Caught KeyboardInterrupt")
        print(traceback.format_exc())
    except Exception as e:
        print("Caught Exception")
        print(traceback.format_exc())

    discord.send_message("Bot is exiting")
    discord.terminate_discord_client()
