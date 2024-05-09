# from ph_unified_data:
import os
import json
import random
import copy
import jsonlines
from pathlib import Path


def construct_response(pre_file, gold_file, output_file):
    print("gold_file:", gold_file)
    with open(gold_file, "r", encoding="utf-8") as reader:
        init_dataset = json.load(reader)
        reader.close()

    pred_dataset = []
    with open(pre_file, "r", encoding="utf-8") as reader:
        for item in jsonlines.Reader(reader):
            pred_dataset.append(item)
        reader.close()

    assert len(init_dataset) == len(
        pred_dataset
    ), "number of predictions and targets are not the same."

    for gold, pred in zip(init_dataset, pred_dataset):

        gold["gold"] = gold["table"]
        gold["output"] = pred["predict"]

    out_file = open(output_file, "w")
    json.dump(init_dataset, out_file, indent=2)
    out_file.close()


if __name__ == "__main__":
    input_file1 = "/data1/qyj/Alignment_on_IE_tasks/Train4LLama/saves/llama-2-base/full/no_schema_desc/predict/zeroshot/ondemand/generated_predictions.jsonl"
    input_folder2 = Path("../../../data/ondemandIE")
    input_file2 = "test_data.json"
    output_folder = Path("./")  # 修改路径
    output_folder.mkdir(exist_ok=True, parents=True)

    construct_response(
        input_file1,
        os.path.join(input_folder2, input_file2),
        os.path.join(output_folder, input_file2),
    )
