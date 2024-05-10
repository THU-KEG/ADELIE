OPTIONS = {
    "few-nerd-supervised": "art-broadcastprogram, art-film, art-music, art-other, art-painting, art-writtenart, building-airport, building-hospital, building-hotel, building-library, building-other, building-restaurant, building-sportsfacility, building-theater, event-attack/battle/war/militaryconflict, event-disaster, event-election, event-other, event-protest, event-sportsevent, location-bodiesofwater, location-GPE, location-island, location-mountain, location-other, location-park, location-road/railway/highway/transit, organization-company, organization-education, organization-government/governmentagency, organization-media/newspaper, organization-other, organization-politicalparty, organization-religion, organization-showorganization, organization-sportsleague, organization-sportsteam, other-astronomything, other-award, other-biologything, other-chemicalthing, other-currency, other-disease, other-educationaldegree, other-god, other-language, other-law, other-livingthing, other-medical, person-actor, person-artist/author, person-athlete, person-director, person-other, person-politician, person-scholar, person-soldier, product-airplane, product-car, product-food, product-game, product-other, product-ship, product-software, product-train, product-weapon"
}


OUTPUT_BASE = [
    (
        'Please give the answer in the form "[Answer]: {entity}: {type}; ".',
        "{entity}: {type}; ",
    ),
    (
        "Please give the answer in natural language.",
        '"{entity}" is classified as a "{type}"; ',
    ),
    (
        'Please give the answer in the form "[Answer]: ({entity}, {type}); ".',
        "({entity}, {type}); ",
    ),
    (
        "Please give the answer in natural language.",
        '"{entity}" signifies a "{type}"; ',
    ),
    (
        "Please give the answer in natural language.",
        '"{entity}" represents a "{type}"; ',
    ),
]
# (prefix,to_type,summary): prefix+ (multi) to_type+summary+[Answer]:+output_base
# {entity}, {stype}, {btype}
OUTPUT_EXPLAN = [
    (
        "Based on the given predefined entity type and text: ",
        '"{entity}" is the {btype} entity representing the "{stype}". ',
        "To sum up, ",
    ),
    (
        "Given the provided predefined entity type and text, ",
        '"{entity}" is identified as the {stype} entity categorized under the type "{btype}" entity. ',
        "In summary, ",
    ),
    (
        "In accordance with the specified entity type and text, ",
        '"{entity}" is recognized as the {btype} entity with the classification "{stype}". ',
        "To recap, ",
    ),
    (
        "Based on the predefined entity type and text, ",
        '"{entity}" is acknowledged as the {stype} entity falling under the "{btype}" category. ',
        "To summarize, ",
    ),
    (
        "According to the given entity type and text, ",
        '"{entity}" is identified as the {btype} entity, specifically categorized as "{stype}". ',
        "In brief, ",
    ),
]

# from data:
import os
import json
import random
from pathlib import Path
import tqdm
import argparse


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


def get_initdataset(all_lines):
    input_text, ref_output_text = "", ""
    request_id = 0
    last_label = "O"
    ongoing_entity = []
    label_pos = 1

    entities = []
    labels = []

    init_dataset = []
    for line in tqdm.tqdm(all_lines, total=len(all_lines)):
        if line and not line.isspace():
            pair = line.split()
            assert len(pair) > label_pos
            word, label = pair[0], pair[label_pos]
            input_text += word + " "
            if last_label != "O":
                if label == last_label:
                    ongoing_entity.append(word)
                else:
                    # ref_output_text += " ".join(ongoing_entity) + ": " + last_label + "; "
                    e = " ".join(ongoing_entity)
                    entities.append(e)
                    labels.append(last_label)
                    ongoing_entity.clear()
                    if label != "O":
                        ongoing_entity.append(word)
            else:  # last_label == "O"
                if label != "O":
                    ongoing_entity.append(word)
            last_label = label
        else:
            if last_label != "O":
                # ref_output_text += " ".join(ongoing_entity) + ": " + label + "; "
                e = " ".join(ongoing_entity)
                entities.append(e)
                labels.append(label)
            last_label = "O"
            ongoing_entity.clear()

            init_data = {"input": input_text, "explain_arg": []}
            for e, t in zip(entities, labels):
                t = t.replace("-", "_")
                t_f = t.split("_")[0]
                t_b = t.split("_")[1]
                init_data["explain_arg"].append((t, e, t_b, t_f))

            init_dataset.append(init_data)
            request_id += 1
            input_text, ref_output_text = "", ""
            entities.clear()
            labels.clear()

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


def get_response(ExFlag, base_tem, vert, new_options, na):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    new_args = []
    for args in vert["explain_arg"]:
        if args[0] in new_options:
            new_args.append(args)
    if len(new_args) == 0:
        response += na
        response_base += "NA"
    else:
        response += explain_tem[0]
        for args in new_args:
            response += explain_tem[1].format(
                entity=args[1], stype=args[2], btype=args[3]
            )
            response_base += base_tem[1].format(entity=args[1], type=args[0])
            ref += OUTPUT_BASE[0][1].format(entity=args[1], type=args[0])
        response += explain_tem[2]
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def construct_response(
    input_folder, output_folder, instruction_dir, split, task, config
):
    if "test" in split:
        config["CLASS_DROPOUT_RATE"] = 0
        config["ALL_DESC"] = 0
        config["BIG_TYPE"] = 0
        # ?
        config["DESC_RATE"] = 0
        config["EXPLAIN_RATE"] = 0

    input_path = os.path.join(input_folder, split + ".txt")
    all_lines = open(input_path, encoding="utf-8").readlines()

    # instruction
    with open(instruction_dir, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["NER"]

    # options
    options = OPTIONS[task].split(", ")
    options = [vert.replace("-", "_") for vert in options]
    print(options)

    # 获得原始数据
    init_dataset = get_initdataset(all_lines)
    example_dataset = []
    if "test" in split:
        input_path = os.path.join(input_folder, "train.txt")
        train_all_lines = open(input_path, encoding="utf-8").readlines()
        example_dataset = get_initdataset(train_all_lines)
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
    task = "few-nerd-supervised"

    parser = argparse.ArgumentParser(description="conll-2003")
    # I/O
    parser.add_argument(
        "--input_dir", type=str, default="../../../data/FewNERD/supervised"
    )
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data/few-nerd-supervised"
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
    parser.add_argument("--fewshot_na_rate", type=float, default=0.2)

    args = parser.parse_args()

    input_folder = Path(args.input_dir)
    output_folder = Path(args.output_dir)
    instruction_dir = args.instruction_file
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

    construct_response(
        input_folder, output_folder, instruction_dir, "test", task, config
    )
    # construct_response(input_folder, output_folder, "train",task,config)
