registry = {}


def register(event, callback):
    registry[event] = callback


def emit(event, **kwargs):
    registry[event](**kwargs)
