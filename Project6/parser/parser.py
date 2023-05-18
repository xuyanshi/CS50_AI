from functools import cache
from typing import List

import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP | NP VP Conj VP | NP VP Conj S | NP Adv VP
NP -> N | Det NP | N PP | Det NP PP | Adj NP 
VP -> V | V Adv | V PP | V NP | V NP Adv | V NP PP
PP -> P NP | Conj S
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():
    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    sentence = nltk.tokenize.word_tokenize(sentence)
    ans = []
    for word in sentence:
        word = word.lower()
        contains_alphabet = any(ch.isalpha() for ch in word)
        if contains_alphabet:
            ans.append(word)
    return ans


def np_chunk(tree: nltk.tree.Tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    @cache
    def findNP(np_tree: nltk.tree.Tree) -> List[nltk.tree.Tree]:
        """
        Find the minimum subtrees with 'NP' tag of one tree whose tag is 'NP'
        """
        np_lst = []
        sub_np = False
        for i in range(len(np_tree)):
            sub_tree = np_tree[i]
            if sub_tree and sub_tree.label() == 'NP':
                sub_np = True
                np_lst.extend(findNP(sub_tree))
        if not sub_np:
            np_lst.append(np_tree)
        return np_lst

    ans = []
    for i in range(len(tree)):
        sub_tree = tree[i]
        if sub_tree and sub_tree.label() == 'NP':
            ans.extend(findNP(sub_tree))
    return ans


if __name__ == "__main__":
    main()
