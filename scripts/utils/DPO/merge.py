from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import json
import os
import jsonlines
from tqdm import tqdm
import random
from pathlib import Path
import copy


files = [
    "../unified_data/train_mixture/sample4dpo_results/ADELIE-SFT/T_1.0_1/mix_vDPO_bleu.json",
    "../unified_data/train_mixture/sample4dpo_results/ADELIE-SFT/T_1.0_2/mix_vDPO_bleu.json",
    "../unified_data/train_mixture/sample4dpo_results/ADELIE-SFT/T_1.0_3/mix_vDPO_bleu.json",
    "../unified_data/train_mixture/sample4dpo_results/ADELIE-SFT/T_1.0_4/mix_vDPO_bleu.json",
    "../unified_data/train_mixture/sample4dpo_results/ADELIE-SFT/T_1.0_5/mix_vDPO_bleu.json",
]
gold_rate = 0.7
No_Gold = False
Limit_DPO_data = 10000
Limit_delta = 0.1
out_dpo_file = "../unified_data/train_mixture/IEFeedback.json"
info_file = "../unified_data/train_mixture/info.IEFeedback.txt"


def GenerateDPOunifiedData_Online_4OpenInstructs():

    infdata = []
    length = 0
    for f in files:
        with open(f, "r", encoding="utf-8") as reader:
            d = json.load(reader)
            reader.close()
        if length == 0:
            length = len(d)
        temp = len(d)
        assert length == temp, "error match length"
        infdata.append(d)

    count = {}
    unified_data = []
    cnt = -1
    samescore = 0
    gold_count = 0

    # gold
    gold_num = int(Limit_DPO_data * gold_rate)
    print(gold_num)

    not_in = []
    for i, instance in enumerate(infdata[0]):
        c_num = -1.0
        r_num = 2.0
        id = instance["id"]
        for j in range(0, len(files)):
            assert infdata[j][i]["id"] == id, "error match id"
            if infdata[j][i]["score"] > c_num:
                chosen_output = {
                    "role": "assistant",
                    "content": infdata[j][i]["output"],
                }
                c_num = infdata[j][i]["score"]
            if infdata[j][i]["score"] < r_num:
                reject_output = {
                    "role": "assistant",
                    "content": infdata[j][i]["output"],
                }
                r_num = infdata[j][i]["score"]

        delta = abs(c_num - r_num)

        if delta <= Limit_delta:
            not_in.append(i)
            continue

        cnt += 1

        if cnt >= Limit_DPO_data - gold_num:
            not_in.append(i)
            continue

        instance = {
            "dataset": instance["dataset"],
            "id": instance["id"],
            "messages": instance["messages"],
            "chosen": instance["messages"][:-1],
            "rejected": instance["messages"][:-1],
        }

        instance["rejected"].append(reject_output)
        instance["chosen"].append(chosen_output)

        if instance["dataset"] not in count:
            count[instance["dataset"]] = 0
            count[instance["dataset"] + "_avg_delta"] = 0
        count[instance["dataset"] + "_avg_delta"] = (
            (count[instance["dataset"] + "_avg_delta"] * count[instance["dataset"]])
            + delta
        ) / (count[instance["dataset"]] + 1)
        count[instance["dataset"]] += 1
        unified_data.append(instance)
        samescore += delta

    gold_idx = random.sample(not_in, gold_num)

    for i, instance in enumerate(infdata[0]):
        if i not in gold_idx:
            continue
        c_num = 1.0
        r_num = 2.0
        id = instance["id"]
        for j in range(0, len(files)):
            assert infdata[j][i]["id"] == id, "error match id"
            if infdata[j][i]["score"] < r_num:
                reject_output = {
                    "role": "assistant",
                    "content": infdata[j][i]["output"],
                }
                r_num = infdata[j][i]["score"]
        chosen_output = infdata[j][i]["messages"][-1]

        delta = abs(c_num - r_num)

        if delta <= Limit_delta:
            continue

        gold_count += 1
        instance = {
            "dataset": instance["dataset"],
            "id": instance["id"],
            "messages": instance["messages"],
            "chosen": instance["messages"][:-1],
            "rejected": instance["messages"][:-1],
        }

        instance["rejected"].append(reject_output)
        instance["chosen"].append(chosen_output)

        if instance["dataset"] not in count:
            count[instance["dataset"]] = 0
            count[instance["dataset"] + "_avg_delta"] = 0
        count[instance["dataset"] + "_avg_delta"] = (
            (count[instance["dataset"] + "_avg_delta"] * count[instance["dataset"]])
            + delta
        ) / (count[instance["dataset"]] + 1)
        count[instance["dataset"]] += 1
        unified_data.append(instance)
        samescore += delta

    out_file = open(out_dpo_file, "w", encoding="utf-8")  ###########################
    json.dump(unified_data, out_file, indent=2)
    out_file.close()

    count["total"] = len(unified_data)
    print(count)
    print(gold_count, count["total"])
    print("gold_rate: ", gold_count / count["total"])
    print("avg_delta: ", samescore / count["total"])
    out_file = open(info_file, "w", encoding="utf-8")  ###########################
    json.dump(count, out_file, indent=2)
    out_file.close()


if __name__ == "__main__":
    GenerateDPOunifiedData_Online_4OpenInstructs()
    # test()
