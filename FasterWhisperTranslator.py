from faster_whisper import download_model, WhisperModel
from Translator import Translator


class FasterWhisperTranslator(Translator):
    """
    Translate using Faster Whisper

    Valid model sizes are: tiny, base, medium, large-v1, large-v2
    """
    MODEL_SIZE = "medium"
    COMPUTE_TYPE = "int8"
    BEAM_SIZE = 1
    TEMPERATURE = 0

    def __init__(self):
        print("Setting Up Faster Whisper")
        model_dir = download_model(self.MODEL_SIZE)
        self.model = WhisperModel(model_dir, compute_type=self.COMPUTE_TYPE)

    def translate(self, audio_file: str, prefix=None) -> list[str]:
        translation = []

        segments, _ = self.model.transcribe(audio_file, language="ja", task="translate", prefix=prefix,
                                            beam_size=self.BEAM_SIZE, temperature=self.TEMPERATURE,
                                            vad_filter=True, vad_parameters=dict(min_silence_duration_ms=2000))

        for segment in segments:
            text = segment.text.strip()
            print(text)
            translation.append(text)

        return translation
