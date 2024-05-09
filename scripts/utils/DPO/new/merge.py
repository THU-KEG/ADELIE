from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import json
import os
import jsonlines
from tqdm import tqdm
import random
from pathlib import Path
import copy


files = [
    "/data1/qyj/Alignment_on_IE_tasks/open-instruct/results/llama-base-7b/full/rate_0.2/mix_vDPO_bleu.json",
    "/data1/qyj/Alignment_on_IE_tasks/open-instruct/results/llama-base-7b/full/rate_0.2/T_1.0/mix_vDPO_bleu.json",
    "/data1/qyj/Alignment_on_IE_tasks/open-instruct/results/llama-base-7b/full/v20/mix_vDPO_bleu.json",
]
gold_rate = 00
No_Gold = False  # 只有rate=0.0的是时候，no gold才能=true
Limit_DPO_data = 50000
out_dpo_file = "/data1/qyj/Alignment_on_IE_tasks/open-instruct/results/llama-base-7b/full/rate_0.2/mixture/mix_vDPO_bleu_4train_mix_.6_3f.json"
info_file = "/data1/qyj/Alignment_on_IE_tasks/open-instruct/results/llama-base-7b/full/rate_0.2/mixture/info_.6_3f.txt"


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

        GoldenF = (int)(random.random() < gold_rate)
        if GoldenF or c_num == r_num:
            if GoldenF == 0 and No_Gold == True:
                continue
            gold_count += 1
            chosen_output = infdata[j][i]["messages"][-1]
            delta = abs(1.0 - r_num)

        if delta == 0.0:
            continue

        cnt += 1
        if cnt >= Limit_DPO_data:
            break

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
    print(count)

    out_file = open(out_dpo_file, "w", encoding="utf-8")  ###########################
    json.dump(unified_data, out_file, indent=2)
    out_file.close()

    count["total"] = len(unified_data)
    print("gold_rate: ", gold_count / count["total"])
    print("avg_delta: ", samescore / count["total"])
    out_file = open(info_file, "w", encoding="utf-8")  ###########################
    json.dump(count, out_file, indent=2)
    out_file.close()


if __name__ == "__main__":
    GenerateDPOunifiedData_Online_4OpenInstructs()
    # test()
