# fuzz-ai-subs-live

This is not production ready.
Just quickly done up in a single morning.
Expect tons of bugs.

This code does the following:
1. Uses ffmpeg to download 30s chunks of audio from youtube livestream
2. Use faster-whisper to translate the chunk
3. Output to translation to discord (It only sends to channels named ai-sub)

### Limitations
Translations is expected to be behind by at least 30s.
We need to buffer for 30s, then spend time translating the chunk.

### How to install
```commandline
git clone https://github.com/FlippFuzz/fuzz-ai-subs-live.git
cd fuzz-ai-subs-live
python3 -m venv venv
. venv/bin/activate
pip3 install -r requirements.txt
# Popluate credentials.py
python3 main.py
```

Note: On Windows, you MIGHT (unsure) need to install gpp/cpp to build the binary for pywhispercpp.
1. Download and extract mingw64 from https://github.com/niXman/mingw-builds-binaries/releases
I used `x86_64-13.1.0-release-win32-seh-msvcrt-rt_v11-rev1.7z`
2. Add gcc/gpp in mingw64 to PATH
 Example: `C:\mingw64\bin`