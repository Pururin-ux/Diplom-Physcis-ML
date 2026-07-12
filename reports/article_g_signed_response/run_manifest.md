# Article-G run manifest (protocol section 14)

- generated: 2026-07-12T22:36:15.938856+00:00
- branch: article-g-signed-shape-response
- commit: 814ca60acc565048e0902f34cf79e422fda14974
- protocol commit on remote (frozen before results): 0fa6cbe
- environment (from the running interpreter):
  - python: 3.12.13
  - platform: Windows-11-10.0.26200-SP0
  - numpy: 2.4.3
  - scipy: 1.17.1
  - kwant: 1.5.0
- exact commands:
  - `python scripts/run_article_g_smoke.py`
  - `python scripts/run_article_g_pilot.py`
  - `python scripts/run_article_g_analysis.py`
  - test suite: `python -m pytest tests -q`

## SHA256 of artifacts
- `protocol.md`: 2ce2ec7727961aea3236fdef6b60d9fa54ffa457c491251e5eb6d4647202bd08
- `smoke_report.md`: 29543e377702fa7a074f1159f68b16d74501ed3c4f9b02af4ad120ce4d3ef3a0
- `pilot_main_rows.csv`: 3480edd06a38411d424882bb72d370c977ac9a3a3d40684f8e79979b6abc3c47
- `pilot_conv_rows.csv`: 52195a4e33c92f56a37eb77ad97bbf3bd75e9417e77eb3fc968e071970573f1e
- `pilot_aggregates.csv`: 376cb777d84a9771262c4653ea026be67d0c219e30e787252000049d07772079
- `pilot_convergence.csv`: 03db186aea18e7a19be9e7e5196b17d0f122730c376390049ef6c92b5f6bd004
- `pilot_chi_split_distributions_xi0.4.csv`: 9cc32d020923c53fb1b5d0493cdb95b18a8e06ccbbca14a143b7458db920d58d
- `analysis_summary.md`: 59d084c092a57473aa9114c8b60538ddf8cac4d3bdb8335748126214326a4e2a
- `pilot_log.txt`: 3a3cfafd084cb684716eedb8a90dacda48646beb8cd42622100a5a7091850fc7