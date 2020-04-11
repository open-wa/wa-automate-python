from base64 import b64encode

import magic
import six


def safe_str(text):
    if not text:
        return "(empty)"
    assert isinstance(text, six.string_types), "obj is not a string: %r" % text
    return str(text.encode('utf-8').decode('ascii', 'ignore')) if text else "(empty)"


def convert_to_base64(path, is_thumbnail=False):
    """
    :param path: file path
    :return: returns the converted string and formatted for the send media function send_media
    """

    mime = magic.Magic(mime=True)
    content_type = mime.from_file(path)
    archive = ''
    with open(path, "rb") as image_file:
        archive = b64encode(image_file.read())
        archive = archive.decode('utf-8')
    if is_thumbnail:
        return archive
    return 'data:' + content_type + ';base64,' + archive
