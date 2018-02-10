from . import persist

import time
import threading


# Map from view_id to threading.Timer objects
timers = {}


def hit(view, callback):
    vid = view.id()
    delay = get_delay()  # [seconds]
    return _queue_lint(vid, delay, callback)


def _queue_lint(vid, delay, callback):  # <-serial execution
    hit_time = time.monotonic()

    try:
        timers[vid].cancel()
    except KeyError:
        pass

    timers[vid] = timer = threading.Timer(delay, lambda: callback(vid, hit_time))
    timer.start()

    return hit_time


def cleanup(vid):
    try:
        timers.pop(vid).cancel()
    except KeyError:
        pass


def get_delay():
    """Return the delay between a lint request and when it will be processed.

    If the lint mode is not background, there is no delay. Otherwise, if
    a "delay" setting is not available in any of the settings, MIN_DELAY is used.
    """
    if persist.settings.get('lint_mode') != 'background':
        return 0

    return persist.settings.get('delay')
