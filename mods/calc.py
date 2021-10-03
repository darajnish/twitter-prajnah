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

MODULE_NAME = 'calc'
MODULE_VERSION = '0.1'

def onModuleLoad(bot, config, logger):
    from asteval import Interpreter
    bot.calc = Interpreter(minimal=True, max_time=3)

def __respondable__(bot, tweet):
    return tweet.just_text.strip().startswith('!calc')

def onTweetReceived(bot, config, logger, tweet):
    if not __respondable__(bot, tweet):
        return
    
    res = ''
    try:
        res = str(bot.calc(tweet.just_text.replace('!calc', '', 1).strip()))
    except Exception as err:
        res = "Error: {0}".format(err)
    
    bot.tweet(res, tweet)
    logger.info('Eval: {0}'.format(tweet.user.screen_name))
