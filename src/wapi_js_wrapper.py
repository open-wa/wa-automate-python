import json
import os
import time
from enum import Enum, auto

import requests
from selenium.common.exceptions import WebDriverException, JavascriptException
from six import string_types
from threading import Thread
from .objects.message import factory_message


class JsException(Exception):
    def __init__(self, message=None):
        super(Exception, self).__init__(message)


class WapiPhoneNotConnectedException(Exception):
    def __init__(self, message=None):
        super(Exception, self).__init__(message)


class WapiJsWrapper(object):
    """
    Wraps JS functions in window.WAPI for easier use from python
    """

    def __init__(self, driver, wapi_driver, wapi_version='master'):
        self.driver = driver
        self.wapi_driver = wapi_driver
        self.wapi_version = wapi_version
        self.available_functions = None

        # Starts new messages observable thread.
        self.new_messages_observable = NewMessagesObservable(self, wapi_driver, driver)
        self.new_messages_observable.start()

    def __getattr__(self, item):
        """
        Finds functions in window.WAPI

        :param item: Function name
        :return: Callable function object
        :rtype: JsFunction
        """
        wapi_functions = dir(self)

        if item not in wapi_functions:
            raise AttributeError("Function {0} doesn't exist".format(item))

        return JsFunction(item, self.driver, self)

    def __dir__(self):
        """
        Load wapi.js and returns its functions

        :return: List of functions in window.WAPI
        """
        if self.available_functions is not None:
            return self.available_functions

        """Sleep wait until WhatsApp loads and creates webpack objects"""
        time.sleep(5)
        try:
            script_path = os.path.dirname(os.path.abspath(__file__))
        except NameError:
            script_path = os.getcwd()

        result = self.driver.execute_script("if (document.querySelector('*[data-icon=chat]') !== null) { return true } else { return false }")
        if result:
            wapi_js = requests.get(f'https://raw.githubusercontent.com/open-wa/wa-automate-nodejs/{self.wapi_version}/src/lib/wapi.js')
            self.driver.execute_script(wapi_js.content.decode())

            patches = json.loads(requests.get(f'https://raw.githubusercontent.com/open-wa/wa-automate-nodejs/{self.wapi_version}/patches.json').content.decode())
            for patch in patches:
                self.driver.execute_script(patch)

            with open(os.path.join(script_path, "js", "pywapi.js"), "r") as script:
                self.driver.execute_script(script.read())

            result = self.driver.execute_script("return Object.keys(window.WAPI)")
            if result:
                self.available_functions = result

                if self.wapi_driver.license_key:
                    me = self.getMe()
                    if isinstance(me, dict):
                        me = self.getMe()['wid']
                    me = me.split('@')[0]
                    self.driver.execute_script(requests.post('https://openwa.web.app/license-check', json={'key': self.wapi_driver.license_key, 'number': me}).content.decode())

                return self.available_functions
            else:
                return []

    def quit(self):
        self.new_messages_observable.stop()


class JsArg(object):
    """
    Represents a JS function argument
    """

    def __init__(self, obj):
        """
        Constructor

        :param obj: Python object to represent
        """
        self.obj = obj

    def __str__(self):
        """
        Casts self.obj from python type to valid JS literal

        :return: JS literal represented in a string
        """
        if isinstance(self.obj, string_types):
            return repr(str(self.obj))

        if isinstance(self.obj, bool):
            return str(self.obj).lower()

        if self.obj is None:
            return 'null'

        return str(self.obj)


class JsFunction(object):
    """
    Callable object represents functions in window.WAPI
    """

    def __init__(self, function_name, driver, wapi_wrapper):
        self.driver = driver
        self.function_name = function_name
        self.wapi_wrapper = wapi_wrapper
        self.is_a_retry = False

    def __call__(self, *args, **kwargs):
        # Selenium's execute_async_script passes a callback function that should be called when the JS operation is done
        # It is passed to the WAPI function using arguments[0]
        if len(args):
            command = "return WAPI.pyFunc(()=>WAPI.{0}({1}), arguments[0])" \
                .format(self.function_name, ",".join([str(JsArg(arg)) for arg in args]))
        else:
            command = "return WAPI.pyFunc(()=>WAPI.{0}(), arguments[0])".format(self.function_name)

        try:
            return self.driver.execute_async_script(command)
        except JavascriptException as e:
            if 'WAPI is not defined' in e.msg and self.is_a_retry is not True:
                self.wapi_wrapper.available_functions = None
                retry_command = getattr(self.wapi_wrapper, self.function_name)
                retry_command.is_a_retry = True
                retry_command(*args, **kwargs)
            else:
                raise JsException(
                    "Error in function {0} ({1}). Command: {2}".format(self.function_name, e.msg, command))
        except WebDriverException as e:
            if e.msg == 'Timed out':
                raise WapiPhoneNotConnectedException("Phone not connected to Internet")
            raise JsException("Error in function {0} ({1}). Command: {2}".format(self.function_name, e.msg, command))


class NewMessagesObservable(Thread):
    def __init__(self, wapi_js_wrapper, wapi_driver, webdriver):
        Thread.__init__(self)
        self.daemon = True
        self.wapi_js_wrapper = wapi_js_wrapper
        self.wapi_driver = wapi_driver
        self.webdriver = webdriver
        self.new_msgs_observers = []
        self.new_acks_observers = []
        self.group_change_observers = {}
        self.liveloc_update_observers = {}
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                js_events = self.wapi_js_wrapper.getBufferedEvents()

                new_js_messages = js_events['new_msgs']
                if isinstance(new_js_messages, list) and len(new_js_messages) > 0:
                    new_messages = []
                    for js_message in new_js_messages:
                        new_messages.append(factory_message(js_message, self.wapi_driver))

                    self._inform_new_msgs(new_messages)

                new_js_acks = js_events['new_acks']
                if isinstance(new_js_acks, list) and len(new_js_acks) > 0:
                    new_acks = []
                    for js_ack in new_js_acks:
                        new_acks.append(factory_message(js_ack, self.wapi_driver))

                    self._inform_new_acks(new_acks)

                events = js_events['parti_changes']
                if isinstance(events, list) and len(events) > 0:
                    self._inform_group_changes(events)

                events = js_events['liveloc_updates']
                if isinstance(events, list) and len(events) > 0:
                    self._inform_liveloc_updates(events)
            except Exception as e:
                pass

            time.sleep(2)

    def stop(self):
        self.running = False

    def subscribe_new_messages(self, observer):
        callback = getattr(observer, "on_message_received", None)
        if callable(callback):
            self.new_msgs_observers.append(observer)

    def subscribe_acks(self, observer):
        callback = getattr(observer, "on_ack_received", None)
        if callable(callback):
            self.new_acks_observers.append(observer)

    def subscribe_group_participants_change(self, observer, chat_id):
        callback = getattr(observer, "on_participants_change", None)
        if callable(callback):
            self.wapi_js_wrapper.onParticipantsChanged(chat_id, None)
            if chat_id not in self.group_change_observers:
                self.group_change_observers[chat_id] = []
            self.group_change_observers[chat_id].append(observer)

    def subscribe_live_location_updates(self, observer, chat_id):
        callback = getattr(observer, "on_live_location_update", None)
        if callable(callback):
            self.wapi_js_wrapper.onLiveLocation(chat_id, None)
            if chat_id not in self.liveloc_update_observers:
                self.liveloc_update_observers[chat_id] = []
            self.liveloc_update_observers[chat_id].append(observer)

    def unsubscribe_new_messages(self, observer):
        try:
            self.new_msgs_observers.remove(observer)
        except ValueError:
            pass

    def unsubscribe_acks(self, observer):
        try:
            self.new_acks_observers.remove(observer)
        except ValueError:
            pass

    def unsubscribe_group_participants_change(self, observer, chat_id):
        try:
            self.group_change_observers[chat_id].remove(observer)
        except (KeyError, ValueError):
            pass

    def unsubscribe_live_location_updates(self, observer, chat_id):
        try:
            self.group_change_observers[chat_id].remove(observer)
        except (KeyError, ValueError):
            pass

    def _inform_new_msgs(self, new_messages):
        for observer in self.new_msgs_observers:
            observer.on_message_received(new_messages)

    def _inform_new_acks(self, new_acks):
        for observer in self.new_acks_observers:
            observer.on_ack_received(new_acks)

    def _inform_group_changes(self, events):
        for event in events:
            if event['id'] in self.group_change_observers:
                for o in self.group_change_observers[event['id']]:
                    o.on_participants_change(event)

    def _inform_liveloc_updates(self, events):
        for event in events:
            if event['id'] in self.liveloc_update_observers:
                for o in self.liveloc_update_observers[event['id']]:
                    o.on_live_location_update(event)
