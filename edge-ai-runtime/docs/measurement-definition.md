# 측정값의 의미와 제한

## Execute latency

Inference 실행 호출이 시작한 시점부터 반환한 시점까지의 시간입니다. 이미지 입력, 전처리, 후처리와 화면 표시를 모두 포함한 end-to-end latency가 아닙니다.

처음 10회의 성공한 실행은 warm-up으로 분리하고 이후 값으로 평균과 percentile을 계산했습니다. P95와 P99는 nearest-rank 방식을 사용했습니다.

## Inference FPS

Warm-up 이후 완료 이벤트 사이의 시간으로 계산했습니다. 카메라 입력 FPS나 화면 render FPS와 같은 값으로 해석하지 않습니다.

## CPU와 RSS

Process CPU 100%는 CPU core 하나를 모두 사용한 상태를 뜻합니다. 여러 core를 사용하는 process는 100%를 넘을 수 있습니다.

RSS는 process의 resident memory를 나타냅니다. 시작 직후 증가나 두 시점 차이만으로 memory leak을 판정하지 않습니다.

## Sequence gap

수신한 driver sequence의 건너뜀을 계산했습니다. 이는 관측 구간의 sequence 누락이며 실제 이미지 센서 frame drop과 같다고 가정하지 않습니다.

## Kernel message count

GPU fault와 page fault는 일치하는 로그 행의 개수입니다. 하나의 사건이 여러 행을 남길 수 있으므로 두 값을 더하거나 독립 사고 횟수로 해석하지 않습니다.

## Temperature

온도 파일에서 숫자를 읽고 `ok` 상태를 기록했다는 사실은 센서값의 정확성과 동시성을 보증하지 않습니다. 영역별 파일을 순서대로 읽으면 같은 순간의 snapshot이 아닐 수 있습니다.

같은 숫자가 과도하게 반복될 경우 냉각 성능의 증거로 사용하지 않고 센서 경로, 갱신 조건과 workload를 다시 확인합니다.
