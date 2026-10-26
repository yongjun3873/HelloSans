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
런타임 → 런타임 유형 변경 → **GPU**(T4 이상)를 고른 뒤 위에서부터 차례로 실행하세요.
결과는 Google Drive의 `fec_runs/` 폴더에 쌓이고, 세션이 끊겨도 이미 기록된 줄은 남습니다.
같은 셀을 다시 실행하면 새 seed로 이어서 쌓입니다(중복 표본 없음).
"""),
    code("""
!nvidia-smi -L
import cupy, numpy
print("cupy", cupy.__version__, "numpy", numpy.__version__)
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
## 1. 속도 측정 (약 3–5분)
두 줄의 `done in ...s`를 알려주시면 아래 본 실행의 예상 시간을 계산해 드립니다.
"""),
    code("""
!python fec_gpu.py staircase --p 0.005 --units 2048 --batch 256 --out {OUT}/bench.jsonl
!python fec_gpu.py product --p 0.0065 --units 8192 --batch 512 --out {OUT}/bench.jsonl
"""),
    md("""
## 2. 본 실행 A — staircase 부호 (Holzbaur et al. 2019 Sec. 4.2 부호, W = 7)
목표: 상수 ξ = 1.6×10⁻³ 모델이 낮은 p에서 맞는지 확인합니다. 한 번에 한 셀씩, 여러 번 실행해도 됩니다.
"""),
    code("""
!python fec_gpu.py staircase --p 0.005 0.0049 --units 2000000 --batch 256 --out {OUT}/staircase.jsonl
"""),
    md("""
## 3. 본 실행 B — [256,239,6]² 제품부호
목표: p = 6.5×10⁻³ 이하에서 ξ(p)가 계속 줄어드는지 확인합니다.
"""),
    code("""
!python fec_gpu.py product --p 0.0065 --units 20000000 --batch 512 --out {OUT}/product.jsonl
"""),
    md("## 4. 요약 (이 출력과 jsonl 파일을 보내 주세요)"),
    code("""
!python fec_gpu.py summary --out {OUT}/staircase.jsonl
!python fec_gpu.py summary --out {OUT}/product.jsonl
"""),
]
nb = {"cells": cells, "metadata": {"accelerator": "GPU", "colab": {"provenance": []},
                                   "kernelspec": {"display_name": "Python 3", "name": "python3"}},
      "nbformat": 4, "nbformat_minor": 0}
json.dump(nb, open(os.path.join(here, "fec_colab.ipynb"), "w"), ensure_ascii=False, indent=1)
print("wrote fec_colab.ipynb")
