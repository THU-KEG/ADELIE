import os
import json
import random
from pathlib import Path
import argparse

OUTPUT_BASE = [
    (
        'Please give the answer in the form "[Answer]: {event}: {class}; ".',
        "{word}: {type}; ",
    ),
    (
        'Please give the answer in the form "[Answer]: ({event}, {class}); ".',
        "({word}, {type}); ",
    ),
    (
        'Please give the answer in the form "[Answer]: (event trigger: {event}, class: {class}); ".',
        "(event trigger: {word}, class: {type}); ",
    ),
    (
        "Please give the answer in natural language.",
        '"{word}" is linked to the "{type}" event. ',
    ),
    (
        "Please give the answer in natural language.",
        '"{word}" triggers an event identified as "{type}". ',
    ),
]
# (prefix,to_type,summary): prefix+ (multi) to_type+summary+[Answer]:+output_base
# {word}, {type}
OUTPUT_EXPLAN = [
    (
        "Based on the given predefined event type and text: ",
        '"{word}" is an event trigger word, which triggers an event of type "{type}". ',
        "To sum up, ",
    ),
    (
        "In consideration of the provided predefined event type and text, ",
        '"{word}" is specifically linked to the category "{type}". ',
        "In brief, ",
    ),
    (
        "Given the predefined event type and text, ",
        '{word} triggers an event classified as "{type}". ',
        "To summarize, ",
    ),
    (
        "According to the provided event type and text, ",
        '"{word}" serves as an event trigger word, instigating an event classified under "{type}". ',
        "In conclusion, ",
    ),
    (
        "Based on the given predefined event type and text, ",
        '"{word}" operates as an event trigger word, initiating an event categorized as "{type}". ',
        "Hence, ",
    ),
]


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


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
        response += explain_tem[0]
        for args in new_args:
            response += explain_tem[1].format(word=args[0], type=args[1])
            response_base += base_tem[1].format(word=args[0], type=args[1])
            ref += OUTPUT_BASE[0][1].format(word=args[0], type=args[1])
        response += explain_tem[2]
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_initdataset(data):
    init_dataset = []
    for i, instance in enumerate(data):
        init_data = {"input": instance["text"], "explain_arg": []}
        for event in instance["events"]:
            for trigger in event["triggers"]:
                init_data["explain_arg"].append(
                    [trigger["trigger_word"], event["type"]]
                )
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

    print(sum_valid_data, len(NA_data), num_NA_data)
    if num_NA_data < len(NA_data):
        NA_data = random.sample(NA_data, num_NA_data)
    valid_data = valid_data + NA_data
    random.shuffle(valid_data)

    print("sample NA:", len(NA_data))
    print("sum:", len(valid_data))

    return valid_data


def construct_response(input_folder, output_folder, inst_file, split, config):

    if "test" in split:
        config["CLASS_DROPOUT_RATE"] = 0
        config["ALL_DESC"] = 0
        config["BIG_TYPE"] = 0
        # ?
        config["DESC_RATE"] = 0
        config["EXPLAIN_RATE"] = 0

    input_path = os.path.join(input_folder, split + ".jsonl")
    data = []
    with open(input_path) as f:
        for line in f.readlines():
            instance = json.loads(line.strip())
            data.append(instance)

    label2id = json.load(open(os.path.join(input_folder, "label2id.json")))
    options = [e for e in list(label2id.keys())]
    options.remove("NA")

    with open(inst_file, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["ED"]

    # 获得原始数据
    init_dataset = get_initdataset(data)
    example_dataset = []
    if "test" in split:
        input_path = os.path.join(input_folder, "train.unified.jsonl")
        train_data = []
        with open(input_path) as f:
            for line in f.readlines():
                instance = json.loads(line.strip())
                train_data.append(instance)
        example_dataset = get_initdataset(train_data)
    else:
        example_dataset = init_dataset
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理原始数据
    out_file = open(os.path.join(output_folder, split + ".jsonl"), "w")

    for i, vert in enumerate(init_dataset):
        # instruction & options
        instruction, na = get_instruction(inst)
        new_options = []
        for op in options:
            flag = (int)(random.random() > config["CLASS_DROPOUT_RATE"])
            if flag == 1:
                new_options.append(op)
        random.shuffle(new_options)

        if "<options>" in instruction:
            instruction = instruction.replace(
                "<options>", "[" + ", ".join(new_options) + "]", 1
            )
        else:
            instruction += "\nOptions: [" + ", ".join(new_options) + "]\n"

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
        HistoryData = random.sample(example_dataset, config["NUM_FEWSHOT_Limit"])
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
        "--output_dir", type=str, default="../../../unified_data/RichERE-ed"
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
    parser.add_argument("--fewshot_na_rate", type=float, default=0.1)

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
    # construct_response(input_folder, output_folder, "train.unified",config)
    construct_response(input_folder, output_folder, inst_file, "test.unified", config)
