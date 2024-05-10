""" Calculate the robust scorers of P, R, F1 for the predicted file and gold file of unified json format.
"""

import sys

sys.path.append("src/utils/CaRB")

import os
import json
import argparse
import numpy as np
from utils.CaRB.carb import Benchmark
from utils.CaRB.oie_readers.extraction import Extraction
from utils.CaRB.matcher import Matcher
from operator import itemgetter


def read_unified(fn):
    """Build inputs of CaRB format, each element for a robust sample containing an original sentences with multiple paraphrases"""
    with open(fn, "r") as f:
        f_data = json.load(f)

    results = {}  # ori sent as keys
    for X in f_data:
        # for CaRB sentence
        sample = {}
        d_carb = {}
        for ori_args in X["ori_args"]:
            curExtraction = Extraction(
                pred=ori_args[0], head_pred_index=-1, sent=X["ori_sent"], confidence=-1
            )
            for i in range(1, len(ori_args)):
                curExtraction.addArg(ori_args[i])
            d_carb[X["ori_sent"]] = d_carb.get(X["ori_sent"], []) + [curExtraction]
        sample[X["ori_sent"]] = d_carb

        # for paraphrases
        for para in X["paraphrases"]:
            d_para = {}
            for para_args in para["args"]:
                curExtraction = Extraction(
                    pred=para_args[0],
                    head_pred_index=-1,
                    sent=para["sent"],
                    confidence=-1,
                )
                for i in range(1, len(para_args)):
                    curExtraction.addArg(para_args[i])
                d_para[para["sent"]] = d_para.get(para["sent"], []) + [curExtraction]
            sample[para["sent"]] = d_para
        results[X["ori_sent"]] = sample
    return results


def main(gold_file, pred_file, save_dir):
    """ """
    pred = read_unified(pred_file)
    gold = read_unified(gold_file)

    all_scores = []
    for ori_sent in pred:
        cur_scores = []
        for sent in pred[ori_sent]:
            p_extraction = pred[ori_sent][sent]
            g_extraction = gold[ori_sent][sent]
            # evaluate one by one
            bench = Benchmark()
            bench.gold = g_extraction
            auc, [p, r, f1] = bench.compare(
                p_extraction, Matcher.binary_linient_tuple_match
            )
            # keep the scores of carb in the first position
            if sent == ori_sent:
                cur_scores.insert(0, [auc, p, r, f1])
                # print("Pred: ", [(ext.pred, ext.args) for ext in p_extraction[sent]])
                # print("Gold", [(ext.pred, ext.args) for ext in g_extraction[sent]])
                # print([auc, p, r, f1])
            else:
                cur_scores.append([auc, p, r, f1])
        all_scores.append(cur_scores)

    print(len(all_scores))
    # get carb scores
    carb_scores = np.array(([sco[0] for sco in all_scores]))
    carb_auc = carb_scores[:, 0].mean()
    carb_p = carb_scores[:, 1].mean()
    carb_r = carb_scores[:, 2].mean()
    carb_f1 = Benchmark.f1(carb_p, carb_r)

    # get the robust socres with worst F1
    robust_scores = [min(score, key=itemgetter(3)) for score in all_scores]
    robust_scores = np.array(robust_scores)
    robust_auc = robust_scores[:, 0].mean()
    robust_p = robust_scores[:, 1].mean()
    robust_r = robust_scores[:, 2].mean()
    # robust_f1 = robust_scores[:, 3].mean()
    robust_f1 = Benchmark.f1(robust_p, robust_r)

    print(
        "The carb scores AUC: {}, P: {}, R: {}, F1: {}".format(
            carb_auc, carb_p, carb_r, carb_f1
        )
    )
    print(
        "The robust scores AUC: {}, P: {}, R: {}, F1: {}".format(
            robust_auc, robust_p, robust_r, robust_f1
        )
    )

    os.makedirs(save_dir, exist_ok=True)
    with open(os.path.join(save_dir, "results.txt"), "w") as f:
        f.write(
            "The carb scores AUC: {}, P: {}, R: {}, F1: {}\n".format(
                carb_auc, carb_p, carb_r, carb_f1
            )
        )
        f.write(
            "The robust scores AUC: {}, P: {}, R: {}, F1: {}\n".format(
                robust_auc, robust_p, robust_r, robust_f1
            )
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pred_file",
        "-pred",
        type=str,
        default="result.json",
        help="The predicted json file with the unified ROBUST format.",
    )
    parser.add_argument(
        "--gold_file",
        "-gold",
        type=str,
        default="../../../data/openie6/ROBUST.json",
        help="The gold ROBUST json file.",
    )
    parser.add_argument(
        "--save_dir",
        "-s",
        type=str,
        default="data/",
        help="The directory to save results.",
    )
    args = parser.parse_args()

    main(args.gold_file, args.pred_file, args.save_dir)
