import spacy
from spacy.lang.de.stop_words import STOP_WORDS



nlp = spacy.load('de_core_news_md')

def preprocess(sentence):
    doc = nlp(sentence)

    lemma_tokens = []
    for token in doc:
        if token.is_stop == False and token.is_punct == False:
            lemma_tokens.append(token.lemma_.lower())
    
    return ' '.join(lemma_tokens)
