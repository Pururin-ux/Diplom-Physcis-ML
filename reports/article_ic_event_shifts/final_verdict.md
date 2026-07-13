# Article-Ic final verdict

## Физика простыми словами (без Git и программной терминологии)

Гладкая форма меняется непрерывно, но её цифровая версия на решётке — это
конечный набор узлов, который не меняется до тех пор, пока граница не пересечёт
очередной узел. В этот момент реальный узел (и его связи) добавляется или
удаляется, и спектр прыгает. Поэтому естественный объект изучения — не
псевдопроизводная (её на фиксированной решётке просто нет), а изменение спектра
при каждом отдельном СОБЫТИИ.

Такой event-скачок `E_j(после) − E_j(до)` — это разность двух физически
определённых чисел. Он не зависит от того, как мы пометим две моды дублета
(p_x или p_y), не требует «переноса» мод и общего пространства. Именно поэтому он
каноничен, в отличие от прежней матрицы отклика, которая зависела от способа
построения.

Механизм каждого события — учебниковый: добавление или удаление узла есть
конечно-ранговое возмущение, и сдвиг уровня определяется формулой Шура (self-
energy) и теоремой Коши о переслаивании. Простой подсчёт числа пересечённых
узлов НЕ предсказывает сдвиг щели — потому что сдвиг определяется не числом
узлов, а тем, какова амплитуда собственной функции на границе в месте события
(матричный элемент). Наши расчёты это подтвердили: как только к геометрии
добавляются веса собственных функций (тот самый матричный элемент Шура),
предсказание сдвига щели резко улучшается (R² с 0.41 до 0.91).

Но это и есть известная физика: «взвешивание собственной функцией важнее
подсчёта» — это ровно формула конечно-рангового возмущения (Крейн, Шур,
матричный элемент граничной деформации). У неё есть прямой аналог в литературе.
Поэтому нового физического эффекта здесь нет: остаточная структура сверх
известной теории не обнаружена.

Что могло бы быть новым: только если бы распределение event-меток показало
структуру, которую известная конечно-ранговая теория и теория дискрепанса
решётки НЕ объясняют. На текущем micro-pilot такого нет. Проект по этой линии
следует остановить как самостоятельную физическую новизну; каноническая
event-формулировка остаётся полезной методической рамкой (она исправляет
ошибки прежних стадий: сортировку щели, невычтенный baseline, ложную
«производную», зависимую от переноса матрицу отклика).

Когда окончательно останавливать: сейчас. Дальнейший большой расчёт не оправдан,
пока не предъявлено конкретное количественное отклонение от известной
конечно-ранговой/дискрепанс-теории.

---

## Outcome (frozen E1-E4)

**E1 CANONICAL EVENT PROCESS VALIDATED + E2 KNOWN FINITE-RANK / DISCREPANCY
PHYSICS.**
- E1: exact complete enumeration (telescoping residual 0.0), basis/transport/
  gauge-independent marks, finite-rank formulas reproduce mechanics.
- E2: the marks are explained by known Schur self-energy / Krein spectral shift /
  Cauchy interlacing plus lattice-point discrepancy; eigenfunction weighting adds
  the KNOWN matrix element (Model 1 R^2 0.91 vs Model 0 0.41), with a direct
  literature analog. E3 (novel structure beyond known theory) is NOT met.

## Stop/go (frozen A-D)

**B - METHOD NOTE ONLY.** The canonical, transport-free, gauge-free, additive
event-shift formulation is a sound methodological object and the correct way to
describe digital-boundary spectral changes; but there is no separate physical
novelty, because the mechanism is textbook finite-rank perturbation and the
geometric event process is lattice-point discrepancy. Not A (there IS a
reproducible, well-defined object and a useful method), not C/D (no structure
beyond known theory).

## Answer to the Article-Ic main question

The boundary events of a digital billiard DO form a canonical, well-defined
marked spectral process (E1). But the eigenfunction-weighted marks do NOT carry
information beyond ordinary lattice-point discrepancy + finite-rank graph
perturbation: the eigenfunction weighting that governs the gap shift is exactly
the known Schur / Krein matrix element (E2). No new physical effect is
established. The line is closed as a methodological contribution (B); no large
64^2 or distribution pilot is warranted, no manuscript.

## What stands from earlier work (unchanged)

- Methodological negatives of Article-F/G/H (sorted-gap + unsubtracted baseline
  false positive; raw-energy normalization artifact).
- Article-I continuum benchmark `j11^2/j01^2 = 2.538734` (derived + MFS-verified)
  and "signed C1 sign is a labeling artifact".
- Article-Ib: the 2x2 response matrix is not a transport/construction-stable
  derivative (V3); the Frobenius `split/sqrt(2)` correction.
- Article-Ic corrections to Ib framing (three distinct objects; ground-state
  completeness; set-inequality event detection).
