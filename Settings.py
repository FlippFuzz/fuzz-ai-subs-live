import json


class Settings:
    video_m3u8: str = ""
    channel: str = ""
    title: str = ""

    must_restart = False

    segment_time_seconds: int = 10

    model_size: str = "base"  # Valid model sizes are: tiny, base, medium, large-v1, large-v2
    compute_type: str = "int8"
    vad_enabled: bool = True
    beam_size: int = 1
    temperature: float = 0

    def restore_defaults(self):
        # Is there a nicer way to do this without creating another tmp instance?
        tmp_settings = Settings()

        self.segment_time_seconds = tmp_settings.segment_time_seconds

        self.model_size = tmp_settings.model_size
        self.compute_type = tmp_settings.compute_type
        self.vad_enabled = tmp_settings.vad_enabled
        self.beam_size = tmp_settings.beam_size
        self.temperature = tmp_settings.temperature

    def __str__(self) -> str:
        return json.dumps({"segment_time_seconds": self.segment_time_seconds,
                           "model_size": self.model_size,
                           "compute_type": self.compute_type,
                           "vad_enabled": self.vad_enabled,
                           "beam_size": self.beam_size,
                           "temperature": self.temperature
                           }, indent=2)
