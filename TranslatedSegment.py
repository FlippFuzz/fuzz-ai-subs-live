class TranslatedSegment:
    """
    A helper class holding on to attributes of a translated segment

    Using a helper class instead of any library's specific implementation because we might want to change the backend
    """
    start: float
    end: float
    text: str
