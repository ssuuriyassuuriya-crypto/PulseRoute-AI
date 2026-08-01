"""
PulseRoute AI - Synthetic Demo Video Generator
Generates synthetic 4-way intersection traffic footage for offline demo & testing.
"""
import os
import math
import random

def generate_demo_video(output_path: str = "uploads/demo_traffic.mp4", duration_sec: int = 10, fps: int = 15):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        import cv2
        import numpy as np
        
        width, height = 640, 480
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        total_frames = duration_sec * fps
        
        for frame_idx in range(total_frames):
            # Create dark road background
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            frame[:] = (30, 35, 40)
            
            # Draw gray asphalt roads (Intersection)
            cv2.rectangle(frame, (260, 0), (380, height), (70, 75, 80), -1) # N-S road
            cv2.rectangle(frame, (0, 180), (width, 300), (70, 75, 80), -1)  # E-W road
            
            # Yellow center lines
            cv2.line(frame, (320, 0), (320, 180), (0, 215, 255), 2)
            cv2.line(frame, (320, 300), (320, height), (0, 215, 255), 2)
            cv2.line(frame, (0, 240), (260, 240), (0, 215, 255), 2)
            cv2.line(frame, (380, 240), (width, 240), (0, 215, 255), 2)
            
            # Animated moving cars
            t = frame_idx / fps
            
            # Vehicles in North lane moving South
            for i in range(4):
                y = int((t * 80 + i * 45) % 180)
                cv2.rectangle(frame, (280, y), (305, y + 25), (200, 50, 50), -1) # Red Car
            
            # Vehicles in South lane moving North
            for i in range(3):
                y = int(height - ((t * 70 + i * 50) % 180))
                cv2.rectangle(frame, (335, y - 25), (360, y), (50, 150, 220), -1) # Blue Car
                
            # Vehicles in East lane moving West
            for i in range(6):
                x = int(width - ((t * 90 + i * 40) % 260))
                cv2.rectangle(frame, (x - 25, 255), (x, 280), (50, 200, 100), -1) # Green Car
                
            # Vehicles in West lane moving East
            for i in range(2):
                x = int((t * 60 + i * 60) % 260)
                cv2.rectangle(frame, (x, 200), (x + 25, 225), (220, 200, 50), -1) # Yellow Car
            
            # Draw HUD overlay
            cv2.putText(frame, "PulseRoute AI - Live Intersection Tracking", (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Frame: {frame_idx}/{total_frames}", (15, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 200), 1)
            
            out.write(frame)
            
        out.release()
        print(f"Synthetic demo video created successfully at {output_path}")
        return True
    except Exception as e:
        print(f"OpenCV not available yet or error creating video: {e}")
        # Create a blank fallback file marker
        with open(output_path, "wb") as f:
            f.write(b"DEMO_VIDEO_DUMMY_DATA")
        return False

if __name__ == "__main__":
    generate_demo_video()
