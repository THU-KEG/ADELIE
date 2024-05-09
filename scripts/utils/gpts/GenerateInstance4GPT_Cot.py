import jsonlines
import json
import argparse
import random
from PromptCot import Prompt,Content,Demo


def get_input(d,rate=0.7):
    instruction=d["instruction"]
    instruction+=d["query"][1]

    text_Flag=False
    if "<text>" in instruction:
        id=(int)(random.random()<=rate)
        if id:
            instruction=instruction.replace("<text>","Text: '"+d["input"]+"'")
            text_Flag=True

    if text_Flag==False:
        input="Text: '"+d["input"]+"'"
        return instruction+" "+input
    else:
        input=""
        return instruction

def get_output(d):
    output=d["output"]
    output=output.split("[Answer]: ")[1]
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="generate")
    # I/O
    parser.add_argument("--input_file", type=str, default="../../../unified_data/other_rc/train.jsonl")
    parser.add_argument("--except_file", type=str, default="../../../unified_data/other_rc/ExplanationIdx.txt")
    parser.add_argument("--output_file", type=str, default="../../../unified_data/other_rc/gpt4cot.jsonl")
    parser.add_argument("--k", type=str, default=500)

    args = parser.parse_args()

    filename=args.input_file
    words_num=random.randint(70,170)
    data={
        "prompt": {
            "instructions": Prompt.format(words_number=words_num),
            "input_prefix": "",
            "input_suffix": "",
            "output_prefix": "",
            "output_suffix": "",
            "demonstrations": Demo,
        },
        "request_states": []
    }
    print(data)

    with open(args.except_file, "r", encoding='utf-8') as reader:
        except_idx=reader.readlines()
        reader.close()

    for i,vert in enumerate(except_idx):
        except_idx[i]=vert[:-1]
    
    # print(except_idx)

    ex_data=[]
    with open(filename, "r", encoding='utf-8') as reader:
        for item in jsonlines.Reader(reader):
            if item["id"] not in except_idx and str(item["id"]) not in except_idx: 
                if item["query"][0]==1:
                    ex_data.append(item)
            # else:
            #     print("in",item["id"])
        reader.close()
    
    print("num of all query=1 data:",len(ex_data))
    k=args.k
    print("num of select:",k)
    ex_data=random.sample(ex_data,k)


    for vert in ex_data:
        unified_data={
            "ori_instance": vert,
            "instance": {
                "input": {
                    "text": Content.format(input=get_input(vert),output=get_output(vert))
                },
                "question_type": 1,
                "id": vert["id"]
            },
            "request": {
                "result": {
                    "success": False,
                    "completions": [
                        {
                            "text": ""
                        }
                    ]
                },
                "request_time": 0,
                "request_datetime": 1
            }
        }
        data["request_states"].append(unified_data)

    json.dump(data, open(args.output_file, "w"), indent=4)