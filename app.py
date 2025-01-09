import cv2
import winsound
import time
import pygame

GREEN_LIGHT_DURATION = 5
RED_LIGHT_DURATION = 5
MIN_CONTOUR_AREA = 3000
BORDER_THICKNESS = 15
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 750

class SquidGame:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        self.eliminated = False
        self.doll_location = (0, 50)
        self.load_resources()
        self.play_background_music('audio/background.mp3')
        # Set up the fullscreen window
        # cv2.namedWindow("Game", cv2.WND_PROP_FULLSCREEN)
        # cv2.setWindowProperty("Game", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        cv2.namedWindow("Game", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Game", WINDOW_WIDTH, WINDOW_HEIGHT)

    def load_resources(self):
        self.bullet_hole_png = self.prepare_image("images/bullet_hole.png", 0.3)
        self.front_doll_png = self.prepare_image("images/front.png", 0.5)
        self.back_doll_png = self.prepare_image("images/back.png", 0.5)

    def prepare_image(self, file_name, scale_factor):
        image = cv2.imread(file_name, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise FileNotFoundError(f"Image file {file_name} not found.")
        new_width = int(image.shape[1] * scale_factor)
        new_height = int(image.shape[0] * scale_factor)
        # Check if new dimensions are valid
        if new_width <= 0 or new_height <= 0:
            raise ValueError(f"Scaled image dimensions are invalid: {new_width}x{new_height} for {file_name}")
        return cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return  image

    def overlay_image_alpha(self, background, overlay, x, y):
        overlay_h, overlay_w = overlay.shape[:2]
        if x + overlay_w > background.shape[1] or y + overlay_h > background.shape[0]:
            return background
        roi = background[y:y + overlay_h, x:x + overlay_w]
        overlay_bgr = overlay[:, :, :3]
        overlay_alpha = overlay[:, :, 3] / 255.0
        for c in range(3):
            roi[:, :, c] = (overlay_alpha * overlay_bgr[:, :, c] + (1 - overlay_alpha) * roi[:, :, c])
        background[y:y + overlay_h, x:x + overlay_w] = roi
        return background

    def play_background_music(self, file_path):
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play(-1)

    def play_mp3(self, file_path):
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)

    def run_game(self):
        while self.cam.isOpened():
            self.green_light_phase()
            self.red_light_phase()
            if self.eliminated:
                break
        self.cleanup()

    def green_light_phase(self):
        start_time = time.time()
        while time.time() - start_time < GREEN_LIGHT_DURATION:
            ret, frame = self.cam.read()
            if not ret:
                print("Error accessing the camera!")
                break
            frame = self.overlay_image_alpha(frame, self.back_doll_png, *self.doll_location)
            # Draw green border
            cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 255, 0), BORDER_THICKNESS)
            cv2.imshow("Game", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def red_light_phase(self):
        start_time = time.time()
        while time.time() - start_time < RED_LIGHT_DURATION and not self.eliminated:
            ret1, frame1 = self.cam.read()
            ret2, frame2 = self.cam.read()
            if not ret1 or not ret2:
                print("Error accessing the camera!")
                break
            diff = cv2.absdiff(frame1, frame2)
            gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(thresh, None, iterations=3)
            contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(frame1, contours, -1, (0, 0, 255), 2)
            for c in contours:
                if cv2.contourArea(c) < MIN_CONTOUR_AREA:
                    continue
                x, y, w, h = cv2.boundingRect(c)
                center_x = x + w // 2
                center_y = y + h // 2
                overlay_x = center_x - self.bullet_hole_png.shape[1] // 2
                overlay_y = center_y - self.bullet_hole_png.shape[0] // 2
                frame1 = self.overlay_image_alpha(frame1, self.bullet_hole_png, overlay_x, overlay_y)
                cv2.putText(frame1, "You died!", (200, 450), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
                # this code only works on Window
                winsound.Beep(1000, 200)
                self.eliminated = True

            self.detect_faces(frame1)
            # insert doll photo as latest because opencv can detect doll face
            frame1 = self.overlay_image_alpha(frame1, self.front_doll_png, *self.doll_location)
            # Draw red border
            cv2.rectangle(frame1, (0, 0), (frame1.shape[1], frame1.shape[0]), (0, 0, 255), BORDER_THICKNESS)
            cv2.imshow("Game", frame1)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        if self.eliminated:
            self.play_mp3('audio/gun.mp3')
            time.sleep(2)

    def detect_faces(self, frame):
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        for (x, y, w, h) in faces:
            center_x = x + w // 2
            center_y = y + h // 2
            # Draw a hologram-like circle
            radius = max(w, h) // 2  # Radius proportional to face size
            thickness = 2  # Circle thickness
            for i in range(1, 6):  # Create a glowing effect with concentric circles
                alpha = i * 50  # Increasing transparency (brighter as it gets closer to the center)
                color = (0, alpha, 255)  # Blue-ish hologram effect
                cv2.circle(frame, (center_x, center_y), radius + i * 15, color, thickness)


    def cleanup(self):
        self.cam.release()
        cv2.destroyAllWindows()
        pygame.mixer.music.stop()

if __name__ == "__main__":
    game = SquidGame()
    game.run_game()
