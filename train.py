import nltk
import csv
import math
from counter import Counter

categories = []
class Category:
    total = 0
    def __init__(self, name):
        self.name = name
        self.words = Counter()
    def __repr__(self):
        return self.name

positive = "The quick brown fox, who it appeared cared deeply about erudite matters; yet not realising it, was ecstatic! What better way to celebrate the day than a glass of warm milk?"
negative = "The small brown hare, who did not appear to care so deeply about anything nearly as erudite, was disappointed. Such disappointment always lead to anger, and then to fear; only to be surpassed later with a call for suffering."

def tokenize(input_string):
    return nltk.word_tokenize(input_string)

def train_text(category, text, stopwords):
    for word in tokenize(text):
        if word in stopwords:
            continue
        train(category, word)

def train(category, word):
    category.total += 1
    category.words[word.lower()] += 1

def word_probability(category, word):
    probability = float(category.words[word.lower()])/float(category.total)
    if probability == 0:
        return 0
    else:
        return -math.log(probability)

def text_probability(category, text):
    total = 0.0
    words = tokenize(text)
    for word in words:
        total += word_probability(category, word)
    return total / len(words)

def totalwords(categories):
    count = 0
    for c in categories:
        count += c.total


def classify(text):
    max_prob = 0.0
    best = None

    for cat in categories:
        prob = text_probability(cat, text)
        if prob > max_prob:
            best = cat
            max_prob = prob
    return best

def get_stopwords(filename):
    stopwords = []
    with open(filename, 'r') as f:
        for word in f:
            stopwords.append(word)
    return stopwords

def train_with_file(categories_map, filename, header=True, stopwords_filename=None):
    stopwords = get_stopwords(stopwords_filename)
    with open(filename, 'r') as f:
        trainingdata = csv.reader(f)
        if header:
            next(csv.reader(f)) 
        for tweet in trainingdata:
            #tweet[0] is category, tweet[1] is text
            try:
                train_text(categories_map[tweet[0]], tweet[1], stopwords)
            except:
                print "Category for "+tweet[0]+"not found."

def do_training():
    categories.append(Category("positive"))
    categories.append(Category("negative"))
    cat_map = {}
    for cat in categories:
        cat_map[cat.name] = cat
    train_with_file(cat_map, "trainingdata.txt", stopwords_filename="stopwords.txt")

def main():
    do_training()
    
if __name__ == "__main__":
    main()
