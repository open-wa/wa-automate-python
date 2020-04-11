import io
from base64 import b64encode

import magic
import six


def safe_str(text):
    if not text:
        return "(empty)"
    assert isinstance(text, six.string_types), "obj is not a string: %r" % text
    return str(text.encode('utf-8').decode('ascii', 'ignore')) if text else "(empty)"


def convert_to_base64(source, is_thumbnail=False):
    """
    :param source: file source
    :return: returns the converted string and formatted for the send media function send_media
    """
    if type(source) is str:
        with open(source, "rb") as image_file:
            source = io.BytesIO(image_file.read())
    archive = b64encode(source.read())
    archive = archive.decode('utf-8')
    if not is_thumbnail:
        mime = magic.Magic(mime=True)
        source.seek(0)
        content_type = mime.from_buffer(source.read())
        archive = 'data:' + content_type + ';base64,' + archive
    return archive
