import cv2
import threading
import time

class CameraStream:
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src, cv2.CAP_DSHOW)

        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.status = self.capture.isOpened()
        self.frame = None
        self.is_running = False

        self.thread = threading.Thread(target = self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        self.is_running = True
        while self.is_running:
            if self.capture.isOpened():
                self.capture.grab()

                success, frame = self.capture.retrieve()

                if success:
                    self.frame = frame
                else:
                    time.sleep(0.01)
    
    def get_frame(self):
        return self.frame
    
    def stop(self):
        self.is_running = False
        self.capture.release()

if __name__ == "__main__":
    print("Testing CameraStream...")
    
    cam = CameraStream(src=1) 
    
    time.sleep(1.0) 

    while True:
        frame = cam.get_frame()
        if frame is not None:
            cv2.imshow("Test Camera (Press q to exit)", frame)
        
        if cv2.waitKey(1) == ord('q'):
            break
    
    cam.stop()
    cv2.destroyAllWindows() 