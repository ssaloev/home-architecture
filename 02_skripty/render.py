"""SVG -> PNG и PDF через headless Chrome/Edge (на Windows нет rsvg-convert). Сборка альбома — PyMuPDF."""
import os, subprocess, shutil, tempfile, pathlib
CANDIDATES = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
              r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", "google-chrome", "chromium", "msedge"]
def browser():
    for c in CANDIDATES:
        if os.path.exists(c) or shutil.which(c): return c
    raise SystemExit("Не найден Chrome/Edge для рендера SVG")
BR = None
def _run(args):
    subprocess.run([BR, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-pdf-header-footer", "--run-all-compositor-stages-before-draw"] + args,
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
def png(svg, out, w=3840, h=2160):
    global BR; BR = BR or browser()
    _run([f"--window-size={w},{h}", "--force-device-scale-factor=1", f"--screenshot={out}", pathlib.Path(svg).resolve().as_uri()])
def pdf(svg, out, w=3840, h=2160):
    """Векторный PDF одного листа: SVG во весь лист A3 альбомный."""
    global BR; BR = BR or browser()
    html = pathlib.Path(tempfile.mkdtemp()) / "p.html"
    body = pathlib.Path(svg).read_text(encoding="utf-8")          # SVG инлайном — PDF остаётся векторным
    html.write_text('<!doctype html><meta charset="utf-8"><style>@page{size:420mm 236.25mm;margin:0}html,body{margin:0}svg{width:420mm;height:236.25mm;display:block}</style>' + body, encoding="utf-8")
    _run([f"--print-to-pdf={out}", html.as_uri()])
