# -*- coding:utf-8 -*-

def precision(my_parse, gold_parse, labeled=True):
    if labeled:
        return labeled_precision(my_parse, gold_parse) / len(gold_parse.productions()) * 100.0
    else:
        return unlabeled_precision(my_parse, gold_parse) / len(gold_parse.productions()) * 100.0

def labeled_precision(my_parse, gold_parse):
    if my_parse[0] in my_parse.leaves():
        if str(my_parse[0]) == str(gold_parse[0]):
            return 1
        else:
            return 0
    else:
        count = 1
        for n in xrange(len(my_parse)):
            if getStart(my_parse)[0] == getStart(gold_parse)[0] and getEnd(my_parse)[0] == getEnd(gold_parse)[0] and str(my_parse.label()) == str(gold_parse.label()): # labeled
                count = count + labeled_precision(my_parse[n], gold_parse[n])
        return count

def unlabeled_precision(my_parse, gold_parse):
    if my_parse[0] in my_parse.leaves():
        if str(my_parse[0]) == str(gold_parse[0]):
            return 1
        else:
            return 0
    else:
        count = 1
        for n in xrange(len(my_parse)):
            if getStart(my_parse)[0] == getStart(gold_parse)[0] and getEnd(my_parse)[0] == getEnd(gold_parse)[
                0]:
                count = count + labeled_precision(my_parse[n], gold_parse[n])
        return count

def recall(my_parse, gold_parse, labeled=True):
    if labeled:
        return labeled_recall(my_parse, gold_parse) / len(gold_parse.productions()) * 100.0
    else:
        return unlabeled_recall(my_parse, gold_parse) / len(gold_parse.productions()) * 100.0

def labeled_recall(my_parse, gold_parse):
    if gold_parse[0] in gold_parse.leaves():
        if str(my_parse[0]) == str(gold_parse[0]):
            return 1
        else:
            return 0
    else:
        count = 1
        for n in xrange(len(gold_parse)):
            if getStart(my_parse)[0] == getStart(gold_parse)[0] and getEnd(my_parse)[0] == getEnd(gold_parse)[0] and str(my_parse.label()) == str(gold_parse.label()):  # labeled
                count = count + labeled_recall(my_parse[n], gold_parse[n])
        return count

def unlabeled_recall(my_parse, gold_parse):
    if gold_parse[0] in gold_parse.leaves():
        if str(my_parse[0]) == str(gold_parse[0]):
            return 1
        else:
            return 0
    else:
        count = 1
        for n in xrange(len(gold_parse)):
            if getStart(my_parse)[0] == getStart(gold_parse)[0] and getEnd(my_parse)[0] == getEnd(gold_parse)[0]:
                count = count + labeled_recall(my_parse[n], gold_parse[n])
        return count

def f1_score(my_parse, gold_parse, labeled=True):
    if labeled:
        p = precision(my_parse, gold_parse, True)
        r = recall(my_parse, gold_parse, True)
        return (2 * p * r) / (p + r)
    else:
        p = precision(my_parse, gold_parse, False)
        r = recall(my_parse, gold_parse, False)
        return (2 * p * r) / (p + r)

def getStart(parse_tree):
    if isinstance(parse_tree[-1], str) or isinstance(parse_tree[-1], unicode):
        return parse_tree
    else:
        return getStart(parse_tree[0])

def getEnd(parse_tree):
    if isinstance(parse_tree[-1], str) or isinstance(parse_tree[-1], unicode):
        return parse_tree
    else:
        return getEnd(parse_tree[-1])