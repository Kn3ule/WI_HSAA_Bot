import token
import nltk
from nltk.stem import PorterStemmer
import spacy

ps = PorterStemmer()
nlp = spacy.load('de_core_news_md')

def tokenize(sentence):
    doc = nlp(sentence)

    lemma_tokens = []
    for token in doc:
        lemma_tokens.append(token.lemma_.lower())
    
    return lemma_tokens
def main():
    Eingabe = "urlaub beurlauben!"

    print(tokenize(Eingabe))

if __name__ == "__main__":
    main()