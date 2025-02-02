import math
import os

import nltk
import sys
import string

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():
    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                if tokens := tokenize(sentence):
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    contents = dict()
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename)) as f:
            contents[filename] = f.read()
    return contents


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by converting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    words = []
    document = nltk.tokenize.word_tokenize(document)
    words.extend(
        w.lower()
        for w in document
        if w not in string.punctuation
        and w not in nltk.corpus.stopwords.words("english")
    )
    return words


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idf_dict = dict()
    for filename in documents:
        for w in documents[filename]:
            if w not in idf_dict:
                idf_dict[w] = set(filename)
            else:
                idf_dict[w].add(filename)
    n = len(documents)
    for w in idf_dict:
        idf_dict[w] = math.log(n / len(idf_dict[w]))
    return idf_dict


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the `n` top
    files that match the query, ranked according to tf-idf.
    """
    filenames = dict()
    for w in query:
        for f in files:
            if w in files[f]:
                if f not in filenames:
                    filenames[f] = {w}
                else:
                    filenames[f].add(w)

    for f in filenames:
        words = filenames[f]
        filenames[f] = 0.0
        for w in words:
            filenames[f] += idfs[w]

    ans = list(filenames.keys())
    # TODO: I'm not sure whether it should be reversed or not.
    ans.sort(key=lambda file: filenames[file], reverse=True)
    return ans if len(ans) < n else ans[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    sentence_idf = dict()
    for w in query:
        for s in sentences:
            if w in sentences[s]:
                if s not in sentence_idf:
                    sentence_idf[s] = {w}
                else:
                    sentence_idf[s].add(w)

    for s in sentence_idf:
        words = sentence_idf[s]
        sentence_idf[s] = 0.0
        for w in words:
            sentence_idf[s] += idfs[w]
        # 1 / query term density
        # TODO: Fix bug of sorting.
        sentence_idf[s] = (sentence_idf[s], len(words) / len(s))
    ans = list(sentence_idf.keys())
    ans.sort(key=lambda file: sentence_idf[file], reverse=True)
    return ans if len(ans) < n else ans[:n]


if __name__ == "__main__":
    main()
