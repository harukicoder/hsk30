#!/usr/bin/env python3
"""Produce the double-blind ARR submission from the named preprint source.

ACL venues review double-blind even where a non-anonymous preprint is allowed,
so the submission needs a build that carries no author name, no repository URL
and no DOI resolving to the author. This derives that build from main.tex
rather than maintaining a second copy, so the two cannot drift apart.

Three things happen here that [review] alone does not do:

  * The availability and ethics statements are rewritten. acl.sty removes the
    author block; it does not remove a GitHub URL containing a username, a
    Zenodo DOI, or a sentence describing a website the author operates.
  * Limitations moves after the conclusion and loses its number. ACL excludes
    a Limitations section from the page limit only when it is unnumbered and
    positioned there; as a numbered section before the conclusion it counts.
  * The authorship guard inverts. build.sh fails a preprint that is NOT named;
    this fails a submission that IS.

    python3 make_review.py && tectonic -X compile main-review.tex
"""
import io
import re
import sys

SRC, DST = "main.tex", "main-review.tex"

s = io.open(SRC, encoding="utf-8").read()

# 1. anonymous mode: author block replaced by acl.sty, line numbers on
s = s.replace("\\usepackage[final]{acl}", "\\usepackage[review]{acl}", 1)

# 2. the author block. acl.sty[review] hides it in the render, but hyperref can
#    still write it into the PDF metadata, so remove it from the source too.
s = re.sub(r"\\author\{.*?\}\n\n", lambda _m: "\\author{}\n\n", s, count=1, flags=re.S)

# 3. availability -- no repository, no DOI, no dataset handle
old_avail = s[s.index("\\section*{Availability}"):s.index("\\section*{Ethics and data statement}")]
new_avail = """\\section*{Availability}

The library, the extracted word and character lists, the aligned corpus and the
benchmark are released openly under permissive licences (code MIT, corpus
CC~BY~4.0), together with the scripts that regenerate every figure in this
paper and the manifest identifying the external sample by revision id. URLs and
archival identifiers are withheld here because they identify the author, and
will be supplied in the camera-ready version.

"""
s = s.replace(old_avail, new_avail, 1)

# 4. ethics -- the operated website identifies the author
s = s.replace("""No human subjects were involved. An intended application is a Chinese-learning
website operated by the author.""",
"""No human subjects were involved. An intended application is a Chinese-learning
website built by the authors.""")

# 5. Limitations: unnumbered, and after the conclusion, so it is excluded
m = re.search(r"\\section\{Limitations\}\n(?:\\label\{[^}]*\}\n)?(.*?)(?=\\section\{Conclusion\})", s, re.S)
if not m:
    sys.exit("could not isolate the Limitations section")
lim_body = m.group(1).rstrip()
s = s[:m.start()] + s[m.end():]
s = s.replace("\\section*{Availability}",
              "\\section*{Limitations}\n\n" + lim_body + "\n\n\\section*{Availability}", 1)

io.open(DST, "w", encoding="utf-8").write(s)

# 6. guard: nothing identifying may survive
bad = [t for t in ("Serrano", "harukicoder", "zenodo", "alvaro", "orcid")
       if t.lower() in s.lower()]
if bad:
    sys.exit("STILL IDENTIFYING: %s" % ", ".join(bad))
print("wrote %s -- anonymous, Limitations unnumbered and after the conclusion" % DST)
