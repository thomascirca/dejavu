import os
import fnmatch
import numpy as np
from pydub import AudioSegment
from hashlib import sha1

def unique_hash(filepath):
    """ Small function to generate a hash to uniquely generate
    a file. Taken / inspired from git's way via stackoverflow:
    http://stackoverflow.com/questions/552659
    """
    filesize_bytes = os.path.getsize(filepath)
    s = sha1()
    s.update(("blob %u\0" % filesize_bytes).encode('ascii'))
    with open(filepath, 'rb') as f:
        s.update(f.read())
    return s.hexdigest()


def find_files(path, extensions):
    # Allow both with ".mp3" and without "mp3" to be used for extensions
    extensions = [e.replace(".", "") for e in extensions]

    for dirpath, dirnames, files in os.walk(path):
        for extension in extensions:
            for f in fnmatch.filter(files, "*.%s" % extension):
                p = os.path.join(dirpath, f)
                yield (p, extension)


def read(filename, limit=None):
    """
    Reads any file supported by pydub (ffmpeg) and returns the data contained
    within.

    Can be optionally limited to a certain amount of seconds from the start
    of the file by specifying the `limit` parameter. This is the amount of
    seconds from the start of the file.

    returns: (channels, samplerate)
    """
    audiofile = AudioSegment.from_file(filename)

    if limit:
        audiofile = audiofile[:limit * 1000]

    data = np.fromstring(audiofile._data, np.int16)

    channels = []
    for chn in xrange(audiofile.channels):
        channels.append(data[chn::audiofile.channels])

    return channels, audiofile.frame_rate, unique_hash(filename)


def path_to_songname(path):
    """
    Extracts song name from a filepath. Used to identify which songs
    have already been fingerprinted on disk.
    """
    return os.path.splitext(os.path.basename(path))[0]
