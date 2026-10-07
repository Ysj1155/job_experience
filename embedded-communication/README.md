# 3보드 통신 검증

교육용 3보드 환경에서 heartbeat 장애와 운전자 개입 이벤트가 상태 변화에 어떻게 반영되는지 확인한 개인 검증 프로젝트입니다.

이 공개본은 당시 실험에서 제가 작성한 검증 로직을 플랫폼 독립적인 예제로 다시 구성한 것입니다. 업체 제공 IPC 예제, 라이브러리, 펌웨어 원본과 장치별 패킷 형식은 포함하지 않습니다.

## 검증 질문

- 일정 시간 동안 heartbeat가 들어오지 않으면 정상 상태에서 안전 상태로 바뀌는가?
- heartbeat가 다시 들어왔을 때 선택한 복귀 정책대로 상태를 유지하는가?
- 운전자 개입 이벤트가 한 번의 상태 변화만 발생시키는가?
- 같은 이벤트가 반복되어도 추가 상태 변화가 발생하지 않는가?
- 기능 경로 확인과 물리 버스 확인을 구분해 판정했는가?

## 제가 한 일

- heartbeat 송신기와 수신 검증 도구 작성
- `INIT`, `AUTO`, `SAFE`, `DRIVER` 상태 모델 작성
- timeout과 수동 복귀 조건을 포함한 시험 시나리오 구성
- 반복 이벤트를 별도로 기록하고 추가 상태 변화를 막는 로직 작성
- JSONL/CSV evidence 구조와 단위 테스트 작성
- 실제 확인 범위와 미확인 범위를 분리해 결과 정리

## 교육 환경에서 제공된 것

- 3보드 하드웨어와 보드별 실행 환경
- 보드 간 IPC/CAN 통신 기반 코드
- 장치 드라이버와 예제 인터페이스
- 스위치 입력과 보드 통신을 시험할 수 있는 기본 펌웨어

제공된 코드와 인터페이스는 공개 저장소에 포함하지 않습니다.

## 공개 예제

```text
src/validation_state_machine.py      플랫폼 독립적인 상태 전이 모델
src/heartbeat_sender.py              localhost에서 실행 가능한 heartbeat 송신기
examples/run_scenario.py             대표 상태 전이 재현
tests/test_validation_state_machine.py
evidence/heartbeat_trials.csv        익명화한 반복 시험 결과
evidence/functional_results.csv      기능 판정과 물리계층 범위 구분
docs/case-study.md                    실험 과정과 해석
```

## 실행

Python 3.10 이상과 표준 라이브러리만 사용합니다.

```bash
python embedded-communication/examples/run_scenario.py
python -m unittest discover -s embedded-communication/tests -v
```

## 판정 범위

실험에서는 이벤트가 수신 애플리케이션까지 전달되고 의도한 상태 변화가 발생하는 기능 경로를 확인했습니다. 별도 계측 장비가 필요한 물리 버스 파형, ACK와 자동 재전송 동작은 확인하지 않았습니다.

`SAFE` 상태에서 heartbeat 복구 후에도 수동 reset을 요구하는 동작은 당시 검증 도구에 선택한 시험 정책입니다. 특정 제품의 공식 안전 요구사항을 의미하지 않습니다.
