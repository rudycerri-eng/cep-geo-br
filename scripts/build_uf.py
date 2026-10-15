"""Centro de cada CEP a partir do CNEFE 2022 (IBGE), para uma UF.

Uso: python build_uf.py 35_SP.zip saida/35_SP.csv

Lê o CSV de dentro do zip em pedaços (SP descompactado passa de 10 GB) e grava,
por CEP: latitude e longitude médias dos endereços, total de endereços, total de
domicílios particulares, o espalhamento (raio_km) e o setor censitário mais comum (liga com a renda do Censo).
"""
import sys
import zipfile

import pandas as pd

COLS = ["CEP", "LATITUDE", "LONGITUDE", "COD_ESPECIE", "COD_SETOR", "NV_GEO_COORD"]


def main(zip_path, out_path):
    soma = []
    setores = []
    with zipfile.ZipFile(zip_path) as z:
        nome = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        with z.open(nome) as f:
            for parte in pd.read_csv(f, sep=";", usecols=COLS, dtype={"CEP": str, "COD_SETOR": str},
                                     chunksize=2_000_000, encoding="latin-1"):
                parte = parte.dropna(subset=["CEP", "LATITUDE", "LONGITUDE"])
                parte["CEP"] = parte["CEP"].str.zfill(8)
                # NV_GEO_COORD 1 a 3 = endereço, face ou quadra; 4+ = setor/localidade (mais grosseiro)
                parte["fino"] = parte["NV_GEO_COORD"] <= 3
                parte["dom"] = parte["COD_ESPECIE"] == 1
                parte["lat2"] = parte["LATITUDE"] ** 2
                parte["lon2"] = parte["LONGITUDE"] ** 2
                soma.append(parte.groupby("CEP").agg(
                    lat=("LATITUDE", "sum"), lon=("LONGITUDE", "sum"), n=("LATITUDE", "size"),
                    lat2=("lat2", "sum"), lon2=("lon2", "sum"),
                    dom=("dom", "sum"), fino=("fino", "sum")))
                setores.append(parte.groupby(["CEP", "COD_SETOR"]).size().rename("q"))
    s = pd.concat(soma).groupby(level=0).sum()
    s["lat"] = s["lat"] / s["n"]
    s["lon"] = s["lon"] / s["n"]
    # espalhamento: desvio padrão dos endereços em km (1 grau de latitude ~ 111 km).
    # CEP genérico de cidade pequena ou de região inteira passa de 2 km e o centro dele não diz onde o cliente mora.
    var = (s["lat2"] / s["n"] - s["lat"] ** 2).clip(lower=0) + (s["lon2"] / s["n"] - s["lon"] ** 2).clip(lower=0)
    s["raio_km"] = (var ** 0.5 * 111).round(2)
    s["lat"] = s["lat"].round(6)
    s["lon"] = s["lon"].round(6)
    st = pd.concat(setores).groupby(level=[0, 1]).sum().reset_index()
    st = st.sort_values("q", ascending=False).drop_duplicates("CEP").set_index("CEP")["COD_SETOR"]
    s["setor"] = st
    s["pct_fino"] = (s["fino"] / s["n"] * 100).round().astype(int)
    s[["lat", "lon", "raio_km", "n", "dom", "pct_fino", "setor"]].to_csv(out_path)
    print(zip_path, len(s), "CEPs")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
