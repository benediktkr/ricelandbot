import asyncio
import os
from argparse import ArgumentParser

import asyncpraw
from loguru import logger

from ricelandbot.matrix import MatrixWebhook
from ricelandbot.reddit import modmail, reports


async def asyncmain(args):
    reddit = asyncpraw.Reddit("riceland")
    if args.subreddit:
        sub = args.subreddit
    else:
        sub = reddit.config.custom['subreddit']
    reddit.config.custom['skip_existing'] = not args.show_existing
    matrix = MatrixWebhook(reddit.config.custom)

    try:
        # returns aggregated list of return values
        await asyncio.gather(
            asyncio.create_task(modmail(reddit, sub, matrix)),
            asyncio.create_task(reports(reddit, sub, matrix))
        )
    except asyncio.CancelledError:
        pass

    await reddit.close()


def main():
    parser = ArgumentParser()
    parser.add_argument("-r", "--subreddit")
    parser.add_argument("-s", "--show-existing", action="store_true")
    args = parser.parse_args()

    logfile = os.environ.get("LOGFILE")
    if logfile is not None:
        logger.remove()
        logger.add(logfile)

    try:
        asyncio.run(asyncmain(args))
    except KeyboardInterrupt:
        logger.info("exiting...")
