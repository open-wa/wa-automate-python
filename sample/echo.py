import time
from src import WhatsAPIDriver
from src.objects.message import Message

driver = WhatsAPIDriver()
print("Waiting for QR")
while not driver.wait_for_login():
    time.sleep(3)

print("Bot started")

while True:
    time.sleep(3)
    print('Checking for more messages')
    for contact in driver.get_unread():
        for message in contact.messages:
            if isinstance(message, Message):  # Currently works for text messages only.
                contact.chat.send_message(message.content)
