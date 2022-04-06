import http.server
import time
from urllib.parse import urlparse

import asyncpraw
from loguru import logger

"""
based on: https://gist.github.com/d-schmidt/d79bf351a9c63872507aceea5cfae34c
https://github.com/reddit/reddit/wiki/API
http://praw.readthedocs.io/en/latest/getting_started/authentication.html
    to get a refresh_token
    - create an app at reddit https://www.reddit.com/prefs/apps/
    - create a praw.ini:
[bot]
client_id=clientIdFromPrefsApps
client_secret=clientSecretFromPrefsApps
user_agent=praw:yourbotname:1.0 (by /u/yourusername)
    - python refreshToken.py
    - copy refreshToken and update praw.ini
"""

listenaddr = "192.168.21.10"
port = 65010
redirect_uri = f'http://{listenaddr}:{port}/authorize_callback'
reddit = asyncpraw.Reddit('riceland', redirect_uri=redirect_uri)
oauth_state = str(int(time.time()))

# https://asyncpraw.readthedocs.io/en/stable/tutorials/refresh_token.html#refresh-token
scopes = [
    'edit',             # edit comments/posts
    'flair',            # flair for user
    'identity',         # reddit username and signup date
    'modconfig',        # sub settings, sidebar, etc
    'modcontributors',  # manage approed uers, ban/unban, mute
    'modflair',         # assign and manages user flairs
    'modlog',           # access modlogs
    'modmail',          # manage modmail
    'modposts',         # approve, remove, nsfw, etc content in subs
    'modtraffic',       # traffic stats
    'privatemessages',  # acces inbox and send pms
    'read',             # access posts and comments
    'report',           # report content/users
    'save',             # save/unsave posts
    'submit',           # submit links and comments
    'vote',             # vote on posts/comments
]


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        query = urlparse(self.path).query
        query_parts = dict(qc.split("=") for qc in query.split("&"))
        if oauth_state != query_parts['state']:
            logger.error(
                f'wrong state: {oauth_state} != {query_parts["state"]}')
            self.wfile.write(bytes("wrong state", "utf8"))
            raise SystemExit(1)
        code = query_parts['code']
        refresh_token = reddit.auth.authorize(code)
        text = f"code: {code} refresh_token: {refresh_token}"
        logger.success(text)
        self.wfile.write(bytes(text, "utf8"))


def main():
    url = reddit.auth.url(scopes, oauth_state, 'permanent')
    logger.info(url)
    callback = http.server.HTTPServer((listenaddr, port), CallbackHandler)
    callback.timeout = None
    logger.info(f"listening on {redirect_uri}")
    callback.handle_request()
    callback.server_close()
