# DaniMoon-Vote-Bot
A python discord bot using pycord. Built for playing a play-by-post variant of Blood on the Clocktower.

## Installing and Running
In order to use this program, make sure your enviroment is set up.
### Step 1:
Download python in one way or another ([Python Site](https://www.python.org/) or [PyCharm](https://www.jetbrains.com/pycharm/)

### Step 2:
Download the required packages using
```
python -m pip install py-cord
python -m pip install dotenv
```

### Step 3:
Create a file with the name ".env" and populate it with the following details (replacing the things in parentheses with actual values):
#.env
DISCORD_TOKEN=(Token of your bot, found through discord's developer portal)
DISCORD_GUILD=(The ID of your server, found by right clicking and hitting "Copy Server ID")
NOMINATIONS_CHANNEL=(This and all following are the ids for their respective names, found similarly to the Server ID)
VOTING_CHANNEL=("")
GENERAL_CHANNEL=("")
PUBLIC_ACTIONS_CHANNEL=("")
SPECTATOR_ROLE=("")

### Step 4:
Run the python script!
