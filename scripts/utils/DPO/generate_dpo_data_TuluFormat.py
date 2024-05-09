import random
import json
import jsonlines
import os
from pathlib import Path
import argparse
import re

from ref_query import QUERY

data = dict()  # {dataset_name:[datas]}
filter_count = dict()

EXPLAN_QUERY = [
    "First explain your thoughts and then give the answer. ",
    "Please give the analysis first. ",
    "Please explain first. ",
    "Make analysis according to the sentence and give the answer. ",
]

EXPLAN_QUERY_COT = [
    "First explain your thoughts step-by-step and then give the answer. ",
    "Please give the step-by-step analysis first. ",
    "Please generate a step-by-step explanation first. ",
    "Make step-by-step analysis according to the sentence and give the answer. ",
]


def get_normal_instruction(d, dirname, args, rate=0.7):
    instruction = d["instruction"]
    # print("===================")
    # print(args)
    # print(type(args.Explanation_filter))
    if args.Explanation_filter == 0:
        if d["query"][0] == 1:
            ex_q = random.sample(EXPLAN_QUERY, 1)[0]
            instruction += ex_q
        if d["query"][0] == 2:
            ex_q = random.sample(EXPLAN_QUERY_COT, 1)[0]
            instruction += ex_q
    instruction += QUERY[dirname][0]

    text_Flag = False
    if "<text>" in instruction:
        id = (int)(random.random() <= rate)
        if id:
            instruction = instruction.replace("<text>", "Text: '" + d["input"] + "'")
            text_Flag = True

    if text_Flag == False:
        input = "Text: '" + d["input"] + "'"
        return instruction, input
    else:
        input = ""
        return instruction, input


def get_output(output, ref, args):
    explain = output.split("[Answer]: ")[0]
    cur_output = output.split("[Answer]: ")[1]
    if args.Explanation_filter == 0:
        output = explain
    output += "[Answer]: " + str(ref)
    if ref == "":
        output += "NA"
    output = output.strip()
    return output


def get_ref(ref):  # 仅限ondemandie
    pattern = re.compile("\((.*); (.*); (.*); (.*); (.*)\)")
    triple = re.findall(pattern, ref)
    if len(triple) == 0:
        ref = ""
    else:
        ref = ""
        # print("======== triple ===========:", triple)
        for t in triple:
            l = []
            for value in t:
                if value != "None":
                    l.append(value)
            ref += "(" + "; ".join(l) + "); \n"
        # print("======== dref ===========:", ref)
    return ref


def reformat(d, name, args):
    word_Limit = args.WORD_Limit
    messages = []

    if name == "openie4":
        d["reference"] = get_ref(d["reference"])

    if "query" in d:
        instruction, input = get_normal_instruction(d, name, args)
        d["output"] = get_output(d["output"], d["reference"], args).strip()
    else:  # ondemandie
        instruction, input = d["instruction"], d["input"]

    if input is not None and input.strip() != "":
        prompt = instruction.strip() + "\n" + input.strip()
    else:
        prompt = instruction.strip()

    if "system" in d:
        messages.append({"role": "system", "content": d["system"]})

    isFew_infer = (int)(random.random() < args.Few_format2_rate)
    if isFew_infer and "examples" in d and d["query"][0] != 2:  # few-shot-infer
        instruction, input = get_normal_instruction(d, name, args, 0)
        instruction = instruction.strip() + "\n"

        numFew = random.randint(1, len(d["examples"]))
        if numFew:
            origin_word = (
                instruction.split(" ") + input.split(" ") + d["output"].split(" ")
            )
            total_word = len(origin_word)
            HIS_Flag = False
            for i, vert in enumerate(d["examples"]):
                if i + 1 > numFew:
                    break
                if total_word > word_Limit:
                    break

                if name == "openie4":
                    vert[2] = get_ref(vert[2])

                if name != "ee" and name != "re" and name != "other_rc":
                    if (
                        vert[2] == "NA"
                        or vert[2] == "[]"
                        or vert[2] == ""
                        or vert[2] == []
                        or vert[2] == "none"
                    ):  # fewshot中na数据处理
                        NA_Flag = (int)(random.random() < args.Fewshot_na_rate)
                        if NA_Flag == False:
                            filter_count[name] += 1
                            continue

                vert[1] = get_output(vert[1], vert[2], args)

                word = vert[0].split(" ") + vert[1].split(" ")
                total_word += len(word)
                if total_word > word_Limit:
                    break
                # 满足字数要求
                if HIS_Flag == False:
                    messages.append(
                        {
                            "role": "user",
                            "content": instruction + "\nText: '" + vert[0] + "'",
                        }
                    )
                    messages.append({"role": "assistant", "content": vert[1]})
                    HIS_Flag = True
                else:
                    messages.append(
                        {"role": "user", "content": "Text: '" + vert[0] + "'"}
                    )
                    messages.append({"role": "assistant", "content": vert[1]})

            # 未满足字数要求
            if HIS_Flag == False:
                messages.append({"role": "user", "content": instruction + "\n" + input})
                messages.append(
                    {
                        "role": "assistant",
                        "content": d["output"],
                    }
                )
            else:  # 满足字数要求
                messages.append({"role": "user", "content": input})
                messages.append(
                    {
                        "role": "assistant",
                        "content": d["output"],
                    }
                )
    else:
        messages.append({"role": "user", "content": prompt})
        messages.append(
            {
                "role": "assistant",
                "content": d["output"],
            }
        )

    unified_data = {"dataset": name, "id": str(d["id"]), "messages": messages}

    word = 0
    for mes in messages:
        word += len(mes["content"].split(" "))
    if word > word_Limit:
        filter_count[name + "_ori"] += 1
        return None
    else:
        return unified_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="mixture")

    parser.add_argument("--unified_data_dir", type=str)
    parser.add_argument("--hold_in_datasets", type=str, nargs="+", default=[])
    parser.add_argument("--ondemandIE_dir", type=str, default="")
    parser.add_argument("--general_training_file", type=str, default="")
    parser.add_argument("--version", type=str)

    parser.add_argument("--Limit_total_data", type=int, default=0)
    parser.add_argument("--General_rate", type=float, default=-1)
    parser.add_argument(
        "--Limit_dataset",
        type=int,
        default=10000,
        help="each dataset max sample number",
    )
    parser.add_argument(
        "--Limit_General",
        type=int,
        default=300000,
        help="general dataset max sample number",
    )
    parser.add_argument("--WORD_Limit", type=int, default=1500, help="cut off")
    parser.add_argument(
        "--Few_format1_rate",
        type=float,
        default=0.0,
        help="format1:instruct(x1)+y1+instruct(x2)+y2+..+instruct(x)+y",
    )
    parser.add_argument(
        "--Few_format2_rate",
        type=float,
        default=0.5,
        help="format2:instruct+x1+y1+x2+y2+..+x+y",
    )
    parser.add_argument("--Fewshot_na_rate", type=float, default=0.1)
    parser.add_argument("--ondemand_cot_rate", type=float, default=0.3)
    parser.add_argument(
        "--general_filter", type=int, default=0
    )  # 是否过滤genral数据中word字数多余limit的数据

    parser.add_argument(
        "--GenerateGPTDatas", type=int, default=1
    )  # 是否采用GPT生成的数据
    parser.add_argument(
        "--reserve_all_gptdata", type=int, default=1
    )  # 是否选择采样全部的GPT数据

    parser.add_argument(
        "--Explanation_filter", type=int, default=0
    )  # 是否过滤全部的explanation数据

    args = parser.parse_args()
    # print(args.Explanation_filter)

    path = args.unified_data_dir

    names = []
    sum_data = 0
    count_gpt_data = dict()
    for dirname in args.hold_in_datasets:
        except_idx = []
        data[dirname] = []
        count_gpt_data[dirname] = 0
        names.append(dirname)

        if args.GenerateGPTDatas == 1:
            # explanation
            except_file = os.path.join(path, dirname, "ExplanationIdx.txt")
            with open(except_file, "r", encoding="utf-8") as reader:
                except_idx = reader.readlines()
                reader.close()
            # print("1. len(except_file):", len(except_idx), except_idx[-1])
            filename = os.path.join(path, dirname, "gpt4explanation_post.jsonl")
            with open(filename, "r", encoding="utf-8") as reader:
                for item in jsonlines.Reader(reader):
                    if "incorrectly" in item["output"]:
                        continue
                    data[dirname].append(item)
                reader.close()
            # cot
            except_file = os.path.join(path, dirname, "CotIdx.txt")
            with open(except_file, "r", encoding="utf-8") as reader:
                except_idx.extend(reader.readlines())
                reader.close()
            # print("2. len(except_file):", len(except_idx), except_idx[-1])

            filename = os.path.join(path, dirname, "gpt4cot_post.jsonl")
            with open(filename, "r", encoding="utf-8") as reader:
                for item in jsonlines.Reader(reader):
                    if "incorrectly" in item["output"]:
                        continue
                    data[dirname].append(item)
                reader.close()

            for i, vert in enumerate(except_idx):
                except_idx[i] = vert[:-1]

            count_gpt_data[dirname] = len(data[dirname])

        try:
            filename = os.path.join(path, dirname, "after_filter_train.jsonl")
            with open(filename, "r", encoding="utf-8") as reader:
                for item in jsonlines.Reader(reader):
                    if (
                        item["id"] not in except_idx
                        and str(item["id"]) not in except_idx
                    ):
                        data[dirname].append(item)
                reader.close()
            print("hold_in_file:", filename, len(data[dirname]))
        except:
            filename = os.path.join(path, dirname, "train.jsonl")
            if "openie" in dirname:
                filename = os.path.join(path, dirname, "openie4_labels.jsonl")
            with open(filename, "r", encoding="utf-8") as reader:
                for item in jsonlines.Reader(reader):
                    if (
                        item["id"] not in except_idx
                        and str(item["id"]) not in except_idx
                    ):
                        data[dirname].append(item)
                reader.close()
            print("hold_in_file:", filename, len(data[dirname]))

    # ondemand: 取一半cot的数据一半no cot的数据
    if args.ondemandIE_dir != "":
        count_gpt_data["ondemand"] = 0
        path_list = os.listdir(args.ondemandIE_dir)
        data["ondemand"] = []
        names.append("ondemand")
        First = False
        rate = args.ondemand_cot_rate
        for filename in path_list:
            if "train" in filename:
                if First == False:
                    if "cot" not in filename:
                        rate = 1 - rate
                cnt = -1
                cnt1 = 0
                cnt2 = 0
                filename = os.path.join(args.ondemandIE_dir, filename)
                with open(filename, "r", encoding="utf-8") as reader:
                    for item in jsonlines.Reader(reader):
                        cnt += 1
                        if First == False:
                            data["ondemand"].append(item)
                            data["ondemand"][cnt]["id"] = cnt
                        else:
                            if cnt >= len(data["ondemand"]) * rate - 1:
                                if cnt >= len(data["ondemand"]):
                                    data["ondemand"].append(item)
                                else:
                                    data["ondemand"][cnt] = item
                                cnt2 += 1
                            else:
                                cnt1 += 1
                            data["ondemand"][cnt]["id"] = cnt
                    reader.close()
                if First == True:
                    print("first_rate:", rate)
                    print("second file:", filename)
                    print("hold_in_file: ondemandIE", cnt1, cnt2)
                First = True

    # 其他数据集处理

    mix = []
    count = dict()

    for i, name in enumerate(names):
        filter_count[name] = 0
        filter_count[name + "_ori"] = 0
        if args.reserve_all_gptdata == 1:  # 保留全部的gpt数据
            print("Sample all gpt data.")
            if count_gpt_data[name] > args.Limit_dataset:
                print(
                    "~~~~~~~~~ Error: Extend Limit_dataset ~~~~~~~~ :",
                    count_gpt_data[name],
                    args.Limit_dataset,
                )
            sampledata = data[name][: count_gpt_data[name]]
            countt = min(args.Limit_dataset, len(data[name])) - count_gpt_data[name]
            sampledata.extend(random.sample(data[name][count_gpt_data[name] :], countt))
        else:
            countt = min(args.Limit_dataset, len(data[name]))
            sampledata = random.sample(data[name], countt)
        random.shuffle(sampledata)
        count[name] = 0
        for j, vert in enumerate(sampledata):
            vert = reformat(vert, name, args)
            if vert != None:
                # print("==========CASE ", name, j, "=================")
                if j < 3:
                    print("==========CASE ", name, j, "=================")
                    print(vert)
                mix.append(vert)
                count[name] += 1

    random.shuffle(mix)

    total = len(mix)

    output_folder = Path(os.path.join(path, "train_mixture"))
    output_folder.mkdir(exist_ok=True, parents=True)

    print(
        "Mixture saves at:",
        os.path.join(output_folder, "mix_v" + args.version + ".jsonl"),
    )
    out_file = open(
        os.path.join(output_folder, "mix_v" + args.version + ".jsonl"),
        "w",
        encoding="utf-8",
    )  ###########################
    for vert in mix:
        out_file.write(json.dumps(vert) + "\n")
    # json.dump(mix, out_file, indent=2)
    out_file.close()

    out_file = open(
        os.path.join(output_folder, "mix_filter_v" + args.version + ".json"),
        "w",
        encoding="utf-8",
    )  ###########################
    json.dump(filter_count, out_file, indent=2)
    out_file.close()

    out_file = open(
        os.path.join(output_folder, "mix_info_v" + args.version + ".txt"),
        "w",
        encoding="utf-8",
    )  ###########################
    for i in range(len(names)):
        print(
            "dataset：%s\tnumber: %d/%d=%.4f"
            % (names[i], count[names[i]], total, count[names[i]] / total),
            file=out_file,
        )
    # print(
    #     "dataset：%s\tnumber: %d/%d=%.4f"
    #     % ("general", count["general"], total, count["general"] / total),
    #     file=out_file,
    # )
    out_file.close()
