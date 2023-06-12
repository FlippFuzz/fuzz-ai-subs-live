import json

import git


class Settings:
    video_m3u8: str = ""
    channel: str = ""
    title: str = ""

    must_restart = False
    must_exit = False
    version = "Unknown"

    buffer_time_seconds: int = 15

    model_size: str = "medium"  # Valid model sizes are: tiny, base, medium, large-v1, large-v2
    compute_type: str = "int8"
    vad_enabled: bool = True
    translate: bool = True
    beam_size: int = 1
    temperature: float = 0

    def __init__(self):
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        self.version = repo.git.rev_parse(sha, short=7)

    def restore_defaults(self):
        # Is there a nicer way to do this without creating another tmp instance?
        tmp_settings = Settings()

        self.buffer_time_seconds = tmp_settings.buffer_time_seconds

        self.model_size = tmp_settings.model_size
        self.compute_type = tmp_settings.compute_type
        self.vad_enabled = tmp_settings.vad_enabled
        self.beam_size = tmp_settings.beam_size
        self.temperature = tmp_settings.temperature

    def __str__(self) -> str:
        return json.dumps({"version": self.version,
                           "buffer_time_seconds": self.buffer_time_seconds,
                           "model_size": self.model_size,
                           "compute_type": self.compute_type,
                           "vad_enabled": self.vad_enabled,
                           "translate": self.translate,
                           "beam_size": self.beam_size,
                           "temperature": self.temperature
                           }, indent=2)
