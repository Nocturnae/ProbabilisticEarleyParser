# -*- coding:utf-8 -*-

import nltk
import nltk.data
from nltk.grammar import Nonterminal
import nltk.parse.chart as chartStruct
import nltk.tree as treeStruct
from nltk.grammar import PCFG, toy_pcfg2, Production
from nltk.tokenize import word_tokenize
import re
import pickle

class EarleyParser(object):

    grammar = None
    parser = None

    nonterminals = []
    word_categories = {}
    rule_probs = {}
    productions = []

    nltk.grammar._STANDARD_NONTERM_RE = re.compile('( [\w/$^<>-]*[\w/#$"(),.:`]*[\w/$^<>-]* ) \s*', re.VERBOSE)

    def __init__(self, grammar_file=None, nltk_grammar=None):
        '''
        read from a text file or load an nltk grammar
        '''
        if grammar_file:
            self.load_grammar(grammar_file)
        elif nltk_grammar:
            self.grammar = nltk_grammar

        # set up list of nonterminals and word categories dict
        for p in self.grammar.productions():
            self.productions.append(p)
            self.rule_probs[nltk.grammar.Production(p.lhs(), p.rhs())] = p.prob()
            if p.lhs() not in self.nonterminals:
                self.nonterminals.append(p.lhs())
            if isinstance(p.rhs()[0], unicode):
                if p.rhs()[0] in self.word_categories: # already added key
                    if p.lhs() not in self.word_categories[p.rhs()[0]]: # nonterminal not already associated with word
                        self.word_categories[p.rhs()[0]].append(p.lhs())
                else:
                    self.word_categories[p.rhs()[0]] = [p.lhs()]


    def load_grammar(self, grammar_file):
        '''
        read a grammar from a text file
        '''
        self.grammar = pickle.load(open(grammar_file, "rb"))
    

    def save_grammar(self, grammar_file):
        '''
        save the grammar to a text file
        '''
        pickle.dump(self.grammar, open("grammar.txt", "wb"))
    
    def parse(self, tokens):
        '''
        parse the tokenized sentence and 
        return the most probable one as a tuple
        (parse_tree, prob)
        '''

        # set up chart with terminals in sentence
        chart = chartStruct.Chart(tokens)

        # create arbitrary root ROOT
        root = Nonterminal("ROOT")
        initial_edge = chartStruct.TreeEdge((0,0), root, [Nonterminal('S')], 0)
        chart.insert(initial_edge, [])

        # parser
        num_words = len(tokens)
        for i in xrange(num_words + 1):
            for e in chart.select(end=i):
                #print e
                # completer
                if e.is_complete():
                    for ne in chart.select(end=e.start()):
                        if ne.is_incomplete() and (ne.rhs()[ne.dot()] == e.lhs()):
                            forward_edge = chartStruct.TreeEdge((ne.start(), e.end()), ne.lhs(), ne.rhs(), ne.dot() + 1)
                            chart.insert_with_backpointer(forward_edge, ne, e)
                    continue
                next_nonterminal = e.rhs()[e.dot()]
                if e.is_incomplete() and next_nonterminal in self.nonterminals:
                    for p in self.productions:
                        # predictor
                        if p.lhs() == next_nonterminal and p.rhs()[0] in self.nonterminals:
                            new_edge = chartStruct.TreeEdge((e.end(), e.end()), p.lhs(), p.rhs(), 0)
                            chart.insert(new_edge, [])
                        # scanner
                        elif p.lhs() == next_nonterminal and p.rhs()[0] not in self.nonterminals:
                            if i != num_words and tokens[i] == p.rhs()[0] and next_nonterminal in self.word_categories[p.rhs()[0]]:
                                # add B -> word rule
                                next_edge = chartStruct.TreeEdge((e.end(), e.end() + 1), p.lhs(), p.rhs(), 1)
                                chart.insert(next_edge, [])

        parserList = []
        for t in chart.select(lhs=Nonterminal('S'), start=0, end=num_words):
            if t.dot() == len(t.rhs()):
                parseTree = self.retrieve(chart, t)
                if parseTree not in parserList:
                    parseProb = self.treeProb(parseTree)
                    parserList.append((parseTree, parseProb))

        self.parser = self.getMaxTree(parserList)

        return self.parser

    def retrieve(self, chart, treeEdge):
        if treeEdge.rhs()[0] not in self.nonterminals:
            return treeStruct.Tree(str(treeEdge.lhs()), [str(treeEdge.rhs()[0])])
        else:
            tempList = []
            for n in xrange(len(chart.child_pointer_lists(treeEdge)[0])):
                tempList.append(self.retrieve(chart, chart.child_pointer_lists(treeEdge)[0][n]))
            return treeStruct.Tree(str(treeEdge.lhs()), tempList)

    def treeProb(self, tree):
        total_prob = 1
        for p in tree.productions():
            total_prob *= self.rule_probs[p]
        return total_prob

    def getMaxTree(self, list):
        if not list:
            return None
        maxTree = list[0]
        for l in list:
            if len(l) > 1 and l[1] > maxTree[1]:
                maxTree = l
        return maxTree

    def parse_raw(self, sent):
        '''
        parse a raw sentence
        '''
        tokenized = nltk.word_tokenize(sent)
        return self.parse(tokenized)
    
    def save(self, filename):
        '''
        save the parser model with the grammar
        '''
        f = open(filename, 'w')
        f.write(str(self.parser))
        f.close()
    
    def load(self, filename):
        '''
        load previously saved model
        '''
        f = open(filename, 'r')
        file_content = f.read()
        parse_tree = treeStruct.Tree.fromstring(file_content)
        self.parser = parse_tree
        f.close()