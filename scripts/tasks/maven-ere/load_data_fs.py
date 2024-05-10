import json
import numpy as np
import random
from pathlib import Path
import copy
import argparse
from desc import *


def diverse_options(x, flag, config, OP2OP, Symbols):
    orix = x
    RepFlag = (int)(random.random() < config["SymbolLabels"])
    if RepFlag == 1 and len(Symbols):
        x = random.sample(Symbols, 1)[0]
        Symbols.remove(x)

    if flag == 0:
        x = x.replace("_", "-")
    if flag == 1:
        x = x.replace("_", " ")
    if flag == 2:
        x = x.replace("-", " ")
    if flag == 3:
        x = x.replace("-", "_")

    OP2OP[orix] = x

    return x


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


# 对文档的处理，返回处理好的文档和关系列表等信息
def gen_prompt_doc(doc):
    temp_rel = doc["temporal_relations"]
    caus_rel = doc["causal_relations"]
    sub_rel = {"subevent": doc["subevent_relations"]}
    temp_rel.update(caus_rel)
    temp_rel.update(sub_rel)
    all_rel = temp_rel
    events = doc["events"]
    tokens = doc["tokens"]
    timexs = doc["TIMEX"]
    if "sentences" in doc.keys():
        sentences = doc["sentences"]
    else:
        sentences = [merge_tokens([toks]) for toks in doc["tokens"]]
    event_num2id = {}
    event_idx = 0
    event_names = []
    event_list = []
    event_num2type = {}

    for event in events:
        if len(event["mention"]) > 1:
            for mention in event["mention"]:
                event_num2id[event_idx] = event["id"]
                event_num2type[event_idx] = [event["type"], "event"]
                event_list.append(mention)
                sent_id = mention["sent_id"]
                offset = mention["offset"]
                new_event_name = (
                    "<Event> "
                    + " ".join(tokens[sent_id][offset[0] : offset[1]])
                    + " </Event>"
                )
                event_names.append(new_event_name)
                event_idx += 1
        else:
            event_num2id[event_idx] = event["id"]
            event_num2type[event_idx] = [event["type"], "event"]
            mention = event["mention"][0]
            event_list.append(mention)
            sent_id = mention["sent_id"]
            offset = mention["offset"]
            new_event_name = (
                "<Event> "
                + " ".join(tokens[sent_id][offset[0] : offset[1]])
                + " </Event>"
            )
            event_names.append(new_event_name)
            event_idx += 1

    for timex in timexs:
        event_num2id[event_idx] = timex["id"]
        event_num2type[event_idx] = [timex["type"], "timex"]
        event_list.append(timex)
        sent_id = timex["sent_id"]
        offset = timex["offset"]
        new_event_name = (
            "<Timex> " + " ".join(tokens[sent_id][offset[0] : offset[1]]) + " </Timex>"
        )
        event_names.append(new_event_name)
        event_idx += 1

    rel_dict = {}
    for i in range(event_idx):
        rel_dict[event_num2id[i]] = {}
        for j in range(event_idx):
            rel_dict[event_num2id[i]][event_num2id[j]] = []
    for rel_name in all_rel.keys():
        rel_list = all_rel[rel_name]
        for rel in rel_list:
            rel_dict[rel[0]][rel[1]].append(rel_name.lower())
    return (
        tokens,
        event_idx,
        rel_dict,
        event_names,
        event_num2id,
        event_list,
        sentences,
        event_num2type,
    )


# 把分离的tokens整合成完整的句子，要考虑到标点符号的特殊性
def merge_tokens(tokens):
    text = ""
    blank = False
    for toks in tokens:
        for tok in toks:
            if tok in [
                ",",
                ".",
                ";",
                ":",
                "!",
                "?",
                ">",
                ")",
                "]",
                "}",
                "''",
                "'s",
                "%",
            ]:
                text += tok
                blank = True
            elif tok == "-":
                text += tok
                blank = False
            elif tok in ["<", "(", "[", "{", "``", "`", "$"]:
                if blank == True:
                    text += " "
                text += tok
                blank = False
            else:
                if blank == True:
                    text += " "
                text += tok
                blank = True
    return text


def get_initdataset(select_list, config):
    init_dataset = []
    count_rel = {}
    count_rel["none"] = 0
    for doc_idx, doc in enumerate(select_list):
        (
            tokens,
            num_event,
            rel_dict,
            event_names,
            event_num2id,
            event_list,
            sentences,
            event_num2type,
        ) = gen_prompt_doc(doc)
        cnt = 0
        for i in range(num_event):
            for j in range(num_event):
                if i == j:
                    continue
                sent_id1 = event_list[i]["sent_id"]
                offset1 = event_list[i]["offset"]
                sent_id2 = event_list[j]["sent_id"]
                offset2 = event_list[j]["offset"]
                work_tokens = []

                for sent_id, toks in enumerate(tokens):
                    if sent_id1 != sent_id and sent_id2 != sent_id:
                        work_tokens.append(sentences[sent_id])
                    else:
                        tmp_tokens = []
                        if sent_id1 == sent_id and sent_id2 != sent_id:
                            for off, tok in enumerate(toks):
                                if offset1[0] == off:
                                    tmp_tokens.append(event_names[i])
                                elif off < offset1[0] or off >= offset1[1]:
                                    tmp_tokens.append(tok)
                        elif sent_id2 == sent_id and sent_id1 != sent_id:
                            for off, tok in enumerate(toks):
                                if offset2[0] == off:
                                    tmp_tokens.append(event_names[j])
                                elif off < offset2[0] or off >= offset2[1]:
                                    tmp_tokens.append(tok)
                        else:
                            for off, tok in enumerate(toks):
                                if offset1[0] == off:
                                    tmp_tokens.append(event_names[i])
                                elif offset2[0] == off:
                                    tmp_tokens.append(event_names[j])
                                elif (off < offset1[0] or off >= offset1[1]) and (
                                    off < offset2[0] or off >= offset2[1]
                                ):
                                    tmp_tokens.append(tok)
                        work_tokens.append(merge_tokens([tmp_tokens]))
                work_tokens = " ".join(work_tokens)

                query = (
                    "Document: "
                    + work_tokens
                    + '\n\nThe first event/"Timex": '
                    + event_names[i]
                    + '\nThe second event/"Timex": '
                    + event_names[j]
                    + "\n"
                )
                if event_num2id[i] == event_num2id[j]:
                    label = ["coreference"]
                else:
                    label = rel_dict[event_num2id[i]][event_num2id[j]]

                name1 = " ".join(event_names[i].split(" ")[1:-1])
                name2 = " ".join(event_names[j].split(" ")[1:-1])

                for item in label:
                    init_data = {
                        "input": query,
                        "btype": REL[item][1],
                        "first": [name1, event_num2type[i][0], event_num2type[i][1]],
                        "second": [name2, event_num2type[j][0], event_num2type[j][1]],
                        "explain_arg": [item],
                    }
                    if item not in count_rel:
                        count_rel[item] = 0

                    if count_rel[item] <= config["Limit_REL"]:
                        count_rel[item] += 1
                        init_dataset.append(init_data)

                if len(label) == 0 and count_rel["none"] <= config["Limit_REL"]:
                    count_rel["none"] += 1
                    init_data = {
                        "input": query,
                        "btype": "",
                        "first": [name1, event_num2type[i][0], event_num2type[i][1]],
                        "second": [name2, event_num2type[j][0], event_num2type[j][1]],
                        "explain_arg": [],
                    }
                    init_data["btype"] = random.choices(BTYPES, k=1)[0]
                    init_dataset.append(init_data)
    print("init_count_rel:", count_rel)
    return init_dataset


def get_exampledata(select_list, config):
    example_dataset = dict()
    for bt in BTYPES:
        example_dataset[bt] = []

    count_rel = {}
    for doc_idx, doc in enumerate(select_list):
        (
            tokens,
            num_event,
            rel_dict,
            event_names,
            event_num2id,
            event_list,
            sentences,
            event_num2type,
        ) = gen_prompt_doc(doc)
        cnt = 0
        for i in range(num_event):
            for j in range(num_event):
                if i == j:
                    continue
                sent_id1 = event_list[i]["sent_id"]
                offset1 = event_list[i]["offset"]
                sent_id2 = event_list[j]["sent_id"]
                offset2 = event_list[j]["offset"]
                work_tokens = []

                for sent_id, toks in enumerate(tokens):
                    if sent_id1 != sent_id and sent_id2 != sent_id:
                        work_tokens.append(sentences[sent_id])
                    else:
                        tmp_tokens = []
                        if sent_id1 == sent_id and sent_id2 != sent_id:
                            for off, tok in enumerate(toks):
                                if offset1[0] == off:
                                    tmp_tokens.append(event_names[i])
                                elif off < offset1[0] or off >= offset1[1]:
                                    tmp_tokens.append(tok)
                        elif sent_id2 == sent_id and sent_id1 != sent_id:
                            for off, tok in enumerate(toks):
                                if offset2[0] == off:
                                    tmp_tokens.append(event_names[j])
                                elif off < offset2[0] or off >= offset2[1]:
                                    tmp_tokens.append(tok)
                        else:
                            for off, tok in enumerate(toks):
                                if offset1[0] == off:
                                    tmp_tokens.append(event_names[i])
                                elif offset2[0] == off:
                                    tmp_tokens.append(event_names[j])
                                elif (off < offset1[0] or off >= offset1[1]) and (
                                    off < offset2[0] or off >= offset2[1]
                                ):
                                    tmp_tokens.append(tok)
                        work_tokens.append(merge_tokens([tmp_tokens]))
                work_tokens = " ".join(work_tokens)

                query = (
                    "Document: "
                    + work_tokens
                    + '\n\nThe first event/"Timex": '
                    + event_names[i]
                    + '\nThe second event/"Timex": '
                    + event_names[j]
                    + "\n"
                )
                if event_num2id[i] == event_num2id[j]:
                    label = ["coreference"]
                else:
                    label = rel_dict[event_num2id[i]][event_num2id[j]]

                name1 = " ".join(event_names[i].split(" ")[1:-1])
                name2 = " ".join(event_names[j].split(" ")[1:-1])

                for item in label:
                    init_data = {
                        "input": query,
                        "btype": REL[item][1],
                        "first": [name1, event_num2type[i][0], event_num2type[i][1]],
                        "second": [name2, event_num2type[j][0], event_num2type[j][1]],
                        "explain_arg": [item],
                    }
                    if item not in count_rel:
                        count_rel[item] = 0
                    if count_rel[item] <= config["limit_sample_relation"]:
                        count_rel[item] += 1
                        example_dataset[init_data["btype"]].append(init_data)
    print("example_count_rel:", count_rel)
    return example_dataset


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


def get_response(ExFlag, base_tem, vert, new_options, na, OP2OP):
    if vert["first"][2] == "event":
        explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
        if config["BanOutputD"] == True:
            explain_tem = OUTPUT_EXPLAN[0]
    else:
        explain_tem = random.sample(OUTPUT_EXPLAN_T, 1)[0]
        if config["BanOutputD"] == True:
            explain_tem = OUTPUT_EXPLAN_T[0]

    response = "[Explanation]: "
    response_base = "[Answer]: "
    ref = []
    new_args = []
    for args in vert["explain_arg"]:
        if args not in OP2OP:
            continue
        type = OP2OP[args]
        if type in new_options:
            new_args.append(args)
    if len(new_args) == 0:
        response += na
        response_base += "NA"
    else:
        response += explain_tem.format(
            e1=vert["first"][0],
            t1=vert["first"][1],
            e2=vert["second"][0],
            t2=vert["second"][1],
        )
        for args in new_args:
            type = OP2OP[args]
            response_base += base_tem[1].format(
                head=vert["first"][0], type=type, tail=vert["second"][0]
            )
            r = REL[args][0].replace("@", vert["first"][0])
            r = r.replace("$", vert["second"][0])
            response += r
            ref.append(type)
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def get_JSONresponse(ExFlag, vert, new_options, na, OP2OP):
    if vert["first"][2] == "event":
        explain_tem = random.sample(OUTPUT_EXPLAN, 1)[0]
        if config["BanOutputD"] == True:
            explain_tem = OUTPUT_EXPLAN[0]
    else:
        explain_tem = random.sample(OUTPUT_EXPLAN_T, 1)[0]
        if config["BanOutputD"] == True:
            explain_tem = OUTPUT_EXPLAN_T[0]

    response = "[Explanation]: "
    response_base = "[Answer]: "
    response_json = {
        "head event": "",
        "relation": "",
        "tail event": "",
    }
    ref = []
    new_args = []
    for args in vert["explain_arg"]:
        if args not in OP2OP:
            continue
        type = OP2OP[args]
        if type in new_options:
            new_args.append(args)
    if len(new_args) == 0:
        response += na
    else:
        response += explain_tem.format(
            e1=vert["first"][0],
            t1=vert["first"][1],
            e2=vert["second"][0],
            t2=vert["second"][1],
        )
        for args in new_args:
            type = OP2OP[args]
            response_json = {
                "head event": vert["first"][0],
                "relation": type,
                "tail event": vert["second"][0],
            }
            # response_base+=base_tem[1].format(head=vert["first"][0],type=type,tail=vert["second"][0])
            r = REL[args][0].replace("@", vert["first"][0])
            r = r.replace("$", vert["second"][0])
            response += r
            ref.append(type)
    response_base += str(response_json)
    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def make_eval_data(
    input_folder, output_folder, inst_file, split, number, config, selection="average"
):

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
        config["Limit_REL"] = 10000000
        config["limit_sample_relation"] = 10000000

    load_split_name = split
    if split == "dev":
        load_split_name = "valid"

    with open(input_folder.joinpath(load_split_name + ".jsonl"), "r") as file:
        load_file = file.readlines()

    select_list = []

    assert selection == "random"
    sel_idx = list(range(len(load_file)))
    random.shuffle(sel_idx)

    with open("sel_idx_" + split + ".txt", "w") as f:
        for i in sel_idx[0:number]:
            f.write(str(i) + "\n")
        f.close()

    for i in sel_idx[0:number]:
        doc = json.loads(load_file[i].strip())
        if split == "test":
            new_doc = {}
            new_doc["tokens"] = doc["doc"]["tokens"]
            new_doc["events"] = doc["events"]
            for events in new_doc["events"]:
                events["mention"] = events["mentions"]
                events["type"] = events["mentions"][0]["event_type"]
            new_doc["TIMEX"] = doc["TIMEX3"]
            new_doc["temporal_relations"] = doc["temporal_event_relation"]
            new_doc["causal_relations"] = doc["causal_relation"]
            new_doc["subevent_relations"] = doc["subevent_relation"]
            select_list.append(new_doc)
        else:
            select_list.append(doc)

    # instruction
    with open(inst_file, "r", encoding="utf-8") as reader:
        INST = json.load(reader)
        reader.close()

    # 获得原始数据
    init_dataset = get_initdataset(select_list, config)
    example_dataset = []
    if "test" in split:
        train_select_list = []
        with open(input_folder.joinpath("train.jsonl"), "r") as file:
            load_file = file.readlines()
        sel_idx = list(range(len(load_file)))
        random.shuffle(sel_idx)
        for i in sel_idx[0:number]:
            doc = json.loads(load_file[i].strip())
            train_select_list.append(doc)
        example_dataset = get_exampledata(train_select_list, config)
    else:
        example_dataset = get_exampledata(select_list, config)
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理原始数据
    na_data = 0
    out_file = open(output_folder.joinpath(f"{split}.jsonl"), "w")
    for i, vert in enumerate(init_dataset):
        # instruction & options
        instruction, na = get_instruction(INST[R_Inst[vert["btype"]]])
        options = OPTIONS[vert["btype"]].split(", ")
        new_options = []
        if len(options) > 2:
            for op in options:
                flag = (int)(random.random() > config["CLASS_DROPOUT_RATE"])
                if flag == 1:
                    new_options.append(op)
        else:
            new_options = options

        REP_Flag = (int)(random.random() < 0.7)
        if REP_Flag:
            if "<event1>" in instruction:
                instruction = instruction.replace(
                    "<event1>", '"' + vert["first"][0] + '"'
                )
            if "<event2>" in instruction:
                instruction = instruction.replace(
                    "<event2>", '"' + vert["second"][0] + '"'
                )

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
                    if args not in new_options:
                        new_options.append(args)
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
        # if OPT_Flag!=-1 and OPT_Flag<4:
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
        HistoryData = random.sample(
            example_dataset[vert["btype"]],
            min(config["NUM_FEWSHOT_Limit"], len(example_dataset[vert["btype"]])),
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
        if DESC_Flag:
            l = range(0, len(new_options))
            desc = random.sample(
                l, min(config["LIMIT_DESC"], len(l))
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

        out_file.write(json.dumps(unified_instance) + "\n")

        if unified_instance["reference"] == []:
            na_data += 1
        else:
            if i < 50:
                print("============== CASE: ", split, i, "====================")
                print(unified_instance)

    print("na_data:", na_data)
    print("valid_data:", len(init_dataset) - na_data)

    out_file.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MAVEN-ERE")
    # I/O
    parser.add_argument(
        "--input_dir",
        type=str,
        default="../../../data/MAVEN-ERE",
    )
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data/MAVEN-ERE-MoreDoc"
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

    parser.add_argument("--big_type_rate", type=float, default=0.05)

    parser.add_argument("--class_dropout_rate", type=float, default=0.1)
    parser.add_argument("--diverse_options", type=bool, default=True)
    parser.add_argument("--explain_rate", type=float, default=0.2)
    parser.add_argument(
        "--limit_sample_relation",
        type=int,
        default=1000,
        help="To balance the relations in training set.",
    )  # 限制每一种relation在训练集中的最大个数，防止例如before占比90%，其他占比极小
    parser.add_argument(
        "--limit_relation",
        type=int,
        default=5000,
        help="To balance the relations in training set.",
    )  # 限制每一种relation在训练集中的最大个数，防止例如before占比90%，其他占比极小

    parser.add_argument("--num_fewshot_limit", type=int, default=8)
    parser.add_argument("--WORD_Limit", type=int, default=1200)
    parser.add_argument("--fewshot_na_rate", type=float, default=0.2)
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
        # b-s type
        "BIG_TYPE": args.big_type_rate,
        # args
        "CLASS_DROPOUT_RATE": args.class_dropout_rate,
        "UNCOMPELETE_OPTION": args.diverse_options,
        "Limit_REL": args.limit_relation,
        "limit_sample_relation": args.limit_sample_relation,
        # explain相关
        "EXPLAIN_RATE": args.explain_rate,
        # few-shot相关
        "NUM_FEWSHOT_Limit": args.num_fewshot_limit,
        "WORD_Limit": args.WORD_Limit,
        "EXAM_NA_RATE": args.fewshot_na_rate,
        "infFormat_rate": args.infFormat_rate,
        "SymbolLabels": args.SymbolLabels,
    }

    output_folder.mkdir(exist_ok=True, parents=True)
    make_eval_data(
        input_folder, output_folder, inst_file, "train", 1000, config, "random"
    )
    # make_eval_data(input_folder,output_folder,inst_file,'test', 100,config,"random")
