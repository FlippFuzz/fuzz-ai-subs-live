import json

import git


class Settings:
    video_m3u8: str = ""
    channel: str = ""
    title: str = ""

    must_restart = False
    must_exit = False
    version = "Unknown"

    buffer_time_seconds: int

    model_size: str
    compute_type: str
    vad_enabled: bool
    prompt_enabled: True
    translate: bool
    beam_size: int
    temperature: float

    def __init__(self):
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        self.version = repo.git.rev_parse(sha, short=7)
        self.restore_defaults()

    def restore_defaults(self):
        self.buffer_time_seconds = 15

        self.model_size = "medium"  # Valid model sizes are: tiny, base, medium, large-v1, large-v2
        self.compute_type = "int8"
        self.vad_enabled = True
        self.prompt_enabled = True
        self.translate = True
        self.beam_size = 1
        self.temperature = 0.0

    def __str__(self) -> str:
        return json.dumps({"version": self.version,
                           "buffer_time_seconds": self.buffer_time_seconds,
                           "model_size": self.model_size,
                           "compute_type": self.compute_type,
                           "vad_enabled": self.vad_enabled,
                           "prompt_enabled": self.prompt_enabled,
                           "translate": self.translate,
                           "beam_size": self.beam_size,
                           "temperature": self.temperature
                           }, indent=2)
