from numpy import average, vectorize
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_recall_fscore_support, precision_score
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.neighbors import KNeighborsClassifier, kneighbors_graph
from sklearn.tree import DecisionTreeClassifier
import spacy
from spacy.lang.de.stop_words import STOP_WORDS
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split as tts
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from nlp import *

#initialize Labelencoder and Tf-idf vectorizer
le = LabelEncoder()
vectorizer = TfidfVectorizer()

#import training data
training_data = pd.read_csv("training_data.csv", sep=';')
patterns = training_data['patterns'].values

tags = []
for i in training_data["tags"]:
    if i not in tags:
        tags.append(i)

X = []
for pattern in patterns:
    X.append(preprocess(pattern))

vectorizer.fit(X)
le.fit(training_data['tags'])


X = vectorizer.transform(X)
y = le.transform(training_data['tags'])

trainx, testx, trainy, testy = tts(X, y, test_size=.25, random_state=42)

#define svm and get accuracy and f1-score
svm_model = SVC(kernel='linear').fit(trainx, trainy)
print("SVM:\naccuracy:", svm_model.score(testx, testy))
svm_prediction = svm_model.predict(testx)
print("f1-score:", f1_score(testy, svm_prediction, average='weighted'))
print('\n\n')


#define kNN
knn_model = KNeighborsClassifier(n_neighbors=2).fit(trainx, trainy)
knn_prediction = knn_model.predict(testx)
print("KNN: \naccuracy:", knn_model.score(testx, testy))
print("f1-score:", f1_score(testy, knn_prediction, average='weighted'))
print('\n\n')

#define NB
NB_model = GaussianNB().fit(trainx.toarray(),trainy)
NB_prediction = NB_model.predict(testx.toarray())
print("NB: \naccuracy:", NB_model.score(testx.toarray(), testy))
print("f1-score:", f1_score(testy, NB_prediction, average='weighted'))
print('\n\n')

#define decision tree algo
dt_model = DecisionTreeClassifier().fit(trainx, trainy)
dt_prediction = dt_model.predict(testx)
print("Decision Tree: \naccuracy:", dt_model.score(testx.toarray(), testy))
print("f1-score:", f1_score(testy, dt_prediction, average='weighted'))
print('\n\n')



def svm(user_input):
    transform_input = vectorizer.transform([preprocess(user_input)])
    tag = le.inverse_transform(svm_model.predict(transform_input))[0]

    return tag

def knn(user_input):
    transform_input = vectorizer.transform([preprocess(user_input)])
    tag = le.inverse_transform(knn_model.predict(transform_input))[0]

    return tag

def NB(user_input):
    transform_input = vectorizer.transform([preprocess(user_input)])
    tag = le.inverse_transform(NB_model.predict(transform_input.toarray()))[0]

    return tag

def dt(user_input):
    transform_input = vectorizer.transform([preprocess(user_input)])
    tag = le.inverse_transform(dt_model.predict(transform_input.toarray()))[0]

    return tag