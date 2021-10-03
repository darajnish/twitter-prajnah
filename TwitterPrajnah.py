#!/usr/bin/env python

'''
MIT License

Copyright (c) 2021 Rajnish Mishra

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''


import tweepy as tw
import json, logging
from time import sleep

MODULES_DIR = 'mods'
CONFIG_FILE = 'config.json'

class TwitterConnectionError(ConnectionError):
    def __init__(self, msg):
        self.message = msg

class ConfigParseError(Exception):
    def __init__(self, msg):
        self.message = msg

class Config:
    '''
        Reads and stores all config attributes
    '''
    def __init__(self, filepath: str):
        logger = logging.getLogger(self.__class__.__name__)
        try:
            config = {}
            with open(filepath, 'r') as jsonfile:
                config = json.loads(jsonfile.read())
            for k,v in config.items():
                setattr(self, k, v)
            self._json = config
            logger.debug("Read config: {0}".format(config))
        except (json.JSONDecodeError, FileNotFoundError, PermissionError):
            logger.exception("Failed to read config: {0}".format(filepath))
            # Throw error for a quickly abort of the program, the config had an issue
            raise ConfigParseError("Failed to read config: {0}".format(filepath))
    
    def __str__(self):
        return str(self._json)

class TwitterBot:
    def __init__(self, config: Config, callback, last_statusid=None):
        import threading

        # Init values
        self.ratelimit_wait = int(getattr(config, 'ratelimit_wait', 15))*60
        self.sleep_time = int(getattr(config, 'sleep_time', 1))*60
        self.last_statusid = last_statusid
        self.running = threading.Event()
        self.thread = threading.Thread(target=self.__bot_process__)
        self.config = config
        self.__callback__ = callback
        self.logger = logging.getLogger(self.__class__.__name__)

        self.logger.debug({
            'config' : str(config),
            'last_statusid': last_statusid
        })

        # Try logging with the twitter API
        try:
            self.auth = tw.OAuthHandler(config.api_key, config.api_secret)
            self.api = self.__loginAPI__(config, self.auth)
            self.username = self.me.screen_name
            self.logger.info("Login successful: {0}".format(self.username))
        except tw.TweepError:
            self.logger.exception("Failed init twitter bot!")
            # Throw error for a quickly abort the program
            raise TwitterConnectionError("Failed init twitter bot!")
        self.logger.debug({'me': self.me, 'username': self.username})
        self.logger.info('Bot Initiated')
    
    def __loginAPI__(self, config, auth):
        # Check if we already have the access_key and access_secret stored in the config
        if hasattr(config, 'access_key') and hasattr(config, 'access_secret'):
            auth.set_access_token(config.access_key, config.access_secret)
        else:
            # else try to get a login into the user's account and get access_key and access_secret by guiding the user
            try:
                url = auth.get_authorization_url()
                print('\nPaste this URL in browser and get the auth code:', url)
                auth_code = input('CODE: ')
                auth.get_access_token(auth_code)
                print("\nSave these into config!\nAccess Token: {0}\nAccess Secret: {1}\n".format(auth.access_token, auth.access_token_secret))
            except tw.TweepError :
                self.logger.exception("Failed to get authorization!")
                # Failure while logging in, we must abort
                raise TwitterConnectionError("Failed to get authorization!")
        
        # Now we've got the access_key and access_secret, time to test login
        try:
            api = tw.API(auth)
            self.me = api.me()
            return api
        except tw.TweepError :
            self.logger.exception("Failed get API access!")
            # Failed? and we've read access_key and access_secret from the config? meaning they must be invalid!
            if hasattr(config, 'access_key') and hasattr(config, 'access_secret'):
                self.logger.error("Looks like the current access_key and access_secret are not valid! Obtaining new ones..")
                # Delete the curret access_key and access_secret from config and retry so that the user goes through the login process
                # to obtain new access_key and access_secret
                del config.access_key, config.access_secret
                return self.__loginAPI__(config, auth)
            else:
                # failed and it wasn't something from config, meaning something weird must have happened, abort the program
                raise TwitterConnectionError("Failed get API access!")
    
    def __rangem(self, mentions):
        ''' Just a handy method to find out the range of user mentions in a tweet text '''
        j,k,i = 0,0,0
        for men in mentions:
            if i==0:
                j = men['indices'][0]
            elif mentions[i-1]['indices'][1]+1 != men['indices'][0]:
                break
            k = men['indices'][1]
            i += 1
        return (j,k)
    
    def __rtlimtc__(self, cursor):
        ''' Handles rate limits within a cursor '''
        while True:
            try:
                yield cursor.next()
            except tw.RateLimitError:
                self.logger.warning("Rate-limited by the twitter api! Retrying after {0}s..".format(self.ratelimit_wait))
                sleep(self.ratelimit_wait)
            except StopIteration:
                return
    
    def __process_requests__(self):
        ''' Each time checks for new tweets and filters out the tagged ones and feeds it for processing '''
        self.logger.debug({'last_statusid': self.last_statusid})
        if self.last_statusid :
            for status in self.__rtlimtc__(tw.Cursor(self.api.mentions_timeline, count=5, since_id=self.last_statusid).items(5)):
                if status.user.screen_name == self.username :
                    continue
                try:
                    status = self.twck(status)
                except tw.RateLimitError:
                    self.logger.warning("Rate-limited by the twitter api! Retrying after {0}s..".format(self.ratelimit_wait))
                    sleep(self.ratelimit_wait)
                    status = self.twck(status)
                
                self.logger.getChild('__process_requests__').debug("Received: {0}".format(status.text))
                self.__callback__(self, status)
                self.last_statusid = status.id
                sleep(3)
        else :
            self.last_statusid = self.api.mentions_timeline(count=1)[0].id
    
    def __bot_process__(self):
        ''' Starts the infinite loop of doing bot stuffs until exit signal is received '''
        while not self.running.wait(self.sleep_time) :
            self.__process_requests__()
    
    def get_tweet(self, tweet_id, ext=False):
        ''' Helpful method to get tweets by id while taking precautions '''
        try:
            if ext :
                return self.twck(self.api.get_status(id=tweet_id))
            else :
                self.api.get_status(id=tweet_id)
        except tw.RateLimitError:
            self.logger.warning("Rate-limited by the twitter api! Retrying after {0}s..".format(self.ratelimit_wait))
            sleep(self.ratelimit_wait)
            return self.get_tweet(tweet_id)
    
    def twck(self, status):
        ''' Checks if the tweet needs to be extended to get the complete text of it '''
        if status.truncated:
            status = self.api.get_status(status.id, tweet_mode='extended')
            status.text = status.full_text
        status.just_text = status.text[self.__rangem(status.entities['user_mentions'])[1]:]
        return status
    
    def start(self):
        ''' Starts the bot '''
        self.logger.info('Starting bot..')
        self.thread.start()
    
    def stop(self):
        ''' Stops the bot '''
        self.logger.info('Stopping bot..')
        self.running.set()
        self.thread.join()
    
    def tweet(self, text: str, replyto=None):
        ''' Helps sending tweets ''' 
        self.logger.getChild('__process_requests__').debug("Sending: {0}{1}".format((" {0} -> ".format(replyto.id)) if replyto else '' , text))
        try:
            if len(text) >= 280 :
                text = "{0}...".format(text[:270])
            if replyto :
                self.api.update_status(status=text, in_reply_to_status_id=replyto.id, auto_populate_reply_metadata=True)
            else:
                self.api.update_status(status=text)
        except tw.RateLimitError:
            self.logger.warning("Rate-limited by the twitter api! Retrying after {0}s..".format(self.ratelimit_wait))
            sleep(self.ratelimit_wait)
            self.tweet(text, replyto)
        except tw.TweepError:
            self.logger.exception("Failed to send the tweet")

def main():
    import importlib as imp
    import pkgutil as pk
    import os, signal, sys
    from argparse import ArgumentParser

    parser = ArgumentParser(description="AI chat bot for Twitter")
    parser.add_argument('-c', '--config', help="Config file (default: config.json)", dest='config', nargs=1, type=str, default=[CONFIG_FILE])
    parser.add_argument('-m', '--mods-dir', help="Modules directory (default: ./mods)", dest='mod_dir', nargs=1, type=str, \
        default=[os.path.dirname(os.path.realpath(sys.argv[0])) + os.sep + MODULES_DIR])
    parser.add_argument('-d', '--debug', help="Enable debug", action='store_true', dest='debug')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()

    # Setup basic logger configurations
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(name)-12s - %(message)s', level=(logging.DEBUG if args.debug else logging.INFO))

    # Try reading the config file
    try:
        config = Config(args.config[0])
    except ConfigParseError as ex :
        logging.getLogger('main').fatal(ex)
        exit(2)

    # Find all modules 
    sys.path.append(args.mod_dir[0])
    modules = []
    for _, name, isPkg in pk.iter_modules([os.path.realpath(args.mod_dir[0])]):
        if not isPkg :
            mod = imp.import_module(name)
            mod.__modname__ = getattr(mod, 'MODULE_NAME', mod.__name__[len(mod.__package__)+1:])
            mod.__modver__ = getattr(mod, 'MODULE_VERSION', '0.1')
            modules.append(mod)
    logging.getLogger('main').info('Found Modules: {0}'.format([x.__modname__ for x in modules]))

    # Handler for bot requests
    def onBotRequest(bot: TwitterBot, tweet):
        for mod in modules:
            if hasattr(mod, 'onTweetReceived'):
                try:
                    mod.onTweetReceived(bot, getattr(config, mod.__modname__, None), logging.getLogger("[{0}]".format(mod.__modname__)), tweet)
                except:
                    logging.getLogger("[{0}]".format(mod.__modname__)).exception("Error while processing the tweet!")

    # Init bot
    try:
        bot = TwitterBot(config, onBotRequest)
    except TwitterConnectionError as ex:
        logging.getLogger('main').error(ex)
        exit(4)

    # Loading all the modules
    for mod in modules:
        logging.getLogger('main').info("Loaded: {} (v{})".format(mod.__modname__, mod.__modver__))
        if hasattr(mod, 'onModuleLoad'):
            try:
                mod.onModuleLoad(bot, getattr(config, mod.__modname__, None), logging.getLogger("[{0}]".format(mod.__modname__)))
            except:
                logging.getLogger("[{0}]".format(mod.__modname__)).exception("Error while loading module!")
    
    # Handler for interrupt and exit signal
    def onExitSignal(signal, frame):
        bot.stop()
        for mod in modules:
            logging.getLogger('main').info("Unloaded: {} (v{})".format(mod.__modname__, mod.__modver__))
            if hasattr(mod, 'onModuleUnload'):
                try:
                    mod.onModuleUnload(bot, getattr(config, mod.__modname__, None), logging.getLogger("[{0}]".format(mod.__modname__)))
                except:
                    logging.getLogger("[{0}]".format(mod.__modname__)).exception("Error while unloading module!")

    signal.signal(signal.SIGTERM, onExitSignal)
    signal.signal(signal.SIGINT, onExitSignal)
    bot.start()


if __name__ == '__main__' :
    main()
