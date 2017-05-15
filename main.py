import json

from fuzzywuzzy import fuzz
import face_recognition

import speech
from libs import utils
from libs.StoppableThread import StoppableThread
from libs.Camera import MacCamera, PiCamera

log = utils.get_logger(__name__)
PROFILE_IMAGES_PATH = 'profile_images/'
IMAGE_EXTENSION = '.jpeg'
MATCH_TOLERANCE = 0.47


def welcome_to_party(person_name):
    speech.play_text('Hello %s, I hope you enjoy the party!' % (person_name,))
    return True


def first_occurrence(person_name, birth_day):
    speech.play_text('Hello %s, what is your birth day?' % (person_name,))

    while True:
        person_input = speech.speech_to_text()
        if not person_input:
            speech.play_text('Please answer the question')
            continue

        cmp_score = fuzz.token_sort_ratio(person_input, birth_day)
        log.info("Phrase comparison score: %s" % (cmp_score,))
        if cmp_score >= 90:
            speech.play_text('Correct!')
            break
        elif cmp_score <= 25:
            speech.play_text('Please answer the question. If you want me to stop, say, "I suck!"')
            person_input = speech.speech_to_text()
            if not person_input:
                continue
            if fuzz.ratio(person_input, "I suck") > 90:
                speech.play_text('Good choice! Have a nice day, %s' % (name,))
                break
            else:
                speech.play_text('Suit yourself, I will continue.')
        else:
            speech.play_text('Wrong Answer, please try again')

    return True


def load_profiles():
    with open('profiles_list.json', 'r') as f:
        loaded_profiles = json.load(f)
        for i, profile in enumerate(loaded_profiles):
            loaded_profiles[i]['img_path'] = PROFILE_IMAGES_PATH + profile['id'] + IMAGE_EXTENSION
        return loaded_profiles


if __name__ == '__main__':

    log.info("Loading...")

    # Init camera
    camera = PiCamera() if utils.is_rpi() else MacCamera()

    # Load a sample picture and learn how to recognize it.
    profiles = load_profiles()

    recognized_faces = []
    for profile in profiles:
        image = face_recognition.load_image_file(profile["img_path"])
        face_encoding = face_recognition.face_encodings(image)
        if len(face_encoding) > 0:
            profile["image"] = image
            profile["encoding"] = face_encoding[0]
            profile["said_hello"] = False
            recognized_faces.append(profile)

    log.info("Loaded!")

    # Initialize some variables
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True
    t = None
    is_speaking = False

    while True:
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
                match = face_recognition.compare_faces(encodings, face_encoding, tolerance=MATCH_TOLERANCE)
                name = "Unknown"

                for i in range(len(encodings)):
                    if match[i]:
                        name = recognized_faces[i]["name"]
                        if not recognized_faces[i]["said_hello"] and not is_speaking:
                            recognized_faces[i]["said_hello"] = True
                            t = StoppableThread(target=welcome_to_party, args=(name,))
                            is_speaking = True
                            t.start()

                face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            camera.add_face_frame(top, right, bottom, left, name)
        camera.display_face_frames()

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            if t is not None:
                t.stop()
            break

    # Release handle to the webcam
    camera.release()

recognized_faces = [
    {"img_path": "ilai.jpg", "name": "Ilai", "birth_day": "5th of August, 1989"},
    {"img_path": "aviv.jpg", "name": "Aviv", "birth_day": "9th of April, 1989"},
    {"img_path": "omri.jpg", "name": "Omri", "birth_day": "5th of October, 1989"},
    {"img_path": "mickey.jpg", "name": "Mickey", "birth_day": "20th of December, 1988"}
]
