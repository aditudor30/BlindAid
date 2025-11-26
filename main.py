import cv2
import time
import winsound

from camera_stream import CameraStream
from vision_depth import DepthEngine
from audio_manager import AudioEngine

def main():
    print("DEBUG: 1. Starting Audio...", flush=True)
    audio = AudioEngine()
    audio.speak("System Initializing")

    print("DEBUG: 2. Starting Depth Engine...", flush=True)
    depth_ai = DepthEngine()
    print("DEBUG: 3. Depth Engine Loaded!", flush=True)


    print("Turning on the Camera...")

    cam = CameraStream(src=1)
    time.sleep(2.0)
    print("DEBUG: 5. Camera Active!", flush=True)

    print("Active System, Press Q to Exit")
    audio.speak("System Ready")

    last_beep_time = 0
    beep_interval = 1.0

    frame_count = 0
    PROCESS_EVERY_N_FRAMES = 3

    last_depth_map = None
    last_danger_score = 0.0

    SMOOTHING_ALPHA = 0.5

    display_depth_map = None

    #counter = 0
    while True:
        frame = cam.get_frame()

        if frame is None:
            #print(".", end = "", flush = True)
            time.sleep(0.1)
            continue

        frame_count += 1

        if frame_count % PROCESS_EVERY_N_FRAMES == 0:
            try:
                depth_map = depth_ai.check_safety(frame)

                h,w =depth_map.shape
                center_zone = depth_map[int(h*0.3):int(h*0.7), int(w*0.3):int(w*0.7)]
                raw_score = center_zone.mean()

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = gray.mean()

                if brightness < 15 :
                     print(f"DEBUG: Obstruction! Brightness:{brightness:.1f}")
                     raw_score = 50.0

                last_danger_score = (SMOOTHING_ALPHA * raw_score) + ((1-SMOOTHING_ALPHA) * last_danger_score)
                display_depth_map = depth_map

            except Exception as e:
                 print(f"Error on AI: {e}")

        if last_danger_score > 4.0:
             calc_score = min(last_danger_score, 20.0)
             factor = (calc_score - 4.0)/16.0
             
             
             beep_interval = 1.0 - (factor * 0.95)
             beep_interval = max(0.05, beep_interval)
             current_time = time.time()

             if current_time - last_beep_time > beep_interval:
                 audio.play_sonar_beep()
                 last_beep_time = current_time

                 cv2.circle(frame, (50,50), 30, (0,0,255), -1)
        
        status_color = (0,255,0)
        status_text = "SAFE"

        if last_danger_score > 16:
             status_color = (0,0,255)
             status_text = "DANGER"
        elif last_danger_score > 4:
             status_color = (0,255,255)
             status_text = "WARNING"


        cv2.putText(frame, f"STATUS: {status_text}", (20, 400),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
        cv2.putText(frame, f"Proximity: {last_danger_score:.1f},", (20,450),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        
        cv2.imshow("BlindAid - Vision", frame)

        if display_depth_map is not None and display_depth_map.max() > 0:
             depth_viz = cv2.normalize(display_depth_map, None, 0, 255, cv2.NORM_MINMAX, dtype = cv2.CV_8U)
             depth_viz = cv2.applyColorMap(depth_viz, cv2.COLORMAP_MAGMA)
             cv2.imshow("BlindAid - Radar", depth_viz)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cam.stop()
    cv2.destroyAllWindows()

                  
            

'''
        try:
            

            is_danger, depth_map = depth_ai.check_safety(frame)

            if is_danger:
                cv2.putText(frame, "STOP!", (50,100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                winsound.Beep(1000, 100)
            else:
                cv2.putText(frame, "All good!", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
            
            cv2.imshow("BlindAid - Vision", frame)
            depth_viz = cv2.normalize(depth_map, None, 0, 255, cv2.NORM_MINMAX, dtype = cv2.CV_8U)
            depth_viz = cv2.applyColorMap(depth_viz, cv2.COLORMAP_MAGMA)
            cv2.imshow("BlindAid - Depth", depth_viz)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"\nEroare in bucla: {e}")
'''
        
if __name__ == "__main__":
            main()