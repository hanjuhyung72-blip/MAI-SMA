# MAI SMA 학생 패키지 이식 및 실습

## 기준과 저작 구분

기준 자료는 교수자가 제공한 **MAI_SMA_학생전달.zip**입니다. 기존에 별도로 제작한 300건 간이 앱과 구분합니다.
`app/`, `tools/`, `eval/`, START/STOP 스크립트는 제공된 학생 패키지에서 가져온 코드입니다. 원본 출처 주석을 유지했으며, 이를 학생이 새로 전부 작성했다고 주장하지 않습니다.
이식 작업은 로컬 Msty 연결 설정, DuckDB 버전 분리, 8,192 토큰 모델 별칭 설정, 실행 도우미, 원본 코드 보존 확인과 자체 점검입니다. ChatGPT Codex의 도움을 받았습니다.

## 데이터 기준

- 정비 문서 1,000건, 작업 라인 2,296건, 선박 6척
- 집계형 100문항, 절차형 100문항
- 검색 색인 1,046건 = 정비 문서 741건 + 참고 기록 305건
- 기준 DB 이름: `data/MAI_SMA_학생용DB_1000.duckdb`

DB, 색인, 실제 정비기록에서 온 가명처리 문맥, 정답 및 평가 문항 데이터는 공개 저장소에서 제외했습니다.
허가받은 검토자는 원본 제공 ZIP의 data/, prompts/, eval/db/, eval/questions/, eval/procedural/, eval/prompts/ 및 기록양식을 로컬에 합쳐 재현할 수 있습니다. 원본 자료는 담당 교수자에게 별도로 받습니다.
공개 저장소에 파일을 합쳐 다시 업로드하지 마세요. 이 저장소 자체만으로는 비공개 자료가 필요한 전체 자체 점검을 실행할 수 없습니다.

## 환경과 실행

Python 3.10 이상, DuckDB **1.5 이상 2 미만**을 사용합니다. 기존 간이 앱의 DuckDB 2.0 환경과 섞지 않습니다.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item config.example.json config.json
.\.venv\Scripts\python.exe -B tools/check_llm.py --quick
.\.venv\Scripts\python.exe -B tools/selftest.py
.\.venv\Scripts\python.exe -B app/maintqa_web.py
```

기본 웹 주소는 `http://127.0.0.1:8780/`입니다. 기존 300건 앱은 8760이므로 서로 다른 프로그램입니다.
제공된 START.bat/STOP.bat도 사용할 수 있습니다. 설치한 Python 환경을 활성화한 상태에서 실행하세요.

## Msty 연결

이 PC에서 확인한 Msty Local AI 주소는 `http://127.0.0.1:11964/v1`입니다.
기존 `llama3.2:3b` 가중치를 재사용해 num_ctx=8192인 별칭 `mai-sma-llama3.2-8k:3b`를 만들었습니다. 새 모델을 내려받거나 학습한 것이 아닙니다.
다른 환경에서는 설치된 모델 ID와 문맥 길이에 맞게 config.json을 수정해야 합니다.

**제공 안내서는 12B~14B급 모델을 권장합니다. 현재 3B 모델은 권장 크기보다 작습니다.**
실제 진단에서 연결·짧은 대화·긴 문맥·간단한 SQL은 통과했지만 기권 지시이행과 절차형 JSON 형식은 실패했습니다. 따라서 설치 성공과 답변 정확도를 구분해야 합니다.
프로그램의 원본 연구 프롬프트와 채점 규칙을 정답에 맞춰 수정하지 않았습니다. 담당 모델을 3B로 유지하여 성공과 실패를 모두 평가합니다. 다른 크기 모델은 이 담당 범위에서 실행하지 않았습니다.

## 점검 결과

- 제공된 전체 자체 점검: **76/76 PASS** (모의 로컬 LLM을 포함한 기능·데이터·평가기 검사)
- 실제 Msty 연결 확인
- 14,048자 / 입력 7,305토큰의 긴 문맥 검사 통과
- 현재 3B 모델: 기권 지시 검사 실패, 절차형 JSON 형식 검사 실패
- 실제 웹 질문의 전체 문서 수 1,000건 확인
- 부품 소모 문서 수의 DB 정답은 75이지만, 현재 3B 모델은 소모 라인 수를 세는 잘못된 SQL을 생성한 사례가 있음
- 실제 3B 모델 200문항 전체 평가 완료: 집계 엄격 29/100, 절차 JSON 유효 70/100. 상세는 [3B 평가 결과](results/llama32_3b/3B_평가결과.md) 참조

## 실행 도우미

StudentKitLauncher.cs는 제공 프로그램을 별도 창 없이 시작하고 웹 화면을 여는 Windows 실행 도우미 소스입니다.
실제 로컬 실행 패키지에는 Python 3.12 경로 설정 및 DuckDB 1.5.6 환경을 따로 두었습니다. 이 환경과 비공개 DB를 담은 실행 ZIP은 Public 저장소에서 제외했습니다.

## 과제 산출물

| 과제 | 위치 | 상태 |
|---|---|---|
| 1. DuckDB 적용 | app/, tools/, config.example.json | 1,000문서 학생판 실행 확인. [논문용 실제 앱 화면](evidence/app/) 추가 |
| 3. Colab GPU ML/DL | notebooks/, evidence/colab/ | 기존 실제 MNIST 실습 사진 5장 유지 |
| 4. Codex 증빙 | evidence/codex/ | 실제 대화 화면 총 5장. 2026-11-16에 2장 보완 |
| 5. 소스 공개 정리 | 이 저장소 | 비공개 DB와 문맥·정답 데이터 제외 |

Colab의 MNIST 학습은 별도 실습이며 Llama 모델을 학습한 실험이 아닙니다. 동봉 노트북은 실행 전 원본이고 실제 GPU 실행 화면은 증빙 폴더에 있습니다.
이전 300건 증빙 PDF는 evidence/previous_300_version/에 이전 버전 기록으로 보관했습니다. 숫자를 편집해 새 버전 결과로 바꾸지 않았습니다.

## 원본 보존

제공된 연구 프롬프트·라우터·채점기와 추론·SQL 실행 코드는 유지했습니다. config.json을 로컬 주소·모델에 맞췄으며, 2026-11-20 HTML 화면에서 모델 ID를 사람이 읽기 쉬운 `Llama 3.2 3B`로 표시하도록 수정했습니다. 실제 연결 모델 ID는 `mai-sma-llama3.2-8k:3b` 그대로입니다.
압축파일에 들어 있던 파생 pickle을 그대로 역직렬화하지 않고, 원본 DB로 같은 검색 색인을 다시 생성했습니다.
문서에 나온 전체 선대 기준 통계를 1,000건 표본 수치로 임의 변경하지 않았습니다.

## 3B 담당 전체 평가 결과

[평가 보고서 PDF](results/llama32_3b/Llama3.2_3B_평가보고서.pdf)와 [지표 요약](results/llama32_3b/3B_평가결과.md), [문항ID별 지표 CSV](results/llama32_3b/item_metrics.csv)를 추가했습니다. 질문·정답·응답 원문은 공개 파일에 포함하지 않았습니다.

재현: 비공개 평가 자료와 동일 config.json을 준비한 환경에서 `python -B tools/run_3b_benchmark.py`를 실행하고, 완료 후 `python -B tools/summarize_3b_metrics.py`로 공개 지표를 다시 집계할 수 있습니다. evaluation_3b/의 원문 파일은 공개하지 않습니다.
