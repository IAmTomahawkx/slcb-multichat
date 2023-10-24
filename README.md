[![development status | 3 - Alpha](https://img.shields.io/badge/Development%20Status-3%20--%20Alpha-red)](https://pypi.org/classifiers/)
[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![license](https://img.shields.io/github/license/IAmTomahawkx/slcb-multichat)
___
<h1 align="center">
MultiChat
</h1>
<p align="center">
<sup>
View your Twitch chat right in the Streamlabs Chatbot from YouTube mode
</sup>
</p>

___

This script exists to allow streamers who stream on both Twitch and YouTube to see their Twitch chat while the bot is in YouTube Mode.
At this time, that's all it does.

## How to use it

This script works by running a background process that connects to Twitch. That background task will need you to have Python 3.10 or 3.11 installed.
You can get Python 3.11 [Here](https://www.python.org/ftp/python/3.11.6/python-3.11.6-amd64.exe).
If you change the install location of Python (which I do not recommend doing), you'll need to set the new location in the script settings. \
By default, the bot expects the install location to be `%LOCALAPPDATA%\Programs\Python\Python311\pythonw.exe`. \
If you decide to use 3.10 you'll need to change that to `%LOCALAPPDATA%\Programs\Python\Python310\pythonw.exe`.

## The Settings
This is a very simple script, and as such only has a couple settings.
The `Refresh Rate` setting changes how often the script fetches info from the background process.
Numbers smaller than 1000 (1 second) may hurt performance. \
you should make sure to always click away from this script and click back onto it when changing settings.
This will prevent you from overriding changes the script makes to the tokens (generation, refreshing, etc.)

The `Python Location` setting is explained above.
It should point to a `pythonw.exe` file, unless you want to see debugging information, in which case point it to `python.exe`.

The `Generate Token` button should be used to generate a token to log in to Twitch Chat with. 
It will open your web browser and direct you to Twitch for token generation. Afterward, you can close the tab.

The `tokens` dropdown contains the tokens fetched from the `Generate Token` button. You shouldn't need to touch these yourself.


## FAQ

### There's something I'd like to see that this script doesn't contain.
I'm open to feature requests, simply open an issue or ping me on discord: `@iamtomahawkx`.

### What about YouTube chat in Twitch mode?
YouTube's chat system is awful, and not something I want to touch. So no.