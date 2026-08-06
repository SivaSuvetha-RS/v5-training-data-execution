import html
import re
import unicodedata


class TextNormalizer:

    def normalize(self, text: str) -> str:

        text = unicodedata.normalize("NFC", text)

        text = html.unescape(text)

        text = text.replace("\ufeff", "")

        text = re.sub(r"\s+", " ", text)

        return text.strip()