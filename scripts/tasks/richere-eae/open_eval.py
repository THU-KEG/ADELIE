import os
import json
import copy
import argparse


rich_role = {
    "NA": 0,
    "entity": 1,
    "person": 2,
    "position": 3,
    "place": 4,
    "giver": 5,
    "recipient": 6,
    "money": 7,
    "time": 8,
    "attacker": 9,
    "target": 10,
    "victim": 11,
    "defendant": 12,
    "crime": 13,
    "agent": 14,
    "sentence": 15,
    "thing": 16,
    "artifact": 17,
    "origin": 18,
    "audience": 19,
    "prosecutor": 20,
    "plaintiff": 21,
    "destination": 22,
    "instrument": 23,
    "adjudicator": 24,
    "org": 25,
    "beneficiary": 26,
}


def comput_f1(input_file):
    tp = 0
    n_gold = 0
    n_pred = 0
    # input_file = os.path.join(input_file, 'test.json')
    with open(input_file) as f:
        for line in f.readlines():
            instance = json.loads(line.strip())
            # gold triple
            gold_text = instance["messages"][-1]["content"].strip().lower()
            gold_text = "".join(gold_text.split())
            gold_label = set()
            for label in gold_text.split(";"):
                if label:
                    gold_label.add(label)
            # pred triple
            pred_text = ""
            if "[Answer]:" in instance["output"]:
                pred_text = instance["output"].split("[Answer]:")[1].strip().lower()
            else:
                pred_text = instance["output"].lower()
            pred_text = "".join(pred_text.split())

            pred_label = set()
            for label in pred_text.split(";"):
                label = label.strip()
                if label != "" and "NA" not in label and ":" in label:
                    word = label.split(":")[0].strip()
                    role = label.split(":")[1].strip()
                    if role in rich_role:
                        pred_label.add(":".join([l.strip() for l in label.split(":")]))

            label_stack = []
            for vert in gold_label:
                label_stack.append(vert)
            print("gold", gold_label)
            print("pred", pred_label)
            for label in pred_label:
                if label in label_stack:
                    tp += 1
                    label_stack.remove(label)
            n_gold += len(gold_label)
            n_pred += len(pred_label)
    precision = tp / (n_pred + 1e-10)
    recall = tp / (n_gold + 1e-10)
    f1 = 2 * precision * recall / (precision + recall + 1e-10)
    return {"precision": precision, "recall": recall, "f1": f1}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate Event Detection")
    # IO
    parser.add_argument(
        "--input_dir",
        type=str,
        default="/data1/qyj/Alignment_on_IE_tasks/open-instruct/saves/llama_v2_7B/full/rate_0.2_plus_2.dpo_0.5_3f_0.1/predict/fewshot/RichERE-eae.jsonl",
    )
    # parser.add_argument("--output_dir", type=str, default='/home/qijy/workspace/Alignment_on_IE_tasks/Train_code/LLaMA-Factory-main/saves/LLaMA2-7B-Chat/lora/predict/ace2005-eae/generated_predictions.jsonl')

    args = parser.parse_args()
    # args.input_dir = '/Users/chenjianhui/Code/Academics/LLM-on-Complex-Tasks/unified_data/TAC-KBP/test.json'

    result = comput_f1(args.input_dir)
    # with open(args.output_dir, 'w') as f:
    #     json.dump(result, f, indent=4)
    print(result)
