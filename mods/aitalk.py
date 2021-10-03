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

MODULE_NAME = 'aitalk'
MODULE_VERSION = '0.1'

class AITalk:
    def __init__(self, bot, config, logger):
        self.logger = logger.getChild('AITalk')
        from chatterbot import ChatBot
        from chatterbot.comparisons import SpacySimilarity

        db_uri = self.__get_database_uri__(config)

        self.chatbot = ChatBot(
            name = bot.me.name,
            logic_adapters = [ "chatterbot.logic.BestMatch", "chatterbot.logic.MathematicalEvaluation" ],
            statement_comparison_function = SpacySimilarity,
            storage_adapter = 'chatterbot.storage.SQLStorageAdapter',
            database_uri = db_uri
            )
        self.logger.debug("AI Talk Bot initalized with name: {}".format(bot.me.name))
    
    def __get_database_uri__(self, config):
        from os import environ
        if 'DATABASE_URL' in environ and len(environ['DATABASE_URL'])>0 :
            self.logger.debug("Detected DATABASE_URL: {}".format(environ['DATABASE_URL']))
            return environ['DATABASE_URL']
        elif config and config.get('db_uri', None) and len(config['db_uri'])>0 :
            return config['db_uri']
        else:
            raise ConnectionError("Failed to get database URI! Provide it in the config or through DATABASE_URL environment variable!")

    def gen_statement(self, text, in_response_to=None):
        Statement = self.chatbot.storage.get_object('statement')
        statement_search_text = self.chatbot.storage.tagger.get_text_index_string(text)
        in_response_to_search_text = ''
        if in_response_to :
            in_response_to_search_text = self.chatbot.storage.tagger.get_text_index_string(in_response_to)
        return Statement(
            text=text,
            search_text=statement_search_text,
            in_response_to=in_response_to,
            search_in_response_to=in_response_to_search_text
        )
    def respond(self, text, in_response_to=None, read_only=False):
        response =  self.chatbot.get_response(text, read_only=True)
        if not read_only :
            if in_response_to :
                self.learn(text, in_response_to)
            else:
                if len(list(self.chatbot.storage.filter(text=text))) == 0 :
                    self.chatbot.storage.create(**self.gen_statement(text=text).serialize())
            self.chatbot.learn_response(response)
        return response.text
    def learn(self, text, in_response_to):
        if len(list(self.chatbot.storage.filter(text=in_response_to))) == 0 :
            self.chatbot.storage.create(**self.gen_statement(text=in_response_to).serialize())
        return self.chatbot.learn_response(self.gen_statement(text=text, in_response_to=in_response_to)).text

def onModuleLoad(bot, config, logger):
    try:
        bot.aitalk = AITalk(bot, config, logger)
    except:
        logger.exception("Error while initializng {}!".format(MODULE_NAME))
        bot.aitalk = None

def __respondable__(bot, tweet):
    return bot.aitalk != None and (tweet.in_reply_to_screen_name == bot.username or tweet.in_reply_to_status_id == None) and \
        (not tweet.just_text.strip().startswith('!'))

def __tweet_context__(bot, tweet):
    return bot.get_tweet(bot.get_tweet(tweet.in_reply_to_status_id).in_reply_to_status_id, ext=True)

def onTweetReceived(bot, config, logger, tweet):
    if __respondable__(bot, tweet) :
        logger.info('Talk [{0}] responding...'.format(tweet.user.screen_name))
        if (config and ((not config.get('restrict_learn', True)) or tweet.user.screen_name in config.get('masters', []))) :
            if tweet.just_text.strip().startswith('learn:') :
                resp = bot.aitalk.learn(tweet.just_text.replace('learn:', '').strip(), __tweet_context__(bot, tweet).just_text)
                bot.tweet("Okay! {0}".format(resp), tweet)
            else:
                if tweet.in_reply_to_status_id == None :
                    bot.tweet(bot.aitalk.respond(tweet.just_text), tweet)
                else:
                    bot.tweet(bot.aitalk.respond(
                        tweet.just_text,
                        in_response_to = bot.get_tweet(tweet.in_reply_to_status_id).just_text
                    ), tweet)
        else:
            bot.tweet(bot.aitalk.respond(tweet.just_text, read_only=True), tweet)
        logger.info('Talk: {0}'.format(tweet.user.screen_name))
