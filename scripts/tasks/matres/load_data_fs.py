# 将所有的事件都在文档中标明
import json
from pathlib import Path
import random
import argparse

OPTIONS = {
    "MATRES": "before, after, equal, vague, none",
    "MAVEN-ERE-temporal_event_relation": "before, overlap, contains, simultaneous, begins-on, ends-on",
    "MAVEN-ERE-causal_relation": "cause, precondition",
    "MAVEN-ERE-coreference_relation": "coreference",
    "MAVEN-ERE-subevent_relation": "subevent",
}
REL = {
    "before": "@ occurs before $. ",  # A..B
    "after": "@ occurs after $. ",  # A..B
    "equal": "@ and $ occur simultaneously. ",
    "vague": "There is a relation between @ and $ but we are not sure of its temporal order. ",
    "none": "There is no temporal relation between @ and $. ",
}
OUTPUT_BASE = [
    (
        'Please give the answer in the tuple form "[Answer]: ({first event}; {relation}; {second event});".',
        "({head}; {type}; {tail}); ",
    ),
    (
        "Please tell me what is the relationship between the two events? ",
        'first event is "{head}", second event is "{tail}", the relation is "{type}". ',
    ),
    (
        'Please give the answer in the tuple form "[Answer]: (first event: {head}; relation: {type}; second event: {tail}); ".',
        "(first event: {head}; relation: {type}; second event: {tail}); ",
    ),
    (
        'Please give the answer in the tuple form "[Answer]: (head: {head}; relation: {type}; tail: {tail}); ".',
        "(head: {head}; relation: {type}; tail: {tail}); ",
    ),
    (
        "Please give the answer in natural language.",
        'the head event is "{head}", the tail event is "{tail}", and the relation between them is "{type}".',
    ),
]
OUTPUT_EXPLAN = [
    'The two events are "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"). ',
    'Two events, "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"), are recognized. ',
    'The identified events are "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"). ',
    'In the context of event relation extraction, the two events are identified as "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"). ',
    'The events "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}") have been distinguished. ',
]


import json
from pathlib import Path


def get_instruction(inst):
    instruction_list = random.sample(inst, 1)
    return instruction_list[0][0], instruction_list[0][1]


def deal_data(doc):
    events = doc["events"]
    relations = doc["relations"]
    rel_dict = {}
    for event in events:
        try:  # some train documents' event does not have eiid
            rel_dict[event["eiid"]] = {}
        except:
            return events, rel_dict, -1, ""
        for event2 in events:
            try:
                rel_dict[event["eiid"]][event2["eiid"]] = "none"
            except:
                return events, rel_dict, -1, ""
    for rel_name in relations.keys():
        rel_list = relations[rel_name]
        for rel in rel_list:
            rel_dict[rel[0]][rel[1]] = rel_name.lower()
    num_event = len(events)
    text = doc["text"]
    return events, rel_dict, num_event, text


# Annotate the two events in the text
def annotate(text, event1, event2):
    sent_id1 = event1["sent_id"]
    offset1 = event1["offset"]
    sent_id2 = event2["sent_id"]
    offset2 = event2["offset"]
    work_sents = []

    for sent_id, sent in enumerate(text):
        if sent_id1 != sent_id and sent_id2 != sent_id:
            work_sents.append(sent)
        else:
            if sent_id1 == sent_id and sent_id2 != sent_id:
                work_sents.append(
                    f"{sent[0:offset1[0]]}<Event> {sent[offset1[0]:offset1[1]]} </Event>{sent[offset1[1]:]}"
                )
                event_name1 = f"<Event> {sent[offset1[0]:offset1[1]]} </Event>"
            elif sent_id2 == sent_id and sent_id1 != sent_id:
                work_sents.append(
                    f"{sent[0:offset2[0]]}<Event> {sent[offset2[0]:offset2[1]]} </Event>{sent[offset2[1]:]}"
                )
                event_name2 = f"<Event> {sent[offset2[0]:offset2[1]]} </Event>"
            else:
                assert (offset1[1] <= offset2[0]) or (offset1[0] >= offset2[1])
                if offset1[1] <= offset2[0]:
                    work_sent = f"{sent[0:offset1[0]]}<Event> {sent[offset1[0]:offset1[1]]} </Event>{sent[offset1[1]:offset2[0]]}"
                    work_sent += f"<Event> {sent[offset2[0]:offset2[1]]} </Event>{sent[offset2[1]:]}"
                    work_sents.append(work_sent)
                else:
                    work_sent = f"{sent[0:offset2[0]]}<Event> {sent[offset2[0]:offset2[1]]} </Event>{sent[offset2[1]:offset1[0]]}"
                    work_sent += f"<Event> {sent[offset1[0]:offset1[1]]} </Event>{sent[offset1[1]:]}"
                    work_sents.append(work_sent)
                event_name1 = f"<Event> {sent[offset1[0]:offset1[1]]} </Event>"
                event_name2 = f"<Event> {sent[offset2[0]:offset2[1]]} </Event>"
    return " ".join(work_sents), event_name1, event_name2


def get_initdataset(raw_data, Example_Flag, config):
    init_dataset = []
    count_rel = {}
    for doc_idx, data in enumerate(raw_data):
        doc = json.loads(data)
        events, rel_dict, num_event, text = deal_data(doc)
        if num_event == -1:
            continue
        cnt = 0
        for i in range(num_event):
            for j in range(i + 1, num_event):
                query, event_name1, event_name2 = annotate(text, events[i], events[j])
                event_name1 = event_name1.split(" ")[1]
                event_name2 = event_name2.split(" ")[1]
                query = f"Document:\n{query}\n\n"
                query += (
                    f"The first event: {event_name1}\nThe second event: {event_name2}\n"
                )
                label = rel_dict[events[i]["eiid"]][events[j]["eiid"]]
                label2 = rel_dict[events[j]["eiid"]][events[i]["eiid"]]
                assert label2 == "none"

                init_data = {
                    "input": query,
                    "head": event_name1,
                    "tail": event_name2,
                    "explain_arg": [],
                }
                if label != "none":
                    init_data["explain_arg"].append(
                        (
                            label,
                            event_name1,
                            events[i]["class"],
                            event_name2,
                            events[j]["class"],
                        )
                    )
                if Example_Flag == True:
                    if label not in count_rel:
                        count_rel[label] = 0
                    count_rel[label] += 1
                    if count_rel[label] <= config["limit_sample_relation"]:
                        init_dataset.append(init_data)
                else:
                    init_dataset.append(init_data)
    print("example_count:", config)
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
        for args in new_args:
            response_base += base_tem[1].format(
                head=args[1], tail=args[3], type=args[0]
            )
            response = explain_tem.format(
                e1=args[1], t1=args[2], e2=args[3], t2=args[4]
            )
            r = REL[args[0]].replace("@", args[1])
            r = r.replace("$", args[2])
            response += r
            ref = args[0]

    response += response_base

    if ExFlag:
        return ref, response
    else:
        return ref, response_base


def make_eval_data(input_folder, output_folder, inst_file, split, config):
    if "test" in split:
        config["CLASS_DROPOUT_RATE"] = 0
        config["ALL_DESC"] = 0
        config["BIG_TYPE"] = 0
        # ?
        config["DESC_RATE"] = 0
        config["EXPLAIN_RATE"] = 0
        config["Limit_REL"] = 10000000
        config["limit_sample_relation"] = 10000000

    with open(input_folder.joinpath(split + ".json"), "r") as file:
        raw_data = file.readlines()

    # instruction
    with open(inst_file, "r", encoding="utf-8") as reader:
        inst = json.load(reader)
        reader.close()
    inst = inst["ERE-Temporal"]

    options = OPTIONS["MATRES"].split(", ")

    # 获得原始数据
    init_dataset = get_initdataset(raw_data, False, config)
    example_dataset = []
    if "test" in split:
        with open(input_folder.joinpath("train.json"), "r") as file:
            train_raw_data = file.readlines()
        example_dataset = get_initdataset(train_raw_data, True, config)
    else:
        example_dataset = get_initdataset(raw_data, True, config)
    example_dataset = get_valid_datasets(example_dataset, config)

    # 处理init-data
    out_file = open(output_folder.joinpath(f"{split}.jsonl"), "w")
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

        REP_Flag = (int)(random.random() < 0.7)
        if REP_Flag:
            if "<event1>" in instruction:
                instruction = instruction.replace("<event1>", '"' + vert["head"] + '"')
            if "<event2>" in instruction:
                instruction = instruction.replace("<event2>", '"' + vert["tail"] + '"')

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

        # if i<10:
        #     print("============== CASE: ",split,i,"====================")
        #     print(unified_instance)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="MATRES")
    # I/O
    parser.add_argument("--input_dir", type=str, default="../../../data/MATRES")
    parser.add_argument(
        "--output_dir", type=str, default="../../../unified_data/MATRES"
    )
    parser.add_argument("--instruction_file", type=str, default="../instructions.json")

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
    parser.add_argument(
        "--limit_sample_relation",
        type=int,
        default=200,
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
        "Limit_REL": args.limit_relation,
        # explain相关
        "EXPLAIN_RATE": args.explain_rate,
        # few-shot相关
        "NUM_FEWSHOT_Limit": args.num_fewshot_limit,
        "WORD_Limit": args.WORD_Limit,
        "EXAM_NA_RATE": args.fewshot_na_rate,
    }

    output_folder.mkdir(exist_ok=True, parents=True)
    # make_eval_data('train',config)
    make_eval_data(input_folder, output_folder, inst_file, "test", config)
