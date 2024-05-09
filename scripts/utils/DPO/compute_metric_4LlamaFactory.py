from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import json
import os
import jsonlines
from tqdm import tqdm
import random
from pathlib import Path


def create_prompt_with_tulu_chat_format(messages, bos="<s>", eos="</s>", add_bos=False):
    formatted_text = ""
    for i, message in enumerate(messages):
        if message["role"] == "system":
            formatted_text += "<|system|>\n" + message["content"] + "\n"
        elif message["role"] == "user":
            formatted_text += "<|user|>\n" + message["content"] + "\n"
        elif message["role"] == "assistant":
            formatted_text += (
                "<|assistant|>\n" + message["content"].strip() + eos + "\n"
            )
        else:
            raise ValueError(
                "Tulu chat template only supports 'system', 'user' and 'assistant' roles. Invalid role: {}.".format(
                    message["role"]
                )
            )
    formatted_text += "<|assistant|>\n"
    formatted_text = bos + formatted_text if add_bos else formatted_text
    return formatted_text


def GenerateDPOunifiedData_4LlamaFactory():
    trainInf_file = "/data1/qyj/Alignment_on_IE_tasks/open-instruct/results/llama-base-7b/full/v20/mix_vDPO.jsonl"
    out_bleu_file = "/data1/qyj/Alignment_on_IE_tasks/open-instruct/results/llama-base-7b/full/v20/mix_vDPO_bleu.json"
    out_dpo_file = "/data1/qyj/Alignment_on_IE_tasks/open-instruct/results/llama-base-7b/full/v20/mix_vDPO_4train.json"
    Limit_DPO_data = 50000

    infdata = []
    with open(trainInf_file, "r", encoding="utf-8") as reader:
        for item in jsonlines.Reader(reader):
            infdata.append(item)
        reader.close()

    bleudata = []
    sum_bleu = 0
    for i, instance in enumerate(infdata):
        if instance["dataset"] == "MAVEN-ERE":
            continue
        gold_text = instance["messages"][-1]["content"].split("[Answer]: ")[1]
        try:
            pre_text = instance["output"].split("[Answer]: ")[1]
        except:
            # prediction的时候失序，出现了过量重复的输出，怀疑可能是和cutoff有关
            # pre_text=instance["output"]
            # print(pre_text)
            continue
        bleu_score = sentence_bleu(
            [list(gold_text)],
            list(pre_text),
            smoothing_function=SmoothingFunction().method3,
        )
        infdata[i]["bleu-4"] = bleu_score
        bleudata.append(instance)
        sum_bleu += bleu_score
    bleudata.sort(key=lambda x: x["bleu-4"])  # 从小到大排序

    out_file = open(out_bleu_file, "w", encoding="utf-8")
    json.dump(bleudata, out_file, indent=2)
    out_file.close()

    sum_bleu = sum_bleu / len(bleudata)
    print("avg_bleu:", sum_bleu)

    count = {}
    unified_data = []
    for i, instance in enumerate(bleudata):
        if i >= Limit_DPO_data:
            break
        unified_instance = {
            "system": instance["system"] if "system" in instance else "",
            "instruction": create_prompt_with_tulu_chat_format(
                instance["messages"][:-1]
            ),
            "input": "",
            "output": [
                instance["messages"][-1]["content"],
                instance["output"],
            ],
            "bleu-4": bleu_score,
        }
        if instance["dataset"] not in count:
            count[instance["dataset"]] = 0
        count[instance["dataset"]] += 1
        unified_data.append(unified_instance)
    print(count)

    out_file = open(out_dpo_file, "w", encoding="utf-8")  ###########################
    json.dump(unified_data, out_file, indent=2)
    out_file.close()

    out_file = open("info.txt", "w", encoding="utf-8")  ###########################
    json.dump(count, out_file, indent=2)
    out_file.close()


if __name__ == "__main__":
    GenerateDPOunifiedData_4LlamaFactory()
