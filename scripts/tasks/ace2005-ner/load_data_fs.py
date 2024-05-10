# from ph_unified_data:
import os
import json
import random
import copy
from pathlib import Path
import argparse
from desc import (
    SUBTYPE,
    BTYPE,
    MENTION_TYPE,
    OUTPUT_BASE,
    OUTPUT_EXPLAN_S,
    OUTPUT_EXPLAN_B,
    ENTITY_TO_CLASS_MAPPING,
    RANDOM_SYMBOLS,
)

JSON_BASE = "Please give the answer in json format."


def diverse_options(x, flag, config, OP2OP, Symbols):
    orix = x
    RepFlag = (int)(random.random() < config["SymbolLabels"])
    if RepFlag == 1 and len(Symbols):
        x = random.sample(Symbols, 1)[0]
        Symbols.remove(x)

    if flag == 0:
        x = x.lower()
    if flag == 1:
        x = x.replace("-", "_")
    if flag == 2:
        x = x.replace(".", "_")
    if flag == 3:
        x = x.replace(".", " ")
    if flag == 4:
        x = x.replace("-", "_").lower()
    if flag == 5:
        x = x.replace(".", "_").lower()
    if flag == 6:
        x = x.replace(".", " ").lower()

    OP2OP[orix] = x

    return x


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


def get_JSONresponse(ExFlag, BIG_FLAG, vert, new_options, na, OP2OP):
    if BIG_FLAG:
        explain_tem = random.sample(OUTPUT_EXPLAN_B, 1)[0]
        if config["BanOutputD"] == True:
            explain_tem = OUTPUT_EXPLAN_B[0]
    else:
        explain_tem = random.sample(OUTPUT_EXPLAN_S, 1)[0]
        if config["BanOutputD"] == True:
            explain_tem = OUTPUT_EXPLAN_S[0]

    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    response_json = {}
    for item in new_options:
        response_json[item] = []

    new_args = []
    for args in vert["explain_arg"]:
        if BIG_FLAG:
            if args[1] not in OP2OP:
                continue
            type = OP2OP[args[1]]
            if type in new_options:
                new_args.append(copy.deepcopy(args))
                new_args[-1][1] = type
        else:
            type = args[1] + "." + args[2]
            if type not in OP2OP:
                continue
            type = OP2OP[type]
            if type in new_options:
                new_args.append(copy.deepcopy(args))
                new_args[-1].append(type)

    if len(new_args) == 0:
        response += na
    else:
        response += explain_tem[0]
        for args in new_args:
            if BIG_FLAG:
                response += MENTION_TYPE[args[3]].format(entity=args[0])
                response += explain_tem[1].format(type=args[1])
                response_json[args[1]].append(args[0])
                ref += OUTPUT_BASE[0][1].format(entity=args[0], type=args[1])
            else:
                type = args[4]
                response += MENTION_TYPE[args[3]].format(entity=args[0])
                response += explain_tem[1].format(stype=args[2], btype=args[1])
                response_json[type].append(args[0])
                ref += OUTPUT_BASE[0][1].format(entity=args[0], type=type)
        response += explain_tem[2]

    response_base += str(response_json)
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_response(ExFlag, BIG_FLAG, base_tem, vert, new_options, na, OP2OP):
    if BIG_FLAG:
        explain_tem = random.sample(OUTPUT_EXPLAN_B, 1)[0]
        if config["BanOutputD"] == True:
            explain_tem = OUTPUT_EXPLAN_B[0]
    else:
        explain_tem = random.sample(OUTPUT_EXPLAN_S, 1)[0]
        if config["BanOutputD"] == True:
            explain_tem = OUTPUT_EXPLAN_S[0]

    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    new_args = []
    for args in vert["explain_arg"]:
        if BIG_FLAG:
            if args[1] not in OP2OP:
                continue
            type = OP2OP[args[1]]
            if type in new_options:
                new_args.append(copy.deepcopy(args))
                new_args[-1][1] = type
        else:
            type = args[1] + "." + args[2]
            if type not in OP2OP:
                continue
            type = OP2OP[type]
            if type in new_options:
                new_args.append(copy.deepcopy(args))
                new_args[-1].append(type)

    if len(new_args) == 0:
        response += na
        response_base += "NA"
    else:
        response += explain_tem[0]
        for args in new_args:
            if BIG_FLAG:
                response += MENTION_TYPE[args[3]].format(entity=args[0])
                response += explain_tem[1].format(type=args[1])
                response_base += base_tem[1].format(entity=args[0], type=args[1])
                ref += OUTPUT_BASE[0][1].format(entity=args[0], type=args[1])
            else:
                type = args[4]
                response += MENTION_TYPE[args[3]].format(entity=args[0])
                response += explain_tem[1].format(stype=args[2], btype=args[1])
                response_base += base_tem[1].format(entity=args[0], type=type)
                ref += OUTPUT_BASE[0][1].format(entity=args[0], type=type)
        response += explain_tem[2]
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_initdataset(data):
    init_dataset = []
    for i, vert in enumerate(data):
        init_data = {"input": vert["sentence"], "explain_arg": []}
        for item in vert["entity_mentions"]:
            if item["entity_type"] in ENTITY_TO_CLASS_MAPPING:
                init_data["explain_arg"].append(
                    [
                        item["text"],
                        ENTITY_TO_CLASS_MAPPING[item["entity_type"]],
                        item["entity_subtype"],
                        item["mention_type"],
                    ]
                )
        init_dataset.append(init_data)
    return init_dataset


def get_Sample(boptions, soptions, data):
    BOptionSample, SOptionSample = {}, {}
    for op in boptions:
        BOptionSample[op] = []
    for op in soptions:
        SOptionSample[op] = []
    for i, vert in enumerate(data):
        for item in vert["entity_mentions"]:
            if item["entity_type"] in ENTITY_TO_CLASS_MAPPING:
                big = ENTITY_TO_CLASS_MAPPING[item["entity_type"]]
                small = big + "." + item["entity_subtype"]
                BOptionSample[big].append(item["text"])
                SOptionSample[small].append(item["text"])
    return BOptionSample, SOptionSample


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
        config["ISALL"] = 0
        config["DESC_RATE"] = 0
        config["EXPLAIN_RATE"] = 0
        config["BIG_TYPE"] = 0
        config["UNCOMPELETE_OPTION"] = False
        config["SAMPLE_RATE"] = 0
        config["JSON_RATE"] = 0

    input_path = os.path.join(input_folder, split + ".sentence.json")
    data = []
    with open(input_path) as f:
        for line in f.readlines():
            instance = json.loads(line.strip())
            data.append(instance)

    # instruction
    with open(inst_file, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["NER"]

    # options
    boptions = [key for key in BTYPE.keys()]
    soptions = []
    for key in SUBTYPE.keys():
        if "Underspecified" not in key:
            type = SUBTYPE[key] + "." + key
            soptions.append(type)
        else:
            soptions.append(key)

    # sample
    BOptionSample, SOptionSample = get_Sample(boptions, soptions, data)

    # 获得原始数据
    init_dataset = get_initdataset(data)
    example_dataset = []
    if "test" in split:
        input_path = os.path.join(input_folder, "train.sentence.json")
        train_data = []
        with open(input_path) as f:
            for line in f.readlines():
                instance = json.loads(line.strip())
                train_data.append(instance)
        example_dataset = get_initdataset(train_data)
    else:
        example_dataset = copy.deepcopy(init_dataset)
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理原始数据
    na_data = 0
    out_file = open(os.path.join(output_folder, split + ".jsonl"), "w")
    for i, vert in enumerate(init_dataset):
        # instruction & options
        instruction, na = get_instruction(inst)
        new_options = []
        BIG_FLAG = (int)(random.random() < config["BIG_TYPE"])
        if BIG_FLAG:
            for op in boptions:
                flag = (int)(random.random() > config["CLASS_DROPOUT_RATE"])
                if flag == 1:
                    new_options.append(op)
        else:
            for op in soptions:
                flag = (int)(random.random() > config["CLASS_DROPOUT_RATE"])
                if flag == 1:
                    new_options.append(op)
        random.shuffle(new_options)

        # desc
        DESC_Flag = (random.random() < config["DESC_RATE"]) and (BIG_FLAG == 1)
        SampleFlag = (int)(random.random() < config["SAMPLE_RATE"])
        length = len(new_options)
        if DESC_Flag or SampleFlag:
            isAll = (
                (random.random() < config["ISALL"])
                or (DESC_Flag and (config["LIMIT_DESC"] > length))
                or (SampleFlag and (config["LIMIT_SAMPLE"] > length))
            )
            # print("ISALL:",isAll)
            if isAll and DESC_Flag:
                new_options = new_options[0 : min(config["LIMIT_DESC"], length)]
            if isAll and SampleFlag:
                length = len(new_options)
                new_options = new_options[0 : min(config["LIMIT_SAMPLE"], length)]

        # deverse option
        OP2OP = dict()
        Symbols = copy.deepcopy(RANDOM_SYMBOLS)
        for op in new_options:
            OP2OP[op] = op

        OPT_Flag = -1
        if config["UNCOMPELETE_OPTION"] == True:
            OPT_Flag = random.randint(0, 10)
        dnew_options = [
            diverse_options(op, OPT_Flag, config, OP2OP, Symbols) for op in new_options
        ]
        # if OPT_Flag!=-1 and OPT_Flag<=6:
        #     print(OPT_Flag)
        #     print(dnew_options)

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
                get_JSONresponse(ExFlag, BIG_FLAG, vert, dnew_options, na, OP2OP)
            )
            unified_instance["query"][1] = JSON_BASE
        else:
            unified_instance["reference"], unified_instance["output"] = get_response(
                ExFlag, BIG_FLAG, base_tem, vert, dnew_options, na, OP2OP
            )

        # examples
        HistoryData = random.sample(example_dataset, config["NUM_FEWSHOT_Limit"])
        for hd in HistoryData:
            if hd == vert:
                continue
            if JsonFlag:
                hdref, hdout = get_JSONresponse(
                    ExFlag, BIG_FLAG, hd, dnew_options, na, OP2OP
                )
            else:
                hdref, hdout = get_response(
                    ExFlag, BIG_FLAG, base_tem, hd, dnew_options, na, OP2OP
                )
            unified_instance["examples"].append([hd["input"], hdout, hdref])

        # desc_options & instructions
        l = range(0, len(new_options))
        length = len(new_options)
        desc = random.sample(
            l, min(config["LIMIT_DESC"], length)
        )  # limit the desc num to avoid cutoff
        samp = random.sample(l, min(config["LIMIT_SAMPLE"], length))
        if BIG_FLAG:
            OptionSample = BOptionSample
        else:
            OptionSample = SOptionSample
        # print("OptionSample:",OptionSample)
        if DESC_Flag:
            idx = (int)(random.random() >= 0.5)
            if idx:
                for k, op in enumerate(new_options):
                    if k in desc:
                        dnew_options[k] = '"' + dnew_options[k] + ": " + BTYPE[op] + '"'
                        if (
                            SampleFlag
                            and k in samp
                            and len(OptionSample[new_options[k]]) >= 10
                        ):
                            samples = random.sample(
                                OptionSample[new_options[k]], config["EACH_SAMPLE_NUM"]
                            )
                            samples = list(set(samples))
                            dnew_options[k] = (
                                dnew_options[k][:-1]
                                + " For example, "
                                + ", ".join(samples)
                                + '."'
                            )
                    else:
                        dnew_options[k] = '"' + dnew_options[k] + '"'
                        if (
                            SampleFlag
                            and k in samp
                            and len(OptionSample[new_options[k]]) >= 10
                        ):
                            samples = random.sample(
                                OptionSample[new_options[k]], config["EACH_SAMPLE_NUM"]
                            )
                            samples = list(set(samples))
                            dnew_options[k] = (
                                dnew_options[k][:-1]
                                + ": Such as "
                                + ", ".join(samples)
                                + '."'
                            )
            else:
                for k, op in enumerate(new_options):
                    if k in desc:
                        dnew_options[k] = (
                            "\"'" + dnew_options[k] + "' means '" + BTYPE[op] + "'\""
                        )
                        if (
                            SampleFlag
                            and k in samp
                            and len(OptionSample[new_options[k]]) >= 10
                        ):
                            samples = random.sample(
                                OptionSample[new_options[k]], config["EACH_SAMPLE_NUM"]
                            )
                            samples = list(set(samples))
                            dnew_options[k] = (
                                dnew_options[k][:-1]
                                + " For example, '"
                                + "', '".join(samples)
                                + "'.\""
                            )
                    else:
                        dnew_options[k] = "\"'" + dnew_options[k] + "'\""
                        if (
                            SampleFlag
                            and k in samp
                            and len(OptionSample[new_options[k]]) >= 10
                        ):
                            samples = random.sample(
                                OptionSample[new_options[k]], config["EACH_SAMPLE_NUM"]
                            )
                            samples = list(set(samples))
                            dnew_options[k] = (
                                dnew_options[k][:-1]
                                + " such as '"
                                + "', '".join(samples)
                                + "'.\""
                            )
        else:
            if SampleFlag:
                for k, op in enumerate(new_options):
                    if k in samp and len(OptionSample[new_options[k]]) >= 10:
                        samples = random.sample(
                            OptionSample[new_options[k]], config["EACH_SAMPLE_NUM"]
                        )
                        samples = list(set(samples))
                        dnew_options[k] = (
                            '"'
                            + dnew_options[k]
                            + ": such as "
                            + ", ".join(samples)
                            + '."'
                        )
                    else:
                        dnew_options[k] = '"' + dnew_options[k] + '"'

        if "<options>" in instruction:
            instruction = instruction.replace(
                "<options>", "[" + ", ".join(dnew_options) + "]", 1
            )
        else:
            instruction += "\nOptions: [" + ", ".join(dnew_options) + "]\n"
        unified_instance["instruction"] = instruction

        out_file.write(json.dumps(unified_instance) + "\n")
        if unified_instance["reference"] == "":
            na_data += 1
            # print("+++++++++++++++++++CASE NA+++++++++++++++++")
            # print(vert)
            # print(OP2OP)
            # print("-------------------------------------------")
            # print(unified_instance)

        if i < 10:
            print("============== CASE: ", split, i, "====================")
            print(unified_instance)

    print("na_num:", na_data)
    print("valid_num", len(init_dataset) - na_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ace2005-ner")
    # I/O
    parser.add_argument(
        "--input_dir",
        type=str,
        default="../../../data/ace2005-en/processed",
    )
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data/ace2005-ner"
    )
    parser.add_argument("--instruction_file", type=str, default="../instructions.json")

    # parameters
    # parameters
    parser.add_argument("--sample_rate", type=float, default=0.2)
    parser.add_argument("--each_sample_num", type=int, default=3)
    parser.add_argument("--limit_sample", type=int, default=15)

    parser.add_argument("--desc_rate", type=float, default=0.2)
    parser.add_argument("--limit_desc", type=int, default=10)
    parser.add_argument("--isall", type=float, default=1.0)

    parser.add_argument("--json_rate", type=float, default=0.1)

    parser.add_argument("--big_type_rate", type=float, default=0.1)

    parser.add_argument("--class_dropout_rate", type=float, default=0.1)
    parser.add_argument("--diverse_options", type=bool, default=True)
    parser.add_argument("--explain_rate", type=float, default=0.2)

    parser.add_argument("--num_fewshot_limit", type=int, default=8)
    parser.add_argument("--WORD_Limit", type=int, default=1200)
    parser.add_argument("--fewshot_na_rate", type=float, default=0.0)
    parser.add_argument("--BanOutputD", type=bool, default=False)

    parser.add_argument("--SymbolLabels", type=float, default=0.05)
    parser.add_argument("--infFormat_rate", type=float, default=0.50)

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
