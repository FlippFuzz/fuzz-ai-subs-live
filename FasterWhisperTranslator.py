import contextlib
import wave
from collections import deque

from faster_whisper import download_model, WhisperModel, tokenizer

from Settings import Settings
from Translator import Translator
from TranslatedSegment import TranslatedSegment


class FasterWhisperTranslator(Translator):
    """
    Translate using Faster Whisper
    """
    prompt_deque = deque(maxlen=224)
    prev_text_deque = deque(maxlen=2)
    language = 'ja'

    def __init__(self, settings: Settings):
        self.settings = settings
        print("Setting Up Faster Whisper")
        model_dir = download_model(self.settings.model_size)
        self.model = WhisperModel(model_dir, compute_type=self.settings.compute_type)

    def translate(self, audio_file: str) -> list[TranslatedSegment]:
        translation = []

        task = "translate"
        if not self.settings.translate:
            task = "transcribe"

        # Figure out the prompt
        if not self.settings.prompt_enabled:
            self.prompt_deque.clear()
        print(f"Prompt: {self.prompt_deque}", flush=True)

        # Figure out the length of the input audio file
        with contextlib.closing(wave.open(audio_file, 'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
        print(f"Wav file duration: {duration}")

        # Translate
        segments, _ = self.model.transcribe(audio_file, language=self.language, task=task,
                                            initial_prompt=self.prompt_deque, beam_size=self.settings.beam_size,
                                            temperature=self.settings.temperature, vad_filter=self.settings.vad_enabled,
                                            vad_parameters=dict(min_silence_duration_ms=2000))

        for segment in segments:
            # Remove any leading and trailing whitespace
            text = segment.text.strip()

            hallucination = False
            # Try to handle hallucinations
            # Method 1 - Treat segments that start after the end of the input wave file as hallucinations
            if segment.start > duration:
                hallucination = True

            # Method 2 - Text repeats too many times
            if not hallucination:
                method2_hallucination_check = True
                for prev_text in self.prev_text_deque:
                    if text != prev_text:
                        method2_hallucination_check = False
                        break
                hallucination = method2_hallucination_check
            self.prev_text_deque.append(text)

            if hallucination:
                text = f"[Possible Hallucination] {text}"

            # Display text to console
            print(f"[{segment.start} -> {segment.end}] {text}")

            # Prepare output
            t_segment = TranslatedSegment()
            t_segment.text = text
            t_segment.start = segment.start
            t_segment.end = segment.end
            t_segment.temperature = segment.temperature
            t_segment.avg_logprob = segment.avg_logprob
            t_segment.compression_ratio = segment.compression_ratio
            t_segment.no_speech_prob = segment.no_speech_prob
            translation.append(t_segment)

            # Update the prompt:
            if not hallucination and self.settings.prompt_enabled:
                self.prompt_deque.extend(segment.tokens)

        return translation
