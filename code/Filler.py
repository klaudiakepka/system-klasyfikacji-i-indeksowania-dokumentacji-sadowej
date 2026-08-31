import re
from datetime import date

class Filler:
    _MONTHS = {
        "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4,
        "maja": 5, "czerwca": 6, "lipca": 7, "sierpnia": 8,
        "września": 9, "wrzesnia": 9, "października": 10, "pazdziernika": 10,
        "listopada": 11, "grudnia": 12,
    }
    _DOCTYPES = [
        "odpowiedź na pozew", "skarga kasacyjna", "nakaz zapłaty",
        "pismo procesowe", "postanowienie", "zażalenie", "apelacja",
        "wniosek", "wezwanie", "skarga", "wyrok", "pozew",
    ]
    _SIDE1_KEY = [
        "powód", "powodo", "strona powodowa", "skarż", "wnioskodaw",
        "poszkodowan", "wierzyciel", "oskarżyciel", "apelując", "apelu",
        "inicjator postępowania", "składając",
    ]
    _SIDE2_KEY = [
        "pozwan", "strona przeciwna", "strona pozwana", "uczestnik",
        "obwinion", "oskarżon", "dłużnik", "obowiązan", "przeciwnik procesowy",
        "interwenient",
    ]
    _SYG_AKT = re.compile(r"\b([IVXLCM]{1,6}\s?[A-Za][a-zA-Z]{0,3}\s?\d{1,5}/\d{2,4})\b")
    _DATE_ISO = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
    _DATE_DOTS = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")
    _DATE_DASH = re.compile(r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b")
    _DATE_SLASH = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
    _COURT_MOD = r"(?:Wojewódzk\w*|Naczeln\w*)"
    _COURT_TYPES = (r"Rejonow\w*|Okręgow\w*|Apelacyjn\w*|Najwyższ\w*|Administracyjn\w*|"
        r"Gospodarcz\w*|Garnizonow\w*|Wojskow\w*|"
        r"Prac\w*(?:\s+i\s+Ubezpiecze\w*\s+Społeczny\w*)?|"
        r"Rodzinn\w*(?:\s+i\s+Nieletni\w*)?")
    _LOCATION = r"[A-ZŁŚŻŹĆŃÓĄĘ][\wąćęłńóśźż\-]*(?:\s+[A-ZŁŚŻŹĆŃÓĄĘ][\wąćęłńóśźż\-]*){0,2}"
    _COURT_RE = re.compile(rf"(?:{_COURT_MOD}\s+)?"
        rf"Sąd\w*(?:\s+(?:{_COURT_TYPES}))?"
        rf"(?:\s+(?:dla|w)\s+{_LOCATION})?"
        rf"(?:\s+w\s+{_LOCATION})?")

    def __init__(self, use_spacy=True):
        self.nlp = None
        if use_spacy:
            try:
                import spacy
                try:
                    self.nlp = spacy.load("pl_core_news_sm")
                except OSError:
                    self.nlp = None
            except ImportError:
                self.nlp = None

    def extract(self, text):
        if not text or not text.strip():
            return {}

        side1, side2 = self._find_sides(text)
        court = None

        if self.nlp is not None:
            doc = self.nlp(text)
            orgs = [ent.text.strip() for ent in doc.ents if ent.label_ == "ORG"]
            persons = [ent.text.strip() for ent in doc.ents if ent.label_ in ("PERSON", "persName")]

            for org in orgs:
                if "sąd" in org.lower() or "sad" in org.lower():
                    court = org
                    break
            if side1 is None and persons:
                side1 = persons[0]
            if side2 is None:
                for p in persons:
                    if p != side1:
                        side2 = p
                        break
        if court is None:
            court = self._find_court(text)

        result = {
            "syg_akt": self._find_syg_akt(text),
            "date": self._find_date(text),
            "doctype": self._find_type(text),
            "court": court,
            "side1": side1,
            "side2": side2,
        }
        return {k: v for k, v in result.items() if v}

    def _find_syg_akt(self, text):
        m = self._SYG_AKT.search(text)
        return m.group(1) if m else None

    def _find_date(self, text):
        candidates = []

        for m in self._DATE_ISO.finditer(text):
            y, mo, d = (int(g) for g in m.groups())
            self._valid(candidates, m.start(), y, mo, d)

        for regex in (self._DATE_DOTS, self._DATE_DASH, self._DATE_SLASH):
            for m in regex.finditer(text):
                d, mo, y = (int(g) for g in m.groups())
                self._valid(candidates, m.start(), y, mo, d)

        months_pattern = "|".join(self._MONTHS.keys())
        for m in re.finditer(rf"\b(\d{{1,2}})\s+({months_pattern})\s+(\d{{4}})\b", text, re.IGNORECASE):
            d, month_name, y = m.groups()
            mo = self._MONTHS[month_name.lower()]
            self._valid(candidates, m.start(), int(y), mo, int(d))

        if not candidates:
            return None
        candidates.sort(key=lambda c: c[0])
        return candidates[0][1]

    @staticmethod
    def _valid(candidates, position, year, month, day):
        try:
            date(year, month, day)
        except ValueError:
            return
        candidates.append((position, f"{year:04d}-{month:02d}-{day:02d}"))

    def _find_type(self, text):
        low = text.lower()
        for dt in self._DOCTYPES:
            if dt in low:
                return dt
        return None

    def _find_sides(self, text):
        return (
            self._find_keywords(text, self._SIDE1_KEY),
            self._find_keywords(text, self._SIDE2_KEY),
        )

    def _find_keywords(self, text, keywords):
        for key in keywords:
            pattern = (
                rf"{key}\w*\s*[:\-]?\s*"
                r"([A-ZŁŚŻŹĆŃÓĄĘ][\w\.\-ĄĆĘŁŃÓŚŹŻąćęłńóśźż]*"
                r"(?:\s+[A-ZŁŚŻŹĆŃÓĄĘ][\w\.\-ĄĆĘŁŃÓŚŹŻąćęłńóśźż]*){0,3})"
            )
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _find_court(self, text):
        m = self._COURT_RE.search(text)
        return m.group(0).strip() if m else None