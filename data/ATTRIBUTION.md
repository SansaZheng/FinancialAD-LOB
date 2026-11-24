# Data and source attribution

WSELOB source: Marszałek, Adam (2023), **WSELOB-2017: The year-long database of
limit order books for the five biggest companies listed on the Warsaw Stock
Exchange**, Mendeley Data, V1, DOI [10.17632/3g4mhdp899.1](https://doi.org/10.17632/3g4mhdp899.1).
License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The original `orderbook2.py`, `order_data.ipynb`, and `trade_data.ipynb` under
`results/data-discovery-20261124/` are unchanged publisher support files, with
hash verification recorded in `support-file-hashes.json`. They were read as
documentation, not executed. The WSE CSV files are converted bounded prefixes
from the public HDF5 sources. Snapshot JSON files and audit statistics are our
derivatives from an independent replay implementation. These changes do not
imply endorsement by the depositor or exchange. Original source and license
notices must remain with redistributed samples or derivatives.

Quant-Arena metadata and archived release documents originate from
[Ashitemaru/Quant-Arena-Public-L1](https://huggingface.co/datasets/Ashitemaru/Quant-Arena-Public-L1),
revision `fa85d7b95e56e81317ac349f52e916ca482f0f68`, under the publisher's
CC BY-NC 4.0 notice. The released LICENSE is preserved. Only release metadata and
documents, not Parquet data rows, are included. Source redistribution provenance
remains pending; see `docs/public-data.md`.

WSE file locators were initially found through the public
[microstructure-lab source manifest](https://github.com/DeepCogNeural/microstructure-lab/blob/main/configs/wselob_sources_v1.json)
and then independently matched to Mendeley's primary API. No results from that
project are used as results of FinancialAD-LOB.
