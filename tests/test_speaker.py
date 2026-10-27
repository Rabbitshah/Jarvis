import threading

from jarvis.voice import tts
from jarvis.voice.speaker import StreamingSpeaker


def make(**kw):
    played, lock = [], threading.Lock()

    def play(wav):
        with lock:
            played.append(wav.decode())

    return StreamingSpeaker(lambda s: s.encode(), play, say=kw.pop("say", lambda m: None), **kw), played


def feed_in_pieces(sp, text, n=5):
    for i in range(0, len(text), n):
        sp.feed(text[i:i + n])


def test_sentences_are_spoken_in_order_as_they_finish():
    sp, played = make()
    feed_in_pieces(sp, "It is quarter past three. You have one meeting today! Anything else?")
    sp.finish()
    assert played == ["It is quarter past three.", "You have one meeting today!", "Anything else?"]
    assert sp.first_sound_at is not None


def test_first_sentence_is_queued_before_the_answer_ends():
    sp, _ = make()
    sp.feed("The first sentence is done. And the secon")
    assert sp.sentences == ["The first sentence is done."]  # known before the rest exists
    sp.finish()


def test_decimals_and_short_abbreviations_do_not_split():
    sp, played = make()
    sp.feed("Dr. Rao scored 3.5 points in the test today. Fine.")
    sp.finish()
    assert played[0] == "Dr. Rao scored 3.5 points in the test today."


def test_markdown_removed_and_empty_skipped():
    sp, played = make()
    sp.feed("**Bold start** of the answer here.\n- item one is here\n")
    sp.finish()
    assert played == ["Bold start of the answer here.", "item one is here"]


def test_limit_stops_long_answers():
    sp, played = make(limit=60)
    sp.feed("This is the first long sentence here. This is the second long sentence here. This is the third one. ")
    sp.finish()
    assert len(played) == 2  # the second sentence crosses 60 characters; the third is dropped


def test_synth_error_is_said_once_and_does_not_hang():
    said = []

    def bad(s):
        raise tts.TtsError("piper down")

    played = []
    sp = StreamingSpeaker(bad, played.append, say=said.append)
    sp.feed("First sentence is long enough. Second sentence is long enough. ")
    sp.finish()
    assert said == ["  [voice] piper down"] and played == [] and sp.first_sound_at is None


def test_stop_drops_the_rest():
    stopped = []
    sp = StreamingSpeaker(lambda s: s.encode(), lambda w: None, stop_playing=lambda: stopped.append(1))
    sp.feed("Sentence number one is here. ")
    sp.stop()
    sp.feed("Sentence number two is here. ")
    sp.finish()
    assert stopped == [1]
