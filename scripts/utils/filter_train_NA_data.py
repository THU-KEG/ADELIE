# 对于数据集中的NA数据进行处理，保证其比例<=0.2

import random
import json
import jsonlines
import os
from pathlib import Path

NA_rate = 0.2


def sample_train():
    path = "../unified_data_updata_rate"
    path_list = os.listdir(path)
    # path_list.remove("tuluv2")
    # path_list.remove("ondemandIE")
    # path_list.remove("train_mixture")
    # path_list.remove("test_format")
    # path_list.remove("re")
    # path_list.remove("ee")
    # path_list.remove("other_rc")
    # path_list.remove("other_ner")

    valid_data = []
    NA_data = []
    for dirname in path_list:
        file_list = os.listdir(os.path.join(path, dirname))
        filename = ""
        for f in file_list:
            if "train" in f and "after_filter" not in f:
                filename = f
                break
        if filename == "":
            continue
        if filename[-6:] != ".jsonl":
            continue

        # if dirname != "MAVEN-ERE-MoreDoc":
        #     continue

        if dirname == "ee" or dirname == "re" or dirname == "other_rc":
            continue

        sum_valid_data = 0
        valid_data.clear()
        NA_data.clear()
        with open(
            os.path.join(path, dirname, filename), "r", encoding="utf-8"
        ) as reader:
            for item in jsonlines.Reader(reader):
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
        print("-------------------------")
        print("filter_dataset:", dirname)
        print("sum_valid_data | sum_NA_data | num_resume_NA_data")
        print(sum_valid_data, " | ", len(NA_data), " | ", num_NA_data)
        if num_NA_data < len(NA_data):
            NA_data = random.sample(NA_data, num_NA_data)
        print("sample NA data:", len(NA_data))
        valid_data = valid_data + NA_data
        random.shuffle(valid_data)
        print("After filter total:", len(valid_data))

        out_file = open(
            os.path.join(path, dirname, "after_filter_train_new.jsonl"),
            "w",
            encoding="utf-8",
        )
        for vert in valid_data:
            out_file.write(json.dumps(vert) + "\n")
        out_file.close()


def sample_test():
    path = "/home/qijy/workspace/Alignment_on_IE_tasks/unified_data"
    path_list = os.listdir(path)
    path_list.remove("tuluv2")
    path_list.remove("train_unseen_hold_out")
    path_list.remove("test_format")

    output_folder = Path(
        "/home/qijy/workspace/Alignment_on_IE_tasks/unified_data/test_format"
    )
    output_folder.mkdir(exist_ok=True, parents=True)

    valid_data = []
    NA_data = []
    names = []
    unified_data = []
    filenames = []
    for dirname in path_list:
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

            # if dirname != "MATRES":
            #     continue

            sum_valid_data = 0
            valid_data.clear()
            NA_data.clear()
            unified_data.clear()
            with open(
                os.path.join(path, dirname, filename), "r", encoding="utf-8"
            ) as reader:
                for item in jsonlines.Reader(reader):
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
            random.shuffle(valid_data)
            print("sum:", len(valid_data))

            for vert in valid_data:
                unified = {
                    "instruction": vert["instruction"],
                    "input": vert["input"],
                    "output": str(vert["reference"]),
                    "history": [],
                }
                unified_data.append(unified)

            n = len(unified_data)
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

    ## Generate dataset_info
    data_info = dict()
    for vert in names:
        data_info[vert] = {"file_name": vert + ".json", "file_sha1": ""}
    out_file = open(os.path.join(output_folder, "dataset_info.json"), "w")
    json.dump(data_info, out_file, indent=2)
    out_file.close()


if __name__ == "__main__":
    sample_train()
