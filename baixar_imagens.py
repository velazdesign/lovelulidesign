#!/usr/bin/env python3
from pathlib import Path
from urllib.request import Request, urlopen
import re, shutil, sys

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"
ASSET_DIR = ROOT / "assets" / "images"
DOMAIN = "https://lovelulidesign.pages.dev"

text = HTML.read_text(encoding="utf-8")
urls = sorted(set(re.findall(r'https://assets\.kleap\.io/[^"\')\s>]+', text)))
if not urls:
    print("Nenhuma imagem externa do Kleap encontrada. O HTML já está local.")
    raise SystemExit(0)

ASSET_DIR.mkdir(parents=True, exist_ok=True)
failed = []
for i, url in enumerate(urls, 1):
    name = url.rsplit('/', 1)[-1]
    dest = ASSET_DIR / name
    print(f"[{i}/{len(urls)}] Baixando {name}...")
    try:
        req = Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urlopen(req, timeout=45) as r, dest.open('wb') as f:
            shutil.copyfileobj(r, f)
    except Exception as exc:
        failed.append((url, str(exc)))
        print(f"  ERRO: {exc}")
        continue
    # Normal <img> references use local path.
    text = text.replace(url, f"/assets/images/{name}")

# Open Graph/Twitter images should use absolute public URLs.
text = re.sub(r'(<meta property="og:image" content=")/assets/images/([^\"]+)(")', rf'\1{DOMAIN}/assets/images/\2\3', text)
text = re.sub(r'(<meta name="twitter:image" content=")/assets/images/([^\"]+)(")', rf'\1{DOMAIN}/assets/images/\2\3', text)

if failed:
    print("\nAlgumas imagens falharam; o index.html não será sobrescrito para evitar um site incompleto.")
    for u,e in failed:
        print("-", u, "=>", e)
    raise SystemExit(1)

HTML.write_text(text, encoding="utf-8")
print(f"\nConcluído: {len(urls)} imagens baixadas e index.html atualizado.")
