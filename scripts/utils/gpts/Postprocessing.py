import json
import jsonlines
import argparse
import re


def get_output(d):
    output = d["output"]
    output = output.split("[Answer]: ")[1]
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="generate")
    # I/O
    parser.add_argument(
        "--input_file",
        type=str,
        default="../../../unified_data/openie4/gpt4cot.jsonl",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="../../../unified_data/openie4/gpt4cot_post.jsonl",
    )

    args = parser.parse_args()

    with open(args.input_file, "r") as f:
        data = json.load(f)
        f.close()

    out_file = open(args.output_file, "w", encoding="utf-8")
    for vert in data["request_states"]:
        ori = vert["ori_instance"]
        output = get_output(ori)
        result = vert["request"]["result"]["completions"][0]["text"]
        if "[Step-by-Step Explanation]:" in result:
            result = result.split("[Step-by-Step Explanation]:")[1].strip()
        if 'Explanation":' in result:
            print("================= need postprocess =================")
            print(result)
            try:
                pattern = r"{[^{}]*}"
                matches = re.findall(pattern, result)
                d = eval(matches[0])
                result = str(d["Step-by-Step Explanation"])
            except:
                print("==== check =====")
                result = result.split('Explanation":')[1].strip()
            # result=result["Explanation"]
            print(ori["id"])
            print(result)
        ori["output"] = "[Step-by-Step Explanation]: " + result + " [Answer]: " + output
        ori["query"][0] = 2
        out_file.write(json.dumps(ori) + "\n")
    out_file.close()
