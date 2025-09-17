import os
import threading
import time
from ..consumers.rtsp_consumer import RTSPConsumer
from .yolo import YoloPipeline
from .stt import STTPipeline
from .eye import EyePipeline

RTSP_URL = os.getenv('RTSP_URL', 'rtsp://localhost:8554/pi')


class PipelineManager:
    def __init__(self):
        self.consumer = RTSPConsumer(RTSP_URL)
        self.yolo = YoloPipeline()
        self.stt = STTPipeline()
        self.eye = EyePipeline()
        self._thread = None
        self._running = False
    
    def _loop(self):
        # RTSP 디코드된 프레임/오디오를 각 파이프라인에 전달
        for kind, payload in self.consumer.iter_frames():
            if not self._running:
                break
            if kind == 'video':
                frame_bgr = payload # np.ndarray (H,W,3)
                # 예: YOLO → Eye 순서로 처리 (필요시 병렬화)
                _ = self.yolo.process_frame(frame_bgr)
                _ = self.eye.process_frame(frame_bgr)
            elif kind == 'audio':
                pcm16, sample_rate = payload # bytes, int
                _ = self.stt.process_audio(pcm16, sample_rate)

    def start(self):
        if self._running:
            return
        self.consumer.start()
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()


    def stop(self):
        self._running = False
        self.consumer.stop()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)


    def status(self):
        return {
            'running': self._running,
            'rtsp': RTSP_URL,
            'consumer': self.consumer.status(),
            'pipelines': {
                'yolo': self.yolo.status(),
                'stt': self.stt.status(),
                'eye': self.eye.status(),
            }
        }


PIPELINE_MANAGER = PipelineManager()