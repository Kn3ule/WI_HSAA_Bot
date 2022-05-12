from numpy import vectorize
import spacy
from spacy.lang.de.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split as tts
from sklearn.svm import SVC
from nlp import *

#initialize Labelencoder and Tf-idf vectorizer
le = LabelEncoder()
vectorizer = TfidfVectorizer()

#import training data
training_data = pd.read_csv("training_data.csv", sep=';')
patterns = training_data['patterns'].values

X = []
for pattern in patterns:
    X.append(preprocess(pattern))

vectorizer.fit(X)
le.fit(training_data['tags'])

X = vectorizer.transform(X)
y = le.transform(training_data['tags'])


trainx, testx, trainy, testy = tts(X, y, test_size=.25, random_state=42)

model = SVC(kernel='linear')
model.fit(trainx, trainy)
print("SVC:", model.score(testx, testy))

def svm(user_input):
    transform_input = vectorizer.transform([preprocess(user_input)])
    tag = le.inverse_transform(model.predict(transform_input))[0]

    return tag