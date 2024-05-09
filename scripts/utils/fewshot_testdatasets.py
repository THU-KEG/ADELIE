# 对test_format生成的few-shot测试集（all few-shot）
# 其中few-shot样例来自于train中随机挑选

import random
import json
import jsonlines
import os
from pathlib import Path
import argparse

word_Limit = 240000
NA_rate = 0.2


EXPLAN_QUERY = [
    "First explain your thoughts and then give the answer. ",
    "Please give the explanation first. ",
    "Please explain first. ",
    "Make explanation according to the sentence and give the answer. ",
]


############### v5 instruct(x)⊕ x1 ⊕ y1 ⊕ ..⊕ x 适配于load_data_fs.py 放入history no desc & explain ###############
def generate_fewshot_format(
    input_folder, output_folder, hold_out_datasets, numFew=4, seed=24
):
    random.seed(seed)

    path = input_folder

    output_folder = Path(output_folder + "/fewshot_test_history")
    output_folder.mkdir(exist_ok=True, parents=True)

    valid_data = []
    NA_data = []
    names = []
    unified_data = []
    filenames = []
    for dirname in hold_out_datasets:
        file_list = os.listdir(os.path.join(path, dirname))
        filenames.clear()
        for f in file_list:
            if "test" in f:
                filenames.append(f)
        for filename in filenames:
            if filename == "":
                continue
            if filename[-6:] != ".jsonl":
                continue

            # if dirname != "ROBUST":
            #     continue

            # if dirname != "semeval":
            #     continue

            sum_valid_data = 0
            valid_data.clear()
            NA_data.clear()
            unified_data.clear()
            with open(
                os.path.join(path, dirname, filename), "r", encoding="utf-8"
            ) as reader:
                for item in jsonlines.Reader(reader):
                    if dirname == "ROBUST":
                        valid_data.append(item)
                    else:
                        if (
                            item["reference"] == "NA"
                            or item["reference"] == "[]"
                            or item["reference"] == ""
                            or item["reference"] == []
                            or item["reference"] == "none"
                        ):
                            NA_data.append(item)
                        else:
                            valid_data.append(item)
                reader.close()
            sum_valid_data = len(valid_data)
            num_NA_data = int((sum_valid_data / (1.0 - NA_rate)) * NA_rate)
            print(dirname)
            print(sum_valid_data, len(NA_data), num_NA_data)
            if num_NA_data < len(NA_data):
                NA_data = random.sample(NA_data, num_NA_data)
            print("sample NA:", len(NA_data))
            valid_data = valid_data + NA_data
            if dirname != "ROBUST":
                random.shuffle(valid_data)
            print("sum:", len(valid_data))

            for d in valid_data:
                instruction = d["instruction"]
                if d["query"][0] == 1:
                    ex_q = random.sample(EXPLAN_QUERY, 1)[0]
                    instruction += ex_q
                instruction += d["query"][1]

                input = "Text: '" + d["input"] + "'"

                unified_instance = {
                    "instruction": instruction,
                    "input": input,
                    "output": str(d["reference"]),
                    "history": [],
                }

                # numFew = 4
                # if dirname == "ROBUST":
                #     numFew = 5
                if numFew:
                    origin_word = instruction.split(" ") + input.split(" ")
                    total_word = len(origin_word)
                    HIS_Flag = False
                    for i, vert in enumerate(d["examples"]):
                        if i + 1 > numFew:
                            break
                        if total_word > word_Limit:
                            break
                        word = vert[0].split(" ") + vert[1].split(" ")
                        total_word += len(word)
                        if total_word > word_Limit:
                            break
                        # 满足字数要求
                        if HIS_Flag == False:
                            unified_instance["history"].append(
                                [instruction + "Text: '" + vert[0] + "'", vert[1]]
                            )
                            HIS_Flag = True
                        else:
                            unified_instance["history"].append(
                                ["Text: '" + vert[0] + "'", vert[1]]
                            )

                    if HIS_Flag == False:
                        unified_instance["instruction"] = instruction
                        unified_instance["input"] = input
                    else:
                        unified_instance["instruction"] = input
                        unified_instance["input"] = ""
                unified_data.append(unified_instance)

            n = len(unified_data)
            if dirname != "ROBUST":
                unified_data = random.sample(unified_data, min(1000, n))
            if len(filenames) == 1:
                names.append(dirname)
                out_file = open(os.path.join(output_folder, dirname + ".json"), "w")
                json.dump(unified_data, out_file, indent=2)
                out_file.close()
            else:
                f = filename[:-6]
                names.append(dirname + "_" + f)
                out_file = open(
                    os.path.join(output_folder, dirname + "_" + f + ".json"), "w"
                )
                json.dump(unified_data, out_file, indent=2)
                out_file.close()

    # Generate dataset_info
    data_info = dict()
    for vert in names:
        data_info[vert] = {"file_name": vert + ".json", "file_sha1": ""}
    out_file = open(os.path.join(output_folder, "dataset_info.json"), "w")
    json.dump(data_info, out_file, indent=2)
    out_file.close()


def get_normal_instruction(d):
    instruction = d["instruction"]
    if d["query"][0] == 1:
        ex_q = random.sample(EXPLAN_QUERY, 1)[0]
        instruction += ex_q
    instruction += d["query"][1]

    text_Flag = False
    if "<text>" in instruction:
        id = (int)(random.random() >= 0.3)
        if id:
            instruction = instruction.replace("<text>", "Text: '" + d["input"] + "'")
            text_Flag = True

    if text_Flag == False:
        input = "Text: '" + d["input"] + "'"
        return instruction, input
    else:
        input = ""
        return instruction, input


def generate_zeroshot_format(
    input_folder, output_folder, hold_out_datasets, numFew=4, seed=24
):
    random.seed(seed)

    path = input_folder
    output_folder = Path(output_folder + "/zeroshot")
    output_folder.mkdir(exist_ok=True, parents=True)

    valid_data = []
    NA_data = []
    names = []
    unified_data = []
    filenames = []
    for dirname in hold_out_datasets:
        file_list = os.listdir(os.path.join(path, dirname))
        filenames.clear()
        for f in file_list:
            if "test" in f:
                filenames.append(f)
        for filename in filenames:
            if filename == "":
                continue
            if filename[-6:] != ".jsonl":
                continue

            # if dirname != "ROBUST":
            #     continue

            # if dirname != "semeval":
            #     continue

            sum_valid_data = 0
            valid_data.clear()
            NA_data.clear()
            unified_data.clear()
            with open(
                os.path.join(path, dirname, filename), "r", encoding="utf-8"
            ) as reader:
                for item in jsonlines.Reader(reader):
                    if dirname == "ROBUST":
                        valid_data.append(item)
                    else:
                        if (
                            item["reference"] == "NA"
                            or item["reference"] == "[]"
                            or item["reference"] == ""
                            or item["reference"] == []
                            or item["reference"] == "none"
                        ):
                            NA_data.append(item)
                        else:
                            valid_data.append(item)
                reader.close()
            sum_valid_data = len(valid_data)
            num_NA_data = int((sum_valid_data / (1.0 - NA_rate)) * NA_rate)
            print(dirname)
            print(sum_valid_data, len(NA_data), num_NA_data)
            if num_NA_data < len(NA_data):
                NA_data = random.sample(NA_data, num_NA_data)
            print("sample NA:", len(NA_data))
            valid_data = valid_data + NA_data
            if dirname != "ROBUST":
                random.shuffle(valid_data)
            print("sum:", len(valid_data))

            for vert in valid_data:
                unified_instance = {
                    "instruction": "",
                    "input": "",
                    "output": vert["reference"],
                    "history": [],
                }

                unified_instance["instruction"], unified_instance["input"] = (
                    get_normal_instruction(vert)
                )
                unified_data.append(unified_instance)

            n = len(unified_data)
            if dirname != "ROBUST":
                unified_data = random.sample(unified_data, min(1000, n))
            if len(filenames) == 1:
                names.append(dirname)
                out_file = open(os.path.join(output_folder, dirname + ".json"), "w")
                json.dump(unified_data, out_file, indent=2)
                out_file.close()
            else:
                f = filename[:-6]
                names.append(dirname + "_" + f)
                out_file = open(
                    os.path.join(output_folder, dirname + "_" + f + ".json"), "w"
                )
                json.dump(unified_data, out_file, indent=2)
                out_file.close()

    # Generate dataset_info
    data_info = dict()
    for vert in names:
        data_info[vert] = {"file_name": vert + ".json", "file_sha1": ""}
    out_file = open(os.path.join(output_folder, "dataset_info.json"), "w")
    json.dump(data_info, out_file, indent=2)
    out_file.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="test generate")
    # I/O
    parser.add_argument("--input_dir", type=str)
    parser.add_argument("--output_dir", type=str)
    parser.add_argument("--hold_out_datasets", type=str, nargs="+")
    parser.add_argument("--num_shot", type=int)

    args = parser.parse_args()

    generate_fewshot_format(
        args.input_dir, args.output_dir, args.hold_out_datasets, args.num_shot
    )
    # generate_zeroshot_format(args.input_dir, args.output_dir, args.hold_out_datasets)
