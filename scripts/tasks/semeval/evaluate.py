import os
import json
import re

OPTIONS = "Component-Whole(e2,e1), Instrument-Agency(e2,e1), Member-Collection(e1,e2), Cause-Effect(e2,e1), Entity-Destination(e1,e2), Content-Container(e1,e2), Message-Topic(e1,e2), Product-Producer(e2,e1), Member-Collection(e2,e1), Entity-Origin(e1,e2), Cause-Effect(e1,e2), Component-Whole(e1,e2), Message-Topic(e2,e1), Product-Producer(e1,e2), Entity-Origin(e2,e1), Content-Container(e2,e1), Instrument-Agency(e1,e2), Entity-Destination(e2,e1)"

STR = " and "
NewF = False

semeval_rel = OPTIONS.lower()
semeval_rel = semeval_rel.split(", ")
for i, item in enumerate(semeval_rel):
    e1 = item.split("-")[0]
    e2 = item.split("-")[1].split("(")[0]
    if NewF == True:
        if "(e1,e2)" in item:
            semeval_rel[i] = "is_" + e1 + "_and_" + e2 + "_is"
        else:
            semeval_rel[i] = "is_" + e2 + "_and_" + e1 + "_is"
    else:
        if "(e1,e2)" in item:
            semeval_rel[i] = e1 + STR + e2
        else:
            semeval_rel[i] = e2 + STR + e1
print(semeval_rel)


def parse_triple(text):
    pattern = re.compile("\((.*); (.*); (.*)\)")
    # print("text:",text)
    triple = re.findall(pattern, text)

    if len(triple) == 0:
        return None

    t = set()
    for vert in triple:
        t.add(vert)
    tlist = []
    for vert in t:
        tlist.append(list(vert))
    return tlist


def comput_f1(input_file):
    tp = 0
    n_gold = 0
    n_pred = 0
    id = -1
    with open(input_file) as f:
        for line in f.readlines():
            id += 1
            instance = json.loads(line.strip())
            # gold triple
            gold_triples = []
            gold_text = instance["label"].strip().lower()
            if gold_text != "" and gold_text != "[answer]: na":
                gold_triple = parse_triple(gold_text)
                # print(gold_text)
                assert gold_triple is not None
                gold_triples = gold_triple

            pred_triples = []
            pred_text = ""
            if "[Answer]:" in instance["predict"]:
                pred_text = instance["predict"].split("[Answer]:")[1].strip().lower()
            else:
                pred_text = instance["predict"].strip().lower()

            pred_triple = parse_triple(pred_text)
            if pred_triple is not None:
                pred_triples = pred_triple

            for triple in gold_triples:
                if triple in pred_triples:
                    tp += 1
                else:
                    # triple=list(triple)[0]
                    # print("triple:",triple)
                    e1 = triple[0]
                    e2 = triple[2]
                    if NewF == True:
                        r1 = triple[1].split("_")[1]
                        r2 = triple[1].split("_")[3]
                        new_triple = [e2, "is_" + r2 + "_and_" + r1 + "_is", e1]
                    else:
                        r1 = triple[1].split(STR)[0]
                        r2 = triple[1].split(STR)[1]
                        new_triple = [e2, r2 + STR + r1, e1]

                    if new_triple in pred_triples:
                        tp += 1
                        # print("pred:",pred_triples)
                        # print("gold:",gold_triples)

            PFlag = False
            for triple in pred_triples:
                if triple[1] in semeval_rel:
                    if len(gold_triples) > 0:
                        if (
                            triple[0] == gold_triples[0][0]
                            and triple[2] == gold_triples[0][2]
                        ):
                            n_pred += 1
                            PFlag = True
                        if (
                            triple[2] == gold_triples[0][0]
                            and triple[0] == gold_triples[0][2]
                        ):
                            n_pred += 1
                            PFlag = True
                    else:
                        n_pred += 1
                        PFlag = True

            if PFlag == True or len(pred_triples) == 0:
                n_gold += len(gold_triples)

    precision = tp / n_pred
    recall = tp / n_gold
    print("tp:", tp)
    print("n_pred:", n_pred)
    print("n_gold:", n_gold)
    if precision + recall == 0:
        f1 = 0
    else:
        f1 = 2 * precision * recall / (precision + recall)
    return {"precision": precision, "recall": recall, "f1": f1}


if __name__ == "__main__":
    result = comput_f1(
        "/data1/qyj/Alignment_on_IE_tasks/Train4LLama/saves/llama-2-base/full/rate_0.2_dpo_.6_3f/predict/fewshot_test_history/semeval/generated_predictions.jsonl"
    )
    print(result)
