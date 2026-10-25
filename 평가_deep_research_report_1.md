# deep-research-report_1 독립 평가 (주제 A·B·C)

- 기준: 연구 주제 평가 체계 v2 (가이드.md 부록 A).
- 목표 저널: 보고서가 제시한 1순위를 따랐다(A: TSP, B: TWC, C: TSP/TVT).
- 표시: **보정 전 잠정치.** 이번 평가에서는 기준점 보정을 따로 하지 않았다.
- 확인 수준: 선행 연구는 검색 결과 요약(초록 수준)으로만 대조했다. 주제 C의 핵심 반증 지표(가속도 때문에 생기는 2차 위상의 크기)는 직접 계산했다.

---

## 0. 결론

| 주제 | 재평가 A (범위) | 분류 | 한 줄 판정 |
|---|---|---|---|
| B. 위상 coherence 추적 + coherent/non-coherent 전환 (TWC) | **58 (43–63)** | 보류 | 문제는 중요하다. 그러나 "부분 coherent 전송"과 "혼합 coherent/non-coherent"가 2022–2024년에 이미 정리되어 공백이 작다 |
| A. Specular–Diffuse 근거리 XL-MIMO 추정 (TSP) | **57 (43–63)** | 보류 | specular + diffuse(DMC) 동시 추정은 채널 측정 분야의 고전(RIMAX)이다. 근거리·가시영역(VR) 결합이 남은 부분이다 |
| C. Doppler-rate-aware OTFS (TSP/TVT) | **46 (31–57)** | 보류 (반증 시험에 실패할 가능성 높음) | 지상 시나리오에서는 효과가 대부분 무시할 만큼 작다. 효과가 큰 LEO 쪽은 2026년 선행 연구가 있다 |

세 주제 모두 **원고(manuscript_1, TIT 기준 74점)보다 낮다.** 이전에 평가한 AI 생성 후보들(46–63점)과 같은 구간이다.

보고서가 제시한 실현 가능성 순서(B → A → C)는 내 점수 순서와 같다. 다만 셋 다 "75점 이상"에는 미치지 못한다.

---

## 1. 주제 A — Specular–Diffuse 근거리 XL-MIMO 채널 추정

**목표 결과:** 근거리 XL-MIMO 채널을 [희소 구면파 경로 × 가시영역 VR] + [공간 상관된 diffuse 성분]으로 정식화한다. 희소 모델만 쓰는 추정기의 모델 불일치 바닥(MCRB)과 실패 영역을 규명하고, 이를 회복하는 베이즈 추정기를 제시한다.

| 항목 | 등급 (범위) | 점수 | 근거 |
|---|---|---|---|
| 중요성 | 3 (2–3) | 18 | (+) 근거리 추정 문헌 대부분이 "소수의 깨끗한 경로" 가정에 의존한다는 지적은 타당하다. THz 표면 거칠기 연구도 동기를 뒷받침한다. (−) diffuse 성분의 전력 비중이 실제 mmWave/THz 근거리 환경에서 얼마나 되는지 데이터가 없다(보고서도 "미지"로 표시). UWB 측정에서는 DMC가 저주파 대역 전력의 최대 50%라는 보고가 있지만, 고주파 근거리 배열에서는 미확인이다. |
| 공백 | 2 (2–3) | 12 | (−) **specular 성분과 dense multipath component(DMC)를 함께 추정하는 것은 고전이다.** RIMAX(Richter–Thomä 계열)는 DMC를 공분산 구조로 모델링해 specular 경로와 함께 최대우도로 추정하는 표준 채널 측정 프레임워크다. THz용 폐형 시공간 DMC 모델과 UWB 확장도 있다. (−) "희소 모델이 틀렸을 때의 오차 바닥"은 MCRB라는 일반 도구의 적용이다. (−) 근거리 혼합 LoS/NLoS 모델(Lu–Dai 2023)과 하이브리드 근·원거리 모델이 있다. (+) **근거리 구면파 + 경로별 VR + DMC**를 합친 추정 문제와, 희소 추정기가 실패하는 영역 지도는 검색에서 찾지 못했다(신규성의 증명은 아님). |
| 답의 크기 | 3 (2–3) | 15 | 실패 영역 지도가 나오면 근거리 추정 설계 지침이 된다. diffuse가 약하면 이득이 작다(보고서도 인정). |
| 저널 적합성 | 4 (3–4) | 12 | TSP의 모델 불일치 + 추정기 유형에 맞다. |

**A = 57 (43–63).** 등급 범위는 [2,2,2,3]–[3,3,3,4]이다.

- B 판단:
  - 성공 가능성: 중간. 식별성이 핵심 난점이다.
  - 근거 신뢰도: 중간.
  - 상태: 보류.
  - 다음 결정적 검증: RIMAX의 DMC 모델을 근거리 배열 응답에 대입했을 때 VR 결합만으로 새 결론이 나오는지 확인한다. 공개 측정이나 레이트레이싱으로 근거리 대역의 DMC 전력비를 먼저 정한다.

## 2. 주제 B — 위상 coherence 추적과 coherent/non-coherent 전환 (셀프리)

**목표 결과:** AP 사이의 상대 위상과 CFO를 동적 상태로 추적한다. 사후 위상 분산이 임계값을 넘으면 coherent 결합보다 부분 coherent나 non-coherent 전송이 유리해지는 조건을 정리로 유도하고, 이를 클러스터링과 모드 선택에 연결한다.

| 항목 | 등급 (범위) | 점수 | 근거 |
|---|---|---|---|
| 중요성 | 4 (3–4) | 24 | (+) 분산 coherent 전송의 실제 병목이 동기화라는 점은 프로토타입(COTS RRU 실험)과 이론이 모두 뒷받침한다. 셋 중 가장 실제적이다. |
| 공백 | 2 (1–2) | 12 | (−) **핵심 아이디어가 이미 있다.** Ganesan–Vu–Larsson(IEEE OJCOMS 2024, arXiv:2403.00674)은 위상 불일치가 있을 때 **클러스터 안에서만 위상을 맞추는 부분 coherent 전송 프레임워크**를 제시했다. arXiv:2408.12329(비동기 셀프리 OFDM의 혼합 coherent/non-coherent 전송)와 arXiv:2212.13950(다중 CPU 혼합 전송)도 있다. 이 밖에 잔여 보정 오차에 강인한 빔포밍(arXiv:2608.10637), 위상잡음 인지 추정(Wu et al., TWC 2026), 비동기 수신 분석(Zheng 2022)이 있다. (−) 보고서의 핵심 식 G ∝ L + L(L−1)e^{−σ²}은 교과서적 결과다. (+) 남는 것은 **온라인 사후 불확실성 → 클러스터와 모드 결정 → SE 임계 정리**를 하나의 폐루프로 묶는 것이다. 이것은 기존 부분 coherent 프레임워크에 추적기를 붙이는 확장으로 보일 위험이 크다. |
| 답의 크기 | 2 (2–3) | 10 | "위상 오차가 크면 coherent를 포기하라"는 결론의 방향은 이미 알려져 있다. 남는 것은 임계값의 정량화다. |
| 저널 적합성 | 4 (3–4) | 12 | TWC에 맞다. |

**A = 58 (43–63).** 등급 범위는 [3,1,2,3]–[4,2,3,4]이다.

- B 판단:
  - 성공 가능성: 높음.
  - 근거 신뢰도: 중간.
  - 상태: 보류.
  - 가장 큰 위험: Ganesan–Vu–Larsson 계열의 직접 확장으로 판정되는 것.
  - 다음 결정적 검증: 2403.00674와 2408.12329 본문에서 "위상 오차 통계에 따른 모드와 클러스터 선택"이 이미 다뤄졌는지 확인한다.
- 참고: 이전 평가의 R-015(Ngo–Larsson OTA 위상 보정)와 같은 영역이다.

## 3. 주제 C — Doppler-rate-aware OTFS

**목표 결과:** 프레임 안에서 경로별 Doppler가 변하는 경우(ν(t) = ν₀ + ν̇t)를 다룬다. 지연–Doppler–Doppler-rate 입출력 관계, 기존 모델의 불일치 오차 바닥, CRLB, 추정기를 제시한다.

**직접 계산 — 반증 지표(보고서가 "가장 먼저 할 일"로 지정한 것):** 프레임 동안의 2차 위상 이탈 π·ν̇·T_f²를 시나리오별로 계산했다.

| 시나리오 | ν̇ | π·ν̇·T_f² |
|---|---|---|
| V2X 5.9 GHz, 급제동 8 m/s², T_f = 1 ms | 157 Hz/s | **0.0005 rad** |
| UAV 28 GHz, 기동 20 m/s², T_f = 2 ms | 1.9 kHz/s | **0.02 rad** |
| 고속철 30 GHz, 100 m/s, 산란체 50 m 통과, T_f = 1 ms | 20 kHz/s | **0.06 rad** |
| 고속철 30 GHz, 산란체 20 m 근접 통과, T_f = 5 ms | 50 kHz/s | 3.9 rad |
| LEO Ka, 보상 전 Doppler-rate 5 kHz/s, T_f = 10 ms | 5 kHz/s | 1.6 rad |
| LEO Ka, 궤도력 보상 후 잔여 50 Hz/s, T_f = 10 ms | 50 Hz/s | **0.016 rad** |

해석:
- **지상 시나리오 대부분에서 효과는 무시할 수준(< 0.1 rad)이다.** 플랫폼 가속도로는 거의 영향이 없다.
- 효과가 큰 경우는 두 가지뿐이다.
  - **근접 통과 기하:** 고속철이 선로변 산란체나 RRH 옆을 지나갈 때다. 이때는 위상이 2차를 넘어 Doppler 부호 반전에 가깝게 변하므로, 2차 모델보다 기저함수 확장(BEM) 모델이 더 맞을 수 있다.
  - **보상 전 LEO:** 그런데 LEO에서는 공통 Doppler-rate를 궤도력으로 보상하는 것이 표준이다. 또 arXiv:2608.03293(CP-OTFS LEO, 2026)이 이미 **프레임 내 Doppler 변화가 만드는 위상 누적을 모델링하고 CRLB를 유도**했다.
- 결론: 보고서 스스로 정한 반증 기준에 비추어 **"지상 고이동 OTFS" 프레이밍은 통과하기 어렵다.**

| 항목 | 등급 (범위) | 점수 | 근거 |
|---|---|---|---|
| 중요성 | 2 (1–3) | 12 | 위 계산대로 효과가 유의한 영역이 좁다. |
| 공백 | 2 (1–2) | 12 | (−) 다항 위상 신호(polynomial-phase)의 파라미터 추정과 CRB는 신호처리의 고전이다(Peleg–Porat 1991 — 기억 기반, 미확인). 레이더의 거리–속도–가속도 추정도 같은 구조다. (−) LEO-OTFS의 프레임 내 Doppler 변화 모델과 CRLB가 있다(arXiv:2608.03293). 시간 변동을 BEM으로 처리하는 OTFS 연구도 많다(보고서 인용). (+) 지상 OTFS를 (τ, ν, ν̇) 3차원 연속 문제로 정식화한 동일 논문은 검색에서 찾지 못했다. |
| 답의 크기 | 2 (2–3) | 10 | 효과가 작은 영역에서는 결론이 "기존 모델로 충분하다"가 된다. |
| 저널 적합성 | 4 (3–4) | 12 | TVT 또는 TSP. |

**A = 46 (31–57).** 등급 범위는 [1,1,2,3]–[3,2,3,4]이다.

- B 판단:
  - 성공 가능성: 중간.
  - 근거 신뢰도: 중간.
  - 상태: **보류. 반증 시험 실패 가능성이 높다.**
  - 살릴 경로: 근접 통과 고속철 기하에 한정해 "2차 모델 대 BEM"을 비교하는 좁은 목표가 남는다. 다만 이 경우 답의 크기도 작다.

---

## 4. 보고서에 대한 의견

- **잘한 점:**
  - 각 주제마다 "이미 알려진 것"과 "가장 큰 위험"을 적었다.
  - 주제 C에서는 반증 시험(breakdown analysis)을 알고리즘보다 먼저 하라고 정확히 지적했다.
  - TOP 3 제목을 모른다는 사실을 솔직하게 밝혔다.
- **아쉬운 점 1 — 이번에도 인접 분야 고전을 놓쳤다.** A는 RIMAX/DMC, B는 부분 coherent 전송 프레임워크, C는 다항 위상 추정이다. B의 경우에는 같은 분야의 직접 선행 연구를 놓쳤다.
- **아쉬운 점 2 — 인용 표기가 출력 형식 그대로 남아 있다.** 본문의 `citeturn…` 같은 표기는 실제 서지로 바꿔야 대조할 수 있다.

## 5. 지금까지의 평가를 종합한 제안

지금까지 평가한 외부 AI 생성 후보는 모두 **43–63점 구간**에 몰렸다. "가정 하나를 깨고 추정기를 붙이는" 생성 방식은 경쟁이 심한 분야에서 공백이 작은 후보를 반복해서 만든다.

반면 사용자가 직접 쓴 **원고(74점)** 는 사용자가 스스로 열어 둔 질문(2차 창)을 다룬다. 그래서 공백 등급이 구조적으로 높다. 다음 주제도 같은 방식으로, **원고의 9절 열린 문제에서 고르는 것이 기대값이 가장 높다**고 본다. 예를 들면 다음과 같다.
- 복소 채널·QPSK에서의 ML 블록 오류 창
- δ < δ\* 구간의 계산 장벽(저차 다항식 또는 일반 1차 방법 하한)
- 유한 N에서 블록 오류를 최소화하는 디노이저 설계

이 방향은 경쟁자가 아직 적고(Papailiopoulos 2026 정도), 사용자가 이미 증명 도구를 갖고 있다. 원하면 이 후보들을 같은 루브릭으로 채점해 줄 수 있다.

## 6. 참고문헌 (확인 수준)

- RIMAX / specular + DMC: "An extension of the RiMAX multipath estimation algorithm for ultra-wideband channel modeling," EURASIP JWCN 2018(UCLouvain); "Estimating Multi-Modal Dense Multipath Components using Auto-Encoders," arXiv:2212.02334 — 검색 요약. 원전(Richter 2005 박사논문)은 미확인
- Y. Lu, L. Dai, "Near-Field Channel Estimation in Mixed LoS/NLoS Environments for Extremely Large-Scale MIMO Systems," arXiv:2205.03615 — 검색 요약
- U. K. Ganesan, T. T. Vu, E. G. Larsson, "Cell-Free Massive MIMO with Multi-Antenna Users and Phase Misalignments: A Novel Partially Coherent Transmission Framework," arXiv:2403.00674 (IEEE OJCOMS 2024) — 검색 요약
- "Asynchronous Cell-Free Massive MIMO-OFDM: Mixed Coherent and Non-Coherent Transmissions," arXiv:2408.12329 — 검색 요약
- "Mixed Coherent and Non-Coherent Transmission for Multi-CPU Cell-Free Systems," arXiv:2212.13950 — 검색 요약
- "Robust Beamforming and Power Allocation for Coherent Cell-Free Massive MIMO with Residual Calibration Errors," arXiv:2608.10637 — 검색 요약
- "Prior-Aided Iterative Channel Reconstruction with Optimized Frame Structure for DSE Mitigation in CP-OTFS-Based LEO Satellite Systems," arXiv:2608.03293 — 검색 요약
- S. Peleg, B. Porat, polynomial-phase signal CRB (IEEE TSP 1991) — 기억 기반, 미확인
