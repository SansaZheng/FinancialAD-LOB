# Unmodified predecessor reference code

Source: Deep Unsupervised Anomaly Detection in High-Frequency Markets - JFDS; Zenodo record 11048480; DOI 10.5281/zenodo.11048480.
Publication date: 2024-04-19.
Creators: Cédric Poutré.

Primary source: https://zenodo.org/records/11048480
License: CC BY 4.0, https://creativecommons.org/licenses/by/4.0/ .

Only the five code/readme/dependency files listed in
`results/engineering/jfds-source-discovery-009.json` were extracted using bounded
HTTP ranges. Files are unchanged, ZIP CRC checked, and locally SHA256 hashed.
The full 192 MB archive was not downloaded, and its published whole-archive
MD5 has not been independently verified. No raw LOBSTER data or pretrained
weights from that archive were extracted. No upstream script was executed.

This is the earlier JFDS project, not the full Lin–Yang 2025 cascaded framework.
The generic controls in lobbench are separately implemented. Static inspection
found unconditional `.cuda()` calls in upstream training paths; do not execute
them on CPU without a separately documented adapter and compatibility tests.
No novelty, original-paper reproduction or numerical parity claim follows from
archiving this reference.
