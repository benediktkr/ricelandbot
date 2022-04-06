from asyncpraw.models import Comment, Subreddit

mail = "📫️   "
report = "⚠️   "


def get_reddit_u_r(item):
    if item is None:
        return "UNKNOWN"
    elif isinstance(item, Subreddit):
        ur = f"/r/{item}"
    else:
        ur = f"/u/{item.name}"
    return f"[{ur}](https://www.reddit.com{ur})"


def quote_lines(body):
    return ">" + "\n>".join(body.split("\n"))


async def modmail(reddit, sub, matrix):
    subreddit = await reddit.subreddit(sub)
    s_e = reddit.config.custom['skip_existing']
    ignore_automod = reddit.config.custom.get("ignore_automod", False)

    async for item in subreddit.mod.stream.unread(skip_existing=s_e):
        author = get_reddit_u_r(item.author)
        dest = get_reddit_u_r(item.dest)
        subject = item.subject
        body = quote_lines(item.body)

        if item.author.name == "AutoModerator" and ignore_automod:
            continue

        if "has received reports" in item.body:
            # handled by riceland.reddit.reports
            continue

        header = f"{mail} **{subject}** <br>{author} -> {dest}"
        msg = f"{header}\n{body}"
        await matrix.sendmsg(msg)


async def reports(reddit, sub, matrix):
    subreddit = await reddit.subreddit(sub)
    s_e = reddit.config.custom['skip_existing']

    async for item in subreddit.mod.stream.reports(skip_existing=s_e):
        author = get_reddit_u_r(item.author)
        link = item.permalink
        if isinstance(item, Comment):
            body = quote_lines(item.body)
            header = f"{report} [reported comment]({link}) by {author}"
            msg = f"{header}\n{body}"
        else:
            header = f'{report} submission "[{item.title}](link)" by {author}'
            if item.is_self:
                selftext = quote_lines(item.selftext)
                msg = f"{header}\n{selftext}"
            else:
                msg = header
        await matrix.sendmsg(msg)
