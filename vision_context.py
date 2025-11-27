import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image
import cv2
import threading

class ContextEngine:
    def __init__(self):
        print("Loading Context Model (Florence-2)...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Florence-2-base",
            torch_dtype = self.torch_dtype,
            trust_remote_code = True,
            attn_implementation = "eager"
        ).to(self.device)

        self.processor = AutoProcessor.from_pretrained(
            "microsoft/Florence-2-base",
            trust_remote_code = True
        )
        print(f"Context Model Loaded on {self.device.upper()}")

    def describe(self, frame):

        if frame is None or frame.size == 0:
            print("Context Error: Empty frame!")
            return {}
    
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(rgb_frame)

        prompt = "<DENSE_REGION_CAPTION>"

        inputs = self.processor(text = prompt, images = image_pil, return_tensors = "pt").to(self.device, self.torch_dtype)

        generated_ids = self.model.generate(
            input_ids = inputs["input_ids"],
            pixel_values = inputs["pixel_values"],
            max_new_tokens = 1024,
            num_beams = 1,
            do_sample = False,
            use_cache = False
        )

        

        try:
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens = False)[0]

            parsed_result = self.processor.post_process_generation(
                generated_text,
                task=prompt,
                image_size = (image_pil.width, image_pil.height)
            )

            return parsed_result[prompt]
        
        except AttributeError:
            print("Warning: Using legacy post-processing...")
            target_sizes = [image_pil.size[::-1]]
            parsed_result = self.processor.post_process_generated_outputs(
                generated_ids, 
                skip_special_tokens=False, 
                target_sizes=target_sizes
            )[0]
            return parsed_result[prompt]
        
        except Exception as e:
            print (f"Post-Processing Error on Florence: {e}")
            return {}
    
    def format_results(self, result, frame_width):
        bboxes = result.get('bboxes', [])
        labels = result.get('labels', [])

        if not labels:
            return None

        largest_area = 0
        main_label = ""
        location = ""

        for box, label in zip(bboxes, labels):
            x1, y1, x2, y2 = box
            area = (x2-x1) * (y2-y1)

            if area > largest_area:
                largest_area = area
                main_label = label

                center_x = (x1 + x2) / 2
                if center_x < frame_width * 0.35:
                    location = "on your left"
                elif center_x > frame_width * 0.65:
                    location = "on your right"
                else:
                    location = "in front of you"
        if main_label:
            return f"{main_label} is {location}"
        return None