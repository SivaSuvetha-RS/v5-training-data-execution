from bs4 import BeautifulSoup

class Extractor:
    def extract(self, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")

        for tag in soup(["script", "style", "header",
                         "footer", "nav", "aside"]):
            tag.decompose()

        return soup.get_text(separator=" ", strip=True)