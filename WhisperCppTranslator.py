from pywhispercpp.model import Model
from Translator import Translator


class WhisperCppTranslator(Translator):
    """
    Translate using Whisper Cpp
    Documentation for the WhisperCpp Binding library can be found at:
    https://abdeladim-s.github.io/pywhispercpp/#pywhispercpp.constants.AVAILABLE_MODELS
    """
    MODEL_SIZE = "large"
    COMPUTE_TYPE = "int8"
    BEAM_SIZE = 1
    TEMPERATURE = 0

    def __init__(self):
        print("Setting Up WhisperCpp")
        self.model = Model(self.MODEL_SIZE)

    def translate(self, audio_file: str) -> str:
        translation = ""

        segments = self.model.transcribe(audio_file)

        for segment in segments:
            translation += segment.text + "\n"
            print(segment.text)

        return translation
