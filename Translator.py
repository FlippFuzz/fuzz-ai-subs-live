import TranslatedSegment


class Translator:
    """
    Base class that is used for translation
    Simply exposes a translaed function
    """
    def translate(self, filename: str) -> list[TranslatedSegment]:
        """
        :param filename: File to be translated
        :return: List of strings containing lines of the translations
        """
        pass
