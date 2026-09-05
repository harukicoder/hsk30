#!/usr/bin/env python3
"""Fail if the built PDF is anonymised or does not name its author.

The ACL class has two modes.  ``[review]`` prints "Anonymous ACL submission"
and line numbers, which is correct for double-blind submission and wrong for
anything deposited or circulated: a PDF that does not carry the author's name
is not evidence of authorship.  ``[final]`` prints the author block.

The failure is easy to miss because both modes compile cleanly, produce the
same page count, and differ only in a header most people skim past.  This ran
undetected into two published Zenodo versions.
"""
import sys

try:
    import pypdf
except ImportError:
    print("authorship: skipped (pypdf not installed)")
    sys.exit(0)

try:
    reader = pypdf.PdfReader("main.pdf")
except Exception as exc:
    print("authorship: cannot read main.pdf (%s)" % exc, file=sys.stderr)
    sys.exit(1)

text = "".join((page.extract_text() or "") for page in reader.pages)

if "Anonymous" in text:
    print("ANONYMISED BUILD — the PDF says 'Anonymous ACL submission'.",
          file=sys.stderr)
    print("Change \\usepackage[review]{acl} to [final] in main.tex.",
          file=sys.stderr)
    sys.exit(1)

if "Serrano" not in text:
    print("The PDF does not name its author.", file=sys.stderr)
    sys.exit(1)

print("authorship: named")
