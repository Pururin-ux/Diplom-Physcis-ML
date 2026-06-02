# Alpha-aware S-objective feasibility audit

This file is an audit/diagnostic record only. It is not a final scientific
S-objective result, not a final experiment report, and not an article draft.

## Purpose

The previous no-output probe for `n = 2.0` used unconstrained top-S method
candidates and found:

- `top5_method_candidates = 5`
- `Ekin feasible = 5`
- `Q feasible at alpha = 0.95 = 0`
- `both Ekin and Q feasible = 0`

That probe could not distinguish real physical S/Q incompatibility from an
implementation artifact caused by proposing unconstrained high-S candidates.
This audit checks alpha-aware proposal logic before any full S-objective
execution.

## Protocol status

- preregistration_commit: `7e28542fda40db288ad2613b49f17b1248f6f2ce`
- implementation_branch: `article-s-objective-implementation`
- frozen rules modified: no
- primary alpha remains: `0.95`
- secondary alpha remains: `0.90`
- full S experiment run: no
- final S outputs produced: no

## Q(rAR) from training data

These diagnostics use already Kwant-computed training rows only. No new Kwant
calculation was performed for this section.

For all four fixed `n` values, training-data Q has positive Spearman rank
correlation with `aspect_ratio`:

| n | Spearman r(aspect_ratio, Q) | Interpretation |
|---|---:|---|
| 1.2 | 0.9901475429766743 | Q increases with aspect_ratio; Q tends to decrease as aspect_ratio decreases |
| 2.0 | 0.9901475429766743 | Q increases with aspect_ratio; Q tends to decrease as aspect_ratio decreases |
| 3.0 | 0.9901475429766743 | Q increases with aspect_ratio; Q tends to decrease as aspect_ratio decreases |
| 4.0 | 0.9901475429766743 | Q increases with aspect_ratio; Q tends to decrease as aspect_ratio decreases |

Training-data Q summary by `aspect_ratio`:

| n | aspect_ratio | n_rows | Q_mean | Q_min | Q_max |
|---|---:|---:|---:|---:|---:|
| 1.2 | 0.67 | 5 | 1.1774382586789458 | 1.1740979902275284 | 1.1801855605349476 |
| 1.2 | 0.72 | 5 | 1.230557896296385 | 1.2247395435970214 | 1.23909624787486 |
| 1.2 | 0.78 | 5 | 1.3015883483723711 | 1.29084234342473 | 1.308919653983595 |
| 1.2 | 0.83 | 5 | 1.3470258598912292 | 1.3376172122376975 | 1.356884580816902 |
| 1.2 | 0.89 | 5 | 1.4093585618013031 | 1.4023728636285782 | 1.415482055553874 |
| 1.2 | 0.94 | 5 | 1.4582315375389467 | 1.4536433776983368 | 1.4619902850572333 |
| 1.2 | 1.00 | 5 | 1.5132618841563745 | 1.5088453047172001 | 1.5159264178177203 |
| 2.0 | 0.67 | 5 | 1.0613621479259892 | 1.0546979936629624 | 1.068182312384693 |
| 2.0 | 0.72 | 5 | 1.1461943446515825 | 1.13319659492928 | 1.1577936136469433 |
| 2.0 | 0.78 | 5 | 1.2358110041180546 | 1.231046065040419 | 1.242774301280115 |
| 2.0 | 0.83 | 5 | 1.3112981504191785 | 1.3073975895928576 | 1.3181545533118146 |
| 2.0 | 0.89 | 5 | 1.3937448552437233 | 1.3878078579933528 | 1.397021697354876 |
| 2.0 | 0.94 | 5 | 1.4637956131238448 | 1.4594177142235323 | 1.468456546729933 |
| 2.0 | 1.00 | 5 | 1.5370365132626704 | 1.5362641228731444 | 1.5376311959164866 |
| 3.0 | 0.67 | 5 | 1.0192454687454937 | 1.011353684696267 | 1.0251134113679525 |
| 3.0 | 0.72 | 5 | 1.0958203931980868 | 1.0741894101142513 | 1.120062107556241 |
| 3.0 | 0.78 | 5 | 1.200706857174414 | 1.1905530784216567 | 1.2083783870099751 |
| 3.0 | 0.83 | 5 | 1.2762404281055926 | 1.2657056273491682 | 1.2938590536770143 |
| 3.0 | 0.89 | 5 | 1.3803060383614683 | 1.371467478023929 | 1.3904578469430298 |
| 3.0 | 0.94 | 5 | 1.4565362578541574 | 1.443957776806677 | 1.4630472645992398 |
| 3.0 | 1.00 | 5 | 1.525120636529817 | 1.5246612800045969 | 1.5257866649051655 |
| 4.0 | 0.67 | 5 | 1.0097651975015394 | 1.000650583723233 | 1.020211689587561 |
| 4.0 | 0.72 | 5 | 1.0748677983739814 | 1.0500152604667572 | 1.104603083845431 |
| 4.0 | 0.78 | 5 | 1.1864813429595689 | 1.1682215364816488 | 1.2038710521747842 |
| 4.0 | 0.83 | 5 | 1.2586929081058302 | 1.2453308143742796 | 1.279091697802021 |
| 4.0 | 0.89 | 5 | 1.3738780259340033 | 1.3588884226859357 | 1.383854352361927 |
| 4.0 | 0.94 | 5 | 1.4486095046997782 | 1.4298156599302503 | 1.4605715335071665 |
| 4.0 | 1.00 | 5 | 1.5124561254599806 | 1.5106926354426646 | 1.513488230931016 |

Interpretation before full Kwant execution: training data support a strong Q
penalty as anisotropy increases. This is compatible with a real S/Q tradeoff,
but it does not by itself decide whether the alpha-aware S method can beat the
pre-registered baselines.

## Alpha-aware proposal results

No direct Kwant verification was run for all candidates in this section. These
are surrogate proposal diagnostics only.

| n | alpha | Ekin_target | Q_iso_pred | threshold_q_pred | raw candidates | predicted-Q-feasible | selected top-k | selected aspect_ratios | selected S_pred | selected Q_pred | failure_mode |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|---|
| 1.2 | 0.95 | 0.010689289799576063 | 1.5116459012790209 | 1.4360636062150698 | 67 | 15 | 4 | 0.93, 0.955, 0.97, 1.0 | 0.1498089076494998, 0.09799867898106673, 0.06684858340272427, 0.004408343364440278 | 1.4379257531536607, 1.4641934582357135, 1.4799869491376108, 1.5116459012790209 | fewer_than_top_k_predicted_q_feasible_candidates |
| 1.2 | 0.90 | 0.010689289799576063 | 1.5116459012790209 | 1.360481311151119 | 67 | 29 | 5 | 0.86, 0.875, 0.885, 0.915, 0.94 | 0.2941371247703991, 0.2633044621659046, 0.24272010480255984, 0.18082969410028302, 0.12910099378506254 | 1.3647566782433431, 1.3803870421138968, 1.390822315571537, 1.4221987134897955, 1.4484245216067386 | ok |
| 2.0 | 0.95 | 0.007727409624868287 | 1.5412612995709263 | 1.4641982345923799 | 67 | 11 | 4 | 0.95, 0.965, 0.985, 1.0 | 0.14230781099868234, 0.09741909104624083, 0.03743836344094001, -0.007642226165358654 | 1.4654145032521426, 1.488119485214236, 1.5184585668572212, 1.5412612995709263 | fewer_than_top_k_predicted_q_feasible_candidates |
| 2.0 | 0.90 | 0.007727409624868287 | 1.5412612995709263 | 1.3871351696138337 | 67 | 21 | 5 | 0.9, 0.92, 0.935, 0.955, 0.975 | 0.2913180116165122, 0.23183013322802556, 0.18711197271670355, 0.12735422938275057, 0.06744699896799372 | 1.3900465201637848, 1.420134512692852, 1.4427526006973619, 1.4729780797998537, 1.5032797172432348 | ok |
| 3.0 | 0.95 | 0.007053480364534792 | 1.53322893607468 | 1.456567489270946 | 67 | 10 | 3 | 0.955, 0.98, 0.99 | 0.13314784950949402, 0.05107328634440056, 0.018180891290107044 | 1.4592393376516135, 1.5003001008633972, 1.516755722427175 | fewer_than_top_k_predicted_q_feasible_candidates |
| 3.0 | 0.90 | 0.007053480364534792 | 1.53322893607468 | 1.379906042467212 | 67 | 19 | 5 | 0.91, 0.925, 0.935, 0.95, 0.98 | 0.28030139398830617, 0.2313349313785645, 0.19864319393900626, 0.1495355352781244, 0.05107328634440056 | 1.3856205897426146, 1.4101177704424521, 1.4264729625492258, 1.4510408120984157, 1.5003001008633972 | ok |
| 4.0 | 0.95 | 0.006858160651241896 | 1.5220619922602496 | 1.445958892647237 | 67 | 10 | 3 | 0.955, 0.985, 0.995 | 0.13211219934934063, 0.03229891692233794, -0.0010354050030339504 | 1.4477121216980064, 1.497243806004484, 1.513785446910933 | fewer_than_top_k_predicted_q_feasible_candidates |
| 4.0 | 0.90 | 0.006858160651241896 | 1.5220619922602496 | 1.3698557930342248 | 67 | 19 | 5 | 0.91, 0.93, 0.935, 0.955, 0.985 | 0.2812802668042304, 0.21506691154073895, 0.19849251424408576, 0.13211219934934063, 0.03229891692233794 | 1.373685858873818, 1.406545344631491, 1.4147705673185789, 1.4477121216980064, 1.497243806004484 | ok |

The alpha-aware proposal step removes the immediate implementation artifact
seen in the previous unconstrained n=2.0 probe: for `alpha = 0.95`, predicted-Q
feasible candidates now exist for every fixed `n`. However, fewer than five
diverse candidates are selected at the primary alpha for every `n`, and the
selected primary-alpha candidates are close to isotropy.

## Decision

The full S-objective experiment remains blocked until explicit authorization.
From an implementation-readiness perspective, the alpha-aware proposal issue is
addressed and no final result-writing occurred. From a scientific perspective,
the diagnostics warn that the primary-alpha search may be constrained to
near-isotropic geometries, so a negative or weak S result remains plausible.
