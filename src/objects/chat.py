from .whatsapp_object import WhatsappObjectWithId, driver_needed
from ..helper import safe_str
import time


def factory_chat(js_obj, driver=None):
    """Factory function for creating appropriate object given selenium JS object"""
    if js_obj["kind"] not in ["chat", "group", "broadcast"]:
        raise AssertionError("Expected chat, group or broadcast object, got {0}".format(js_obj["kind"]))

    if js_obj["isGroup"]:
        return GroupChat(js_obj, driver)

    if js_obj["kind"] == "broadcast":
        return BroadcastChat(js_obj, driver)

    return UserChat(js_obj, driver)


class Chat(WhatsappObjectWithId):

    def __init__(self, js_obj, driver=None):
        super(Chat, self).__init__(js_obj, driver)
        self.last_seen = None
        if 'lastSeen' in js_obj:
            self.last_seen = js_obj["lastSeen"]

    @driver_needed
    def open(self):
        return self.driver.open_chat(self.id)

    @driver_needed
    def send_media(self, image_path, caption=None):
        return self.driver.send_media(image_path, self.id, caption)

    @driver_needed
    def send_video_as_gif(self, image_path, caption=None):
        return self.driver.send_video_as_gif(image_path, self.id, caption)

    @driver_needed
    def send_giphy(self, giphy_url, caption=None):
        return self.driver.send_giphy(giphy_url, self.id, caption)

    @driver_needed
    def send_location(self, lat, long, text=None):
        return self.driver.send_location(self.id, lat, long, text)

    @driver_needed
    def send_message_with_thumb(self, image_path, url, title, description, text):
        return self.driver.send_message_with_thumbnail(image_path, self.id, url, title, description, text)

    @driver_needed
    def send_message(self, message):
        return self.driver.chat_send_message(self.id, message)

    @driver_needed
    def send_seen(self):
        return self.driver.chat_send_seen(self.id)

    @driver_needed
    def get_messages(self, include_me=False, include_notifications=False):
        return list(self.driver.get_all_messages_in_chat(self, include_me, include_notifications))

    @driver_needed
    def get_unread_messages(self,
                            include_me=False,
                            include_notifications=False):
        """
        I fetch unread messages.

        :param include_me: if user's messages are to be included
        :type  include_me: bool

        :param include_notifications: if events happening on chat are to be included
        :type  include_notifications: bool

        :return: list of unread messages
        :rtype: list
        """
        return list(self.driver.get_unread_messages_in_chat(
            self.id,
            include_me,
            include_notifications
        ))

    # get_unread_messages()

    @driver_needed
    def load_earlier_messages(self):
        self.driver.chat_load_earlier_messages(self.id)

    @driver_needed
    def load_all_earlier_messages(self):
        self.driver.chat_load_all_earlier_messages(self.id)

    @driver_needed
    def load_earlier_messages_till(self, last):
        """
        Triggers loading of messages till a specific point in time

        :param last: Datetime object for the last message to be loaded
        :type last: datetime
        :return: Nothing
        :rtype: None
        """
        timestamp = time.mktime(last.timetuple())
        self.driver.wapi_functions.loadEarlierMessagesTillDate(self.id, timestamp)

    @driver_needed
    def set_typing_simulation(self, typing):
        self.driver.set_typing_simulation(self.id, typing)


class UserChat(Chat):
    def __init__(self, js_obj, driver=None):
        super(UserChat, self).__init__(js_obj, driver)

    def __repr__(self):
        safe_name = safe_str(self.name)

        return "<User chat - {name}: {id}>".format(
            name=safe_name,
            id=self.id)


class BroadcastChat(Chat):
    def __init__(self, js_obj, driver=None):
        super(BroadcastChat, self).__init__(js_obj, driver)

    def __repr__(self):
        safe_name = safe_str(self.name)
        return "<Broadcast chat - {name}: {id}>".format(
            name=safe_name,
            id=self.id)


class GroupChat(Chat):
    def __init__(self, js_obj, driver=None):
        super(GroupChat, self).__init__(js_obj, driver)

    @driver_needed
    def get_participants_ids(self):
        return self.driver.wapi_functions.getGroupParticipantIDs(self.id)

    @driver_needed
    def get_participants(self):
        return list(self.driver.group_get_participants(self.id))

    @driver_needed
    def get_admins(self):
        return list(self.driver.group_get_admins(self.id))

    @driver_needed
    def add_participant_group(self, id_participant):
        return self.driver.add_participant_group(self.id, id_participant)

    @driver_needed
    def remove_participant_group(self, id_participant):
        return self.driver.remove_participant_group(self.id, id_participant)

    @driver_needed
    def promove_participant_admin_group(self, id_participant):
        return self.driver.promove_participant_admin_group(self.id, id_participant)

    @driver_needed
    def demote_participant_admin_group(self, id_participant):
        return self.driver.demote_participant_admin_group(self.id, id_participant)

    def __repr__(self):
        safe_name = safe_str(self.name)
        return "<Group chat - {name}: {id}, {participants} participants>".format(
            name=safe_name,
            id=self.id,
            participants=len(self.get_participants_ids()))
