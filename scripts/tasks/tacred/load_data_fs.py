import os
import json
import random
from pathlib import Path
import copy
import argparse
from desc import JSON_BASE, OUTPUT_BASE, OUTPUT_EXPLAN, RANDOM_SYMBOLS


def diverse_options(x, flag, config, OP2OP, Symbols):
    orix = x
    RepFlag = (int)(random.random() < config["SymbolLabels"])
    if RepFlag == 1 and len(Symbols):
        x = random.sample(Symbols, 1)[0]
        Symbols.remove(x)

    if flag == 0:
        x = x.replace(":", "-")
    if flag == 1:
        x = x.replace(":", "_")
    if flag == 2:
        x = x.replace(":", " ")
    if flag == 3:
        x = x.replace(":", ".")
    if flag == 4:
        x = x.replace("_", "-")
    if flag == 5:
        x = x.replace("_", " ")

    OP2OP[orix] = x
    return x


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


def mark_entity(tokens, h_pos, t_pos, markers=["<entity>", "</entity>"]):
    text = ""
    for i, token in enumerate(tokens):
        if i == h_pos[0]:
            text += "<entity>" + " "
        if i == t_pos[0]:
            text += "<entity>" + " "
        text += token + " "
        if i == h_pos[1] - 1:
            text += "</entity>" + " "
        if i == t_pos[1] - 1:
            text += "</entity>" + " "
    text = text.strip()
    return text


def get_initdataset(data, rel2id):
    init_dataset = []
    for i, instance in enumerate(data):
        text = mark_entity(
            instance["token"], instance["h"]["pos"], instance["t"]["pos"]
        )

        init_data = {
            "input": text,
            "head": instance["h"]["name"],
            "tail": instance["t"]["name"],
            "explain_arg": [],
        }
        if instance["relation"] != "no_relation":
            if instance["h"]["pos"][0] < instance["t"]["pos"][0]:
                init_data["explain_arg"].append(
                    [
                        instance["h"]["name"],
                        instance["h"]["type"],
                        instance["t"]["name"],
                        instance["t"]["type"],
                        instance["h"]["name"],
                        instance["relation"],
                        instance["t"]["name"],
                    ]
                )
            else:
                init_data["explain_arg"].append(
                    [
                        instance["t"]["name"],
                        instance["t"]["type"],
                        instance["h"]["name"],
                        instance["h"]["type"],
                        instance["h"]["name"],
                        instance["relation"],
                        instance["t"]["name"],
                    ]
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


def get_response(ExFlag, base_tem, vert, new_options, na, OP2OP):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    if config["BanOutputD"] == True:
        explain_tem = OUTPUT_EXPLAN[0]
    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    new_args = []
    for args in vert["explain_arg"]:
        if args[5] not in OP2OP:
            continue
        type = OP2OP[args[5]]
        if type in new_options:
            new_args.append(copy.deepcopy(args))
            new_args[-1][5] = type
            # print("new:",type)
            # print("origin:",args)
        # else:
        #     print("Error:",OPT_Flag)
        #     print(args[5])
        #     print(new_options)
    if len(new_args) == 0:
        response += na
        response_base += "NA"
    else:
        for args in new_args:
            response += explain_tem.format(
                entity1=args[0],
                etype1=args[1],
                entity2=args[2],
                etype2=args[3],
                head=args[4],
                type=args[5],
                tail=args[6],
            )
            response_base += base_tem[1].format(
                head=args[4], type=args[5], tail=args[6]
            )
            ref += OUTPUT_BASE[0][1].format(head=args[4], type=args[5], tail=args[6])
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_JSONresponse(ExFlag, vert, new_options, na, OP2OP):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    if config["BanOutputD"] == True:
        explain_tem = OUTPUT_EXPLAN[0]
    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    response_json = {
        "subject": "",
        "relation": "",
        "object": "",
    }
    new_args = []
    for args in vert["explain_arg"]:
        if args[5] not in OP2OP:
            continue
        type = OP2OP[args[5]]
        if type in new_options:
            new_args.append(copy.deepcopy(args))
            new_args[-1][5] = type
    if len(new_args) == 0:
        response += na
    else:
        for args in new_args:
            response += explain_tem.format(
                entity1=args[0],
                etype1=args[1],
                entity2=args[2],
                etype2=args[3],
                head=args[4],
                type=args[5],
                tail=args[6],
            )
            response_json["subject"] = args[4]
            response_json["object"] = args[6]
            response_json["relation"] = args[5]
            # response_base+=base_tem[1].format(head=args[4],type=args[5],tail=args[6])
            ref += OUTPUT_BASE[0][1].format(head=args[4], type=args[5], tail=args[6])
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

    input_path = os.path.join(input_folder, split + ".txt")
    data = []
    with open(input_path) as f:
        for line in f.readlines():
            instance = json.loads(line.strip())
            data.append(instance)
        f.close()

    rel_path = os.path.join(input_folder, "rel_des.json")
    rel2id = json.load(open(rel_path))
    options = [rel for rel in list(rel2id.keys())]
    assert len(set(options)) == len(rel2id)
    if "no_relation" in options:
        options.remove("no_relation")

    # instruction
    with open(inst_file, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["RC"]

    # 获得原始数据
    init_dataset = get_initdataset(data, rel2id)
    example_dataset = []
    if "test" in split:
        input_path = os.path.join(input_folder, "train.txt")
        train_data = []
        with open(input_path) as f:
            for line in f.readlines():
                instance = json.loads(line.strip())
                train_data.append(instance)
            f.close()
        example_dataset = get_initdataset(train_data, rel2id)
    else:
        example_dataset = copy.deepcopy(init_dataset)
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理原始数据
    out_file = open(os.path.join(output_folder, split + ".jsonl"), "w")
    na_data = 0
    for i, vert in enumerate(init_dataset):

        # instruction & options
        instruction, na = get_instruction(inst)
        REP_Flag = (int)(random.random() < 0.7)
        if REP_Flag:
            if "<entity1>" in instruction:
                instruction = instruction.replace("<entity1>", '"' + vert["head"] + '"')
            if "<entity2>" in instruction:
                instruction = instruction.replace("<entity2>", '"' + vert["tail"] + '"')
            if "<head>" in instruction:
                instruction = instruction.replace("<head>", '"' + vert["head"] + '"')
            if "<tail>" in instruction:
                instruction = instruction.replace("<tail>", '"' + vert["tail"] + '"')
        new_options = []
        for op in options:
            flag = (int)(random.random() > config["CLASS_DROPOUT_RATE"])
            if flag == 1:
                new_options.append(op)
        random.shuffle(new_options)

        # if desc -> ALL_DESC
        DESC_Flag = (int)(random.random() < config["DESC_RATE"])
        length = len(new_options)
        if DESC_Flag:
            isAll = (random.random() < config["ISALL"]) or (
                config["LIMIT_DESC"] > length
            )
            if isAll:
                new_options = new_options[0 : min(config["LIMIT_DESC"], length)]
                In_Flag = False
                for args in vert["explain_arg"]:
                    if args[5] not in new_options:
                        new_options.append(args[5])
                        In_Flag = True
                if In_Flag:
                    # print("New Options:",new_options)
                    random.shuffle(new_options)

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
        # if OPT_Flag!=-1 and OPT_Flag<6:
        #     print(OPT_Flag)
        #     print(dnew_options)

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
                get_JSONresponse(ExFlag, vert, dnew_options, na, OP2OP)
            )
            unified_instance["query"][1] = JSON_BASE
        else:
            unified_instance["reference"], unified_instance["output"] = get_response(
                ExFlag, base_tem, vert, dnew_options, na, OP2OP
            )

        # examples
        HistoryData = random.sample(example_dataset, config["NUM_FEWSHOT_Limit"])
        for hd in HistoryData:
            if hd == vert:
                continue
            if JsonFlag:
                hdref, hdout = get_JSONresponse(ExFlag, hd, dnew_options, na, OP2OP)
            else:
                hdref, hdout = get_response(
                    ExFlag, base_tem, hd, dnew_options, na, OP2OP
                )
            unified_instance["examples"].append([hd["input"], hdout, hdref])

        # desc_options & instructions
        if DESC_Flag:
            l = range(0, len(new_options))
            desc = random.sample(
                l, config["LIMIT_DESC"]
            )  # limit the desc num to avoid cutoff
            idx = (int)(random.random() >= 0.5)
            if idx:
                for k, op in enumerate(new_options):
                    if k in desc:
                        dnew_options[k] = dnew_options[k] + ": '" + rel2id[op] + "'"
                    else:
                        dnew_options[k] = dnew_options[k] + ": ''"
            else:
                for k, op in enumerate(new_options):
                    if k in desc:
                        dnew_options[k] = (
                            "'" + dnew_options[k] + "' means '" + rel2id[op] + "'"
                        )
                    else:
                        dnew_options[k] = "'" + dnew_options[k] + "' means ''"
        if "<options>" in instruction:
            instruction = instruction.replace(
                "<options>", "[" + ", ".join(dnew_options) + "]", 1
            )
        else:
            instruction += "\nOptions: [" + ", ".join(dnew_options) + "]\n"
        unified_instance["instruction"] = instruction

        if unified_instance["reference"] == "":
            na_data += 1
        out_file.write(json.dumps(unified_instance) + "\n")

        if i < 10:
            print("============== CASE: ", split, i, "====================")
            print(unified_instance)

    print("na_num:", na_data)
    print("valid_num", len(data) - na_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="tacred")
    # I/O
    parser.add_argument(
        "--input_dir", type=str, default="../../../data/Relation_Extraction/tacred"
    )
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data/tacred"
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
