import numpy as np

FRAME_REDUCTION = 4


class Camera:
    camera_module = None
    video_capture = None
    frame = None
    small_frame = None

    def __init__(self):
        pass

    def capture(self):
        pass

    def get_frame(self):
        return self.frame

    def get_small_frame(self):
        return self.small_frame

    def add_face_frame(self, top, right, bottom, left, name):
        pass

    def display_face_frames(self):
        pass

    def release(self):
        pass


class MacCamera(Camera):
    def __init__(self):
        Camera.__init__(self)

        import cv2
        self.camera_module = cv2

        self.video_capture = self.camera_module.VideoCapture(0)

    def capture(self):
        ret, frame = self.video_capture.read()
        self.frame = frame
        # Resize frame of video to 1/4 size for faster face recognition processing
        self.small_frame = self.camera_module.resize(self.frame, (0, 0), fx=1.0 / FRAME_REDUCTION,
                                                     fy=1.0 / FRAME_REDUCTION)

    def add_face_frame(self, top, right, bottom, left, name):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= FRAME_REDUCTION
        right *= FRAME_REDUCTION
        bottom *= FRAME_REDUCTION
        left *= FRAME_REDUCTION

        # Draw a box around the face
        self.camera_module.rectangle(self.frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        self.camera_module.rectangle(self.frame, (left, bottom - 35), (right, bottom), (0, 0, 255),
                                     self.camera_module.FILLED)
        font = self.camera_module.FONT_HERSHEY_DUPLEX
        self.camera_module.putText(self.frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    def display_face_frames(self):
        # Display the resulting image
        self.camera_module.imshow('Video', self.frame)

    def release(self):
        self.video_capture.release()
        self.camera_module.destroyAllWindows()


class PiCamera(Camera):
    def __init__(self):
        Camera.__init__(self)

        import picamera
        self.camera_module = picamera

        video_capture = self.camera_module.PiCamera()
        video_capture.resolution = (320, 240)
        self.frame = np.empty((240, 320, 3), dtype=np.uint8)

    def capture(self):
        self.camera_module.capture(self.frame, format="rgb")
