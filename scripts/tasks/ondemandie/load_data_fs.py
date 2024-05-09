#from ph_unified_data:
import os
import json
import random
import copy
from pathlib import Path

EXPLAN_QUERY=[
    "First explain your thoughts and then give the answer. ",
    "Please give the analysis first. ",
    "Please explain first. ",
    "Make analysis according to the sentence and give the answer. "
]


def construct_response(input_folder,output_folder,split,config):

    input_path=os.path.join(input_folder,split+".json")
    with open(input_path, "r", encoding='utf-8') as reader:
        init_dataset = json.load(reader)
        reader.close()


    #获得example数据
    if config["IsCoT"] == False:
        tinput_path=os.path.join(input_folder,"training_data.json")
    else:
        tinput_path=os.path.join(input_folder,"training_data_cot.json")
    example_dataset = []
    with open(tinput_path, "r", encoding='utf-8') as reader:
        example_dataset = json.load(reader)
        reader.close()
    


    # 处理原始数据
    unified_dataset=[]
    fewshot_num=0
    for i,vert in enumerate(init_dataset):
        unified_instance={
            "instruction":vert["instruction"]+"\n",
            "input":"Text: "+vert["text"],
            "output":"[Answer]: "+vert["table"],
            "system":"You are a helpful assistant. Follow the user instruction to extract information from the given text into a concise markdown table.",
            "history":[]
        }
        if config["IsCoT"] == True:
            ex_q=random.sample(EXPLAN_QUERY,1)[0]
            unified_instance["instruction"]+=ex_q
            unified_instance["output"]="[Explanation]: "+vert["explanation"]+"\n[Answer]: "+vert["table"]

        #examples
        HistoryData=random.sample(example_dataset,config["NUM_FEWSHOT_Limit"])
        origin_word=unified_instance["instruction"].split(" ")+unified_instance["input"].split(" ")
        total_word=len(origin_word)
        for hd in HistoryData:
            if hd==vert:
                continue
            if total_word>config["WORD_Limit"]:
                break
            
            input=hd["instruction"]+"\n"+"Text: "+hd["text"]
            if config["IsCoT"]:
                output="[Explanation]: "+hd["explanation"]+"\n[Answer]: "+hd["table"]
            else:
                output="[Answer]: "+hd["table"]
            
            word=input.split(" ")+output.split(" ")
            total_word+=len(word)
            if total_word>config["WORD_Limit"]:
                break
            fewshot_num+=1
            unified_instance["history"].append([input,output])
        unified_dataset.append(unified_instance)

    fewshot_num/=len(unified_dataset)
    print("fewshot_avg:",fewshot_num)
    if "train" in split:
        if config["IsCoT"] == False:
            out_name=split+"_"+str(config["NUM_FEWSHOT_Limit"])+"shot.jsonl"
        else:
            out_name=split+"_"+str(config["NUM_FEWSHOT_Limit"])+"shotCoT.jsonl"
        out_file = open(os.path.join(output_folder,out_name), "w")
        for vert in unified_dataset:
            out_file.write(json.dumps(vert) + "\n")
        out_file.close()
    else:
        out_name="ondemand.json"
        out_file = open(os.path.join(output_folder,out_name), "w")
        json.dump(unified_dataset,out_file,indent=2)
        out_file.close()
    
    print("total:",len(unified_dataset))


if __name__ == "__main__":
    input_folder=Path("../data/ondemandIE")
    output_folder = Path("../unified_data/ondemandIE")
    # args
    config={
        #COT
        "IsCoT":False,
        #few-shot相关
        "NUM_FEWSHOT_Limit":0,
        "WORD_Limit":2000,
        "EXAM_NA_RATE":0.0
    }
    output_folder.mkdir(exist_ok=True, parents=True)
    construct_response(input_folder, output_folder, "training_data",config)
    config["IsCoT"]=True
    construct_response(input_folder, output_folder, "training_data_cot",config)
    config["IsCoT"]=False
    construct_response(input_folder, output_folder, "test_data",config)
