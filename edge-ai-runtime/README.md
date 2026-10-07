# Edge AI Runtime 검증

교육용 Edge AI 보드에서 AI pipeline의 실행 상태를 계측하고, 화면 출력 중 관측한 kernel 메시지와 온도값의 의미를 단계적으로 확인한 개인 검증 프로젝트입니다.

이 공개본에는 제가 작성한 분석 로직을 범용 입력 형식으로 다시 구성한 코드와 집계 결과만 포함합니다. 업체 SDK 소스, 매뉴얼, 바이너리, 수정 patch와 원본 시스템 로그는 포함하지 않습니다.

## 검증 질문

- 기준 실행에서 inference latency, FPS, CPU와 메모리는 어느 수준인가?
- 화면이 정상으로 보일 때도 kernel log에 오류가 남는가?
- rendering 요소를 나눠 실행하면 GPU 오류가 특정 경로에서 더 잘 재현되는가?
- 온도 인터페이스가 숫자를 반환한다는 사실만으로 그 값을 신뢰할 수 있는가?

## 제가 한 일

- inference 이벤트와 프로세스 자원 사용량을 수집하는 측정 절차 구성
- warm-up 제외, 평균과 P99, 완료 간격 FPS, sequence gap 분석
- 실행 전후 kernel log를 비교해 신규 오류 메시지 집계
- rendering 조건을 나눈 반복 시험과 결과 비교
- 영역별 온도 수집과 고정값 여부 분석
- 측정값의 의미와 판정 한계를 문서화

## 교육 환경에서 제공된 것

- Edge AI 평가 보드와 카메라 실행 환경
- NPU runtime, AI 모델과 예제 application
- GPU, camera, PVT driver와 SDK toolchain
- application을 수정하고 실보드에서 실행할 수 있는 개발 환경

제공된 소스와 실행 파일은 공개 저장소에 포함하지 않습니다.

## 공개 자료

```text
src/summarize_runtime.py             이벤트 기반 latency와 FPS 분석
src/summarize_kernel_messages.py     kernel 오류 메시지 집계
src/summarize_temperature.py         영역별 온도와 고정값 비율 분석
tests/                               공개 분석기의 단위 테스트
examples/                            익명화한 소형 입력 예제
evidence/                            원본 로그에서 추출한 집계 결과
docs/case-study.md                   실험 과정과 해석
docs/measurement-definition.md       측정값의 의미와 제한
```

## 실행

Python 3.10 이상과 표준 라이브러리만 사용합니다.

```bash
python edge-ai-runtime/src/summarize_runtime.py edge-ai-runtime/examples/sample_events.jsonl --warmup 1
python edge-ai-runtime/src/summarize_kernel_messages.py edge-ai-runtime/examples/sample_kernel_messages.txt
python edge-ai-runtime/src/summarize_temperature.py edge-ai-runtime/examples/sample_temperature.csv
python -m unittest discover -s edge-ai-runtime/tests -v
```

## 핵심 결과

- 120초 기준 실행에서 3577회 inference 완료와 약 30 FPS를 관측했습니다.
- warm-up 10회를 제외한 execute 평균은 3.074 ms, P99는 3.306 ms였습니다.
- application은 정상 종료했지만 신규 GPU fault와 page fault 메시지가 남았습니다.
- 짧은 조건 분리 시험에서는 texture와 box만 그릴 때 오류가 재현되지 않았고 text rendering이 포함된 조건에서 다시 나타났습니다.
- vertex buffer 변경 후보로도 오류가 재현되어 단일 원인 가설을 확정하지 않았습니다.
- pipeline 동시 온도 수집에서는 동일 값이 과도하게 반복되어 센서값 유효성을 판정하지 않았습니다.

이 결과는 제한된 교육용 보드와 시험 조건에서 수행한 개인 실험입니다. 특정 업체나 제품 전체에 대한 성능, 안정성 또는 결함 판정이 아닙니다.
