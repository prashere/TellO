# import cv2

# # Open the default camera (0 is usually your built-in webcam)
# cap = cv2.VideoCapture(1)

# if not cap.isOpened():
#     print("Cannot open camera")
#     exit()

# while True:
#     # Read a frame from the webcam
#     ret, frame = cap.read()

#     # If frame is not read correctly, break the loop
#     if not ret:
#         print("Can't receive frame. Exiting ...")
#         break
#     flipped_frame = cv2.flip(frame, 1)
    
#     # Display the frame in a window named 'Live Video'
#     cv2.imshow('Live Video', flipped_frame)

#     # Press 'q' to break the loop and close the window
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break



# # Release the camera and close all OpenCV windows
# cap.release()
# cv2.destroyAllWindows()

from importlib.metadata import version
print(version("flet"))
