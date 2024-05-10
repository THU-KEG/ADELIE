import os
import json
import random
from pathlib import Path
import copy
import argparse

OUTPUT_BASE = [
    (
        'Please give the answer in the form "[Answer]: {word}: {role}; ".',
        "{word}: {type}; ",
    ),
    (
        'Please give the answer in the form "[Answer]: (word: {word}, role: {type}); ".',
        "(word: {word}, role: {type}); ",
    ),
    (
        "Please give the answer in natural language.",
        'the event role "{type}" is "{word}"; ',
    ),
    (
        "Please give the answer in natural language.",
        '"{word}" is the role of "{type}"; ',
    ),
    (
        'Please give the answer in the form "[Answer]: ({word}, {role}); ".',
        "({word}, {type}); ",
    ),
]

OUTPUT_EXPLAN = [
    'In the given context, the event "{event}" is associated with the event type "{etype}".',
    'Within the provided context, the event "{event}" is linked to the event type "{etype}".',
    'In the given context, the event "{event}" is connected to the event type "{etype}".',
    'According to the context, the event "{event}" is correlated with the event type "{etype}".',
    'In the provided context, the event "{event}" is aligned with the event type "{etype}".',
]


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


def find_schema(data):
    schema = {}
    for sample in data:
        for event in sample["events"]:
            if event["type"] not in schema:
                schema[event["type"]] = set()
            for trigger in event["triggers"]:
                for arg in trigger["arguments"]:
                    schema[event["type"]].add(arg["role"])
    return schema


def mark_event(input_text, h_pos, t_pos, markers=["<event>", "</event>"]):
    text = ""
    for i, ch in enumerate(input_text):
        if i == h_pos:
            text += f"{markers[0]} "
        if i == t_pos:
            text += f" {markers[1]}"
        text += ch
    if t_pos == len(input_text):
        text += f" {markers[1]}"
    return text


def get_response(ExFlag, base_tem, vert, new_options, na):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    new_args = []
    for args in vert["explain_arg"]:
        if args[1] in new_options:
            new_args.append(args)
    if len(new_args) == 0:
        response += na
        response_base += "NA"
    else:
        for args in new_args:
            response += explain_tem.format(
                event=vert["event"], etype=vert["event_type"]
            )
            response_base += base_tem[1].format(word=args[0], type=args[1])
            ref += OUTPUT_BASE[0][1].format(word=args[0], type=args[1])
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_initdataset(data):
    init_dataset = []
    for instance in data:
        for event in instance["events"]:
            event_type = event["type"]
            for trigger in event["triggers"]:
                text = mark_event(
                    instance["text"], trigger["position"][0], trigger["position"][1]
                )
                init_data = {
                    "input": text,
                    "event": trigger["trigger_word"],
                    "event_type": event["type"],
                    "explain_arg": [],
                }
                for arg in trigger["arguments"]:
                    for mention in arg["mentions"]:
                        init_data["explain_arg"].append(
                            (mention["mention"], arg["role"])
                        )
                init_dataset.append(init_data)
    return init_dataset


def get_exampledata(data):
    example_dataset = dict()
    for instance in data:
        for event in instance["events"]:
            event_type = event["type"]
            if event["type"] not in example_dataset:
                example_dataset[event["type"]] = []
            for trigger in event["triggers"]:
                text = mark_event(
                    instance["text"], trigger["position"][0], trigger["position"][1]
                )
                init_data = {
                    "input": text,
                    "event": trigger["trigger_word"],
                    "event_type": event["type"],
                    "explain_arg": [],
                }
                for arg in trigger["arguments"]:
                    for mention in arg["mentions"]:
                        init_data["explain_arg"].append(
                            (mention["mention"], arg["role"])
                        )
                example_dataset[event["type"]].append(init_data)
    return example_dataset


def read_jsonlines(file):
    with open(file, "r") as f:
        data = []
        for line in f.readlines():
            data.append(json.loads(line.strip()))
    return data


# 处理NA数据,注意这是第一次处理，在后面option dropout后仍然有可能为NA
def get_valid_datasets(example_dataset, config):
    sum_valid_data = 0
    valid_data = []
    NA_data = []
    for key, values in example_dataset.items():
        sum_valid_data = 0
        valid_data.clear()
        NA_data.clear()
        for vert in values:
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

        print("key:", key)
        print("sample NA:", len(NA_data))
        print("sum:", len(valid_data))

        example_dataset[key] = copy.deepcopy(valid_data)

    return example_dataset


def construct_response(input_folder, output_folder, inst_file, split, config):
    if "test" in split:
        config["CLASS_DROPOUT_RATE"] = 0
        config["ALL_DESC"] = 0
        config["BIG_TYPE"] = 0
        # ?
        config["DESC_RATE"] = 0
        config["EXPLAIN_RATE"] = 0

    d = input_folder.joinpath(split + ".unified.jsonl")
    data = read_jsonlines(d)
    schema = find_schema(data)

    with open(inst_file, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["EAE"]

    # 获得原始数据
    init_dataset = get_initdataset(data)
    example_dataset = []
    if "test" in split:
        d = input_folder.joinpath("train.unified.jsonl")
        train_data = read_jsonlines(d)
        example_dataset = get_exampledata(train_data)
    else:
        example_dataset = get_exampledata(data)
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理原始数据
    out_file = open(os.path.join(output_folder, split + ".jsonl"), "w")

    for i, vert in enumerate(init_dataset):
        # instruction & options
        instruction, na = get_instruction(inst)
        new_options = []
        for op in schema[vert["event_type"]]:
            flag = (int)(random.random() > config["CLASS_DROPOUT_RATE"])
            if flag == 1:
                new_options.append(op)
        random.shuffle(new_options)

        REP_Flag = (int)(random.random() < 0.7)
        if REP_Flag:
            if "{event}" in instruction:
                instruction = instruction.replace("{event}", '"' + vert["event"] + '"')

        if "<options>" in instruction:
            instruction = instruction.replace(
                "<options>", "[" + ", ".join(new_options) + "]"
            )
        else:
            instruction += "\nRoleset: [" + ", ".join(new_options) + "]\n"

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
        explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
        if "test" in split:
            base_tem = OUTPUT_BASE[0]
        else:
            base_tem = random.sample(OUTPUT_BASE, 1)[0]

        # query
        unified_instance["query"].append(ExFlag)
        unified_instance["query"].append(base_tem[0])

        # ref & output
        unified_instance["reference"], unified_instance["output"] = get_response(
            ExFlag, base_tem, vert, new_options, na
        )

        # examples
        HistoryData = random.sample(
            example_dataset[vert["event_type"]],
            min(config["NUM_FEWSHOT_Limit"], len(example_dataset[vert["event_type"]])),
        )
        for hd in HistoryData:
            if hd == vert:
                continue
            _, hdout = get_response(ExFlag, base_tem, hd, new_options, na)
            unified_instance["examples"].append([hd["input"], hdout])

        out_file.write(json.dumps(unified_instance) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="conll-2003")
    # I/O
    parser.add_argument("--input_dir", type=str, default="../../../data/RichERE")
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data/RichERE-eae"
    )
    parser.add_argument("--instruction_file", type=str, default="../instruction.json")

    # parameters
    parser.add_argument("--sample_rate", type=float, default=0.5)
    parser.add_argument("--each_sample_num", type=int, default=5)
    parser.add_argument("--limit_sample", type=int, default=15)

    parser.add_argument("--desc_rate", type=float, default=0.3)
    parser.add_argument("--limit_desc", type=int, default=8)
    parser.add_argument("--isall", type=float, default=0.9)

    parser.add_argument("--json_rate", type=float, default=0.1)

    parser.add_argument("--big_type_rate", type=float, default=0.2)

    parser.add_argument("--class_dropout_rate", type=float, default=0.1)
    parser.add_argument("--diverse_options", type=bool, default=True)
    parser.add_argument("--explain_rate", type=float, default=0.5)

    parser.add_argument("--num_fewshot_limit", type=int, default=8)
    parser.add_argument("--WORD_Limit", type=int, default=1200)
    parser.add_argument("--fewshot_na_rate", type=float, default=0.0)

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
        # b-s type
        "BIG_TYPE": args.big_type_rate,
        # args
        "CLASS_DROPOUT_RATE": args.class_dropout_rate,
        "UNCOMPELETE_OPTION": args.diverse_options,
        # explain相关
        "EXPLAIN_RATE": args.explain_rate,
        # few-shot相关
        "NUM_FEWSHOT_Limit": args.num_fewshot_limit,
        "WORD_Limit": args.WORD_Limit,
        "EXAM_NA_RATE": args.fewshot_na_rate,
    }

    output_folder.mkdir(exist_ok=True, parents=True)

    # construct_response(input_folder,output_folder,inst_file,"train",config)
    construct_response(input_folder, output_folder, inst_file, "test", config)
