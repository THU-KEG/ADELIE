from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import json
import os
import jsonlines
from tqdm import tqdm
import random
from pathlib import Path
import evaluate


def get_score(pred, gold, metric):
    return metric.compute(predictions=pred, references=gold)["rougeLsum"]


def GenerateDPOunifiedData_4OpenInstructs(path, metric):
    trainInf_file = path + ".jsonl"
    out_bleu_file = path + "_" + metric + ".json"
    out_dpo_file = path + "_" + metric + "_4train.json"
    Limit_DPO_data = 50000
    if metric == "rough-l":
        metric_evaluate = evaluate.load("rouge")

    infdata = []
    with open(trainInf_file, "r", encoding="utf-8") as reader:
        for item in jsonlines.Reader(reader):
            infdata.append(item)
        reader.close()

    bleudata = []
    sum_bleu = 0
    for i, instance in enumerate(infdata):
        gold_text = instance["messages"][-1]["content"].split("[Answer]: ")[1]
        infdata[i]["metric"] = metric
        try:
            pre_text = instance["output"].split("[Answer]: ")[1]
            if metric == "bleu":
                bleu_score = sentence_bleu(
                    [list(gold_text)],
                    list(pre_text),
                    smoothing_function=SmoothingFunction().method3,
                )
                infdata[i]["score"] = bleu_score
            elif metric == "rough-l":
                print("================")
                print("pre_text:", pre_text)
                print("gold_text:", gold_text)
                cur_score = get_score([pre_text], [gold_text], metric_evaluate)
                infdata[i]["score"] = cur_score
                print("cur_score:", cur_score)
            else:
                print("No metric")
            sum_bleu += infdata[i]["score"]
        except:
            # prediction的时候失序，出现了过量重复的输出，怀疑可能是和cutoff有关
            # pre_text=instance["output"]
            # print(pre_text)
            # continue
            infdata[i]["score"] = -1

        bleudata.append(instance)

    out_file = open(path + "_" + metric + ".json", "w", encoding="utf-8")
    json.dump(bleudata, out_file, indent=2)
    out_file.close()

    bleudata.sort(key=lambda x: x["score"])  # 从小到大排序

    out_file = open(path + "_" + metric + "_sorted.json", "w", encoding="utf-8")
    json.dump(bleudata, out_file, indent=2)
    out_file.close()

    sum_bleu = sum_bleu / len(bleudata)
    print("avg_score:", sum_bleu)

    count = {}
    unified_data = []
    cnt = -1
    for i, instance in enumerate(bleudata):
        if instance["score"] == -1:
            continue
        cnt += 1
        if cnt >= Limit_DPO_data:
            break
        # if instance["dataset"]=="ondemand":
        #     continue
        if instance["score"] >= 1:
            print("Now is score >= 1.0:", i)
            break
        instance["chosen"] = instance["messages"]
        instance["rejected"] = instance["messages"][:-1]
        reject_output = {"role": "assistant", "content": instance["output"]}
        instance["rejected"].append(reject_output)
        if instance["dataset"] not in count:
            count[instance["dataset"]] = 0
            count[instance["dataset"] + "_avg_delta"] = 0
        count[instance["dataset"] + "_avg_delta"] = (
            (count[instance["dataset"] + "_avg_delta"] * count[instance["dataset"]])
            + (1 - instance["score"])
        ) / (count[instance["dataset"]] + 1)
        count[instance["dataset"]] += 1
        unified_data.append(instance)
    print(count)

    out_file = open(out_dpo_file, "w", encoding="utf-8")  ###########################
    json.dump(unified_data, out_file, indent=2)
    out_file.close()

    count["total"] = len(unified_data)
    out_file = open(
        "info_t_1.0.txt", "w", encoding="utf-8"
    )  ###########################
    json.dump(count, out_file, indent=2)
    out_file.close()


if __name__ == "__main__":
    path = "/data1/qyj/Alignment_on_IE_tasks/open-instruct/results/llama-base-7b/full/v20/mix_vDPO"
    GenerateDPOunifiedData_4OpenInstructs(path, "bleu")  # bleu rough-l
    # test()
