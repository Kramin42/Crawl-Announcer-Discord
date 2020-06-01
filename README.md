# Crawl-Announcer-Discord

### Installation
- Run `pipenv install` (may need to install pipenv first)
- Create a file called `TOKEN` with your discord bot token in the same directory as `main.py`
- Run with `pipenv run python main.py`


### Commands
- `$addchannel <channel>` (e.g. `$addchannel #milestones`), enables mielstone announcement in a channel. Server admin permissions required to use this command.
- `$addnick <crawl online nick>` (e.g. $addnick Kramin), adds user name for announcement. Must be used in the announcement channel.
