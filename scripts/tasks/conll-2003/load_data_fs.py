# from ph_unified_data:
import os
import json
import random
import copy
from pathlib import Path
import argparse
from desc import OUTPUT_BASE, OUTPUT_EXPLAN, JSON_BASE, OPTIONS, RANDOM_SYMBOLS


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


def get_response(ExFlag, base_tem, vert, new_options, na):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    if config["BanOutputD"] == True:
        explain_tem = OUTPUT_EXPLAN[0]

    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    new_args = []
    for args in vert["explain_arg"]:
        if args[2] in new_options:
            new_args.append(args)
    if len(new_args) == 0:
        response += na
        response_base += "NA"
    else:
        response += explain_tem[0]
        for args in new_args:
            response += explain_tem[1].format(entity=args[0], type=args[1])
            response_base += base_tem[1].format(entity=args[0], type=args[2])
            ref += OUTPUT_BASE[0][1].format(entity=args[0], type=args[2])
        response += explain_tem[2]
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_JSONresponse(ExFlag, vert, new_options, na):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    if config["BanOutputD"] == True:
        explain_tem = OUTPUT_EXPLAN[0]

    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    response_json = {}
    for item in new_options:
        response_json[item] = []

    new_args = []
    for args in vert["explain_arg"]:
        if args[2] in new_options:
            new_args.append(args)
    if len(new_args) == 0:
        response += na
    else:
        response += explain_tem[0]
        for args in new_args:
            response += explain_tem[1].format(entity=args[0], type=args[1])
            response_json[args[2]].append(args[0])
            ref += OUTPUT_BASE[0][1].format(entity=args[0], type=args[2])
        response += explain_tem[2]

    response_base += str(response_json)
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_initdataset(data, rel2id):
    init_dataset = []
    for i, vert in enumerate(data):
        instance = vert["instance"]
        text = instance["input"]["text"]
        output = instance["references"][0]["output"]["text"]

        if text == "-DOCSTART- ":
            continue
        init_data = {"input": text, "explain_arg": []}
        if output != "":
            entities = output.split("; ")
            output = ""
            for node in entities:
                if node == "":
                    continue
                node = node.split(": ")
                t = node[-1].strip()
                e = ": ".join(node[:-1])
                init_data["explain_arg"].append((e, rel2id[t][1], t))
        init_dataset.append(init_data)
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

    # print(sum_valid_data,len(NA_data),num_NA_data)
    if num_NA_data < len(NA_data):
        NA_data = random.sample(NA_data, num_NA_data)
    valid_data = valid_data + NA_data
    random.shuffle(valid_data)

    # print("sample NA:",len(NA_data))
    # print("sum:",len(valid_data))

    return valid_data


def get_Sample(options, data):
    OptionSample = {}
    for op in options:
        OptionSample[op] = []
    for i, vert in enumerate(data):
        instance = vert["instance"]
        text = instance["input"]["text"]
        output = instance["references"][0]["output"]["text"]

        if text == "-DOCSTART- ":
            continue

        if output != "":
            entities = output.split("; ")
            output = ""
            for node in entities:
                if node == "":
                    continue
                node = node.split(": ")
                t = node[-1].strip()
                e = ": ".join(node[:-1])
                OptionSample[t].append(e)
    return OptionSample


def construct_response(input_folder, output_folder, inst_file, split, config):

    if "test" in split:
        config["CLASS_DROPOUT_RATE"] = 0
        config["ISALL"] = 0
        config["BIG_TYPE"] = 0
        # ?
        config["DESC_RATE"] = 0
        config["EXPLAIN_RATE"] = 0
        config["SAMPLE_RATE"] = 0
        config["JSON_RATE"] = 0

    input_path = os.path.join(input_folder, split + ".json")
    data = []
    with open(input_path, "r", encoding="utf-8") as reader:
        data = json.load(reader)
        reader.close()

    # instruction
    with open(inst_file, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["NER"]

    # options
    options = OPTIONS["conll-2003"].split(", ")

    rel_path = os.path.join(input_folder, "rel_des.json")
    rel2id = json.load(open(rel_path))

    OptionSample = get_Sample(options, data["request_states"])

    # 获得原始数据
    init_dataset = get_initdataset(data["request_states"], rel2id)
    example_dataset = []
    if "test" in split:
        input_path = os.path.join(input_folder, "train.json")
        train_data = []
        with open(input_path, "r", encoding="utf-8") as reader:
            train_data = json.load(reader)
            reader.close()
        example_dataset = get_initdataset(train_data["request_states"], rel2id)
    else:
        example_dataset = init_dataset
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理原始数据
    out_file = open(os.path.join(output_folder, split + ".jsonl"), "w")

    valid_data = 0
    na_data = 0
    for i, vert in enumerate(init_dataset):
        # instruction & options
        instruction, na = get_instruction(inst)
        new_options = []
        for op in options:
            flag = (int)(random.random() > config["CLASS_DROPOUT_RATE"])
            if flag == 1:
                new_options.append(op)
        random.shuffle(new_options)

        # if sample -> ISALL
        SampleFlag = (int)(random.random() < config["SAMPLE_RATE"])
        length = len(new_options)
        if SampleFlag:
            isAll = (random.random() < config["ISALL"]) or (
                SampleFlag and (config["LIMIT_SAMPLE"] > length)
            )
            if isAll:
                new_options = new_options[0 : min(config["LIMIT_SAMPLE"], length)]
            if isAll:
                In_Flag = False
                for args in vert["explain_arg"]:
                    if args[2] not in new_options:
                        new_options.append(args[2])
                        In_Flag = True
                if In_Flag:
                    # print("New Options:",new_options)
                    random.shuffle(new_options)

        # definition
        unified_instance = {
            "id": i,
            "instruction": instruction,
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

        InfFlag = (int)(random.random() < config["infFormat_rate"])
        if config["BanOutputD"] == True or InfFlag:
            base_tem = OUTPUT_BASE[0]

        # query
        unified_instance["query"].append(ExFlag)
        unified_instance["query"].append(base_tem[0])

        # ref & output
        JsonFlag = (int)(random.random() < config["JSON_RATE"])
        if JsonFlag:
            unified_instance["reference"], unified_instance["output"] = (
                get_JSONresponse(ExFlag, vert, new_options, na)
            )
            unified_instance["query"][1] = JSON_BASE
        else:
            unified_instance["reference"], unified_instance["output"] = get_response(
                ExFlag, base_tem, vert, new_options, na
            )

        # examples
        HistoryData = random.sample(example_dataset, config["NUM_FEWSHOT_Limit"])
        for hd in HistoryData:
            if hd == vert:
                continue
            if JsonFlag:
                hdref, hdout = get_JSONresponse(ExFlag, hd, new_options, na)
            else:
                hdref, hdout = get_response(ExFlag, base_tem, hd, new_options, na)
            unified_instance["examples"].append([hd["input"], hdout, hdref])

        # Sample & Desc
        if SampleFlag:
            l = range(0, len(new_options))
            length = len(new_options)
            samp = random.sample(
                l, min(length, config["LIMIT_SAMPLE"])
            )  # limit the desc num to avoid cutoff
            for k, op in enumerate(new_options):
                if k in samp and len(OptionSample[new_options[k]]) >= 10:
                    samples = random.sample(
                        OptionSample[new_options[k]], config["EACH_SAMPLE_NUM"]
                    )
                    samples = list(set(samples))
                    new_options[k] = (
                        '"' + new_options[k] + ": such as " + ", ".join(samples) + '."'
                    )
                else:
                    new_options[k] = '"' + new_options[k] + '"'

        if "<options>" in instruction:
            instruction = instruction.replace(
                "<options>", "[" + ", ".join(new_options) + "]", 1
            )
        else:
            instruction += "\nOptions: [" + ", ".join(new_options) + "]\n"
        unified_instance["instruction"] = instruction

        out_file.write(json.dumps(unified_instance) + "\n")

        if i < 10:
            print("============== CASE: ", split, i, "====================")
            print(unified_instance)
        if unified_instance["reference"] != "":
            valid_data += 1
        else:
            na_data += 1
    print("valid:", valid_data)
    print("na_data:", na_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="conll-2003")
    # I/O
    parser.add_argument(
        "--input_dir",
        type=str,
        default="../../../data/CoNLL2003/processed",
    )
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data/conll-2003"
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
    construct_response(input_folder, output_folder, inst_file, "train", config)
    # construct_response(input_folder, output_folder, inst_file, "test", config)
