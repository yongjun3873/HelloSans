# 원고 재평가 (목표 저널: IEEE Transactions on Information Theory)

- 대상: "The Maximum-Likelihood Block-Error Window of Binary Gaussian MIMO: When Soft-Bit Approximate Message Passing Reproduces the ML Decision" (manuscript_1.pdf)
- 기준: 연구 주제 평가 체계 v2 (가이드.md 부록 A). 목표 저널을 **IEEE TIT**로 바꿔 다시 평가했다.
- 이전 평가(평가_manuscript_1.md)와 다른 점:
  - TIT 기준으로 **기준점 보정**을 새로 했다(1절).
  - 각 항목을 TIT에 실린 비교 대상 논문과 대조해 다시 매겼다.
- 확인 수준: 원고 전문을 읽었고, 수치 상수 7개를 재계산했다(이전 평가 4절). 선행 연구는 검색 결과 요약 수준으로 대조했다.

---

## 0. 결론

**A = 74 (범위 63–83)**

- 이전 TIT 추정치는 74 (57–77)였다. 중앙값은 같고 범위가 위로 이동했다(5절).
- 분류: 중앙값 74가 75에 1점 모자라 규칙상 **보류(A < 75)** 다. 다만 범위 상단이 83이라 **제한적 검증 후보(75–84)와 경계**에 있다.
- 범위가 85를 걸치지 않으므로, 증명이 모두 맞더라도 지금 형태로는 "우선 연구 주제(≥ 85)"에는 닿지 않는다.
- 6절의 보강 중 하나(역방향 강화 또는 복소/QPSK 확장)를 하면 중앙값이 79–80으로 올라 제한적 검증 후보가 된다.

---

## 1. 기준점 보정 (TIT, 1회)

제안 시점에 알 수 있던 정보만으로 매기려고 했다. 사후 지식(인용 수 등)은 반영하지 않았다.

| 구분 | 논문 | 중요성 | 공백 | 답의 크기 | 적합성 | A |
|---|---|---|---|---|---|---|
| 대표 1 | E. Abbe, A. S. Bandeira, G. Hall, "Exact Recovery in the Stochastic Block Model," IEEE TIT 62(1), 2016 | 4 | 5 | 5 | 5 | **94** |
| 대표 2 | G. Reeves, H. D. Pfister, "The replica-symmetric prediction for random linear estimation with Gaussian matrices is exact," IEEE TIT 65(4), 2019 | 4 | 4 | 5 | 5 | **88** |
| 대조 1 (직접 대입) | 알려진 AMP 상태 진화를 새 성상(예: QPSK)의 MIMO 검출에 그대로 적용하고 시뮬레이션만 붙인 유형 | 2 | 1 | 2 | 2 | **34** |
| 대조 2 (작은 확장) | 박스 완화의 Poisson 법칙(Hu–Lu)을 같은 기법으로 다른 성상에 옮긴 유형 | 3 | 2 | 2 | 4 | **52** |

판단 근거:
- **Abbe–Bandeira–Hall:** 정확 복원 문턱이 미지였다(공백 5). 날카로운 문턱과 그것을 달성하는 효율적 알고리즘을 함께 제시했다(답의 크기 5).
- **Reeves–Pfister:** 비엄밀 예측(replica)이 이미 있었으므로 공백은 4다.
- 대표(88–94)와 대조(34–52)가 뚜렷하게 갈린다. 이 원고는 이 사이, 대표 쪽에 가깝게 놓인다(74).

---

## 2. A 항목별 채점 (TIT 기준)

| 항목 | 등급 (범위) | 점수 | 근거 |
|---|---|---|---|
| 중요성 | **3** (3–4) | 18 | (+) 이산 사전분포를 갖는 가우시안 랜덤 선형 추정은 TIT의 정준 모델이다(Tse–Verdú, Reeves–Pfister, Barbier et al.). "다항시간 수신기가 ML의 **블록 결정**까지 재현하는가"는 계산-통계 격차 질문의 날카로운 형태다. TIT 독자 기준에서는 무부호·i.i.d. 가정이 결함이 아니라 표준 설정이므로, 하단을 2에서 3으로 올렸다. (−) 실수 채널과 BPSK에 한정되어 영향 범위가 좁다. 복소 채널·QPSK로의 확장이 원고에서 열린 문제로 남아 있어 4는 주지 않았다. |
| 공백 | **4** (3–4) | 24 | (+) 1차 문턱은 Papailiopoulos(arXiv:2609.19405, 2026)가 정리했고, 2차 창은 열린 채로 남았다. 이 창에서 ML = 지니, AMP = ML 결정이라는 결론은 검색에서 찾지 못했다. (−) TIT 심사위원은 **SBM 정확 복원 패러다임**과 비교할 것이다. Abbe–Bandeira–Hall(2016)은 ML이 최적 문턱을 달성하고, 부분 복원 + 국소 개선(local improvement)으로 효율적으로 문턱에 도달함을 보였다. "단일 뒤집기(single flip)로 ML 실패를 특징짓고 효율적 알고리즘이 따라잡는다"는 구조는 TIT에 익숙한 틀이다. 기법의 익숙함은 공백 감점 사유가 아니지만, 결론의 새로움을 이 틀과 분명히 구분해 보여야 한다. 희소 회귀에서 다항시간이 전수 탐색의 정확 복원 조건을 달성한다는 결과(Ndaoud–Tsybakov, arXiv:1809.03145)도 같은 이유로 대조가 필요하다. |
| 답의 크기 | **4** (3–4) | 20 | (+) 결과가 1차 문턱이 아니라 **2차 창 안의 결정 등가성**이다. ABH 같은 1차 문턱 결과보다 해상도가 높고, ML 오류 수가 Poisson이며 그 1차 항이 δ와 무관하다는 관찰도 새롭다. (−) TIT에서는 역방향의 강도가 더 중요하게 평가된다. Theorem 3은 데이터 비의존 홀함수 디노이저, 0 시작, o((log N/log log N)^{1/3})회 반복으로 한정된다. 일반 1차 방법(GFOM, Celentano–Montanari–Wu)이나 저차 다항식(low-degree) 수준의 증거가 없다. 검색해 본 범위에서는 이진 선형 회귀나 MIMO 검출에 대한 저차 다항식 하한도 아직 없었다. 이것이 5가 아닌 이유다. |
| 저널 적합성 | **4** (4–5) | 12 | (+) 엄밀한 정리·증명 중심, 점근 해석, Poisson 근사, AMP 이론으로 이루어져 TIT의 핵심 출판 영역(Rush–Venkataramanan 2018, Reeves–Pfister 2019, Barbier et al. 2020)과 맞는다. (−) Theorem 2와 3의 N₀가 [1](Bao–Han–Xu)의 비명시적 상수에 의존한다. 기여의 상당 부분이 응용확률 도구의 정교한 적용이어서, 일부 심사위원은 응용확률 저널(AAP 등)이 더 맞다고 볼 수 있다. |

**A = 18 + 24 + 20 + 12 = 74 (범위 63–83)**
- 하단 등급 [3, 3, 3, 4] → 18 + 18 + 15 + 12 = 63
- 상단 등급 [4, 4, 4, 5] → 24 + 24 + 20 + 15 = 83

---

## 3. B (추진 판단, TIT 기준)

- **성공 가능성: 높음.** 목표 결과는 원고 안에서 증명되어 있다. 남은 위험은 증명 세부와 심사다.
- **근거 신뢰도: 중간.** 증명 전체와 [1]의 가정 충족 여부(부록 B)를 독립 검증하지 않았다. TIT 쪽 선행 연구 대조도 검색 요약 수준이다.
- **상태: 진행** (TIT 투고 준비).
- **가장 큰 위험 (TIT에 특화된 것):**
  1. **[1] 적용의 엄밀성.** TIT 심사는 증명을 줄 단위로 본다. 반복 수에 따른 인자 (C log N)^{CT³}, (6.4)의 N^{−1/C₀^T}, [1, Thm 2.10]의 slack 선택이 가장 먼저 점검될 것이다.
  2. **"sharp threshold" 표현.** 부류 𝒜에만 해당한다는 점이 초록·제목에서 충분히 드러나지 않으면 과장으로 지적받을 수 있다.
  3. **선점 위험.** TIT는 심사가 길다(통상 1년 안팎). 그동안 Papailiopoulos의 후속 연구나 다른 그룹이 창을 다룰 수 있다.
- **다음 결정적 검증:**
  1. 부록 B를 [1](arXiv:2312.05911v3)의 정리와 가정 번호에 1:1로 대조한다. AMP 이론을 아는 제3자 1명에게 부록 B와 Proposition 6.3만이라도 검토받는다.
  2. ABH(2016)와 Ndaoud–Tsybakov 대비 차이를 관련 연구에 한 문단으로 넣는다.
  3. 투고 전에 2609.19405의 개정판과 인용 논문을 다시 확인한다.

---

## 4. TIT 투고 전략 제안

1. **arXiv 선공개.** 선점 위험을 줄이는 가장 싼 방법이다. Papailiopoulos 논문이 2026년 9월에 나왔으므로 빠를수록 좋다.
2. **ISIT 단축판 병행.** TIT 정식 투고와 별개로 ISIT에 5쪽 요약판을 내는 것이 정보이론 분야의 관행이다. 마감은 보통 1월경이니 정확한 날짜를 확인해야 한다. 학회 발표는 우선권을 남기는 효과도 있다.
3. **원고 구성 조정 (선택).** TIT 독자에게는 8절 시뮬레이션의 비중을 줄이고, 2절 정리와 3절 증명 구조를 앞에 두는 현재 배치가 적절하다. 단일 칼럼 47쪽은 투고 형식으로 문제없다.
4. **AI 사용 고지.** 원고 Acknowledgment에 이미 명시되어 있어 IEEE 정책에 맞는다. 그대로 유지하면 된다.

---

## 5. 변경 이력

| 항목 | 이전 (TIT 추정) | 이번 | 근거 유형과 이유 |
|---|---|---|---|
| 중요성 | 3 (2–3) | 3 (3–4) | 목표 저널 변경에 따른 재평가. TIT 독자 기준에서는 이상화된 정준 모델이 결함이 아니므로 하단을 2→3으로 올렸다. 복소/QPSK 확장 시 4가 가능해 상단을 열었다. |
| 공백 | 4 (3–4) | 4 (3–4) | 변경 없음. ABH 패러다임과 Ndaoud–Tsybakov 대조 필요성을 명시했다. |
| 답의 크기 | 4 (3–4) | 4 (3–4) | 변경 없음. TIT에서 역방향 강도가 더 중요하다는 점을 감점 근거로 명시했다. |
| 적합성 | 4 (4–5) | 4 (4–5) | 변경 없음. |
| A | 74 (57–77) | **74 (63–83)** | 중앙값 같음, 범위 상향. 목표 변경 없음(논문 내용 그대로). |

---

## 6. 점수를 올리는 경로 (TIT 기준, 효과 순)

| 보강 | 영향받는 항목 | 예상 A |
|---|---|---|
| ① Theorem 3을 일반 1차 방법(GFOM) 부류로 확장하거나, δ < δ\*에서 저차 다항식 하한 증거를 추가 | 답의 크기 4 → 5 | 79 |
| ② 복소 채널·QPSK로 Theorem 1–2 확장 (적어도 Theorem 1) | 중요성 3 → 4 | 80 |
| ③ ①과 ② 모두 | 중요성·답의 크기 | **85 (우선 연구 주제 문턱)** |
| ④ ABH, Ndaoud–Tsybakov 대비 차이를 명확히 서술 | 공백의 하단 위험 감소 (범위 하단 63 → 69) | 74 (69–83) |

①은 원고 9절이 이미 열린 문제로 든 방향이다. 다만 하나만 고른다면 ②가 더 현실적이다. 원고가 복소 QPSK를 "구조화된 실수 행렬"로 바꿔야 한다고 적었는데, 이를 위해 [1]의 leave-one-out 결과를 다시 확인해야 하지만 Theorem 1(ML 창)은 AMP 없이 기초적으로 증명되므로 확장 부담이 상대적으로 작다.

---

## 7. 참고문헌 (확인 수준)

- E. Abbe, A. S. Bandeira, G. Hall, "Exact Recovery in the Stochastic Block Model," IEEE TIT 62(1), 2016, arXiv:1405.3267 — 검색 요약
- G. Reeves, H. D. Pfister, "The replica-symmetric prediction for random linear estimation with Gaussian matrices is exact," IEEE TIT 65(4), 2019 — 원고 참고문헌 [23]으로 확인
- D. Papailiopoulos, "Polynomial-Time MIMO Detection at the Maximum-Likelihood Threshold," arXiv:2609.19405, 2026 — 검색 요약
- M. Ndaoud, A. B. Tsybakov, "Optimal variable selection and adaptive noisy Compressed Sensing," arXiv:1809.03145 — 검색 요약
- M. Celentano, A. Montanari, Y. Wu, "The estimation error of general first order methods," COLT 2020 — 원고 참고문헌 [27]으로 확인
- A. S. Wein, T. Schramm, "Computational Barriers to Estimation from Low-Degree Polynomials," arXiv:2008.02269 — 검색 요약
- Z. Bao, Q. Han, X. Xu, "A leave-one-out approach to approximate message passing," Ann. Appl. Probab. 35(4), 2025, arXiv:2312.05911 — 검색 요약(서지 정보), 본문 미대조
