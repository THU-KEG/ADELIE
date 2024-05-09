import os
import json
import copy
import argparse

rich_ed = {
    "NA": 0,
    "endposition": 1,
    "transfermoney": 2,
    "fine": 3,
    "attack": 4,
    "die": 5,
    "startposition": 6,
    "convict": 7,
    "chargeindict": 8,
    "demonstrate": 9,
    "transaction": 10,
    "sentence": 11,
    "pardon": 12,
    "releaseparole": 13,
    "transferownership": 14,
    "transportartifact": 15,
    "arrestjail": 16,
    "broadcast": 17,
    "contact": 18,
    "divorce": 19,
    "execute": 20,
    "trialhearing": 21,
    "meet": 22,
    "sue": 23,
    "transportperson": 24,
    "beborn": 25,
    "marry": 26,
    "injure": 27,
    "correspondence": 28,
    "elect": 29,
    "nominate": 30,
    "acquit": 31,
    "startorg": 32,
    "extradite": 33,
    "endorg": 34,
    "appeal": 35,
    "declarebankruptcy": 36,
    "mergeorg": 37,
    "artifact": 38,
}


def comput_f1(input_file):
    tp = 0
    n_gold = 0
    n_pred = 0
    with open(input_file) as f:
        for line in f.readlines():
            instance = json.loads(line.strip())

            # gold triple
            gold_text = instance["messages"][-1]["content"].strip()
            gold_text = "".join(gold_text.split())
            gold_label = set()
            for label in gold_text.split(";"):
                if label:
                    gold_label.add(label)
            # pred triple
            pred_text = instance["output"]
            if "[Answer]:" in instance["output"]:
                pred_text = instance["output"].split("[Answer]:")[1].strip()
            else:
                pred_text = instance["output"]
            pred_text = "".join(pred_text.split())

            pred_label = set()
            for label in pred_text.split(";"):
                label = label.strip()
                if label != "" and "NA" not in label and ":" in label:
                    word = label.split(":")[0].strip()
                    role = label.split(":")[1].strip()
                    if role in rich_ed:
                        pred_label.add(":".join([l.strip() for l in label.split(":")]))

            label_stack = []
            for vert in gold_label:
                label_stack.append(vert)
            # print('gold', gold_label)
            # print('pred', pred_label)

            for label in pred_label:
                for vert in label_stack:
                    if label == vert:
                        tp += 1
                        label_stack.remove(vert)
                        break

            n_gold += len(gold_label)
            n_pred += len(pred_label)
    precision = tp / (n_pred + 1e-10)
    recall = tp / (n_gold + 1e-10)
    f1 = 2 * precision * recall / (precision + recall + 1e-10)
    print("gold:", n_gold)
    print("pred:", n_pred)
    print("tp:", tp)
    return {"precision": precision, "recall": recall, "f1": f1}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Event Detection")
    # IO
    parser.add_argument(
        "--input_dir",
        type=str,
        default="/data1/qyj/Alignment_on_IE_tasks/open-instruct/saves/llama_v2_7B/full/rate_0.2_plus_2.dpo_0.5_3f_0.1/predict/fewshot/RichERE-ed.jsonl",
    )
    parser.add_argument("--output_dir", type=str, default="result.json")

    args = parser.parse_args()
    # args.input_dir = '/Users/chenjianhui/Code/Academics/LLM-on-Complex-Tasks/unified_data/TAC-KBP/test.json'

    result = comput_f1(args.input_dir)
    print(result)
    # with open(args.output_dir, 'w') as f:
    #     json.dump(result, f, indent=4)
    # print(result)
