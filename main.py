import cv2
import time
import threading
import numpy as np
import traceback

from camera_stream import CameraStream
from vision_depth import DepthEngine
from vision_context import ContextEngine
from audio_manager import AudioEngine

def main():
    print("DEBUG: 1. Starting Audio...", flush=True)
    audio = AudioEngine()
    audio.speak("System Initializing")

    print("DEBUG: 2. Starting Depth Engine...", flush=True)
    depth_ai = DepthEngine()
    
    print("DEBUG: 3. Starting Context Engine (Florence-2)...", flush=True)
    context_ai = ContextEngine()
    
    print("DEBUG: 4. Starting Camera...", flush=True)
    cam = CameraStream(src=1) 
    time.sleep(2.0)
    print("DEBUG: 5. Camera Active!", flush=True)

    print("--- SYSTEM ACTIVE --- (Press Q to Exit)")
    audio.speak("Guide Dog Mode Active")

    
    last_beep_time = 0
    beep_interval = 1.0 
    
    frame_count = 0
    PROCESS_EVERY_N_FRAMES = 3 
    
    
    last_danger_score = 0.0
    SMOOTHING_ALPHA = 0.5 

    
    last_description_time = 0
    DESCRIPTION_INTERVAL = 5.0 
    last_spoken_text = ""
    is_describing_now = False 

    
    display_depth_map = None
    display_desc = "Listening..."

    while True:
        frame = cam.get_frame()
        if frame is None: 
            time.sleep(0.01)
            continue

        frame_count += 1
        
        
        current_time = time.time()

     
        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            try:
                
                depth_map = depth_ai.check_safety(frame)
                
                
                h, w = depth_map.shape
                center_zone = depth_map[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
                raw_score = center_zone.mean()
                
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
          
                if gray.mean() < 15:
                    raw_score = 50.0 


                last_danger_score = (SMOOTHING_ALPHA * raw_score) + ((1 - SMOOTHING_ALPHA) * last_danger_score)
                display_depth_map = depth_map

            except Exception as e:
                print(f"Depth Error: {e}")


        if (current_time - last_description_time > DESCRIPTION_INTERVAL) and \
           (last_danger_score < 15.0) and \
           (not is_describing_now):
            
            def run_description_thread(target_frame):
                nonlocal last_description_time, last_spoken_text, is_describing_now, display_desc
                is_describing_now = True
                try:
          
                    raw_result = context_ai.describe(target_frame)
                    
                    height, width, _ = target_frame.shape
                    clean_text = context_ai.format_results(raw_result, width)
                    
                    if clean_text:
                        if clean_text != last_spoken_text:
                            print(f"Narrator: {clean_text}")
                            audio.speak(clean_text)
                            last_spoken_text = clean_text
                            display_desc = clean_text
                    
                except Exception as e:
                    print(f"Context Thread Error:{e}")
                    traceback.print_exc()
                finally:
                    last_description_time = time.time()
                    is_describing_now = False

          
            threading.Thread(target=run_description_thread, args=(frame.copy(),)).start()
            last_description_time = time.time() 

        if last_danger_score > 4.0:
            calc_score = min(last_danger_score, 20.0)
            factor = (calc_score - 4.0) / 16.0
            beep_interval = max(0.05, 1.0 - (factor * 0.95))

            if current_time - last_beep_time > beep_interval:
                audio.play_sonar_beep()
                last_beep_time = current_time
                cv2.circle(frame, (50, 50), 30, (0, 0, 255), -1) 
        

        status_color = (0, 255, 0)
        status_text = "SAFE"
        if last_danger_score > 15: 
            status_color = (0, 0, 255)
            status_text = "CRITICAL"
        elif last_danger_score > 4: 
            status_color = (0, 255, 255)
            status_text = "WARNING"

        cv2.putText(frame, f"STATUS: {status_text}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
        cv2.putText(frame, f"PROXIMITY: {last_danger_score:.1f}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (128,128,128), 1)
        cv2.putText(frame, f"AI SEES: {display_desc}", (20, 440), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 255), 1)
        
        cv2.imshow("BlindAid - Vision", frame)

        if display_depth_map is not None:
            depth_viz = cv2.normalize(display_depth_map, None, 0, 255, cv2.NORM_MINMAX, dtype = cv2.CV_8U)
            depth_viz = cv2.applyColorMap(depth_viz, cv2.COLORMAP_MAGMA)
            cv2.imshow("BlindAid - Radar", depth_viz)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cam.stop()
    audio.stop_all()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()