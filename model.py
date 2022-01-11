from keras.metrics import Accuracy
from nltk.corpus.reader.chasen import test
from sklearn.linear_model import SGDClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from nltk.corpus import stopwords

import sklearn.utils
import pandas as pd
import re

import database

s = set(stopwords.words('english'))

def preprocess_text(sen, symbol):
    # Remove punctuations and numbers
    sentence = re.sub('[^a-zA-Z]', ' ', sen)

    # Single character removal
    sentence = re.sub(r"\s+[a-zA-Z]\s+", ' ', sentence)

    # Removing multiple spaces
    sentence = re.sub(r'\s+', ' ', sentence)

    # Remove stopwords
    sentence = sentence.lower()
    sentence = ' '.join(word for word in sentence.split() if word not in s)
    sentence = sentence.replace(' ' + symbol.lower() + ' ', '')
    sentence = sentence.replace('deleted', '')
    sentence = sentence.replace('removed', '')
    return sentence

def build_hour_model():
    db = database.Database()

    # Collect data to be used and preprocess
    allList = db.get_all_post_records()
    data = {"1hourWinner": [], "not1Hour": []}
    for p in allList:
        if p.oneHourWinner:
            data['1hourWinner'].append(preprocess_text(p.title + " " + p.description, p.ticker))
        else:
            data['not1Hour'].append(preprocess_text(p.title + " " + p.description, p.ticker))

    # Adjust the dataset
    while len(data['1hourWinner']) > len(data['not1Hour']):
        data['1hourWinner'].pop()
    while len(data['not1Hour']) > len(data['1hourWinner']):
        data['not1Hour'].pop()

    # Do this calculation 100 times to check average
    win_sum = 0.0
    lose_sum = 0.0
    unclassified_sum = 0.0
    num_points = 0
    for x in range(100):
        # Build dataframes
        train_df = pd.DataFrame(columns = ['classification', 'text'])
        for t in data['1hourWinner']:
            train_df = train_df.append({'classification': '1hourWinner', 'text': t}, ignore_index=True)
        for t in data['not1Hour']:
            train_df = train_df.append({'classification': 'not1Hour', 'text': t}, ignore_index=True)
        train_df = sklearn.utils.shuffle(train_df, random_state = x)

        rows_to_keep = round(len(train_df.index) * .80)
        test_df = train_df.iloc[:rows_to_keep, :]
        train_df = train_df.iloc[rows_to_keep + 1:, :]

        # Build a pipeline
        text_clf = Pipeline([('vect', CountVectorizer()),
                            ('tfidf', TfidfTransformer()),
                            ('clf', MultinomialNB()),
                            ])
        text_clf = text_clf.fit(train_df.text, train_df.classification)

        # Check predicted
        win_num_correct = 0
        lose_num_correct = 0
        local_win_total = 0
        local_lose_total = 0
        unclassified_percent = 0
        predicted = text_clf.predict_proba(test_df.text)
        i = 0
        for index, row in test_df.iterrows():
            if predicted[i][1] > .53:
                local_lose_total += 1
                if row.classification == 'not1Hour':
                    lose_num_correct += 1
            elif predicted[i][0] > .53:
                local_win_total += 1
                if row.classification == '1hourWinner':
                    win_num_correct += 1
            else:
                unclassified_percent += 1
            i += 1
        print('Win Accuracy:', float(win_num_correct) / float(local_win_total), 'Lose Accuracy:', float(lose_num_correct) / float(local_lose_total))
        win_sum += float(win_num_correct) / float(local_win_total)
        lose_sum += float(lose_num_correct) / float(local_lose_total)
        unclassified_sum += float(unclassified_percent) / float(i)
        num_points += 1
        if float(win_num_correct) / float(local_win_total) > .58 and float(lose_num_correct) / float(local_lose_total) > .55:
            return text_clf
    print('Total Long Accuracy:', float(win_sum / num_points))
    print('Total Short Accuracy:', float(lose_sum / num_points))
    print('Amount unclassified:', float(unclassified_sum / num_points))

    return None

def build_30min_model():
    db = database.Database()

    # Collect data to be used and preprocess
    allList = db.get_all_post_records()
    data = {"30minuteWinner": [], "not30Minute": []}
    for p in allList:
        if p.thirtyMinuteWinner:
            data['30minuteWinner'].append(preprocess_text(p.title + " " + p.description, p.ticker))
        else:
            data['not30Minute'].append(preprocess_text(p.title + " " + p.description, p.ticker))

    # Adjust the dataset
    while len(data['30minuteWinner']) > len(data['not30Minute']):
        data['30minuteWinner'].pop()
    while len(data['not30Minute']) > len(data['30minuteWinner']):
        data['not30Minute'].pop()

    # Do this calculation 100 times to check average
    win_sum = 0.0
    lose_sum = 0.0
    unclassified_sum = 0.0
    num_points = 0
    for x in range(100):
        # Build dataframes
        train_df = pd.DataFrame(columns = ['classification', 'text'])
        for t in data['30minuteWinner']:
            train_df = train_df.append({'classification': '30minuteWinner', 'text': t}, ignore_index=True)
        for t in data['not30Minute']:
            train_df = train_df.append({'classification': 'not30Minute', 'text': t}, ignore_index=True)
        train_df = sklearn.utils.shuffle(train_df, random_state = x)

        rows_to_keep = round(len(train_df.index) * .80)
        test_df = train_df.iloc[:rows_to_keep, :]
        train_df = train_df.iloc[rows_to_keep + 1:, :]

        # Build a pipeline
        text_clf = Pipeline([('vect', CountVectorizer()),
                            ('tfidf', TfidfTransformer()),
                            ('clf', MultinomialNB()),
                            ])
        text_clf = text_clf.fit(train_df.text, train_df.classification)

        # Check predicted
        win_num_correct = 0
        lose_num_correct = 0
        local_win_total = 0
        local_lose_total = 0
        unclassified_percent = 0
        predicted = text_clf.predict_proba(test_df.text)
        i = 0
        for index, row in test_df.iterrows():
            if predicted[i][1] > .53:
                local_lose_total += 1
                if row.classification == 'not30Minute':
                    lose_num_correct += 1
            elif predicted[i][0] > .53:
                local_win_total += 1
                if row.classification == '30minuteWinner':
                    win_num_correct += 1
            else:
                unclassified_percent += 1
            i += 1
        print('Win Accuracy:', float(win_num_correct) / float(local_win_total), 'Lose Accuracy:', float(lose_num_correct) / float(local_lose_total))
        win_sum += float(win_num_correct) / float(local_win_total)
        lose_sum += float(lose_num_correct) / float(local_lose_total)
        unclassified_sum += float(unclassified_percent) / float(i)
        num_points += 1
        if float(win_num_correct) / float(local_win_total) > .60:
            return text_clf
    print('Total Long Accuracy:', float(win_sum / num_points))
    print('Total Short Accuracy:', float(lose_sum / num_points))
    print('Amount unclassified:', float(unclassified_sum / num_points))

    return None
