import torch
import cv2
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

class DepthEngine:
    def __init__(self):
        print("Depth Model Loading (Depth Anything)")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.processor = AutoImageProcessor.from_pretrained("depth-anything/Depth-Anything-V2-Small-hf")
        self.model = AutoModelForDepthEstimation.from_pretrained("depth-anything/Depth-Anything-V2-Small-hf").to(self.device)
        print(f"Depth Model Loaded on {self.device.upper()}")

    def check_safety(self, frame):

        small_frame = cv2.resize(frame, (480, 360))
        '''
        gray_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        brightness = gray_frame.mean()

        if brightness < 30:
            print(f"Obstruction Detected! Brightness {brightness:.2f}")
            return True, np.zeros((360,480), dtype = np.uint8)
        '''
        rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_frame)

        inputs = self.processor(images = small_frame, return_tensors = "pt").to(self.device)

        

        with torch.no_grad():
            outputs = self.model(**inputs)
            predicted_depth = outputs.predicted_depth
        
        prediction = torch.nn.functional.interpolate(
            predicted_depth.unsqueeze(1),
            size = small_frame.shape[:2],
            mode = "bicubic",
            align_corners= False
        )
        
        depth_map = prediction.squeeze().cpu().numpy()

        # h,w = depth_map.shape

        # cy1, cy2 = int(h*0.35), int(h*0.65)
        # cx1, cx2 = int(w*0.35), int(w*0.65)

        # center_zone = depth_map[cy1:cy2, cx1:cx2]

        # avg_closeness = center_zone.mean()

        # #print(f"DISTANTA DETECTATA: {avg_closeness:.2f}")

        # is_danger = avg_closeness > 4.0

        return depth_map