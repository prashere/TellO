import cv2
from detector_model.head_gaze_emotion_detector import VideoProcessor

# Path to your dlib's shape_predictor_68_face_landmarks.dat file
predictor_path = "detector_model/assets/shape_predictor_68_face_landmarks.dat"

# Initialize Video Processor
video_processor = VideoProcessor(predictor_path)

try:
    while True:
        frame = video_processor.process_frame()
        frame = cv2.flip(frame, 1)  # Flip for mirror effect
        if frame is None:
            break

        state = video_processor.get_latest_state()

        # Draw bounding boxes and head pose
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = video_processor.face_analyzer.detect_faces(gray)

        for face in faces:
            x1, y1 = face.left(), face.top()
            x2, y2 = face.right(), face.bottom()

            # Draw yellow rectangle around face
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

            # Prepare head pose text (horizontal movement)
            head_pose_text = state['horizontal'] if state['horizontal'] else "Unknown"

            # Put head pose direction above the rectangle
            cv2.putText(frame, head_pose_text, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        # Show the frame
        cv2.imshow("Face, Head Pose Detection", frame)

        # Exit on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    video_processor.release()
