import json
import jsonlines
import argparse

if __name__ == '__main__':
    idx=set()
    parser = argparse.ArgumentParser(description="generate")
    # I/O
    parser.add_argument("--input_file", type=str, default="../../../unified_data/RAMS-eae/gpt4cot.jsonl")
    parser.add_argument("--output_file", type=str, default="../../../unified_data/RAMS-eae/CotIdx.txt")
    args = parser.parse_args()


    with open(args.input_file, 'r') as f:
        data = json.load(f)
        f.close()

    for vert in data["request_states"]:
        idx.add(vert["instance"]["id"])
    
    with open(args.output_file, 'w') as f:
        for vert in idx:
            f.write(str(vert)+"\n")
        f.close()