# Article-Ib final verdict

## Физика простыми словами (no Git/test terminology)

Мы изучаем частицу в двумерной области с жёсткой стенкой, заданной набором
узлов квадратной решётки. У гладкой симметричной области первый возбуждённый
уровень — двукратный (пара мод). Хотелось понять, как этот дублет реагирует на
деформацию формы, и построить для этого матрицу «отклика» 2×2, инварианты
которой (собственные значения) считались бы физической характеристикой.

Почему цифровой гамильтониан меняется скачками. При фиксированной решётке
область — это конечный набор узлов. Когда форма плавно деформируется, набор
узлов НЕ меняется до тех пор, пока граница не пересечёт очередной узел. В этот
момент узел (и его связи) добавляется или удаляется — гамильтониан прыгает.
Между такими событиями он вообще не меняется.

Почему обычной производной может не существовать. Раз гамильтониан кусочно
постоянен, его производная по деформации равна нулю почти всюду и не определена
в точках событий. Значит, «производной формы» на фиксированной решётке нет;
есть только конечная разность, накопленная по событиям. Наш плотный скан это
подтвердил: отклик стоит ровно на нуле, пока не случится событие, а затем
прыгает.

Чем endpoint-отклик отличается от континуальной производной Адамара. У гладкой
(континуальной) области производная дублета существует и равна известному
учебниковому значению j₁₁²/j₀₁²≈2.54. Но это свойство НЕПРЕРЫВНОГО семейства, а
не решётки. На решётке «матрица отклика» — это конечная разность, зависящая от
того, какие события уже произошли.

Что такое transport и embedding, и почему они важны. Базовый и деформированный
гамильтонианы живут на РАЗНЫХ наборах узлов, поэтому их нельзя просто вычесть —
нужно решить, как отождествить два пространства (embedding) и как «перенести»
пару мод (transport). Мы проверили: перенос (сырой или полярный) почти не
влияет, НО сам способ построения матрицы влияет катастрофически. Два стандартных
и одинаково законных построения — проекция на деформированный дублет и точная
компрессия базовых мод (Рэлея–Ритца) — дают ответы, отличающиеся примерно ВДВОЕ
(иногда впятеро), а для некоторых симметричных размещений одно даёт ноль, а
другое — единицу с лишним.

Почему «положительный инвариантный split» сам по себе тривиален. Расщепление
(разность двух собственных значений) неотрицательно по определению. Поэтому
«отклик положителен» — не открытие. И, что важнее, его ВЕЛИЧИНА не является
устойчивой: она зависит от построения и от того, попало ли граничное событие в
интервал деформации.

Что осталось потенциально новым. Сама «матрица отклика» как инвариант —
не устоялась (снимается). Единственное, что реально есть, — это цифровая
статистика граничных СОБЫТИЙ (сколько узлов пересекает границу, с какими весами
собственных функций, как это зависит от плоских рационально ориентированных
участков). Но у этого уже есть развитая математическая теория (дискрепанс числа
узлов решётки), и пока не показано, что наш спектральный вариант от неё
отличается. Поэтому большой расчёт запрещён до вывода конкретного отличающего
предсказания.

---

## Outcome (frozen V1-V4)

**V3 — CONSTRUCTION NOT ROBUST**, with a narrow V2 remnant.

- Two admissible constructions (deformed-doublet projection vs fixed-mode
  Rayleigh-Ritz compression) disagree by ~50-460% (frozen tolerance 5%),
  including qualitative disagreement (exact zeros vs O(1)).
- The response is event-driven (piecewise-constant operator, proven; dense
  scans confirm jumps), so it is not a fixed-`a` derivative.
- Transport (raw vs polar) is stable (~1%), but that does not rescue the object.
- The Article-I invariant micro-pilot (two-state construction, interpreted as a
  shape-derivative matrix) is therefore WITHDRAWN.
- V2 remnant: IF one fixes the construction to the exact large-barrier
  Rayleigh-Ritz compression AND a fixed transport, and defines the observable as
  an explicit EVENT-AVERAGED statistic (not a per-placement derivative), a
  reproducible digital object may exist. That is a redefinition, not the
  Article-I matrix.

## Stop/go (frozen A-D)

**A — STOP the invariant-response-matrix line** (as a derivative / absolute
invariant), with a conditional, narrow **B — REDEFINE** available only as an
explicit event-averaged digital statistic AND only after a discriminating
lattice-point-discrepancy prediction is derived (currently
`DIRECT DISCREPANCY COMPARISON NOT YET FULLY DEFINED`, so no large pilot).

Not chosen: C (CONTINUE DIGITAL) — the construction is not validated; D (RETURN
TO CONTINUUM) — the continuum quantity is textbook (`j11^2/j01^2`), already
established in Article-I, no new continuum quantity found.

## Answer to the Article-Ib main question

The reconstructed 2x2 invariant matrix is NOT a correct, transport-stable
digital event-response observable. Article-I replaced the earlier label artifact
with a construction that is truncation- and embedding-dependent and event-driven:
different admissible constructions change the eigenvalues by far more than the
claimed effect. The only defensible remaining object is an explicitly defined,
fixed-construction, event-averaged digital statistic, whose novelty is not
established against existing discrepancy theory. No 64^2, no distribution pilot,
no manuscript.

## What still stands from earlier work

- Article-F/G/H methodological negatives (sorted-gap + unsubtracted baseline
  false positive; raw-energy normalization artifact) — unchanged.
- Article-I continuum benchmark `j11^2/j01^2 = 2.538734` (derived + MFS-verified)
  and the finding that the Article-H signed C1 sign is a labeling artifact —
  unchanged (they do not depend on the invariant-matrix construction).
- Corrected: the traceless Frobenius norm is `split/sqrt(2)` (see
  `correction_record.md`).
