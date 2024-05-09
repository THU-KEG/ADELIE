import os
import json
import re


def get_args(id, pred):
    # print("ID", id, len(pred))
    try:
        prediction = pred[id]["predict"].split("[Answer]: ")[1]
    except:
        prediction = pred[id]["predict"]
    pattern = re.compile("\((.*)\);")
    triple = re.findall(pattern, prediction)
    if triple == []:
        pattern = re.compile("\((.*)\)\n")
        triple = re.findall(pattern, prediction)
    # print("PRED:", prediction)
    # print("TRIPLE: ", triple)
    args = []
    for vert in triple:
        arg = vert.split("; ")
        a = []
        for item in arg:
            if item != "None":
                a.append(item)
        args.append(a)

    # print("ARGS:", args)
    return args


def reformat(input_file):
    pred = []
    with open(input_file) as f:
        for line in f.readlines():
            instance = json.loads(line.strip())
            pred.append(instance)

    with open("/data1/qyj/Alignment_on_IE_tasks/data/openie6/ROBUST.json", "r") as f:
        gold = json.load(f)
        f.close()

    result = []
    idx = -1
    for instance in gold:
        # ori_sentence
        idx += 1
        args = get_args(idx, pred)
        instance["ori_args"] = args
        # para
        for i, para in enumerate(instance["paraphrases"]):
            idx += 1
            args = get_args(idx, pred)
            instance["paraphrases"][i]["args"] = args
        result.append(instance)

    print("idx:", idx)
    print("pred num:", len(pred))
    return result


if __name__ == "__main__":
    result = reformat(
        "/data1/qyj/Alignment_on_IE_tasks/Train4LLama/saves/llama-2-base/full/no_schema_desc/predict/fewshot_test_history/ROBUST/generated_predictions.jsonl"
    )
    out_file = open("result_no_schema_desc.json", "w")
    json.dump(result, out_file, indent=1)
    out_file.close()
