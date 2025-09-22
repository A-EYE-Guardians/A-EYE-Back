## 구조
/consumers/rtsp_consumer.py  : (1) 백그라운드에서 RTSP를 안정적으로 디코드하고, (2) 최신성을 보장하는 큐 정책으로 지연을 억제하며, (3) 외부에는 깔끔한 제너레이터 인터페이스

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

sudo apt update
sudo apt install -y ffmpeg rpicam--apps

mkdir -p ~/streaming && cd ~/streaming
nano video_cam1.sh


#### 파이 코드
set -euo pipefail

SERVER_IP="192.168.162.36"
RTSP_URL="rtsp://${SERVER_IP}:8554/pi1"   # 고유 경로

W=960; H=540; FPS=30; INTRA=$FPS

pkill -9 rpicam-vid ffmpeg 2>/dev/null || true

rpicam-vid --width $W --height $H --framerate $FPS \
  --codec h264 --profile baseline --inline --intra $INTRA \
  --timeout 0 -o - | \
ffmpeg -hide_banner -loglevel warning \
  -fflags nobuffer -flags low_delay -use_wallclock_as_timestamps 1 \
  -avioflags direct -flush_packets 1 \
  -probesize 1M -analyzeduration 0.5 \
  -thread_queue_size 32 -f h264 -r $FPS -i - \
  -map 0:v:0 -c:v copy -fps_mode passthrough \
  -muxdelay 0 -muxpreload 0 \
  -f rtsp -rtsp_transport tcp "$RTSP_URL"


Ctrl+O 로 저장 후 엔터
Ctrl+X 로 나가기

 chmod +x video_cam1.sh
./video_cam1.sh

#### 다른 powershell에
 mkdir -p ~/streaming && cd ~/streaming
nano video_cam2.sh

#### 파이 코드
set -euo pipefail

SERVER_IP="192.168.162.36"
RTSP_URL="rtsp://${SERVER_IP}:8554/pi2"   # 고유 경로

W=960; H=540; FPS=30; INTRA=$FPS

pkill -9 rpicam-vid ffmpeg 2>/dev/null || true

rpicam-vid --width $W --height $H --framerate $FPS \
  --codec h264 --profile baseline --inline --intra $INTRA \
  --timeout 0 -o - | \
ffmpeg -hide_banner -loglevel warning \
  -fflags nobuffer -flags low_delay -use_wallclock_as_timestamps 1 \
  -avioflags direct -flush_packets 1 \
  -probesize 1M -analyzeduration 0.5 \
  -thread_queue_size 32 -f h264 -r $FPS -i - \
  -map 0:v:0 -c:v copy -fps_mode passthrough \
  -muxdelay 0 -muxpreload 0 \
  -f rtsp -rtsp_transport tcp "$RTSP_URL"

 저장 후 엔터
 나가기

 chmod +x video_cam2.sh
./video_cam2.sh

브라우저에 http:// 내 IP :8000/web  으로 접속

