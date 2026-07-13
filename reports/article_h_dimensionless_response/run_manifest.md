# Article-H run manifest (protocol section 16)

- generated: 2026-07-13T05:02:05.952747+00:00
- branch: article-h-dimensionless-signed-response
- commit: 29d5da0cc5e3d75ab3ce15e8e68231de6c148943
- source branch: article-g-signed-shape-response
- exact parent SHA: 2744ef0cfecff1a7ef9f8b1fbdee80134800ad0b
- frozen protocol commit (on remote before results): 29d5da0
- NO new eigensolves were run; reanalysis of existing CSVs only.
- hashing convention: SHA256 over LF-normalized bytes (CRLF->LF), for cross-platform stability.

## Environment (running interpreter)
- python: 3.12.13
- numpy: 2.4.3
- scipy: 1.17.1

## Exact commands
- `python -m pytest tests/test_article_h_dimensionless_analysis.py -q`
- `python scripts/run_article_h_dimensionless_analysis.py`
- `python scripts/run_article_h_manifest.py`

## Inputs (read-only, canonical SHA256)
- `pilot_main_rows.csv`: rows=15104, 8ce559e0bd60e7fb1f4340e89dccc64c7978f94516598e94ede8e7cf35856380
- `pilot_conv_rows.csv`: rows=5120, c409cdc491bf2d891aa116a65e9d04a4cfe493f529d1bb942cfb6512bff389b6

## Outputs (canonical SHA256)
- `protocol.md`: d4d78020c382af7390fdf46a64c536217f727a161d7e17d6f32eac40014ea06c
- `article_h_dimensionless_rows.csv`: 94df3e1c3f01dca2811e45820507a45de434d55b533ac5ed986b007bb182b1d4, rows=20224
- `dimensionless_statistics.csv`: 4dd6f5a83cafeb1dfe0f74791883d35cb2359c965a17aee19a4c0712cb0178e1, rows=216
- `dimensionless_conditional.csv`: df1d34427905ba75f403d08d0d187911cd010737acd290610c8732df8da3b1ef, rows=30
- `dimensionless_convergence.csv`: b47e0471336ff6d792680bd76782da7efac9cf2cc63e15e640d8934c06c6d5d6, rows=5
- `dimensionless_n2_vs_n4.csv`: c29bb89c12370fb4036f7a5640220bb6f060cfa3e92917ff91d200b8a8e073ab, rows=15
- `dimensionless_scaling.csv`: af9651d6f6229ed4c6e24ffe0e196affcfd8a6e76ae691a34d25957d6093949c, rows=36
- `dimensionless_legacy_control.csv`: 067e9f56b4512a84dd452a3b0933c1b105492ce6cceb6dd1530c50640c66814b, rows=5
- `outcome_and_verdict.md`: 816153c36cb4ce9575b180da816c02efac25c218a45abbffb18e266ed81a0ef8

- derived-row count: 20224 (expected 20224)