"""Builds fec_colab.ipynb with fec_gpu.py embedded (so the notebook needs no repository access)."""
import json, os
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, "fec_gpu.py")).read()


def md(t):
    return {"cell_type": "markdown", "metadata": {}, "source": t.strip("\n").splitlines(True)}


def code(t):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": t.strip("\n").splitlines(True)}


cells = [
    md("""
# FEC 오류 바닥 시뮬레이션 (Colab GPU)
1. 런타임 → 런타임 유형 변경 → **GPU**(T4 이상)를 고릅니다.
2. 위에서부터 차례로 실행합니다.
3. 결과는 Google Drive의 `fec_runs/` 폴더에 기록됩니다.
   - 약 1–3분마다 한 줄씩 저장됩니다. 세션이 끊기거나 중간에 멈춰도 저장된 줄은 그대로 남습니다.
   - 같은 셀을 다시 실행하면 새 seed로 같은 파일에 이어서 쌓입니다(표본 중복 없음).
"""),
    code("""
!nvidia-smi -L
try:
    import cupy
except ImportError:
    !pip -q install cupy-cuda12x
    import cupy
print("cupy", cupy.__version__, cupy.cuda.runtime.getDeviceCount(), "GPU")
"""),
    code("""
from google.colab import drive
drive.mount('/content/drive')
import os
OUT = '/content/drive/MyDrive/fec_runs'
os.makedirs(OUT, exist_ok=True)
%cd /content
"""),
    code("%%writefile fec_gpu.py\n" + src),
    md("""
## 1. 자체 검증 + 속도 측정 (약 5분)
- 첫 줄 끝에 `SELFTEST PASSED`가 나와야 합니다. GPU 결과가 CPU 기준값과 비트 단위로 같다는 뜻입니다.
- 나머지 두 줄의 `done in ...s` 시간을 알려 주시면 본 실행 시간을 계산해 드립니다.
"""),
    code("""
!python fec_gpu.py selftest
!python fec_gpu.py staircase --p 0.005 --units 2560 --batch 256 --out {OUT}/bench.jsonl
!python fec_gpu.py product --p 0.0065 --units 16384 --batch 512 --out {OUT}/bench.jsonl
"""),
    md("""
## 2. 본 실행 A: staircase 부호 (가장 중요)
- 대상: Holzbaur et al. 2019, 4.2절 부호. 255×255 블록, [510,491] 성분부호, 창 크기 W = 7.
- 목적: 논문의 "p = 5×10⁻³에서 오류 바닥 약 2×10⁻¹⁰, ξ = 1.6×10⁻³"을 재현하는지, 그리고 낮은 p에서 상수 ξ 모델이 맞는지 확인합니다.
- p 값은 앞에 둔 것부터 실행됩니다. 중간에 멈춰도 그때까지의 결과는 저장됩니다.
"""),
    code("""
!python fec_gpu.py staircase --p 0.005 0.0048 0.0046 --units 1000000 --batch 256 --out {OUT}/staircase_W7.jsonl
"""),
    md("""
### (선택) 창 크기 W = 10
같은 p에서 복호기 설정에 따라 결과가 얼마나 달라지는지 봅니다.
"""),
    code("""
!python fec_gpu.py staircase --p 0.005 --units 300000 --batch 256 --W 10 --out {OUT}/staircase_W10.jsonl
"""),
    md("""
## 3. 본 실행 B: [256,239,6]² 제품부호
목적: p = 6.5×10⁻³에서도 ξ(p)가 계속 줄어드는지 확인합니다.
"""),
    code("""
!python fec_gpu.py product --p 0.0065 --units 10000000 --batch 512 --out {OUT}/product.jsonl
"""),
    md("""
## 4. 요약
이 출력, 그리고 Drive `fec_runs/` 폴더의 `.jsonl` 파일을 보내 주세요.
"""),
    code("""
import glob
for f in sorted(glob.glob(OUT + '/*.jsonl')):
    print(f)
    !python fec_gpu.py summary --out {f}
"""),
]
nb = {"cells": cells, "metadata": {"accelerator": "GPU", "colab": {"provenance": []},
                                   "kernelspec": {"display_name": "Python 3", "name": "python3"}},
      "nbformat": 4, "nbformat_minor": 0}
json.dump(nb, open(os.path.join(here, "fec_colab.ipynb"), "w"), ensure_ascii=False, indent=1)
print("wrote fec_colab.ipynb")
