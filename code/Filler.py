import re
from datetime import date

class Filler:
    _MONTHS = {"stycznia":1, "lutego":2, "marca":3, "kwietnia":4,"maja":5, "czerwca":6,"lipca":7,
               "sierpnia":8,"września":9, "wrzesnia":9, "października":10, "pazdziernika":10,
               "listopada":11, "grudnia":12
    }
    _DOCTYPES = ["odpowiedź na pozew", "skarga kasacyjna", "nakaz zapłaty","pismo procesowe", "postanowienie",
                 "zażalenie", "apelacja","wniosek", "wezwanie", "skarga", "wyrok", "pozew"
    ]
    _SIDE1_KEY = ["powód", "powodo", "strona powodowa", "skarż", "wnioskodaw","poszkodowan", "wierzyciel",
                  "oskarżyciel", "apelując", "apelu","inicjator postępowania", "składając"
    ]
    _SIDE2_KEY = ["pozwan", "strona przeciwna", "strona pozwana", "uczestnik","obwinion", "oskarżon",
                  "dłużnik", "obowiązan", "przeciwnik procesowy","interwenient","przeciwko"
    ]
    _SYG_AKT = re.compile(r"\b([IVXLCM]{1,6}\s?[A-Z][a-zA-Z]{0,3}\s?\d{1,5}/\d{2,4})\b")
    _SYG_KEYWORD = re.compile(r"sygn\w*", re.IGNORECASE)
    _DATE_ISO = re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b")
    _DATE_DOTS = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{4})\b")
    _DATE_DASH = re.compile(r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b")
    _DATE_SLASH = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
    _DATE_KEYWORD = re.compile(r"\bdni[au]\b", re.IGNORECASE)
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
    _COURT_QUALIFIER = re.compile(_COURT_TYPES)
    _CONT_WORD = r"(?:[A-ZŁŚŻŹĆŃÓĄĘ][\w\.\-ĄĆĘŁŃÓŚŹŻąćęłńóśźż]*|(?i:z|o\.o\.|s\.a\.))"
    _ABBR_ENDINGS = {"sp.", "s.a.", "o.o.", "sp.j.", "sp.k."}

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

    def get_data(self, text):
        if not text or not text.strip():
            return {}

        regex_side1, regex_side2 = self._find_sides(text)
        court = None
        side1, side2 = regex_side1, regex_side2

        if self.nlp is not None:
            doc = self.nlp(text)
            orgs = [ent.text.strip() for ent in doc.ents if ent.label_ in ("ORG", "orgName")]
            court_orgs = [o for o in orgs if "sąd" in o.lower() or "sad" in o.lower()]
            qualified_orgs = [o for o in court_orgs if self._COURT_QUALIFIER.search(o)]
            spacy_court = qualified_orgs[0] if qualified_orgs else (court_orgs[0] if court_orgs else None)
            regex_court = self._find_court(text)
            court = self._choose(doc, regex_court, spacy_court)
            side1 = self._choose(doc, regex_side1, self._near_keyword(doc, self._SIDE1_KEY))
            used = {side1} if side1 else set()
            side2 = self._choose(doc, regex_side2, self._near_keyword(doc, self._SIDE2_KEY, used))

        if court is None:
            court = self._find_court(text)

        if side1 and side2 and side1 == side2:
            side2 = None

        result = {"syg_akt": self._find_syg_akt(text),
            "date": self._find_date(text),
            "doctype": self._find_type(text),
            "court": court,
            "side1": side1,
            "side2": side2,
        }
        return {k: v for k, v in result.items() if v}

    @staticmethod
    def _choose(doc, regex_result, spacy_result):
        if regex_result:
            if Filler._check_name(doc, regex_result):
                return regex_result
            return spacy_result
        return spacy_result

    @staticmethod
    def _check_name(doc, candidate):
        cand_low = candidate.lower()
        for ent in doc.ents:
            if ent.label_ not in ("PERSON", "persName", "ORG", "orgName"):
                continue
            ent_low = ent.text.strip().lower()
            if ent_low and (ent_low in cand_low or cand_low in ent_low):
                return True
        return False

    def _near_keyword(self, doc, keywords, used=frozenset()):
        low = doc.text.lower()
        positions = []
        for kw in keywords:
            kw_low = kw.lower()
            start = 0
            while True:
                idx = low.find(kw_low, start)
                if idx == -1:
                    break
                positions.append(idx)
                start = idx + 1
        if not positions:
            return None

        best, best_dist = None, None
        for ent in doc.ents:
            if ent.label_ not in ("PERSON", "persName", "ORG", "orgName"):
                continue
            name = ent.text.strip()
            if not name or name in used:
                continue
            dist = min(abs(ent.start_char - p) for p in positions)
            if dist > 150:
                continue
            if best_dist is None or dist < best_dist:
                best, best_dist = name, dist
        return best

    def _find_syg_akt(self, text):
        matches = list(self._SYG_AKT.finditer(text))
        if not matches:
            return None

        for m in matches:
            window = text[max(0, m.start() - 40):m.start()]
            if self._SYG_KEYWORD.search(window):
                return m.group(1)
        return matches[0].group(1)

    def _find_date(self, text):
        cands = []

        for m in self._DATE_ISO.finditer(text):
            y, mo, d = (int(g) for g in m.groups())
            self._check_date(cands, m.start(), y, mo, d)

        for regex in (self._DATE_DOTS, self._DATE_DASH, self._DATE_SLASH):
            for m in regex.finditer(text):
                d, mo, y = (int(g) for g in m.groups())
                self._check_date(cands, m.start(), y, mo, d)

        mon_pat = "|".join(self._MONTHS.keys())
        for m in re.finditer(rf"\b(\d{{1,2}})\s+({mon_pat})\s+(\d{{4}})\b", text, re.IGNORECASE):
            d, mname, y = m.groups()
            mo = self._MONTHS[mname.lower()]
            self._check_date(cands, m.start(), int(y), mo, int(d))

        if not cands:
            return None

        def score(c):
            pos, _ = c
            window = text[max(0, pos - 15):pos]
            near_keyword = bool(self._DATE_KEYWORD.search(window))
            return (0 if near_keyword else 1, pos)

        cands.sort(key=score)
        return cands[0][1]

    @staticmethod
    def _check_date(cands, pos, year, month, day):
        try:
            date(year, month, day)
        except ValueError:
            return
        cands.append((pos, f"{year:04d}-{month:02d}-{day:02d}"))

    def _find_type(self, text):
        low = text.lower()
        best = None
        for dt in self._DOCTYPES:
            idx = low.find(dt)
            if idx != -1 and (best is None or idx < best[0]):
                best = (idx, dt)
        return best[1] if best else None

    def _find_sides(self, text):
        return (
            self._find_side(text, self._SIDE1_KEY),
            self._find_side(text, self._SIDE2_KEY),
        )

    def _find_side(self, text, keys):
        for key in keys:
            pat = (rf"(?i:{key}\w*)[ \t]*[:\-]?[ \t]*\n?[ \t]*"
                rf"([A-ZŁŚŻŹĆŃÓĄĘ][\w\.\-ĄĆĘŁŃÓŚŹŻąćęłńóśźż]*"
                rf"(?:[ \t]+{self._CONT_WORD}){{0,4}})"
            )
            m = re.search(pat, text)
            if m:
                name = m.group(1).strip()
                if name.endswith("."):
                    last_tok = name.rsplit(None, 1)[-1].lower()
                    is_abbr = (last_tok in self._ABBR_ENDINGS or
                               re.fullmatch(r"[a-ząćęłńóśźż]\.", last_tok))
                    if not is_abbr:
                        name = name[:-1]
                return name
        return None

    def _find_court(self, text):
        matches = list(self._COURT_RE.finditer(text))
        if not matches:
            return None
        qualified = [m for m in matches if self._COURT_QUALIFIER.search(m.group(0))]
        best = qualified[0] if qualified else matches[0]
        return best.group(0).strip()