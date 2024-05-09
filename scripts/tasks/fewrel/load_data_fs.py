import os
import json
import random
from pathlib import Path
import copy
import argparse
from desc import JSON_BASE, OUTPUT_BASE, OUTPUT_EXPLAN, RANDOM_SYMBOLS


def diverse_options(x, flag):
    # orix = x
    # RepFlag = (int)(random.random() < config["SymbolLabels"])
    # if RepFlag == 1 and len(Symbols):
    #     x = random.sample(Symbols, 1)[0]
    #     Symbols.remove(x)

    if flag == 0:
        x = x.lower()
    if flag == 1:
        x = x.replace(" ", "_")
    if flag == 2:
        x = x.replace(" ", "-")
    if flag == 3:
        x = x.replace(" ", "_").lower()
    if flag == 4:
        x = x.replace(" ", "-").lower()

    # OP2OP[orix] = x
    return x


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


def mark_entity(tokens, h_pos, t_pos):
    text = ""
    for i, token in enumerate(tokens):
        for v in h_pos:
            if i == v[0]:
                text += "<head>" + " "
                break
        for v in t_pos:
            if i == v[0]:
                text += "<tail>" + " "
                break
        text += token + " "
        for v in h_pos:
            l = len(v) - 1
            if i == v[l]:
                text += "</head>" + " "
                break
        for v in t_pos:
            l = len(v) - 1
            if i == v[l]:
                text += "</tail>" + " "
                break
    text = text.strip()
    return text


def convert_usual_format(data, rel2id, flag):
    d = []
    for key, value in data.items():
        for instance in value:
            if flag == 0:
                r = rel2id[key][0]
            else:
                r = key
            instance["relation_key"] = key
            instance["relation"] = r
            d.append(instance)
    return d


def get_initdataset(data, rel2id):
    init_dataset = []
    for i, instance in enumerate(data):
        text = mark_entity(instance["tokens"], instance["h"][2], instance["t"][2])

        init_data = {
            "input": text,
            "head": instance["h"][0],
            "tail": instance["t"][0],
            "explain_arg": [],
        }
        if instance["relation"] != "no_relation":
            if instance["h"][2][0] < instance["t"][2][0]:
                init_data["explain_arg"].append(
                    [
                        instance["relation_key"],
                        instance["h"][0],
                        instance["t"][0],
                        instance["h"][0],
                        instance["relation"],
                        instance["t"][0],
                    ]
                )
            else:
                init_data["explain_arg"].append(
                    [
                        instance["relation_key"],
                        instance["t"][0],
                        instance["h"][0],
                        instance["h"][0],
                        instance["relation"],
                        instance["t"][0],
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


def get_response(ExFlag, base_tem, vert, new_options, na, OPT_Flag):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    if config["BanOutputD"] == True:
        explain_tem = OUTPUT_EXPLAN[0]
    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    new_args = []
    for args in vert["explain_arg"]:
        if args[0] in new_options:
            new_args.append(copy.deepcopy(args))
            new_args[-1][4] = diverse_options(args[4], OPT_Flag)
    if len(new_args) == 0:
        response += na
        response_base += "NA"
    else:
        for args in new_args:
            response += explain_tem.format(
                entity1=args[1],
                entity2=args[2],
                head=args[3],
                type=args[4],
                tail=args[5],
            )
            response_base += base_tem[1].format(
                head=args[3], type=args[4], tail=args[5]
            )
            ref += OUTPUT_BASE[0][1].format(head=args[3], type=args[4], tail=args[5])
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_JSONresponse(ExFlag, vert, new_options, na, OPT_Flag):
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
        if args[0] in new_options:
            new_args.append(copy.deepcopy(args))
            new_args[-1][4] = diverse_options(args[4], OPT_Flag)
    if len(new_args) == 0:
        response += na
    else:
        if len(new_args) > 1:
            print("============ ERROR : relations > 1 ==============")
        for args in new_args:
            response += explain_tem.format(
                entity1=args[1],
                entity2=args[2],
                head=args[3],
                type=args[4],
                tail=args[5],
            )
            response_json["subject"] = args[3]
            response_json["object"] = args[5]
            response_json["relation"] = args[4]
            ref += OUTPUT_BASE[0][1].format(head=args[3], type=args[4], tail=args[5])
    response_base += str(response_json)
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def construct_response(input_folder, output_folder, inst_file, split, config):
    if "test" in split:
        config["CLASS_DROPOUT_RATE"] = 0
        config["ALL_DESC"] = 0
        config["BIG_TYPE"] = 0
        # ?
        config["DESC_RATE"] = 0
        config["EXPLAIN_RATE"] = 0
        config["UNCOMPELETE_OPTION"] = False
        config["NUM_FEWSHOT_Limit"] = 0  # fewrel数据集特殊
        config["SAMPLE_RATE"] = 0
        config["JSON_RATE"] = 0

    input_path = os.path.join(input_folder, split + ".json")
    with open(input_path, "r", encoding="utf-8") as reader:
        d = json.load(reader)
        reader.close()

    # options
    rel_path = os.path.join(input_folder, "pid2name.json")
    rel2id = json.load(open(rel_path))
    options = []
    if split == "test_wiki" or split == "train_wiki":
        for key, value in d.items():
            options.append(key)  # rel_key
    if split == "test_pubmed":
        options = [dd for dd in list(d.keys())]  # rel_name
    if "no_relation" in options:
        options.remove("no_relation")

    data = convert_usual_format(d, rel2id, split == "test_pubmed")

    # instruction
    with open(inst_file, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["RC"]

    # 获得原始数据
    init_dataset = get_initdataset(data, rel2id)
    example_dataset = []
    if "test" in split:
        input_path = os.path.join(input_folder, "train_wiki.json")
        train_data = dict()
        with open(input_path, "r", encoding="utf-8") as reader:
            train_data = json.load(reader)
            reader.close()
        train_data = convert_usual_format(train_data, rel2id, False)
        example_dataset = get_initdataset(train_data, rel2id)
    else:
        example_dataset = copy.deepcopy(init_dataset)
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理init-data
    na_data = 0
    out_file = open(os.path.join(output_folder, split + ".jsonl"), "w")
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
        DESC_Flag = False
        if "wiki" in split:
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
                        if args[0] not in new_options:
                            new_options.append(args[0])
                            In_Flag = True
                    if In_Flag:
                        # print("New Options:",new_options)
                        random.shuffle(new_options)

        # deverse option
        OPT_Flag = -1
        if config["UNCOMPELETE_OPTION"] == True:
            OPT_Flag = random.randint(0, 10)
        # dnew_options=[diverse_options(op,OPT_Flag) for op in new_options]
        # if OPT_Flag!=-1 and OPT_Flag<=4:
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
                get_JSONresponse(ExFlag, vert, new_options, na, OPT_Flag)
            )
            unified_instance["query"][1] = JSON_BASE
        else:
            unified_instance["reference"], unified_instance["output"] = get_response(
                ExFlag, base_tem, vert, new_options, na, OPT_Flag
            )

        # examples
        HistoryData = random.sample(example_dataset, config["NUM_FEWSHOT_Limit"])
        for hd in HistoryData:
            if hd == vert:
                continue
            if JsonFlag:
                hdref, hdout = get_JSONresponse(ExFlag, hd, new_options, na, OPT_Flag)
            else:
                hdref, hdout = get_response(
                    ExFlag, base_tem, hd, new_options, na, OPT_Flag
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
                        opt = diverse_options(rel2id[op][0], OPT_Flag)
                        new_options[k] = opt + ": '" + rel2id[op][1] + "'"
                    else:
                        opt = diverse_options(rel2id[op][0], OPT_Flag)
                        new_options[k] = opt + ": ''"
            else:
                for k, op in enumerate(new_options):
                    if k in desc:
                        opt = diverse_options(rel2id[op][0], OPT_Flag)
                        new_options[k] = "'" + opt + "' means '" + rel2id[op][1] + "'"
                    else:
                        opt = diverse_options(rel2id[op][0], OPT_Flag)
                        new_options[k] = "'" + opt + "' means ''"
        elif "wiki" in split:
            for k, op in enumerate(new_options):
                opt = diverse_options(rel2id[op][0], OPT_Flag)
                new_options[k] = opt

        if "<options>" in instruction:
            instruction = instruction.replace(
                "<options>", "[" + ", ".join(new_options) + "]", 1
            )
        else:
            instruction += "\nOptions: [" + ", ".join(new_options) + "]\n"
        unified_instance["instruction"] = instruction

        out_file.write(json.dumps(unified_instance) + "\n")
        if unified_instance["reference"] == "":
            na_data += 1

        if i < 10:
            print("============== CASE: ", split, i, "====================")
            print(unified_instance)

    print("na_num:", na_data)
    print("valid_num", len(init_dataset) - na_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fewerel")
    # I/O
    parser.add_argument(
        "--input_dir", type=str, default="../../../data/Relation_Extraction/fewrel"
    )
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data/fewrel"
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
    construct_response(input_folder, output_folder, inst_file, "train_wiki", config)
    # construct_response(input_folder, output_folder, inst_file, "test_wiki", config)
