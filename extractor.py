import nltk
from nltk import Tree
from nltk.grammar import Nonterminal, Production
from nltk.corpus import treebank
from nltk.text import Text
import pickle

def simplify_lhs(prod):
    tag = str(prod.lhs())
    split_tag = tag.split('-')
    if len(split_tag) != 1 and split_tag[1] != "NONE":
        return split_tag[0]
    else:
        return tag


def simplify_rhs(prod):
    tags = prod.rhs()
    replace_rhs = []
    for t in tags:
        if isinstance(t, Nonterminal):
            split_tags = str(t).split('-')
            if len(split_tags) != 1 and split_tags[1] != "NONE":
                replace_rhs.append(Nonterminal(split_tags[0]))
            else:
                replace_rhs.append(t)
        else:
            replace_rhs.append(t)
    return replace_rhs

f = open("grammar2.txt", 'w')

allPairs = treebank.tagged_words()
extractSet = treebank.parsed_sents()[:160]

rules = []
for es in extractSet:
    for et in es.productions():
        simplified_lhs = simplify_lhs(et)
        simplified_rhs = simplify_rhs(et)
        new_lhs = Nonterminal(simplified_lhs)
        new_rhs = tuple(simplified_rhs)
        new_rule = Production(new_lhs, new_rhs)
        rules.append(new_rule)

for w, t in allPairs:
    cur = Tree.fromstring("(" + t + " " + w + ")")
    for p in cur.productions():
        rules.append(p)

grammar = nltk.grammar.induce_pcfg(Nonterminal('S'), rules)
pickle.dump(grammar, open("grammar.txt", "wb"))

# text file
for g in grammar.productions():
    f.write(str(g))
    f.write("\n")

f.close()
