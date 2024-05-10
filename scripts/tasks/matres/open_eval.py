import argparse
import json
import numpy as np
import re
import random


parser = argparse.ArgumentParser(description="Query OpenAI")
parser.add_argument(
    "--output_file",
    type=str,
    default="/SSD_DATA/qyj/open-instruct-main/saves/llama_v2_7B/full/no_output_desc/predict/zeroshot/MATRES.jsonl",
)  # fewshot_test_history_3
args = parser.parse_args()


# 对于4种关系，num_ans为label的数量、num_out为回答的数量、num_cor为答对的数量
num_ans, num_out, num_cor = [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]
with open(args.output_file) as file:
    lines = file.readlines()
rel_class = {"before": 0, "after": 1, "equal": 2, "vague": 3}


def parse_triple(text):
    pattern = re.compile("\((.*); (.*); (.*)\)")
    # print("Text:",text)
    triple = re.findall(pattern, text)
    if len(triple) == 0:
        return None
    # print("text:",text)
    # print("Triple:",triple[0])
    return triple[0][1]


for line in lines:
    result = json.loads(line)
    label = result["messages"][-1]["content"]
    output = result["output"]
    if label != "none" and label != "":
        num_ans[rel_class[label]] += 1
    try:
        search_obj = re.search(r"[Answer](.*?): (.*)", output)
        out_label = re.findall(r"([a-zA-Z-]+)", search_obj.group(2))[0]
    except:
        continue
    la = output.lower()
    # if la in rel_class.keys():
    #     num_out[rel_class[la]] += 1
    #     if la in label:
    #         num_cor[rel_class[la]] += 1
    # else:
    #     num_out[random.randint(0, 3)] += 1

    pre_triple = parse_triple(la)
    # print("pre_triple:",pre_triple)
    if pre_triple != [] and pre_triple != None:
        for k in rel_class.keys():
            if k in pre_triple:
                num_out[rel_class[k]] += 1
                if k in label:
                    num_cor[rel_class[k]] += 1

print("ANS:", num_ans)
print("OUT:", num_out)
print("COR:", num_cor)
num_ans.append(np.sum(num_ans))
num_out.append(np.sum(num_out))
num_cor.append(np.sum(num_cor))
num_ans = np.array(num_ans)
num_out = np.array(num_out)
num_cor = np.array(num_cor)
p = num_cor / num_out
r = num_cor / num_ans
f1 = 2 * p * r / (p + r)
print("            Before | After | Equal | Vague | Total")
print(f"precision:  {p[0]:.4f} | {p[1]:.4f}| {p[2]:.4f}| {p[3]:.4f}| {p[4]:.4f}")
print(f"recall:     {r[0]:.4f} | {r[1]:.4f}| {r[2]:.4f}| {r[3]:.4f}| {r[4]:.4f}")
print(f"f1-score:   {f1[0]:.4f} | {f1[1]:.4f}| {f1[2]:.4f}| {f1[3]:.4f}| {f1[4]:.4f}")
