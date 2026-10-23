import unittest
from unittest.mock import Mock

from src import WhatsAPIDriver
from src.objects.chat import UserChat
from src.objects.message import Message, MessageGroup


def message_data(message_id, chat_id, timestamp):
    return {
        'id': message_id,
        'type': 'chat',
        'ack': 1,
        'sender': {'id': chat_id, 'formattedName': 'Sender'},
        'timestamp': timestamp,
        'chatId': chat_id,
        'content': 'Hello',
        'mediaData': {},
        'isNotification': False,
    }


def chat_data(chat_id, messages):
    return {
        'id': chat_id,
        'name': 'Chat',
        'kind': 'chat',
        'isGroup': False,
        'messages': messages,
    }


class UnreadMessagesTests(unittest.TestCase):
    def setUp(self):
        # Exercise the real conversion code with a WAPI response, without starting Selenium.
        self.driver = object.__new__(WhatsAPIDriver)
        self.driver.wapi_functions = Mock(spec=['getUnreadMessages'])

    def test_converts_groups_filters_missing_messages_and_sorts_chronologically(self):
        first_chat = '111@c.us'
        second_chat = '222@c.us'
        self.driver.wapi_functions.getUnreadMessages.return_value = [
            chat_data(first_chat, [
                None,
                message_data('later', first_chat, 200),
                None,
                message_data('earlier', first_chat, 100),
            ]),
            chat_data(second_chat, [message_data('other', second_chat, 150), None]),
        ]

        groups = self.driver.get_unread(
            include_me=True, include_notifications=True, use_unread_count=True,
        )

        self.driver.wapi_functions.getUnreadMessages.assert_called_once_with(True, True, True)
        self.assertEqual([group.chat.id for group in groups], [first_chat, second_chat])
        self.assertEqual([[message.id for message in group.messages] for group in groups],
                         [['earlier', 'later'], ['other']])
        for group in groups:
            self.assertIsInstance(group, MessageGroup)
            self.assertIsInstance(group.chat, UserChat)
            for message in group.messages:
                self.assertIsInstance(message, Message)
                self.assertEqual(message.chat_id, group.chat.id)
                self.assertIs(message.driver, self.driver)

    def test_empty_unread_response(self):
        self.driver.wapi_functions.getUnreadMessages.return_value = []

        self.assertEqual(self.driver.get_unread(), [])
        self.driver.wapi_functions.getUnreadMessages.assert_called_once_with(False, False, False)

    def test_group_with_only_missing_messages(self):
        self.driver.wapi_functions.getUnreadMessages.return_value = [chat_data('111@c.us', [None, None])]

        groups = self.driver.get_unread()

        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0].chat.id, '111@c.us')
        self.assertEqual(groups[0].messages, [])


if __name__ == '__main__':
    unittest.main()
