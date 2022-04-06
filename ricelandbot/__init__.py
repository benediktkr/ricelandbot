import importlib.metadata

__version__ = importlib.metadata.version(__name__)
# avoid a stupid sed command i added to a jenkins pipeline
# until i throw it out
_version = importlib.metadata.version(__name__)
version_dict = {
    'version': _version,
    'name': __name__
}
