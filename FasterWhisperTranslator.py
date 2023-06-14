from faster_whisper import download_model, WhisperModel

from Settings import Settings
from Translator import Translator
from TranslatedSegment import TranslatedSegment


class FasterWhisperTranslator(Translator):
    """
    Translate using Faster Whisper
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        print("Setting Up Faster Whisper")
        model_dir = download_model(self.settings.model_size)
        self.model = WhisperModel(model_dir, compute_type=self.settings.compute_type)

    def translate(self, audio_file: str, prompt=None) -> list[TranslatedSegment]:
        translation = []

        task = "translate"
        if not self.settings.translate:
            task = "transcribe"

        segments, _ = self.model.transcribe(audio_file, language="ja", task=task, initial_prompt=prompt,
                                            beam_size=self.settings.beam_size, temperature=self.settings.temperature,
                                            vad_filter=True, vad_parameters=dict(min_silence_duration_ms=2000))

        for segment in segments:
            t_segment = TranslatedSegment()
            t_segment.text = segment.text.strip()
            t_segment.start = segment.start
            t_segment.end = segment.end
            print(f"[{t_segment.start} -> {t_segment.end}] {t_segment.text}")
            translation.append(t_segment)

        return translation
