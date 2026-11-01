"""Baixa fotos de campo do Wikimedia Commons (licença livre) como candidatas a referência.

Uso: python fetch_commons.py <dir_saida> <attr_saida.json> especie=Categoria1|Categoria2 [especie=...]
Ex.: astronium_urundeuva=Myracrodruon_urundeuva

- só arquivos de imagem das categorias da espécie (sem subcategorias);
- licença CC0, domínio público, CC BY ou CC BY-SA (nada NC/ND);
- ficam de fora exsicatas de herbário e ilustrações (títulos com MPEG, INMA, MBML, BHL, herbário, PDF, TIF);
- tamanho de 500 px no lado maior (como as fotos "medium" do iNaturalist).
A chave de cada foto é "<-pageid>_<pageid>" para não colidir com IDs de observação do iNaturalist.
"""
import json, os, re, sys, time, requests

API = "https://commons.wikimedia.org/w/api.php"
H = {"User-Agent": "saberia-avaliacao/1.0 (avaliacao academica)"}
SKIP = re.compile(r"MPEG|INMA|MBML|BHL|herb[aá]rio|herbarium|exsicata|\.pdf|\.tif|\.svg|Archivos do Museu|Jard[ií]n bot[aá]nico de Buenos", re.I)


def ok_license(short):
    s = (short or "").lower().replace("-", " ")
    if "nc" in s.split() or "nd" in s.split(): return False
    return s.startswith("cc0") or "public domain" in s or s.startswith("cc by") or s == "pd"


def main():
    out, attr_path = sys.argv[1:3]
    attr = json.load(open(attr_path)) if os.path.exists(attr_path) else {}
    for arg in sys.argv[3:]:
        sp, cats = arg.split("=")
        d = os.path.join(out, sp); os.makedirs(d, exist_ok=True)
        n, skipped = 0, {"titulo": 0, "licenca": 0}
        for cat in cats.split("|"):
            r = requests.get(API, params={"action": "query", "generator": "categorymembers", "gcmtitle": "Category:" + cat,
                                          "gcmtype": "file", "gcmlimit": 200, "prop": "imageinfo", "iiprop": "url|extmetadata",
                                          "iiurlwidth": 500, "format": "json"}, headers=H, timeout=60).json()
            for pid, p in r.get("query", {}).get("pages", {}).items():
                if SKIP.search(p["title"]): skipped["titulo"] += 1; continue
                ii = p["imageinfo"][0]; md = ii.get("extmetadata", {})
                lic = md.get("LicenseShortName", {}).get("value")
                if not ok_license(lic): skipped["licenca"] += 1; continue
                key = f"-{pid}_{pid}"
                fn = os.path.join(d, key + ".jpg")
                if not os.path.exists(fn):
                    b = requests.get(ii["thumburl"], headers=H, timeout=60).content
                    if len(b) < 2000: continue
                    open(fn, "wb").write(b); time.sleep(0.5)
                artist = re.sub("<[^>]+>", "", md.get("Artist", {}).get("value", "")).strip()
                attr[key] = {"id": sp, "obs": -int(pid), "photo": int(pid), "taxon": cat.replace("_", " "),
                             "license": {"cc0": "cc0"}.get(lic.lower().split()[0], lic.lower().replace(" ", "-")),
                             "license_original": lic, "attribution": f"{artist}, {lic}, via Wikimedia Commons",
                             "url": ii["descriptionurl"]}
                n += 1
        print(sp, "fotos", n, "descartadas", skipped, flush=True)
    json.dump(attr, open(attr_path, "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
