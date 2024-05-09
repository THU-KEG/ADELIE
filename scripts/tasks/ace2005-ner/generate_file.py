import os
import json
import random
from pathlib import Path

def generate(input_folder,output_folder,split):
    input_path=os.path.join(input_folder,split+".json")
    with open(input_path) as f:
        data = json.load(f)

    files=set()
    for instance in data:
        files.add(instance["file"])
    
    out_file = open(os.path.join(output_folder,split+".txt"), "w")
    for vert in files:
        out_file.write(vert + "\n")


if __name__ == "__main__":
    input_folder=Path("../../data/Event Extraction/ace2005-en")
    output_folder = Path("/home/qijy/workspace/Alignment_on_IE_tasks/GoLLIE-main/data/ace05/splits")

    generate(input_folder, output_folder, "train")
    generate(input_folder, output_folder, "test")