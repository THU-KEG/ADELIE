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
        x = x.lower()
    if flag == 1:
        x = x.replace("-", "_")
    if flag == 2:
        x = x.replace("-", " ")
    if flag == 3:
        x = x.replace("-", "_").lower()
    if flag == 4:
        x = x.replace("-", " ").lower()

    OP2OP[orix] = x

    return x


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


def find_schema(data):
    schema = {}
    entities = {}
    roles = set()
    for i, sample in enumerate(data):
        entities.clear()
        for entity in sample["entities"]:
            if entity["id"] not in entities:
                entities[entity["id"]] = set()
            for mention in entity["mention"]:
                # print(entities)
                entities[entity["id"]].add(mention["mention"])
        for event in sample["events"]:
            if event["type"] not in schema:
                schema[event["type"]] = dict()
            for role, value in event["argument"].items():
                if role not in schema[event["type"]]:
                    schema[event["type"]][role] = set()
                    roles.add(role)
                for mention in value:
                    if "content" in mention:
                        schema[event["type"]][role].add(mention["content"])
                    else:
                        schema[event["type"]][role] = schema[event["type"]][role].union(
                            entities[mention["entity_id"]]
                        )
            # if i<1:
            #     print("============== schema: ",i,"====================")
            #     print(entities)
            #     print(schema)
    for type, value in schema.items():
        for role, sample in value.items():
            schema[type][role] = list(sample)
    print(roles)
    print(len(roles))
    return schema


def mark_event(tokens, sentens, senid, h_pos, t_pos, markers=["<event>", "</event>"]):
    text = (
        " ".join(tokens[senid][:h_pos])
        + f" {markers[0]} "
        + " ".join(tokens[senid][h_pos:t_pos])
        + f" {markers[1]} "
        + " ".join(tokens[senid][t_pos:])
        + " "
    )
    new_text = " ".join(sentens[:senid]) + text + " ".join(sentens[senid + 1 :])
    return new_text


def get_response(ExFlag, base_tem, vert, new_options, na, OP2OP):
    explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
    if config["BanOutputD"] == True:
        explain_tem = OUTPUT_EXPLAN[0]
    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = ""
    new_args = []
    for args in vert["explain_arg"]:
        if args[1] not in OP2OP:
            continue
        type = OP2OP[args[1]]
        if type in new_options:
            new_args.append(copy.deepcopy(list(args)))
            new_args[-1][1] = type
    if len(new_args) == 0:
        response += na
        response_base += "NA"
    else:
        response += explain_tem.format(event=vert["event"], etype=vert["event_type"])
        for args in new_args:
            response_base += base_tem[1].format(word=args[0], type=args[1])
            ref += OUTPUT_BASE[0][1].format(word=args[0], type=args[1])
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
    response_json = {}
    for item in new_options:
        response_json[item] = []

    new_args = []
    for args in vert["explain_arg"]:
        if args[1] not in OP2OP:
            continue
        type = OP2OP[args[1]]
        if type in new_options:
            new_args.append(copy.deepcopy(list(args)))
            new_args[-1][1] = type
    if len(new_args) == 0:
        response += na
    else:
        response += explain_tem.format(event=vert["event"], etype=vert["event_type"])
        for args in new_args:
            response_json[args[1]].append(args[0])
            # response_base+=base_tem[1].format(word=args[0],type=args[1])
            ref += OUTPUT_BASE[0][1].format(word=args[0], type=args[1])

    response_base += str(response_json)
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_initdataset(data):
    init_dataset = []
    entities = {}
    labels = set()
    for instance in data:
        entities.clear()
        for entity in instance["entities"]:
            if entity["id"] not in entities:
                entities[entity["id"]] = set()
            for mention in entity["mention"]:
                entities[entity["id"]].add(mention["mention"])
        for event in instance["events"]:
            labels.clear()
            for role, value in event["argument"].items():
                for mention in value:
                    if "content" in mention:
                        labels.add((mention["content"], role))
                    else:
                        for men in entities[mention["entity_id"]]:
                            labels.add((men, role))

            for trigger in event["mention"]:
                text = mark_event(
                    instance["tokens"],
                    instance["sentences"],
                    trigger["sent_id"],
                    trigger["offset"][0],
                    trigger["offset"][1],
                )
                init_data = {
                    "input": text,
                    "event": trigger["trigger_word"],
                    "event_type": event["type"],
                    "explain_arg": copy.deepcopy(list(labels)),
                }
                init_dataset.append(init_data)
    return init_dataset


def get_exampledata(data):
    example_dataset = dict()
    entities = {}
    labels = set()
    for instance in data:
        entities.clear()
        for entity in instance["entities"]:
            if entity["id"] not in entities:
                entities[entity["id"]] = set()
            for mention in entity["mention"]:
                entities[entity["id"]].add(mention["mention"])
        for event in instance["events"]:
            if event["type"] not in example_dataset:
                example_dataset[event["type"]] = []
            labels.clear()
            for role, value in event["argument"].items():
                for mention in value:
                    if "content" in mention:
                        labels.add((mention["content"], role))
                    else:
                        for men in entities[mention["entity_id"]]:
                            labels.add((men, role))
            id = random.randint(0, len(event["mention"]) - 1)
            trigger = event["mention"][id]
            text = mark_event(
                instance["tokens"],
                instance["sentences"],
                trigger["sent_id"],
                trigger["offset"][0],
                trigger["offset"][1],
            )
            init_data = {
                "input": text,
                "event": trigger["trigger_word"],
                "event_type": event["type"],
                "explain_arg": copy.deepcopy(list(labels)),
            }
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
    tot_na = 0
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
        tot_na += len(NA_data)

        if num_NA_data < len(NA_data):
            NA_data = random.sample(NA_data, num_NA_data)
        valid_data = valid_data + NA_data
        random.shuffle(valid_data)

        print("event_type:", key)
        print("sample NA:", len(NA_data))
        print("sum instances:", len(valid_data))

        example_dataset[key] = copy.deepcopy(valid_data)
    print("tot_na:", tot_na)

    return example_dataset


def desc_load(rel_path):
    rel = json.load(open(rel_path))
    rel2id = {}
    for vert in rel:
        rel2id[vert["type"]] = vert["argument_role"]
    return rel2id


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

    print("CONFIG:", config)

    d = input_folder.joinpath(split + ".jsonl")
    data = read_jsonlines(d)
    schema = find_schema(data)  # schema & samples

    with open(inst_file, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["EAE"]

    rel_path = os.path.join(input_folder, "English_EventSchema.json")
    rel2id = desc_load(rel_path)

    # 获得原始数据
    init_dataset = get_initdataset(data)
    example_dataset = []
    if "test" in split:
        d = input_folder.joinpath("train.jsonl")
        train_data = read_jsonlines(d)
        example_dataset = get_exampledata(train_data)
    else:
        example_dataset = get_exampledata(data)
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理原始数据
    out_file = open(os.path.join(output_folder, split + ".jsonl"), "w")

    na_data = 0
    for i, vert in enumerate(init_dataset):
        # instruction & options
        instruction, na = get_instruction(inst)
        new_options = []
        for op in schema[vert["event_type"]].keys():
            flag = (int)(random.random() > config["CLASS_DROPOUT_RATE"])
            if flag == 1:
                new_options.append(op)
        random.shuffle(new_options)

        REP_Flag = (int)(random.random() < 0.7)
        if REP_Flag:
            if "{event}" in instruction:
                instruction = instruction.replace("{event}", '"' + vert["event"] + '"')

        # if desc -> ALL_DESC
        DESC_Flag = (int)(random.random() < config["DESC_RATE"])
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
            if isAll:
                In_Flag = False
                for args in vert["explain_arg"]:
                    if args[1] not in new_options:
                        new_options.append(args[1])
                        In_Flag = True
                if In_Flag:
                    # if i<50:
                    #     print("ALL Options:",schema[vert["event_type"]].keys())
                    #     print("New Options:",new_options)
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
        # if OPT_Flag!=-1 and OPT_Flag<=4:
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
                get_JSONresponse(ExFlag, vert, dnew_options, na, OP2OP)
            )
            unified_instance["query"][1] = JSON_BASE
        else:
            unified_instance["reference"], unified_instance["output"] = get_response(
                ExFlag, base_tem, vert, dnew_options, na, OP2OP
            )

        # examples
        HistoryData = random.sample(
            example_dataset[vert["event_type"]],
            min(config["NUM_FEWSHOT_Limit"], len(example_dataset[vert["event_type"]])),
        )
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
        l = range(0, len(new_options))
        length = len(new_options)
        desc = random.sample(
            l, min(config["LIMIT_DESC"], length)
        )  # limit the desc num to avoid cutoff
        samp = random.sample(l, min(config["LIMIT_SAMPLE"], length))
        # print("schema[vert["event_type"]]:",schema[vert["event_type"]])
        if DESC_Flag:
            idx = (int)(random.random() >= 0.5)
            if idx:
                for k, op in enumerate(new_options):
                    if k in desc:
                        dnew_options[k] = (
                            '"'
                            + dnew_options[k]
                            + ": "
                            + rel2id[vert["event_type"]][op]
                            + '"'
                        )
                        if (
                            SampleFlag
                            and k in samp
                            and len(schema[vert["event_type"]][new_options[k]]) >= 10
                        ):
                            samples = random.sample(
                                schema[vert["event_type"]][new_options[k]],
                                config["EACH_SAMPLE_NUM"],
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
                            and len(schema[vert["event_type"]][new_options[k]]) >= 10
                        ):
                            samples = random.sample(
                                schema[vert["event_type"]][new_options[k]],
                                config["EACH_SAMPLE_NUM"],
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
                            "\"'"
                            + dnew_options[k]
                            + "' means '"
                            + rel2id[vert["event_type"]][op]
                            + "'\""
                        )
                        if (
                            SampleFlag
                            and k in samp
                            and len(schema[vert["event_type"]][new_options[k]]) >= 10
                        ):
                            samples = random.sample(
                                schema[vert["event_type"]][new_options[k]],
                                config["EACH_SAMPLE_NUM"],
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
                            and len(schema[vert["event_type"]][new_options[k]]) >= 10
                        ):
                            samples = random.sample(
                                schema[vert["event_type"]][new_options[k]],
                                config["EACH_SAMPLE_NUM"],
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
                    if (
                        k in samp
                        and len(schema[vert["event_type"]][new_options[k]]) >= 10
                    ):
                        samples = random.sample(
                            schema[vert["event_type"]][new_options[k]],
                            config["EACH_SAMPLE_NUM"],
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
            instruction += "\nRoleset: [" + ", ".join(dnew_options) + "]\n"

        unified_instance["instruction"] = instruction

        out_file.write(json.dumps(unified_instance) + "\n")
        if unified_instance["reference"] == "":
            na_data += 1

        if i < 10:
            print("============== CASE: ", split, i, "====================")
            # print(new_options)
            print(json.dumps(unified_instance))

    print("na_num:", na_data)
    print("valid_num", len(init_dataset) - na_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ace2005-eae")
    # I/O
    parser.add_argument(
        "--input_dir", type=str, default="../../../data/Event_Extraction/MAVEN-Arg"
    )
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data_test/maven-eae"
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

    # config在内部修改后，在外部也会修改，所以先跑train！
    construct_response(input_folder, output_folder, inst_file, "train", config)
    # construct_response(input_folder, output_folder, inst_file, "test", config)
