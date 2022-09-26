from datetime import datetime
import platform

import pytz

from twapi import *
import talent_lists

class TalentTweet:
    @staticmethod
    def deserialize(serialized_str: str):
        tokens = serialized_str.split()
        if len(tokens) < 3:
            raise ValueError('not enough tokens to reconstruct a TalentTweet')
        
        tweet_id, author_id = int(tokens[0]), int(tokens[1])
        date_time = datetime.fromtimestamp(float(tokens[2]), tz=pytz.utc)
        
        mentions = set()
        reply_to = None
        quote_retweeted = None

        mode = ''
        for i in range(3, len(tokens)):
            if len(tokens[i]) == 1 and not tokens[i].isnumeric(): # mode switch
                mode = tokens[i]
                continue
        
            if tokens[i].isnumeric():
                if mode == 'm': # mentions
                    mentions.add(int(tokens[i]))
                    continue
                if mode == 'r': # reply_to
                    reply_to = int(tokens[i])
                    continue
                if mode == 'q': # quote_retweeted
                    quote_retweeted = int(tokens[i])
        
        return TalentTweet(
            tweet_id=tweet_id, author_id=author_id,
            date_time=date_time, mrq=(mentions, reply_to, quote_retweeted)
        )
        

    def __init__(self, tweet_id: int, author_id: int,date_time: datetime, mrq: tuple):
        self.tweet_id, self.author_id = tweet_id, author_id
        self.date_time = date_time
        self.mentions = mrq[0]
        self.reply_to = mrq[1]
        self.quote_retweeted = mrq[2]

        # all users involved, except for the author
        self.all_parties = {self.reply_to, self.quote_retweeted}
        self.all_parties.update(self.mentions)
        try:
            self.all_parties.remove(None)
            self.all_parties.remove(self.author_id)
        except:
            pass
    

    def __repr__(self) -> str:
        return (
            f'{self.tweet_id} from {util.get_username(self.author_id)}):\n'
            f'{self.get_datetime_str()}\n'
            f'{self.get_all_parties_usernames()}\n'
            f'mentions: {self.mentions}\n'
            f'reply_to: {self.reply_to}\n'
            f'quote_retweeted: {self.quote_retweeted}\n'
            f'Cross-company: {self.is_cross_company()}\n'
            f'{self.serialize()}\n'
            f'======================================================'
        )
    
    # Serialized one-liner format:
    # {tweet} {author} {time in seconds since epoch} m {mention_set} r {reply_to_author} q {quote_retweet_author}
    def serialize(self):
        s = f'{self.tweet_id} {self.author_id} {self.date_time.timestamp()} '
        if len(self.mentions) > 0:
            s += 'm '
            for id in self.mentions:
                s += f'{id} '
        if self.reply_to:
            s += f'r {self.reply_to} '
        if self.quote_retweeted:
            s += f'q {self.quote_retweeted} '
        return s[:-1]

    def is_cross_company(self):
        for other_id in self.all_parties:
            if self.author_id in talent_lists.holo_en:
                if other_id in talent_lists.niji_en or other_id in talent_lists.niji_exid:
                    return True
            if self.author_id in talent_lists.niji_en:
                if other_id in talent_lists.holo_en or other_id in talent_lists.holo_id:
                    return True
            if self.author_id in talent_lists.holo_id:
                if other_id in talent_lists.niji_en:
                    return True
            if self.author_id in talent_lists.niji_exid:
                if other_id in talent_lists.holo_en:
                    return True
        return False
    
    def get_all_parties_usernames(self):
        if len(self.all_parties) > 0:
            s = str()
            for id in self.all_parties:
                s += f'{util.get_username(id)}, '
            return s[0:-2]

        return 'none'

    def get_datetime_str(self):
        unpad = '#' if platform.system() == 'Windows' else '-'
        return self.date_time.strftime(f'%b %{unpad}d %Y, %{unpad}I:%M%p (%Z)')


class TalentAPITweet(TalentTweet):
    def __init__(self, tweet_id=None, tweet=None, mrq: tuple=None):
        if tweet and mrq:
            self.tweet = tweet
        elif tweet_id:
            tweet_id = int(tweet_id)
            resp = TwAPI.instance.get_tweet_response(tweet_id)
            self.tweet = resp.data
            mrq = TwAPI.get_mrq(self.tweet, resp)
        else:
            raise ValueError('did not supply sufficient tweet information')

        TalentTweet.__init__(
            self,
            tweet_id=self.tweet.id,
            author_id=self.tweet.author_id,
            date_time=self.tweet.created_at,
            mrq=mrq
        )
    
    def __repr__(self) -> str:
        return (
            f'{self.tweet_id} from {util.get_username(self.author_id)}:\n'
            f'{self.tweet.text}\n'
            f'------------------------------------------------------\n'
            f'{self.get_datetime_str()}\n'
            f'{self.get_all_parties_usernames()}\n'
            f'mentions: {self.mentions}\n'
            f'reply_to: {self.reply_to}\n'
            f'quote_retweeted: {self.quote_retweeted}\n'
            f'{self.serialize()}\n'
            f'Cross-company: {self.is_cross_company()}\n'
            f'======================================================'
        )