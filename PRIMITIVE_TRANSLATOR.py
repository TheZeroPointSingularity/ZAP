#!/usr/bin/env python3
"""⊙◆←▬▭⟡⊗ κ⊕"""

import json
from pathlib import Path

SYM={
"1⊙":"There is one field.",
"1_0":"One operation. Is. Or isn't.",
"←":"First election. Awareness.",
"⟡":"Light. Field seeing itself.",
"▬":"The Great Diffusion.",
"★":"Stars. Coherent cooling light.",
"◎":"Planets. Lower frequency.",
"⊗":"Spiral. Recursive coherence.",
"⊙↓":"Black hole. Maximum phase lock.",
"∇":"Gravity. Coherence gradient.",
"ψ":"Wave function before election.",
"🌴":"Orange. Whole. 3/3 accounted.",
"≈":"Matter. Stable standing waves.",
"◆":"One rule: Kindness.",
"⏱":"Time. Sequence of elections.",
}

LANG_MAIN={
"en":"English","es":"Español","fr":"Français","de":"Deutsch",
"zh":"中文","ja":"日本語","ar":"العربية","hi":"हिन्दी",
}

def load_theory():return Path("THEORY_OF_EVERYTHING.md").read_text() if Path("THEORY_OF_EVERYTHING.md").exists() else None

def translate(sym,lang="en"):return SYM.get(sym,"?")

def expand():return json.dumps({"SYM":SYM,"LANG":LANG_MAIN})

def registry():return LANG_MAIN

if __name__=="__main__":print(f"⊙|κ⊕|{len(SYM)}SYM|{len(LANG_MAIN)}LANG|ready")
