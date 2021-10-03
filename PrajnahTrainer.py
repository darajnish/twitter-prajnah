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

from chatterbot import ChatBot
from chatterbot.comparisons import SpacySimilarity
from chatterbot.trainers import ChatterBotCorpusTrainer
from argparse import ArgumentParser

def get_database_uri(config):
    from os import environ
    if 'DATABASE_URL' in environ and len(environ['DATABASE_URL'])>0 :
        return environ['DATABASE_URL']
    elif config and config.get('db_uri', None) and len(config['db_uri'])>0 :
        return config['db_uri']
    else:
        raise ConnectionError("Failed to get database URI! Provide it in the config or through DATABASE_URL environment variable!")

def main():
    parser = ArgumentParser(description="Helps training the aitalk module with chat corpus files")
    parser.add_argument('-c', '--config', help="Config file (default: config.json)", dest='config', nargs=1, type=str, default=['config.json'])
    parser.add_argument('-f', '--file', help="Trainer file", dest='file', nargs=1, type=str)
    parser.add_argument('-n', '--name', help="Bot name", dest='name', nargs=1, type=str)
    parser.add_argument('-d', '--database', help="Database URI", dest='dburi', nargs=1, type=str)
    parser.add_argument('-V', '--version', action='version', version='%(prog)s 0.1')
    args = parser.parse_args()

    from TwitterPrajnah import Config
    config = Config(args.config[0])

    if not (len(args.file)>0 and len(args.file[0])>0) :
        raise Exception("No file to train!")
    
    if not (len(args.name)>0 and len(args.name[0])>0) :
        raise Exception("No bot name given!")
    
    if not (len(args.dburi)>0 and len(args.dburi[0])>0) :
        db_uri = get_database_uri(getattr(config, 'aitalk', None))
        if db_uri == None :
            raise Exception("No Database Url Provided!")
    else:
        db_uri = args.dburi[0]

    chatbot = ChatBot(
        args.name[0],
        logic_adapters = [ "chatterbot.logic.BestMatch", "chatterbot.logic.MathematicalEvaluation" ],
        statement_comparison_function = SpacySimilarity,
        storage_adapter='chatterbot.storage.SQLStorageAdapter',
        database_uri=db_uri
        )
    trainer = ChatterBotCorpusTrainer(chatbot)
    trainer.train(args.file[0])
    exit(0)

if __name__ == '__main__' :
    main()
