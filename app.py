from flask import Flask
import time
from selenium import webdriver
import textblob
import re
from selenium.webdriver.chrome.options import Options
import os


app = Flask(__name__)


# remove symbols and letters from tweet_elements
def clean_tweet(tweet):
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())


# determine sentiment for a statement using textblob
def sentiment(statement):
    x = textblob.TextBlob(str(statement))
    l = x.sentiment.polarity
    if l == 0:
        return "Neutral"
    elif l > 0:
        return "Positive"
    elif l < 0:
        return "Negative"


# scroll down page to load more content
def scrolldown(browser):
    for _ in range(10):
        browser.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)


# return list of text (of tweet_elements) extracted from list of WebDriverElement's
def get_tweet_text(tweet_elements):
    tweet_text = []
    for tweet in tweet_elements:
        try:
            tweet_text.append(clean_tweet(tweet.get_attribute("textContent")))
        except:
            continue
    return tweet_text


@app.route('/')
def main():
    return "Try giving a query"


@app.route('/<query>')
def hello(query):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    browser = webdriver.Chrome(chrome_options=options)

    tweet_xpath = '//*[@id="react-root"]/div/div/div[2]/main/div/div/div/div/div/div[2]/div/div/section/div/div/*/div/div/article/div/div/div/div[2]/div[2]/div[2]'
    base_url = 'https://twitter.com/search?q='
    query = query

    url = base_url + query

    browser.get(url)

    # wait for page to load
    time.sleep(3)

    scrolldown(browser)

    tweet_elements = browser.find_elements_by_xpath(tweet_xpath)
    tweet_text = get_tweet_text(tweet_elements)

    score = []
    for i in tweet_text:
        score.append(sentiment(clean_tweet(i)))

    num_tweets = len(tweet_text)

    # print the results
    print("Got "+str(len(tweet_text))+" tweet_elements\n")
    print("Positive: "+str(int(score.count("Positive")/num_tweets*100)))
    print("Negative: "+str(int(score.count("Negative")/len(tweet_text)*100)))
    print("Neutral: "+str(int(score.count("Neutral")/len(tweet_text)*100)))

    final_data = dict(tweets=[dict(text=a, sentiment=b) for a, b in zip(tweet_text, score)], results=dict(positive=str(int(score.count(
        "Positive")/num_tweets*100)), negative=str(int(score.count("Negative")/num_tweets*100)), neutral=str(int(score.count("Neutral")/num_tweets*100))))
    print(final_data)
    browser.quit()

    return str(final_data)


if __name__ == "__main__":
    app.run(debug=True)
