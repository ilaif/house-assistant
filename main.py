import json

import face_recognition

from libs import utils, speech
from libs.Camera import MacCamera, PiCamera
from libs.StoppableThread import StoppableThread
from modules import speech_module
import time

utils.change_cwd_to_file_directory(__file__)
CONFIG_PATH = "config.json"
with open(CONFIG_PATH, 'r') as f:
    conf = json.load(f)
log = utils.get_logger(__name__)
last_time = time.time()


def load_profiles():
    with open(conf["profiles_list"], 'r') as f:
        loaded_profiles = json.load(f)
        for i, profile in enumerate(loaded_profiles):
            loaded_profiles[i]['img_path'] = conf["profile_images_path"] + profile['id'] + conf["image_extension"]
        return loaded_profiles


if __name__ == '__main__':

    log.info("Loading...")
    speech.play_text('I am loading...')

    # Init camera
    camera = PiCamera() if utils.is_rpi() else MacCamera()

    # Load a sample picture and learn how to recognize it.
    profiles = load_profiles()

    recognized_faces = []
    log.info("Feed-forwarding %s profiles" % (len(profiles)))
    speech.play_text('Now feeding the deep neural network with target profiles...')
    cou = 0
    for profile in profiles:
        image = face_recognition.load_image_file(profile["img_path"])
        face_encoding = face_recognition.face_encodings(image)
        if len(face_encoding) > 0:
            profile["image"] = image
            profile["encoding"] = face_encoding[0]
            profile["said_hello"] = False
            recognized_faces.append(profile)

        cou += 1
        if cou % 2 == 0:
            log.info("Progress: %s/%s" % (cou, len(profiles)))

    log.info("Loaded!")
    speech.play_text('Profiles loaded! I am ready.')

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    t = None
    is_speaking = False

    while True:
        try:

            # Grab a single frame of video
            camera.capture()

            if t is not None and not t.is_alive():
                is_speaking = False

            # Only process every other frame of video to save time
            if process_this_frame:
                # Find all the faces and face encodings in the current frame of video
                face_locations = face_recognition.face_locations(camera.get_small_frame())
                face_encodings = face_recognition.face_encodings(camera.get_small_frame(), face_locations)

                face_names = []
                for face_encoding in face_encodings:
                    # See if the face is a match for the known face(s)
                    encodings = [f["encoding"] for f in recognized_faces]
                    match = face_recognition.compare_faces(encodings, face_encoding, tolerance=conf["match_tolerance"])
                    name = "Unknown"

                    for i in range(len(encodings)):
                        if match[i]:
                            name = recognized_faces[i]["name"]
                            if not recognized_faces[i]["said_hello"] and not is_speaking:
                                log.info("Detected %s" % (name,))
                                recognized_faces[i]["said_hello"] = True
                                if conf["do_say_hello"]:
                                    t = StoppableThread(target=speech_module.welcome_to_party, args=(name,))
                                    is_speaking = True
                                    t.start()

                    face_names.append(name)

            process_this_frame = not process_this_frame

            # Display the results
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                camera.add_face_frame(top, right, bottom, left, name)
            camera.display_face_frames()

            # Hit 'q' on the keyboard to quit!
            if camera.did_stop():
                if t is not None:
                    t.stop()
                break

            if time.time() - last_time > 30:
                with open(CONFIG_PATH, 'r') as f:
                    conf = json.load(f)
                last_time = time.time()

        except Exception as e:
            log.error(e)

    # Release handle to the webcam
    camera.release()
