# TwitterPrajnah
_Prajñāh (प्राज्ञः) meaning, the intelligent one_

[ChatterBot](https://github.com/gunthercox/ChatterBot) based AI chat bot for [Twitter](https://twitter.com/) with [Spacy](https://spacy.io/) NLP backend


This bot can can run on Twitter as a user and it can accept texts from those who tag it in their tweet, and it can then process their texts by matching their texts against various Logic Adapters (using **ChatterBot** API with **Spacy NLP**) and producing a response accordingly, which will then be sent to Twitter user as a reply. It can even learn from the responses of the people who interact with it, though learning can be controlled using its configuration. Additionally, the bot can be trained with a basic [chat-corpus](https://github.com/darajnish/ChatterBot/blob/master/docs/corpus.rst) used for training **ChatterBot** bots. Initially, the user needs to go through the login process to acquire **access_key** and **access_secret**, which then the user needs to save into the config to avoid logging in each time the bot starts.  Additional modules can be easily accommodated into the bot by simply placing the respective python script of the module into the modules directory, and the bot picks them up while booting.

### Features

* Interactive AI chat bot for Twitter
* Learns from the conversations of the people who interact with it
* Learning from people can be limited and controlled to avoid spams
* Simple and clear command line based login
* Rate limit handled protection on Twitter API
* Support for auto loading additional / custom modules
* Configure any custom module with extensible config
* [Heroku](https://www.heroku.com/) dynos compatible (RAM >= 1G)

## Requirements

##### For running the script

- [Python](https://www.python.org/downloads/) 3.8 or above
- [pip](https://pip.pypa.io/en/stable/installing/) 20.1 or above (To installs the dependencies below)
- [Tweepy](https://github.com/tweepy/tweepy) 3.9 or above
- [ChatterBot](https://github.com/darajnish/ChatterBot) (for **aitalk** module)
- [ASTEVAL](https://newville.github.io/asteval/) 0.9.23 or above (for **calc** module)

##### For making the bot work

- [Twitter developer](https://developer.twitter.com/) API key and API secret: 
- Twitter account to be used as a Bot
- [PostgreSQL Server](https://www.postgresql.org/download/) / [MySQL Server](https://mariadb.org/download/) (for **aitalk** module i.e ChatterBot can its store data)
- RAM ≥ 1GB

## Running

First, install the required dependencies if you haven't already installed. All the dependencies can be installed using **pip** (using a terminal in this directory) as follows.

```bash
pip install -r requirements.txt
```



Now, create a json based config file for the program, with all required values for all API keys, you may wish to skip the `access_key` and `access_secret` fields as you may first want to go through the login process and then want to store the acquired keys permanently within the config. The example config file `config.json.example` will help you making your own config file, make sure the config file is in json format and ends with `.json` file extension. For ex: `my-config.json`, `/some/path/my-config.json`(default config file: `config.json`, in the same directory as the script)

**Example config.json**

```json
{
    "api_key" : "TWITTER-DEVELOPER-APP-KEY",
    "api_secret" : "TWITTER-DEVELOPER-APP-SECRET",
    "access_key" : "TWITTER-AUTH-ACCESS-KEY",
    "access_secret" : "TWITTER-AUTH-ACCESS-SECRET",
    "sleep_time" : 15,
    "ratelimit_wait" : 15,
    "aitalk" : {
        "db_uri" : "protocol://user:password@hostname:port/database",
        "masters" : ["TWITTER-USERNAME"],
        "restrict_learn" : false
    }
}
```



**Config Values**


| **Key**                 | **Description**                                                                                                                                                                                                                          |
|:-----------------------:|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `api_key`               | Twitter developer API Key (Required)                                                                                                                                                                                                     |
| `api_secret`            | Twitter developer API Secret (Required)                                                                                                                                                                                                  |
| `access_key`            | Twitter authentication access key (acquired after a successful login)                                                                                                                                                                    |
| `access_secret`         | Twitter authentication access secret (acquired after a successful login)                                                                                                                                                                 |
| `sleep_time`            | The time in minutes to wait before seeking newer tweets responding to them (default: 1)                                                                                                                                                  |
| `ratelimit_wait`        | The time in minutes to wait before trying again when rate-limited by the Twitter server (default: 15)                                                                                                                                    |
| `aitalk.db_uri`         | URI of a PostgreSQL or MySQL server used by the bot to store data (Required! can be set using DATABASE_URL environment var)                                                                                                              |
| `aitalk.masters`        | List of twitter usernames who're allowed to teach the bot even if `restrict_learn` is set `true`                                                                                                                                         |
| `aitalk.restrict_learn` | Setting this `true` disables learning from unknown twitter handles except those whose usernames are in `masters` list, though the bot will still continue to respond to requests from unknown handles using just the already learnt data |



Next, Make sure the **PostgreSQL** / **MySQL** server is setup with a username and password and it's running.

The bot can be configured to use the database server either by putting the database URI in the config, or through defining `DATABASE_URL` as environment variable which holds the URI for the database.

The format for URI for `DATABASE_URL` should be like,

```
<protocol>://<user>:<password>@<hostname>:<port>/<database>
```




With all setup, start the bot feeding the path of your config file, and optionally the path to the modules directory where all the python scripts for modules are kept (including **aitalk**), the default modules directory is `./mods` (the `mods` directory in the same directory as the main script) and the module **aitalk** is already present in the directory so you may start the bot by,

```bash
python TwitterPrajnah.py --config /some/path/my-config.json
```

**OR**

```bash
python TwitterPrajnah.py --config my-config.json
```


However, if you wish to shift the modules directory to some other location, you must use the option `--mods-dir` while running the script and provide the path to the modules directory,
```bash
python TwitterPrajnah.py --config my-config.json --mods-dir /path/to/modules_directory
```


Running using the `DATABASE_URL` environment variable on the same line,

```bash
DATABASE_URL="<protocol>://<user>:<password>@<hostname>:<port>/<database>" python TwitterPrajnah.py --config my-config.json
```


When the bot runs for the first time without having the values for `access_key` and `access_secret` in the config, it tries to help the user login through the browser and get the auth code which then will be used to acquire `access_key` and `access_secret` keys,

```bash
Paste this URL in browser and get the auth code: https://api.twitter.com/oauth/authorize?oauth_token=xxxxxxxxxxxxxxxxxxxxxxxxxxx
CODE:
```

Then, we just need to put the URL provided in the output `https://api.twitter.com/oauth/authorize?oauth_token=xxxxxxxxxxxxxxxxxxxxxxxxxxx`in a web browser and follow all the login procedures, and finally paste the code given by Twitter into the line `CODE:`. 

```
Paste this URL in browser and get the auth code: https://api.twitter.com/oauth/authorize?oauth_token=xxxxxxxxxxxxxxxxxxxxxxxxxxx
CODE: 1234

Save these into config!
Access Token: 1234567890123456789-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Access Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

```

When, the auth code gets accepted, `access_key` and `access_secret` will be displayed below, which should be put into the config file so that the next time it doesn't ask for login and uses the keys provided in the config to login.



#### Setting up on Heroku

The bot is already compatible with heroku dynos, and this repository already contains files for **heroku/python** buildpack, `requirements.txt`, `runtime.txt` and `Procfile`.

Just create a config file as described above and update the config filename in `Procfile` arguments (default filename: `config.json`) and push the contents to Heroku git.



#### Debugging

To run the bot in debug mode, just pass the flag `-d`  or `--debug` in the arguments.

```bash
python TwitterPrajnah.py --debug --config my-config.json
```



###  Training

Training the bot with a chat corpus is easy and can be done using `PrajnahTrainer.py` script. 
First create a chat corpus in **yaml** file, more details on creating chat corpus is given in the documentation [here](https://github.com/darajnish/ChatterBot/blob/master/docs/corpus.rst) 
Then, just use the script `PrajnahTrainer.py` to start training the bot with the corpus file, providing the config file including the database URI into `aitalk.db_uri` key, with the path to corpus yaml file and the name of bot,

```bash
python PrajnahTrainer.py --config config.json --name Prajnah --file corpus/example.yml
```

You can even provide database URI as an argument to the trainer script,

```bash
python PrajnahTrainer.py --config config.json --name BotName --database "protocol://user:password@hostname:port/database" --file /path/to/corpus.yml
```

Depending upon the length of the corpus, the script may take from a few seconds to a couple of minutes, and once the bot is trained it's ready to interact with the people on Twitter.



###  Custom Modules

The Bot supports adding custom modules to add new capabilities to the bot. All the modules reside in the modules directory (default: `./mods`) and each time the bot runs, the modules are detected and loaded, and get unloaded each time the bot exits.

A basic module is a simple python script file placed inside the modules directory with this basic structure:

```python
MODULE_NAME = 'modX' # Module Name
MODULE_VERSION = '0.1' # Module Version

def onModuleLoad(bot, config, logger):
    ''' This function runs for once when the bot is started
        bot: the instance of bot
        config: config for the current module if defined in the config file or None
        logger: a logger in the name of this module
    '''
    logger.info("Module loaded!")
    
def onTweetReceived(bot, config, logger, tweet):
    ''' This function runs each time the bot receives a request from a Twitter user
        bot: the instance of bot
        config: config for the current module if defined in the config file or None
        logger: a logger in the name of this module
        tweet: a object of tweepy Status containing details of the current tweet
    '''
    logger.info("Tweet received! {}: {}".format(tweet.user.screen_name, tweet.text))

def onModuleUnload(bot, config, logger):
    ''' This function runs for once when the bot exits
        bot: the instance of bot
        config: config for the current module if defined in the config file or None
        logger: a logger in the name of this module
    '''
    logger.info("Module unloaded!")

```

After creating the module, save it into the modules directory as a python file (example: `mods/test_mod.py`), and it'll get loaded and execute whenever a tweet is received.

Every module can be configured directly from the config file, by creating a key with the respective module name and placing all key-value configurations related to the module inside it. For example, how we've created a key for our example module **modX** below,

```json
{
    "api_key" : "TWITTER-DEVELOPER-APP-KEY",
    "api_secret" : "TWITTER-DEVELOPER-APP-SECRET",
    "access_key" : "TWITTER-AUTH-ACCESS-KEY",
    "access_secret" : "TWITTER-AUTH-ACCESS-SECRET",
    "sleep_time" : 15,
    "ratelimit_wait" : 15,
    "aitalk" : {
        "db_uri" : "protocol://user:password@hostname:port/database",
        "masters" : ["TWITTER-USERNAME"],
        "restrict_learn" : false
    },
    
    "modX" : {
        "key1" : 1,
        "key2" : "value"
    }
}
```

## Contributing

All kinds of contributions towards the improvement and enhancement of this project are welcome. Any valuable pull request for fixing an issue or enhancing the project are welcome. You can even help by [reporting bugs](https://github.com/darajnish/twitter-prajnah/issues/new/choose) and creating issues for suggestions and ideas related to new improvements and enhancements.

##  Credits

- [ChatterBot](https://github.com/gunthercox/ChatterBot) for the backbone library for this project and a good documentation of how to use it

## License

This project is under the [MIT License](LICENSE)
