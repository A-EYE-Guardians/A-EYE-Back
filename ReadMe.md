## 구조
/consumers/rtsp_consumer.py  : rtsp에서 프레임을 읽어서 공유버퍼에 최신 프레임 저장

/pipelines/eye.py: 아이트래킹 파이프라인
/pipelines/stt.py: stt 파이프라인
/pipelines/yolo.py: yolo 파이프라인
/pipelines/registry.py: 모델 주입 지점, env에서 경로 읽어서 load

/web/index.html: 간단 영상 페이지

main.py: FastAPI 엔트리, 라우터에서 pipelines 호출
docker-compose.yml, Dockerfile: 배포/실행
mediamtx.yml: RTSP 서버 설정

## 파이 실행
보드에 전원 연결 후 일정 시간 대기

powershell 열기

입력:
보드1: ssh raspberrypi@192.168.162.44 
보드2: ssh raspberrypi@192.168.162.68

비밀번호: 1357924680

nano ~/stream_gst_b.sh

##### 그 안에
#!/usr/bin/env bash
set -euo pipefail
export PULSE_LATENCY_MSEC=10
export PIPEWIRE_LATENCY="128/48000"

SERVER_IP="192.168.162.36"
RTSP_URL="rtsp://${SERVER_IP}:8554/pi"

# 필요하면 W,H를 1280x720으로 올려도 됨 (영상만 OK 확인 후)
W=960; H=540; FPS=30
INTRA=$FPS

AIN_CH=1; AIN_SR=16000    # 오디오는 16kHz/mono로 매우 얇게
AABR=48k                  # AAC 48kbps

pkill -9 arecord ffmpeg libcamera-vid 2>/dev/null || true

libcamera-vid --width $W --height $H --framerate $FPS \
  --codec h264 --profile baseline --inline --intra $INTRA \
  --timeout 0 -o - | \
ffmpeg -hide_banner -loglevel warning \
  -fflags nobuffer -flags low_delay -use_wallclock_as_timestamps 1 \
  -avioflags direct -flush_packets 1 \
  -probesize 1M -analyzeduration 0.5 \
  -thread_queue_size 4 -f h264 -r $FPS -i - \
  -thread_queue_size 4 -f pulse -i default \
  -af "aresample=async=1:first_pts=0" -ac $AIN_CH -ar $AIN_SR \
  -map 0:v:0 -map 1:a:0 \
  -c:v copy -fps_mode passthrough \
  -c:a aac -b:a $AABR -ac $AIN_CH -ar $AIN_SR \
  -muxdelay 0 -muxpreload 0 \
  -f rtsp -rtsp_transport tcp "$RTSP_URL"

Ctrl+O 로 저장 후 엔터
Ctrl+X 로 나가기

chmod +x ~/stream_gst_b.sh
~/stream_gst_b.sh

브라우저에 http:// 내 IP :8000/web  으로 접속

## 흐름
### 1.카메라 입력

Pi에서 RTSP로 밀거나(메디아MTX 사용) / HTTP로 푸시.

consumers/rtsp_consumer.py가 RTSP 스트림을 구독해 **공유버퍼(메모리)**에 {camera_id, role(scene/eye) -> frame} 최신 프레임을 저장.

### 2.API 호출

/yolo/detect 호출 → pipelines/yolo.py → registry.detector().predict(frame)

/stt/transcribe 호출 → pipelines/stt.py → registry.stt().transcribe_wav(wav)

/gaze/calibrate & /gaze/estimate → pipelines/eye.py → registry.gaze().calibrate/estimate(...)

### 3.플러그인 바꿔끼우기

모델 교체는 코드가 아니라 경로 문자열(Import Path)만 교체: env나 yaml로 지정 → registry.py가 importlib로 로드.

## 모델 끼우기
pipelines에 각 모델 넣기

## registry.py (주입 지점) — 어떻게 읽고, 어떻게 로딩하나

환경변수 또는 config에서 아래 세 값을 읽어 importlib로 클래스를 로드:

DETECTOR_IMPL (예: app.pipelines.plugins.yolo.ultra.UltraYolo)

STT_IMPL (예: app.pipelines.plugins.stt.whisper.WhisperTiny)

GAZE_IMPL (예: app.pipelines.plugins.eye.mediapipe.MediaPipeGaze)

(선택) 가중치 경로나 하이퍼파라미터는 DETECTOR_WEIGHTS, STT_MODEL_SIZE 같은 추가 env로 넘기면 좋음.