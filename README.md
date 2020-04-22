<div align="center">
<img src="https://raw.githubusercontent.com/open-wa/wa-automate-nodejs/master/resources/hotfix-logo.png" width="128" height="128"/>

# wa-automate-python

## (Based on web.whatsapp.com)
![PyPI version](https://badge.fury.io/py/openwa.svg)
<a href="https://discord.gg/dnpp72a"><img src="https://img.shields.io/discord/661438166758195211?color=blueviolet&label=discord&style=flat" /></a>
[![Firefox version](https://img.shields.io/badge/Firefox-75.0-green.svg)]()
</div>

## What is it?
This package is used to provide a python interface for interacting with WhatsAPP Web to send and receive Whatsapp messages.
It is based on the official Whatsapp Web Browser Application and uses Selenium browser automation to communicate with Whatsapp Web.

### Functions list
| Function                          | Description | Implemented |
| --------------------------------- | ----------- | ----------- |
| Receive message                   |             | ✅          |
| Automatic QR Refresh              |             | ✅          |
| Send text                         |             | ✅          |
| Get contacts                      |             | ✅          |
| Get chats                         |             | ✅          |
| Get groups                        |             | ✅          |
| Get group members                 |             | ✅          |
| Send contact                      |             | ✅          |
| Get contact detail                |             | ✅          |
| Send Images (image)               |             | ✅          |
| Send media (audio, doc)  |             | ✅          |
| Send media (video)  |             | ✅          |
| Send stickers                     |             |✅           |
| Decrypt media (image, audio, doc) |             | ✅          |
| Capturing QR Code                 |             | ✅          |
| Multiple Sessions                 |             | ✅          |
| Last seen & isOnline (beta)      |             | ✅          |
| 📍 SEND LOCATION!! (beta)         |             | ✅          |
| Simulated '...typing'             |             | ✅          |
| Send GIFs!                       |             | ✅          |
| Forward Messages                  |             | ✅          |
| Listen to New Messages           |             | ✅          |
| Listen to Read Receipts           |             | ✅          |
| Listen to Live Locations           |             | ✅          |
| Group participant changes         |             | ❌          |
| Create Groups         |             | ✅          |
| add, remove, promote, demote participants         |             | ✅          |

## Local installation

##### Dependencies
You will need to install [Gecko Driver](https://github.com/mozilla/geckodriver) separately, if using firefox, which is the default.

#### From PyPI
- Install from pip
`pip install openwa`

## Usage

### 1. Import library

    from openwa import WhatsAPIDriver

### 2. Instantiate driver 

    driver = WhatsAPIDriver()

Possible arguments for constructor:

- client : Type of browser. The default is Firefox, but Chrome and Remote is supported too. See sample directory for remote examples.
- username : Can be any value.
- proxy: The proxy server to configure selenium to. Format is "<proxy>:<portnumber>"
- command_executor: Passed directly as an argument to Remote Selenium. Ignore if not using it. See sample directory for remote examples. 
- loadstyles: Default is False. If True, it will load the styling in the browser.
- profile: Pass the full path to the profile to load it. Profile folder will be end in ".default". For persistent login, open a normal firefox tab, log in to whatsapp, then pass the profile as an argument.

### 3. Wait until you are loged in, or you are asked to scan the QR

    driver.wait_for_login()
    
### 4. Get the QR in one of these ways

    # Save image to file
    driver.get_qr()
    
    # Get image in base64 
    driver.get_qr_base64()

The QR code is automatically reloaded if it has expired
    
### 5. Scan the QR code with your phone
Once you scan the QR obtained, you are ready to use the rest of the funcionality 

### Viewing unread messages

    unread_messages = driver.get_unread()

### Forwarding messages
You need to pass the following params:

- chat id to forward messages to
- messages: a single or array of message ids
- skipMyMessages: true or false, if true it will filter out messages sent by you from the list of messages, default false.


    driver.forward_messages(to_chat_id, messages, False)

### Reply messages

    <Message Object>.reply_message('I like that option!')

### List all chats

    driver.get_all_chats()

### Get chat by name
Fetches a chat given its name. Must be an exact match

    driver.get_chat_from_name(chat_name)

### Get chat by number
Fetches a chat given its phone number. Must be in the international format.\
For example, for the number: +123-45-678-9123, this function expects: 123456789123

    driver.get_chat_from_phone_number('123456789123')

### To send a message, get a Chat object from before, and call the send_message function with the message.

    <Chat Object>.send_message("Hello")

### Sending Media/Files

    <Chat Object>.send_media(image_path, "look at this!")

### Sending Gifs

There are two ways to send GIFs - by Video or by giphy link.

##### 1.  Sending Video as a GIF.     
WhatsApp doesn't actually support the .gif format - probably due to how inefficient it is as a filetype - they instead convert GIFs to video then process them.

In order to send gifs you need to convert the gif to an mp4 file then use the following method:

    <Chat Object>.send_video_as_gif(mp4_file_path, "look at this gif!")
##### 2. Sending a Giphy Media Link
This is a convenience method to make it easier to send gifs from the website [GIPHY](https://giphy.com). You need to make sure you use a giphy media link as shown below.

    <Chat Object>.send_video_as_gif("https://media.giphy.com/media/oYtVHSxngR3lC/giphy.gif", "look at this giphy!")

### Sending Location
You need to pass the following params:

- latitude: '51.5074'
- longitude: '0.1278'
- location text: 'LONDON!'


    <Chat Object>.send_location('51.5074', '0.1278',  'London')

### Simulate typing
You need to pass the following param:

- typing: `True` or `False`


    <Chat Object>.set_typing_simulation(True)

### Create group
The first parameter is the group name, the second parameter is the contact ids to add as participants

    driver.create_group('The Groopers', [chat_id1, chat_id2])

### Edit group participants
You can get the GroupChat object with the previously explained methods to obtain chats. 

    <GroupChat Object>.add_participant_group(id_participant)
    <GroupChat Object>.remove_participant_group(id_participant)
    <GroupChat Object>.promove_participant_admin_group(id_participant)
    <GroupChat Object>.demote_participant_admin_group(id_participant)

### Listening for new messages
For this we must define a new observer class that implements the `on_message_received` method and receives the new messages. 
    
    class NewMessageObserver:
        def on_message_received(self, new_messages):
            for message in new_messages:
                print("New message received from number {}".format(message.sender.id))
    
    driver.subscribe_new_messages(NewMessageObserver())

## Limitation
Phone needs to manually scan the QR Code from Whatsapp Web. Phone has to be on and connected to the internet.

## Docker and remote Selenium Installation

It may be favorable to run Selenium and the wa-automate-python client as Docker containers. This almost completely avoids any installation problems and any messy local installation or dependency hell. The result is a more stable runtime environment for the client, which could run on a headless server.
Using Docker may also help in developing the library itself.

### 1. Create network

    docker network create selenium

### 2. Run Selenium grid/standalone container

This is based on the official Selenium image (https://github.com/SeleniumHQ/docker-selenium).
The following Docker command runs a Selenium standalone Firefox browser in debug (VNC) mode. You can use VNC on port 5900 to view the browser. It uses the network "selenium" and the container is named "firefox" for later reference.

    docker run -d -p 4444:4444 -p 5900:5900 --name firefox --network selenium -v /dev/shm:/dev/shm selenium/standalone-firefox-debug:3.141.59

### 3. Build python/wa-automate-python docker base image

The following command uses the dockerfile to build a new image based on Python 2.7 with all required packages from requirements.txt. 

    docker build -t wa-automate-python .

### 4. Run client container

Now to the client container. The following command installs a local webwhatsapi inside the base container and runs a client. It maps the local directory to the app directory inside the container for easy development. Also sets the network to "selenium" and an environment variable for the remote selenium url. Please note that the remote Selenium hostname must be identical to the name of the Selenium container. 

    docker run --network selenium -it -e SELENIUM='http://firefox:4444/wd/hub' -v $(pwd):/app  wa-automate-python /bin/bash -c "pip install ./;pip list;python sample/remote.py"
    
For Windows (cmd):

    docker run --network selenium -it -e SELENIUM='http://firefox:4444/wd/hub' -v "%cd%:/app" wa-automate-python /bin/bash -c "pip install ./;pip list;python sample/remote.py"

For Windows (PowerShell):

    docker run --network selenium -it -e SELENIUM='http://firefox:4444/wd/hub' -v "$(pwd):/app".ToLower() wa-automate-python /bin/bash -c "pip install ./;pip list;python sample/remote.py"

It is also certainly possible to fully build the docker image in advance and define an entrypoint/cmd inside the dockerfile to run a full client.


## Contribute
Contributing is simple as cloning, making changes and submitting a pull request.
If you would like to contribute, here are a few starters:
- Bug Hunts
- More sorts of examples
- Additional features/ More integrations (This api has the minimum amount, but I don't mind having more data accessible to users)
- Create an env/vagrant box to make it easy for others to contribute. (At the moment, all I have is a requirements.txt

## Legal
This code is in no way affiliated with, authorized, maintained, sponsored or endorsed by WhatsApp or any of its affiliates or subsidiaries. This is an independent and unofficial software. Use at your own risk.

## License
[Hippocratic + Do Not Harm Version 1.0](https://github.com/open-wa/wa-automate-python/blob/master/LICENSE.md)
