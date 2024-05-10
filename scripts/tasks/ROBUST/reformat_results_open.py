import os
import json
import re
import argparse


def get_args(id, pred):
    # print("ID",id,len(pred))
    try:
        prediction = pred[id]["output"].split("[Answer]: ")[1]
    except:
        prediction = pred[id]["output"]
    pattern = re.compile("\((.*)\)")
    triple = re.findall(pattern, prediction)
    # print("PRED:",prediction)
    # print("TRIPLE: ",triple)
    args = []
    for vert in triple:
        arg = vert.split("; ")
        args.append(arg)

    # print("ARGS:",args)
    return args


def reformat(input_file):
    pred = []
    with open(input_file) as f:
        for line in f.readlines():
            instance = json.loads(line.strip())
            pred.append(instance)

    with open(
        "/SSD_DATA/qyj/Alignment_on_IE_tasks/scripts/tasks/ROBUST/data/ROBUST.json", "r"
    ) as f:
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
    parser = argparse.ArgumentParser(description="tacred")
    parser.add_argument(
        "--input_dir",
        type=str,
        default="/SSD_DATA/qyj/Alignment_on_IE_tasks/scripts/tasks/ROBUST/data/",
    )
    args = parser.parse_args()

    result = reformat(args.input_dir)
    out_file = open("result.json", "w")
    json.dump(result, out_file, indent=1)
    out_file.close()
