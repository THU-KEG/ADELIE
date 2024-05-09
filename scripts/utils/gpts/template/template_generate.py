from openai import OpenAI
import os
import json
import time
import math
import requests
from pathlib import Path
from tqdm import tqdm
import argparse
from multiprocessing import Pool, Lock

# from desc import OUTPUT_BASE,OUTPUT_EXPLAN,PROMPT
from desc4openie import *
import random
import re
import pprint

api_key_pool = [  # your api pool
    ""
    # "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"
]


def query_openai_api_per_example(
    api_key, args, model, sleep_second, max_tokens, demonstrations=None
):
    # print(api_key)
    client = OpenAI(
        # This is the default and can be omitted
        api_key=api_key,
    )

    Prompt = PROMPT
    demo_answer = random.sample(OUTPUT_BASE, 3)
    demo_explain = random.sample(OUTPUT_EXPLAN, 3)
    demo_inst = random.sample(INST["OPENIE"], 3)
    demos = []
    for vert in demo_answer:
        # d={
        #     "input template":vert[0],
        #     "answer template":vert[1],
        #     "explanation template":""
        # }
        d = {
            "instruction": "",
            "fail output": "",
            "input template": vert[0],
            "answer template": vert[1],
            "explanation template": "",
        }
        demos.append(d)

    for i, vert in enumerate(demo_explain):
        demos[i]["explanation template"] = vert
    for i, vert in enumerate(demo_inst):
        demos[i]["instruction"] = vert[0]
        demos[i]["fail output"] = vert[1]

    for i, vert in enumerate(demos):
        Prompt += f"Template {i}: " + json.dumps(vert) + "\n\n"
    Prompt += "Please follow the format given in the example to generate 3 templates."

    print("\033[0;42;40m\tINPUT:\033[0m")
    print(Prompt)

    s_time = time.time()
    success = False
    if model in [
        "gpt-4",
        "gpt-4-1106",
        "gpt-4-1106-preview",
        "gpt-3.5-turbo-1106",
        "gpt-4-0125-preview",
    ]:
        messages = [
            {
                "role": "system",
                "content": "You are a helpful, pattern-following assistant.",
            }
        ]
        messages.append({"role": "user", "content": Prompt})
        while not success:
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages, model=model, max_tokens=max_tokens, temperature=0
                )
            except Exception as e:
                if args.debug:
                    import pdb

                    pdb.set_trace()
                print(e)
                time.sleep(sleep_second)
            else:
                success = True
        # import pdb; pdb.set_trace()
        # result = chat_completion['choices'][0]['message']['content']
        result = chat_completion.choices[0].message.content

        print("\033[0;31;40m\tPREDICT:\033[0m")
        print(result)

        pattern = r'{"instruction": "(.*?)", "fail output": "(.*?)", "input template": "(.*?)", "answer template": "(.*?)", "explanation template"'
        # pattern = r'{"input template": "(.*?)", "answer template": "(.*?)", "explanation template": "(.*?)"}'
        # pattern = r'{"input template": "(.*?)", "answer template": "(.*?)", "explanation template"'
        matches = re.findall(pattern, result, re.DOTALL)
        for match in matches:
            inst = match[0]
            fo = match[1]
            input = match[2]
            answer = match[3]
            print("---")
            print("inst:", inst)
            print("fo:", fo)
            INST["OPENIE"].append([inst, fo])

            print("input template:", input)
            print("answer template:", answer)

            OUTPUT_BASE.append((input, answer))
            # explain = match[2]
            # print("explanation templat:", explain)
            # OUTPUT_EXPLAN.append(explain)
    print("=============OUTPUT INST=============", len(INST["OPENIE"]))
    pprint.pprint(INST["OPENIE"], width=400, indent=4)
    print("=============OUTPUT_BASE=============", len(OUTPUT_BASE))
    pprint.pprint(OUTPUT_BASE, width=400, indent=4)
    print("=============OUTPUT_EXPLAN=============", len(OUTPUT_EXPLAN))
    pprint.pprint(OUTPUT_EXPLAN, width=400, indent=4)


def main(args):
    # args.n_threads = min(len(api_key_pool), args.n_threads)
    # demonstrations
    for i in range(0, 1):
        query_openai_api_per_example(
            api_key_pool[0], args, args.model, args.sleep_second, args.max_tokens
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query OpenAI")
    # multiple processing
    parser.add_argument("--n_threads", type=int, default=16)
    # I/O
    # parser.add_argument("--input_dir", type=str, default="prompts")
    parser.add_argument("--test_file", type=str, default=None)

    # model & parameters
    parser.add_argument("--model", type=str, default="gpt-4-0125-preview")
    parser.add_argument("--max_tokens", type=int, default=1024)
    parser.add_argument("--sleep_second", type=float, default=10.0)
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()
    main(args)
