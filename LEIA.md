# cep-geo-br

Coordenada de cada CEP do Brasil, calculada a partir do CNEFE do Censo 2022 (IBGE, dado público).

- Branch `dados`, pasta `cep/`: um JSON por prefixo de 3 dígitos do CEP.
  `{"01310100": [lat, lon, raio_km, domicilios, setor_censitario], "_01310": [lat, lon]}`
- `lat`/`lon`: média dos endereços do CEP. `raio_km`: espalhamento desses endereços; acima de 2 km o CEP é genérico (cidade pequena ou região inteira) e o ponto é só aproximado.
- `_xxxxx`: centro do prefixo de 5 dígitos, para CEP que não aparece no IBGE.
- Gerado pelo workflow `build` (rodar à mão). Fonte: `ftp.ibge.gov.br/Cadastro_Nacional_de_Enderecos_para_Fins_Estatisticos/Censo_Demografico_2022/Arquivos_CNEFE/CSV/UF/`.

Usado pelo mapa de clientes do Grupo Carrera. Não contém nenhum dado de cliente.
