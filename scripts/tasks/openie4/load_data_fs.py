import os
import json
import random
from pathlib import Path
import copy
import argparse
from desc import JSON_BASE, JSON_FORMAT, OUTPUT_BASE, OUTPUT_EXPLAN


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


def get_initdataset(data):
    init_dataset = []
    tokens = None
    sentence = None
    text = None
    args = []
    BAD_FLAG = False
    for i, line in enumerate(data):
        line = line.strip()

        if "[unused" in line:
            if text is not None:
                if BAD_FLAG == False:
                    init_data = {"input": text, "explain_arg": copy.deepcopy(args)}
                    init_dataset.append(init_data)
                args.clear()
                BAD_FLAG = False
                # print("======== init data =========")
                # print(init_data)
            text = line.split("[unused1]")[0].strip()
            tokens = line.split()
        else:
            sentence = line.split()
            pre = ""
            words = []
            tup = {
                "REL": "None",
                "ARG1": "None",
                "ARG2": "None",
                "TIME": "None",
                "LOC": "None",
            }
            for label, word in zip(sentence, tokens):
                if pre != label:
                    if pre != "" and pre != "NONE":
                        if pre not in tup:
                            print("========== Error : Unseen Labels ============", pre)
                        tup[pre] = " ".join(words)
                    words.clear()
                words.append(word)
                pre = label
            for value in tup.values():
                if "[unused" in value:
                    BAD_FLAG = True
            if tup["REL"] == "None" or tup["ARG1"] == "None":
                BAD_FLAG = True
            args.append(tup)
            # print(tokens)
            # print(sentence)
            # print("TUPLE:",tup)

    return init_dataset


# 处理NA数据,注意这是第一次处理，在后面option dropout后仍然有可能为NA
def get_valid_datasets(example_dataset, config):
    sum_valid_data = 0
    valid_data = []
    NA_data = []
    for vert in example_dataset:
        if vert["explain_arg"] == []:
            NA_data.append(vert)
        else:
            valid_data.append(vert)
    sum_valid_data = len(valid_data)
    num_NA_data = int(
        (sum_valid_data / (1.0 - config["EXAM_NA_RATE"])) * config["EXAM_NA_RATE"]
    )

    print(sum_valid_data, len(NA_data), num_NA_data)
    if num_NA_data < len(NA_data):
        NA_data = random.sample(NA_data, num_NA_data)
    valid_data = valid_data + NA_data
    random.shuffle(valid_data)

    print("sample NA:", len(NA_data))
    print("sum:", len(valid_data))

    return valid_data


def get_response(ExFlag, base_tem, vert, na):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    if len(vert["explain_arg"]) == 0:
        response += na
        response_base += "NA"
    else:
        for args in vert["explain_arg"]:
            response += explain_tem[0].format(
                subject=args["ARG1"],
                object=args["ARG2"],
                predicate=args["REL"],
                time=args["TIME"],
                location=args["LOC"],
            )
            if args["TIME"] != "None" or args["LOC"] != "None":
                response = (
                    response
                    + " "
                    + explain_tem[1].format(time=args["TIME"], location=args["LOC"])
                )
            if base_tem[1] != "":
                response_base += base_tem[1].format(
                    subject=args["ARG1"],
                    object=args["ARG2"],
                    predicate=args["REL"],
                    time=args["TIME"],
                    location=args["LOC"],
                )
            else:
                l = []
                for value in args.values():
                    if value != "None":
                        l.append(value)
                # print("============ args ===========")
                # print(args)
                # print(l)
                response_base += "(" + "; ".join(l) + "); \n"
                # print(response_base)
            ref += OUTPUT_BASE[0][1].format(
                subject=args["ARG1"],
                object=args["ARG2"],
                predicate=args["REL"],
                time=args["TIME"],
                location=args["LOC"],
            )
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_JSONresponse(ExFlag, vert, na):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    response_json = copy.deepcopy(JSON_FORMAT)
    if len(vert["explain_arg"]) == 0:
        response += na
        response_base += "NA"
    else:
        for args in vert["explain_arg"]:
            response += explain_tem[0].format(
                subject=args["ARG1"],
                object=args["ARG2"],
                predicate=args["REL"],
                time=args["TIME"],
                location=args["LOC"],
            )
            if args["TIME"] != "None" or args["LOC"] != "None":
                response = (
                    response
                    + " "
                    + explain_tem[1].format(time=args["TIME"], location=args["LOC"])
                )
            response_json["Subject"] = args["ARG1"]
            response_json["Object"] = args["ARG2"]
            response_json["Predicate"] = args["REL"]
            response_json["Time"] = args["TIME"]
            response_json["Location"] = args["LOC"]
            ref += OUTPUT_BASE[0][1].format(
                subject=args["ARG1"],
                object=args["ARG2"],
                predicate=args["REL"],
                time=args["TIME"],
                location=args["LOC"],
            )
    response_base += str(response_json)
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def construct_response(input_folder, output_folder, inst_file, split, config):
    if "test" in split:
        config["CLASS_DROPOUT_RATE"] = 0
        config["ISALL"] = 0
        config["BIG_TYPE"] = 0
        # ?
        config["DESC_RATE"] = 0
        config["EXPLAIN_RATE"] = 0
        config["UNCOMPELETE_OPTION"] = False
        config["SAMPLE_RATE"] = 0
        config["JSON_RATE"] = 0

    input_path = os.path.join(input_folder, split)

    data = []
    with open(input_path, "r") as f:
        for line in f.readlines():
            data.append(line)
        f.close()

    # instruction
    with open(inst_file, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["OPENIE"]

    # 获得原始数据
    init_dataset = get_initdataset(data)

    example_dataset = []
    example_dataset = copy.deepcopy(init_dataset)
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理原始数据
    out_file = open(os.path.join(output_folder, split + ".jsonl"), "w")
    na_data = 0
    for i, vert in enumerate(init_dataset):

        # instruction & options
        instruction, na = get_instruction(inst)

        # definition
        unified_instance = {
            "id": i,
            "instruction": "",
            "query": [],
            "examples": [],
            "input": vert["input"],
            "reference": "",
            "output": "",
        }

        ExFlag = (int)(random.random() < config["EXPLAIN_RATE"])
        if "test" in split:
            base_tem = OUTPUT_BASE[0]
        else:
            base_tem = random.sample(OUTPUT_BASE, 1)[0]

        # InfFlag = (int)(random.random() < config["infFormat_rate"])
        # if config["BanOutputD"] == True or InfFlag:
        #     base_tem = OUTPUT_BASE[0]

        # query
        unified_instance["query"].append(ExFlag)
        unified_instance["query"].append(base_tem[0])

        # ref & output
        JsonFlag = (int)(random.random() < config["JSON_RATE"])
        if JsonFlag:
            unified_instance["reference"], unified_instance["output"] = (
                get_JSONresponse(ExFlag, vert, na)
            )
            unified_instance["query"][1] = JSON_BASE
        else:
            unified_instance["reference"], unified_instance["output"] = get_response(
                ExFlag, base_tem, vert, na
            )

        # examples
        HistoryData = random.sample(example_dataset, config["NUM_FEWSHOT_Limit"])
        for hd in HistoryData:
            if hd == vert:
                continue
            if JsonFlag:
                hdref, hdout = get_JSONresponse(ExFlag, hd, na)
            else:
                hdref, hdout = get_response(ExFlag, base_tem, hd, na)
            unified_instance["examples"].append([hd["input"], hdout, hdref])

        unified_instance["instruction"] = instruction

        if unified_instance["reference"] == "":
            na_data += 1
        out_file.write(json.dumps(unified_instance) + "\n")

        if i < 10:
            print("============== CASE: ", split, i, "====================")
            print(unified_instance)

    print("na_num:", na_data)
    print("valid_num", len(init_dataset) - na_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="tacred")
    # I/O
    parser.add_argument("--input_dir", type=str, default="../../../data/openie6")
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data/openie4"
    )
    parser.add_argument("--instruction_file", type=str, default="../instructions.json")

    # parameters
    parser.add_argument("--sample_rate", type=float, default=0.2)
    parser.add_argument("--each_sample_num", type=int, default=3)
    parser.add_argument("--limit_sample", type=int, default=15)

    parser.add_argument("--desc_rate", type=float, default=0.2)
    parser.add_argument("--limit_desc", type=int, default=10)
    parser.add_argument("--isall", type=float, default=1.0)

    parser.add_argument("--json_rate", type=float, default=0.1)
    parser.add_argument("--infFormat_rate", type=float, default=0.50)

    parser.add_argument("--big_type_rate", type=float, default=0.05)

    parser.add_argument("--class_dropout_rate", type=float, default=0.1)
    parser.add_argument("--diverse_options", type=bool, default=True)
    parser.add_argument("--SymbolLabels", type=float, default=0.05)

    parser.add_argument("--explain_rate", type=float, default=0.2)

    parser.add_argument("--num_fewshot_limit", type=int, default=8)
    parser.add_argument("--WORD_Limit", type=int, default=1200)
    parser.add_argument("--fewshot_na_rate", type=float, default=0.0)
    parser.add_argument("--BanOutputD", type=bool, default=False)

    args = parser.parse_args()

    input_folder = Path(args.input_dir)
    output_folder = Path(args.output_dir)
    inst_file = args.instruction_file
    # args
    config = {
        # sample
        "SAMPLE_RATE": args.sample_rate,
        "EACH_SAMPLE_NUM": args.each_sample_num,
        "LIMIT_SAMPLE": args.limit_sample,
        # desc
        "DESC_RATE": args.desc_rate,
        "LIMIT_DESC": args.limit_desc,
        "ISALL": args.isall,  # for sample & desc
        # output_json
        "JSON_RATE": args.json_rate,
        "BanOutputD": args.BanOutputD,
        "infFormat_rate": args.infFormat_rate,
        # b-s type
        "BIG_TYPE": args.big_type_rate,
        # args
        "CLASS_DROPOUT_RATE": args.class_dropout_rate,
        "UNCOMPELETE_OPTION": args.diverse_options,
        "SymbolLabels": args.SymbolLabels,
        # explain相关
        "EXPLAIN_RATE": args.explain_rate,
        # few-shot相关
        "NUM_FEWSHOT_Limit": args.num_fewshot_limit,
        "WORD_Limit": args.WORD_Limit,
        "EXAM_NA_RATE": args.fewshot_na_rate,
    }

    output_folder.mkdir(exist_ok=True, parents=True)
    construct_response(input_folder, output_folder, inst_file, "openie4_labels", config)
