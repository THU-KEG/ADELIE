import pyarrow as pa
import pyarrow.parquet as pq
import os
import json
import random
from pathlib import Path

def construct_response(input_folder,output_folder,split):
    path_list=os.listdir(input_folder)
    df=[]
    for filename in path_list:
        df.append(pq.read_table(os.path.join(input_folder,filename)).to_pandas())
    
    out_file = open(os.path.join(output_folder,split+".jsonl"), "w")
    count=0
    for data in df:
        l=len(data)
        for i in range(0,l):
            count+=1
            lst=data.iloc[i]["messages"]
            # unified_instance = {
            #     "instruction":lst[0]["content"],
            #     "input":"",
            #     "output":lst[1]["content"],
            #     "history":[]
            # }
            unified_instance = {
                "dataset": data.iloc[i]["dataset"],
                "id": data.iloc[i]["id"],
                "messages": list(data.iloc[i]["messages"])
            }
            # print(unified_instance)
            out_file.write(json.dumps(unified_instance) + "\n")
    print("total num of instance:",count)
    out_file.close()


if __name__ == "__main__":
    input_folder=Path("../data/General/tuluv2")
    output_folder = Path("../unified_data/tuluv2")
    output_folder.mkdir(exist_ok=True, parents=True)
    construct_response(input_folder, output_folder, "train")