from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import json
import os
import jsonlines
from tqdm import tqdm
import random
from pathlib import Path
import copy


def GenerateDPOunifiedData_Online_4OpenInstructs():
    file1="/SSD_DATA/qyj/open-instruct-main/results/llama_v2_7B/full/rate_0.2/mix_vDPO_bleu.json"
    file2="/SSD_DATA/qyj/open-instruct-main/results/llama_v2_7B/full/rate_0.2/T_1.0/mix_vDPO_bleu.json"
    out_dpo_file="/SSD_DATA/qyj/open-instruct-main/results/llama_v2_7B/full/rate_0.2/T_1.0/mix_vDPO_bleu_4train_online.json"
    Limit_DPO_data = 50000

    with open(file1, "r", encoding="utf-8") as reader:
        infdata1=json.load(reader)
        reader.close()
    with open(file2, "r", encoding="utf-8") as reader:
        infdata2=json.load(reader)
        reader.close()

    print(len(infdata1))
    print(len(infdata2))
    assert len(infdata1) == len(infdata2)
    count = {}
    unified_data = []
    cnt=-1
    samescore=0
    for ins1,ins2 in zip(infdata1,infdata2):
        if ins1["dataset"] != ins2["dataset"] or ins1["id"] != ins2["id"]:
            print("Error Match")
            continue
        if ins1["score"] == -1 or ins2["score"] == -1: #无效输出
            continue
        if ins1["score"] == ins2["score"]:
            samescore+=1
            continue

        cnt+=1
        if cnt >= Limit_DPO_data:
            break

        instance={
            "dataset": ins1["dataset"],
            "id": ins1["id"],
            "messages": ins1["messages"],
            "chosen": ins1["messages"][:-1],
            "rejected": ins1["messages"][:-1],
        }

        if ins1["score"] > ins2["score"]:
            chosen_output = {"role": "assistant", "content": ins1["output"]}
            reject_output = {"role": "assistant", "content": ins2["output"]}
        else:
            chosen_output = {"role": "assistant", "content": ins2["output"]}
            reject_output = {"role": "assistant", "content": ins1["output"]}

        instance["rejected"].append(reject_output)
        instance["chosen"].append(chosen_output)

        delta = abs(ins1["score"] - ins2["score"])

        if instance["dataset"] not in count:
            count[instance["dataset"]] = 0
            count[instance["dataset"]+"_avg_score"]=0
        count[instance["dataset"]+"_avg_score"]=((count[instance["dataset"]+"_avg_score"]*count[instance["dataset"]])+delta)/(count[instance["dataset"]]+1)
        count[instance["dataset"]] += 1
        unified_data.append(instance)
    print(count)
    print(samescore)

    out_file = open(out_dpo_file, "w", encoding="utf-8")  ###########################
    json.dump(unified_data, out_file, indent=2)
    out_file.close()

    count["total"]=len(unified_data)
    out_file = open("info_1.0_0.1.txt", "w", encoding="utf-8")  ###########################
    json.dump(count, out_file, indent=2)
    out_file.close()


if __name__ == "__main__":
    GenerateDPOunifiedData_Online_4OpenInstructs()
    # test()