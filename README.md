# Splat2 Assistant
This is an application created to help view player statistics and information on stages and SplatNet. Located at (splat2assistant.herokuapp.com)[http://splat2assistant.herokuapp.com/].

Requires Python3 and the requests, Pillow, Flask, livereload, and WTForms modules.

To use, run `python3 splat2assistant_web.py`.

## A Note on Usage
In order to get data from NSOnline, you need to capture your identifying cookie, or the `iksm_session`. [I wrote a guide on doing this here.](https://bitbucket.org/chococakes/splathelper/wiki/Using%20Fiddler%20to%20Get%20Your%20SplatNet%20Cookie) It takes about ten minutes for the first time and four for every time after that. My cookies seem to expire after a day and a half, but doing this every day gets tedious. You shouldn't have much to worry about - as long as you update at least once every fifty battles, you shouldn't lose any data.

Just enter in the cookie on the home page. It's not live, but as long as the cookie works, if you refresh the page, it will update the data.

## Features
The website allows you to get data from a cookie, but once you've done that once, you'll be given an ID. You can use that ID in the future to view saved data without a cookie, although you can't update data with it.

1. View kills, deaths, plays, wins, losses, and win/play ratio for weapons used.
2. View list of battles.
3. View gear, level, nickname, weapon details, and more of players you've played with.
