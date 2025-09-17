class YoloPipeline:
    def __init__(self):
        self._loaded = False
        # TODO: 모델 파일 경로/가중치 지정
        # ex) from ultralytics import YOLO; self.model = YOLO("yolov8n.pt")


    def process_frame(self, bgr):
        if not self._loaded:
            self._load()
            # TODO: 추론/박스 드로잉 등
        return None


    def _load(self):
        # TODO: 실제 모델 로딩
        self._loaded = True


    def status(self):
        return {"loaded": self._loaded}