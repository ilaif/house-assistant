from libs import speech, utils
from fuzzywuzzy import fuzz

log = utils.get_logger(__name__)


def welcome_to_party(person_name):
    speech.play_text('Hello %s. I hope you enjoy the party!!!' % (person_name,))
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
                speech.play_text('Good choice! Have a nice day, %s' % (person_name,))
                break
            else:
                speech.play_text('Suit yourself, I will continue.')
        else:
            speech.play_text('Wrong Answer, please try again')

    return True
