"""Minimal xlsx reader -- a zip of XML, so no third-party dependency is needed.

Used by tocfl_compare.py to read the official TOCFL workbook.
"""
import re, zipfile
from xml.etree import ElementTree as ET

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _col(ref):
    m = re.match(r"([A-Z]+)", ref or "A")
    n = 0
    for ch in m.group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


class Book:
    def __init__(self, path):
        self.z = zipfile.ZipFile(path)
        self.shared = []
        if "xl/sharedStrings.xml" in self.z.namelist():
            root = ET.fromstring(self.z.read("xl/sharedStrings.xml"))
            for si in root:
                self.shared.append("".join(t.text or "" for t in si.iter(NS + "t")))
        rels = ET.fromstring(self.z.read("xl/_rels/workbook.xml.rels"))
        target = {r.get("Id"): r.get("Target") for r in rels}
        wb = ET.fromstring(self.z.read("xl/workbook.xml"))
        self.sheets = {}
        for sh in wb.iter(NS + "sheet"):
            t = target[sh.get(RID)].lstrip("/")
            self.sheets[sh.get("name")] = t if t.startswith("xl/") else "xl/" + t

    def rows(self, name):
        root = ET.fromstring(self.z.read(self.sheets[name]))
        for row in root.iter(NS + "row"):
            cells = {}
            for c in row.iter(NS + "c"):
                v = c.find(NS + "v")
                if c.get("t") == "inlineStr":
                    isx = c.find(NS + "is")
                    val = "".join(t.text or "" for t in isx.iter(NS + "t")) if isx is not None else ""
                elif v is None:
                    continue
                elif c.get("t") == "s":
                    val = self.shared[int(v.text)]
                else:
                    val = v.text
                cells[_col(c.get("r"))] = (val or "").strip()
            if cells:
                yield [cells.get(i, "") for i in range(max(cells) + 1)]
