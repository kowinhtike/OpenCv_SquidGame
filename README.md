# OpenCV Squid Game 🎮

A computer vision-based interactive game inspired by the popular "Squid Game." This project uses OpenCV, Pygame, and motion detection to replicate the "Red Light, Green Light" game.

## 🚀 Features
- **Green Light, Red Light Phases**: Detect player motion and eliminate them if they move during the red light.
- **Face Detection**: Highlights detected faces with a hologram-like effect.
- **Real-time Feedback**: Uses camera input to track movement and display the game state.
- **Audio Integration**: Background music and sound effects enhance the gaming experience.
- **Dynamic Overlays**: Displays doll images and bullet hole effects during gameplay.

## 🛠️ Tech Stack
- [Python](https://www.python.org/)
- [OpenCV](https://opencv.org/) for computer vision
- [Pygame](https://www.pygame.org/) for audio playback
- Camera input for real-time interaction

## 📂 Folder Structure
SquidGame/ ├── images/ │ ├── back.png # Doll back image │ ├── front.png # Doll front image │ ├── bullet_hole.png # Bullet hole overlay ├── audio/ │ ├── background.mp3 # Background music │ ├── gun.mp3 # Gunshot sound ├── main.py # Main game script ├── README.md # Project documentation


## 🔧 Prerequisites
1. Python 3.6 or higher
2. Libraries:
   - OpenCV
   - Pygame
3. A webcam connected to your system

Install dependencies using:
```bash
pip install opencv-python pygame
```
## Notes 📝
- **The game uses the default webcam for motion detection.
- **Ensure proper lighting and a stable camera position for better performance.
- **This code is optimized for Windows due to the winsound dependency.

