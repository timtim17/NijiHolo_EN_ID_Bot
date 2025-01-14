from tweety.types import *

def url(t: Tweet):
	return f'https://twitter.com/{t.author.username}/status/{t.id}'

def print_tweets(tweets: list[Tweet | TweetThread]):
	print(f'{len(tweets)} tweets:')
	for t in tweets:
		if isinstance(t, Tweet):
			print(f'{t.date} : {url(t)} :', end=' ')

			if t.is_retweet:
				print(f'RT ({t.retweeted_tweet.author.username})', end=' ')

			if t.is_reply:
				print(f'is reply!', end=' ')
			if t.replied_to is not None:
				print(f'reply to {t.replied_to.author.username}', end=' ')

			print("m=" + ",".join([x.username for x in t.user_mentions]))
		elif isinstance(t, TweetThread):
			print('-----------TTd----------')
			print_tweets(t.tweets)
			print('-----------end----------')