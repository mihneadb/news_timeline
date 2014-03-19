import feedparser
import requests
import json

from twitter import *

d = feedparser.parse('http://rss.nytimes.com/services/xml/rss/nyt/InternationalHome.xml')

OAUTH_TOKEN = '76676542-MtVUCk5nwS2gG4ITiRnqXcPEJt3FZfUb40Sx5BFHc'
OAUTH_SECRET = 'WBUpsrvlDkoINp1VcQpAwVflCLr3nkwZDDRJinIhfnu36'
API_KEY = '6qWnsulmUskS7zSXHQg'
API_SECRET = 'VEFLsUcCm1aAvOKem1pivlKgfKIB6S0PJb9dP8gDmA'

BING_ACCT_KEY = 'bYRbTbIK8xd3lbtQsFgvD+OxIikQrEz0fGCbgg0vLU0='

tw = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET,
                        API_KEY, API_SECRET))

SENTIMENT = {
    0: 'negative',
    2: 'neutral',
    4: 'positive'
}

URL = 'http://www.sentiment140.com/api/bulkClassifyJson?appid=mihnea@linux.com'


def make_request(tweets):
    body = {'data': tweets}
    response = requests.post(URL, data=json.dumps(body))
    return response

def process_response(response):
    data = response.json()['data']
    for tweet in data:
        tweet['sentiment'] = SENTIMENT[tweet['polarity']]
    return data

def remove_title_words(tweet, title):
    for word in title.split():
        tweet['text'] = tweet['text'].replace(word, '')
    return tweet

def get_photos(title, limit=20):
    base_url = 'https://api.datamarket.azure.com/Bing/Search/v1/Image'

    query = ' '.join([w for w in title.split() if len(w) > 2])
    params = {
        '$format': 'json',
        'Query': "'" + query + "'",
    }

    r = requests.get(base_url, params=params, auth=('', BING_ACCT_KEY))

    data = r.json()['d']['results']
    photos = [
        {
            'source_url': p['SourceUrl'],
            'photo_url': p['MediaUrl']
        }
        for p in data
    ]
    return photos[:limit]

def clean_tweets(tweets):
    return [
        {
            'text': t['text'],
            'id': t['id'],
            'author': t['user']['screen_name'],
            'html_url': 'https://twitter.com/%s/status/%s' % (t['user']['screen_name'], t['id']),
        }
        for t in tweets
    ]

def process_story(rss_entry):
    # original data from NYTimes rss
    story = {
        'title': rss_entry.title,
        'datetime': rss_entry.published,
        'summary': rss_entry.summary,
        'tags': [t.term for t in rss_entry.tags],
        'caption': [i['url'] for i in rss_entry.media_content][0],
        'link': rss_entry.id,
        'author': rss_entry.author
    }

    # sample tweet
    query = ' OR '.join([s for s in story['title'].split() if len(s) > 2])
    tweets = tw.search.tweets(q=query, count=100, result_type='mixed')
    story['tweets'] = clean_tweets(tweets['statuses'])

    # some photos
    photos = get_photos(story['title'])
    story['photos'] = photos

    # sentiment from twitter
    tweets = [{'text': t['text']} for t in tweets['statuses']]
    tweets = [remove_title_words(t, story['title']) for t in tweets]
    tagged = process_response(make_request(tweets))
    sentiment = {
        'negative': 0,
        'positive': 0,
        'neutral': 0,
        'total': 0
    }
    for tweet in tagged:
        sentiment[tweet['sentiment']] += 1
        sentiment['total'] += 1
    story['sentiment'] = sentiment

    return story

stories = []
for e in d.entries:
    try:
        story = process_story(e)
        stories.append(story)
    except:
        pass
print(json.dumps(stories, indent=2))
