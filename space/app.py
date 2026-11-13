"""Hugging Face Space: grade Chinese text against a named HSK document.

Runs the hsk30 package (pip install hsk30). Nothing typed here is stored.
"""

import gradio as gr
import hsk30

DOCS = {
    "HSK 3.0 exam syllabus (2025), used by the exam from 13 Dec 2026": "2025",
    "HSK 3.0 national standard GF0025-2021": "2021",
}
IDS = {"2025": "hsk-syllabus-2025", "2021": "gf0025-2021"}

EXAMPLE = "我每天早上七点起床，然后去公园跑步。跑步以后，我回家吃早饭。"


def run(text, doc_label, threshold):
    std = DOCS[doc_label]
    text = text or ""
    p = hsk30.grade(text, threshold=threshold / 100, standard=std)
    other = "2021" if std == "2025" else "2025"
    q = hsk30.grade(text, threshold=threshold / 100, standard=other)
    if not p.chars:
        return "Paste some Chinese text.", [], ""
    head = f"## HSK {p.label}\n\nGraded against **{IDS[std]}**"
    if p.script == "traditional":
        head += " (traditional input converted to simplified: an upper bound)"
    head += f". {p.chars} characters, {p.ungraded} outside every level."
    if q.level != p.level:
        head += (f"\n\nThe other document called \"HSK 3.0\" ({IDS[other]}) grades this text "
                 f"**HSK {q.label}**. Say which one you used.")
    rows = [[hsk30.label(lvl), f"{100 * v:.1f}%"] for lvl, v in p.curve().items()]
    target = p.level - 1 if p.level and p.level > 1 else None
    hard = ""
    if target:
        share, ranked = hsk30.budget_violations(text, target, standard=std)
        top = ", ".join(f"{c} (HSK {hsk30.label(l)})" for c, l, _s in ranked[:8])
        hard = (f"To reach HSK {hsk30.label(target)}, {100 * share:.1f}% of the text is above it; "
                f"the bar allows {100 - threshold:.0f}%. Hardest characters: {top}")
    return head, rows, hard


with gr.Blocks(title="HSK level checker") as demo:
    gr.Markdown(
        "# HSK level checker\n"
        "Paste Chinese text to see the HSK level a reader needs: the lowest level at which they know "
        "95% of its characters. \"HSK 3.0\" names two official documents that disagree on 41.5% of "
        "shared words, so the result names the one it used. Built on "
        "[hsk30](https://github.com/harukicoder/hsk30) (`pip install hsk30`, `npm install hsk30`).")
    with gr.Row():
        with gr.Column():
            text = gr.Textbox(label="Chinese text", lines=8, value=EXAMPLE)
            doc = gr.Radio(list(DOCS), value=list(DOCS)[0], label="Document")
            thr = gr.Slider(80, 100, value=95, step=1, label="Coverage threshold (%)")
            btn = gr.Button("Grade", variant="primary")
        with gr.Column():
            out = gr.Markdown()
            curve = gr.Dataframe(headers=["Level", "Coverage"], label="Coverage at each level", interactive=False)
            hard = gr.Markdown()
    btn.click(run, [text, doc, thr], [out, curve, hard])
    demo.load(run, [text, doc, thr], [out, curve, hard])

if __name__ == "__main__":
    demo.launch()
