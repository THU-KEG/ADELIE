'''
Usage:
   benchmark --gold=GOLD_OIE --out=OUTPUT_FILE (--openiefive=OPENIE5 | --stanford=STANFORD_OIE | --ollie=OLLIE_OIE |--reverb=REVERB_OIE | --clausie=CLAUSIE_OIE | --openiefour=OPENIEFOUR_OIE | --props=PROPS_OIE | --tabbed=TABBED_OIE | --benchmarkGold=BENCHMARK_GOLD | --allennlp=ALLENNLP_OIE ) [--exactMatch | --predMatch | --lexicalMatch | --binaryMatch | --simpleMatch | --strictMatch] [--error-file=ERROR_FILE] [--binary]

Options:
  --gold=GOLD_OIE              The gold reference Open IE file (by default, it should be under ./oie_corpus/all.oie).
  --benchmarkgold=GOLD_OIE     The benchmark's gold reference. 
  --out-OUTPUT_FILE            The output file, into which the precision recall curve will be written.
  --clausie=CLAUSIE_OIE        Read ClausIE format from file CLAUSIE_OIE.
  --ollie=OLLIE_OIE            Read OLLIE format from file OLLIE_OIE.
  --openiefour=OPENIEFOUR_OIE  Read Open IE 4 format from file OPENIEFOUR_OIE.
  --openiefive=OPENIE5         Read Open IE 5 format from file OPENIE5.
  --props=PROPS_OIE            Read PropS format from file PROPS_OIE
  --reverb=REVERB_OIE          Read ReVerb format from file REVERB_OIE
  --stanford=STANFORD_OIE      Read Stanford format from file STANFORD_OIE
  --tabbed=TABBED_OIE          Read simple tab format file, where each line consists of:
                                sent, prob, pred,arg1, arg2, ...
  --exactmatch                 Use exact match when judging whether an extraction is correct.
'''
from __future__ import division
import docopt
import string
import numpy as np
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import auc
import re
import logging
import pdb
import ipdb
from _collections import defaultdict
logging.basicConfig(level = logging.INFO)

from oie_readers.stanfordReader import StanfordReader
from oie_readers.ollieReader import OllieReader
from oie_readers.reVerbReader import ReVerbReader
from oie_readers.clausieReader import ClausieReader
from oie_readers.openieFourReader import OpenieFourReader
from oie_readers.openieFiveReader import OpenieFiveReader
from oie_readers.propsReader import PropSReader
from oie_readers.tabReader import TabReader
from oie_readers.benchmarkGoldReader import BenchmarkGoldReader

from oie_readers.goldReader import GoldReader
from matcher import Matcher
from operator import itemgetter
import pprint
from copy import copy
pp = pprint.PrettyPrinter(indent=4)

class Benchmark:
    ''' Compare the gold OIE dataset against a predicted equivalent '''
    def __init__(self, gold_fn=None):
        ''' Load gold Open IE, this will serve to compare against using the compare function '''
        gr = GoldReader()
        if gold_fn is not None:
            gr.read(gold_fn)
            self.gold = gr.oie
        else:
            self.gold = None

    def compare(self, predicted, matchingFunc, output_fn=None, error_file = None, binary=False):
        ''' Compare gold against predicted using a specified matching function.
            Outputs PR curve to output_fn '''

        y_true = []
        y_scores = []
        errors = []
        correct = 0
        incorrect = 0

        correctTotal = 0
        unmatchedCount = 0
        predicted = Benchmark.normalizeDict(predicted)
        gold = Benchmark.normalizeDict(self.gold)
        if binary:
            predicted = Benchmark.binarize(predicted)
            gold = Benchmark.binarize(gold)
        #gold = self.gold

        # taking all distinct values of confidences as thresholds
        confidence_thresholds = set()
        for sent in predicted:
            for predicted_ex in predicted[sent]:
                confidence_thresholds.add(predicted_ex.confidence)

        confidence_thresholds = sorted(list(confidence_thresholds))
        num_conf = len(confidence_thresholds)

        results = {}
        p = np.zeros(num_conf)
        pl = np.zeros(num_conf)
        r = np.zeros(num_conf)
        rl = np.zeros(num_conf)

        for sent, goldExtractions in gold.items():

            if sent in predicted:
                predictedExtractions = predicted[sent]
            else:
                predictedExtractions = []

            scores = [[None for _ in predictedExtractions] for __ in goldExtractions]

            # print("***Gold Extractions***")
            # print("\n".join([goldExtractions[i].pred + ' ' + " ".join(goldExtractions[i].args) for i in range(len(goldExtractions))]))
            # print("***Predicted Extractions***")
            # print("\n".join([predictedExtractions[i].pred+ " ".join(predictedExtractions[i].args) for i in range(len(predictedExtractions))]))

            for i, goldEx in enumerate(goldExtractions):
                for j, predictedEx in enumerate(predictedExtractions):
                    score = matchingFunc(goldEx, predictedEx,ignoreStopwords = True,ignoreCase = True)
                    scores[i][j] = score


            # OPTIMISED GLOBAL MATCH
            sent_confidences = [extraction.confidence for extraction in predictedExtractions]
            sent_confidences.sort()
            prev_c = 0
            for conf in sent_confidences:
                c = confidence_thresholds.index(conf)
                ext_indices = []
                for ext_indx, extraction in enumerate(predictedExtractions):
                    if extraction.confidence >= conf:
                        ext_indices.append(ext_indx)

                recall_numerator = 0
                for i, row in enumerate(scores):
                    max_recall_row = max([row[ext_indx][1] for ext_indx in ext_indices ], default=0)
                    recall_numerator += max_recall_row

                precision_numerator = 0

                selected_rows = []
                selected_cols = []
                num_precision_matches = min(len(scores), len(ext_indices))
                for t in range(num_precision_matches):
                    matched_row = -1
                    matched_col = -1
                    matched_precision = -1 # initialised to <0 so that it updates whenever precision is 0 as well
                    for i in range(len(scores)):
                        if i in selected_rows:
                            continue
                        for ext_indx in ext_indices:
                            if ext_indx in selected_cols:
                                continue
                            if scores[i][ext_indx][0] > matched_precision:
                                matched_precision = scores[i][ext_indx][0]
                                matched_row = i
                                matched_col = ext_indx

                    selected_rows.append(matched_row)
                    selected_cols.append(matched_col)
                    precision_numerator += scores[matched_row][matched_col][0]
                
                p[prev_c:c+1] += precision_numerator
                pl[prev_c:c+1] += len(ext_indices)
                r[prev_c:c+1] += recall_numerator
                rl[prev_c:c+1] += len(scores)

                prev_c = c+1

            # for indices beyond the maximum sentence confidence, len(scores) has to be added to the denominator of recall
            rl[prev_c:] += len(scores)

        prec_scores = [a/b if b>0 else 1 for a,b in zip(p,pl) ]
        rec_scores = [a/b if b>0 else 0 for a,b in zip(r,rl)]

        f1s = [Benchmark.f1(p,r) for p,r in zip(prec_scores, rec_scores)]
        try:
            optimal_idx = np.nanargmax(f1s)
            optimal = (prec_scores[optimal_idx], rec_scores[optimal_idx], f1s[optimal_idx])
        except ValueError:
            # When there is no prediction
            optimal = (0,0,0)

        # In order to calculate auc, we need to add the point corresponding to precision=1 , recall=0 to the PR-curve
        temp_rec_scores = rec_scores.copy()
        temp_prec_scores = prec_scores.copy()
        temp_rec_scores.append(0)
        temp_prec_scores.append(1)
        # print("AUC: {}\t Optimal (precision, recall, F1): {}".format( np.round(auc(temp_rec_scores, temp_prec_scores),3), np.round(optimal,3) ))
        
        if output_fn:
            with open(output_fn, 'w') as fout:
                fout.write('{0}\t{1}\t{2}\n'.format("Precision", "Recall", "Confidence"))
                for cur_p, cur_r, cur_conf in sorted(zip(prec_scores, rec_scores, confidence_thresholds), key = lambda cur: cur[1]):
                   fout.write('{0}\t{1}\t{2}\n'.format(cur_p, cur_r, cur_conf))

        if len(f1s)>0:
            return np.round(auc(temp_rec_scores, temp_prec_scores),3), np.round(optimal,3)
        else:
            # When there is no prediction
            return 0, (0,0,0)

    @staticmethod
    def binarize(extrs):
        res = defaultdict(lambda: [])
        for sent,extr in extrs.items():
            for ex in extr:
                #Add (a1, r, a2)
                temp = copy(ex)
                temp.args = ex.args[:2]
                res[sent].append(temp)
                
                if len(ex.args) <= 2:
                    continue
                
                #Add (a1, r a2 , a3 ...)
                for arg in ex.args[2:]:
                    temp.args = [ex.args[0]]
                    temp.pred = ex.pred + ' '  + ex.args[1]
                    words = arg.split()

                    #Add preposition of arg to rel
                    if words[0].lower() in Benchmark.PREPS:
                        temp.pred += ' ' + words[0]
                        words = words[1:]
                    temp.args.append(' '.join(words))
                    res[sent].append(temp)

        return res

    @staticmethod
    def f1(prec, rec):
        try:
            return 2*prec*rec / (prec+rec)
        except ZeroDivisionError:
            return 0

    @staticmethod
    def aggregate_scores_greedily(scores):
        # Greedy match: pick the prediction/gold match with the best f1 and exclude
        # them both, until nothing left matches. Each input square is a [prec, rec]
        # pair. Returns precision and recall as score-and-denominator pairs.
        matches = []
        while True:
            max_s = 0
            gold, pred = None, None
            for i, gold_ss in enumerate(scores):
                if i in [m[0] for m in matches]:
                    # Those are already taken rows
                    continue
                for j, pred_s in enumerate(scores[i]):
                    if j in [m[1] for m in matches]:
                        # Those are used columns
                        continue
                    if pred_s and Benchmark.f1(*pred_s) > max_s:
                        max_s = Benchmark.f1(*pred_s)
                        gold = i
                        pred = j
            if max_s == 0:
                break
            matches.append([gold, pred])
        # Now that matches are determined, compute final scores.
        prec_scores = [scores[i][j][0] for i,j in matches]
        rec_scores = [scores[i][j][1] for i,j in matches]
        total_prec = sum(prec_scores)
        total_rec = sum(rec_scores)
        scoring_metrics = {"precision" : [total_prec, len(scores[0])],
                           "recall" : [total_rec, len(scores)],
                           "precision_of_matches" : prec_scores,
                           "recall_of_matches" : rec_scores
        }
        return scoring_metrics

    # Helper functions:
    @staticmethod
    def normalizeDict(d):
        return dict([(Benchmark.normalizeKey(k), v) for k, v in d.items()])

    @staticmethod
    def normalizeKey(k):
        # return Benchmark.removePunct(unicode(Benchmark.PTB_unescape(k.replace(' ','')), errors = 'ignore'))
        return Benchmark.removePunct(str(Benchmark.PTB_unescape(k.replace(' ',''))))

    @staticmethod
    def PTB_escape(s):
        for u, e in Benchmark.PTB_ESCAPES:
            s = s.replace(u, e)
        return s

    @staticmethod
    def PTB_unescape(s):
        for u, e in Benchmark.PTB_ESCAPES:
            s = s.replace(e, u)
        return s

    @staticmethod
    def removePunct(s):
        return Benchmark.regex.sub('', s) 

    # CONSTANTS
    regex = re.compile('[%s]' % re.escape(string.punctuation))

    # Penn treebank bracket escapes
    # Taken from: https://github.com/nlplab/brat/blob/master/server/src/gtbtokenize.py
    PTB_ESCAPES = [('(', '-LRB-'),
                   (')', '-RRB-'),
                   ('[', '-LSB-'),
                   (']', '-RSB-'),
                   ('{', '-LCB-'),
                   ('}', '-RCB-'),]

    PREPS = ['above','across','against','along','among','around','at','before','behind','below','beneath','beside','between','by','for','from','in','into','near','of','off','on','to','toward','under','upon','with','within']

def f_beta(precision, recall, beta = 1):
    """
    Get F_beta score from precision and recall.
    """
    beta = float(beta) # Make sure that results are in float
    return (1 + pow(beta, 2)) * (precision * recall) / ((pow(beta, 2) * precision) + recall)


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    logging.debug(args)

    if args['--stanford']:
        predicted = StanfordReader()
        predicted.read(args['--stanford'])

    if args['--props']:
        predicted = PropSReader()
        predicted.read(args['--props'])

    if args['--ollie']:
        predicted = OllieReader()
        predicted.read(args['--ollie'])

    if args['--reverb']:
        predicted = ReVerbReader()
        predicted.read(args['--reverb'])

    if args['--clausie']:
        predicted = ClausieReader()
        predicted.read(args['--clausie'])

    if args['--openiefour']:
        predicted = OpenieFourReader()
        predicted.read(args['--openiefour'])

    if args['--openiefive']:
        predicted = OpenieFiveReader()
        predicted.read(args['--openiefive'])

    if args['--benchmarkGold']:
        predicted = BenchmarkGoldReader()
        predicted.read(args['--benchmarkGold'])
 
    if args['--tabbed']:
        predicted = TabReader()
        predicted.read(args['--tabbed'])

    if args['--binaryMatch']:
        matchingFunc = Matcher.binary_tuple_match

    elif args['--simpleMatch']:
        matchingFunc = Matcher.simple_tuple_match

    elif args['--exactMatch']:
        matchingFunc = Matcher.argMatch

    elif args['--predMatch']:
        matchingFunc = Matcher.predMatch

    elif args['--lexicalMatch']:
        matchingFunc = Matcher.lexicalMatch

    elif args['--strictMatch']:
        matchingFunc = Matcher.tuple_match

    else:
        matchingFunc = Matcher.binary_linient_tuple_match

    b = Benchmark(args['--gold'])
    out_filename = args['--out']

    logging.info("Writing PR curve of {} to {}".format(predicted.name, out_filename))

    auc, optimal_f1_point = b.compare(predicted = predicted.oie,
                            matchingFunc = matchingFunc,
                            output_fn = out_filename,
                            error_file = args["--error-file"],
                            binary = args["--binary"])

    print("AUC: {}\t Optimal (precision, recall, F1): {}".format( auc, optimal_f1_point ))
