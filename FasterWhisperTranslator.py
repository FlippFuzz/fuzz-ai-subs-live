from faster_whisper import download_model, WhisperModel

from Settings import Settings
from Translator import Translator


class FasterWhisperTranslator(Translator):
    """
    Translate using Faster Whisper
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        print("Setting Up Faster Whisper")
        model_dir = download_model(self.settings.model_size)
        self.model = WhisperModel(model_dir, compute_type=self.settings.compute_type)

    def translate(self, audio_file: str, prefix=None) -> list[str]:
        translation = []

        task = "translate"
        if not self.settings.translate:
            task = "transcribe"

        segments, _ = self.model.transcribe(audio_file, language="ja", task=task, prefix=prefix,
                                            beam_size=self.settings.beam_size, temperature=self.settings.temperature,
                                            vad_filter=True, vad_parameters=dict(min_silence_duration_ms=2000))

        for segment in segments:
            text = segment.text.strip()
            print(text)
            translation.append(text)

        return translation
