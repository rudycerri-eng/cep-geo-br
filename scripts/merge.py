"""Junta os CSVs por UF e grava um JSON por prefixo de 3 dígitos do CEP.

Uso: python merge.py pasta_csvs/ dist/

dist/cep/013.json = {"01310100": [lat, lon, raio_km, domicilios, setor], ...,
                     "_01310": [lat, lon]}   <- centro do prefixo de 5 dígitos, para CEP que não está no IBGE
dist/resumo.json  = contagens por UF, para conferência
"""
import glob
import json
import os
import sys

import pandas as pd


def main(pasta, dist):
    partes = []
    for f in sorted(glob.glob(os.path.join(pasta, "**", "*.csv"), recursive=True)):
        d = pd.read_csv(f, dtype={"CEP": str, "setor": str})
        d["uf"] = os.path.basename(f)[3:5]
        partes.append(d)
    t = pd.concat(partes)
    # o mesmo CEP em duas UFs é raro (divisa); fica o que tem mais endereços
    t = t.sort_values("n", ascending=False).drop_duplicates("CEP")
    t["p3"] = t["CEP"].str[:3]
    t["p5"] = t["CEP"].str[:5]
    # centro do prefixo de 5 dígitos ponderado por endereços, só com CEPs de espalhamento normal
    ok = t[t["raio_km"] <= 2]
    p5 = ok.assign(wl=ok.lat * ok.n, wo=ok.lon * ok.n).groupby("p5").agg(wl=("wl", "sum"), wo=("wo", "sum"), n=("n", "sum"))
    p5["lat"] = (p5.wl / p5.n).round(6)
    p5["lon"] = (p5.wo / p5.n).round(6)

    os.makedirs(os.path.join(dist, "cep"), exist_ok=True)
    for p3, g in t.groupby("p3"):
        out = {r.CEP: [r.lat, r.lon, r.raio_km, int(r.dom), r.setor if isinstance(r.setor, str) else ""]
               for r in g.itertuples()}
        for k, r in p5[p5.index.str[:3] == p3].iterrows():
            out["_" + k] = [r.lat, r.lon]
        with open(os.path.join(dist, "cep", p3 + ".json"), "w") as fh:
            json.dump(out, fh, separators=(",", ":"))
    resumo = {"ceps": int(len(t)), "por_uf": t.groupby("uf").size().to_dict(),
              "genericos_raio_maior_2km": int((t.raio_km > 2).sum()),
              "fonte": "IBGE CNEFE Censo 2022 (Arquivos_CNEFE/CSV/UF)"}
    with open(os.path.join(dist, "resumo.json"), "w") as fh:
        json.dump(resumo, fh, indent=1)
    print(resumo)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
