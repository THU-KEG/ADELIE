import json
import jsonlines
from prompts import *
from pathlib import Path
import os

# NER Zero-shot from ours Fewshot
shots = {"1", "2", "4", "8", "16", "32"}
datasets = [
    ("few-nerd-supervised", NER_Zeroshot),
    ("semeval", RC_Zeroshot),
    ("RichERE-ed", ED_Zeroshot),
    ("RichERE-eae", EAE_Zeroshot),
    # "MATRES",
    # "ROBUST",
]


if __name__ == "__main__":
    for shot in shots:
        for dataset in datasets:
            input_path = (
                "/data1/qyj/Alignment_on_IE_tasks/unified_data/test_format_"
                + shot
                + "shot/fewshot_test_history/"
                + dataset[0]
                + ".json"
            )
            output_path = (
                "/data1/qyj/Alignment_on_IE_tasks/unified_data/test_format_"
                + shot
                + "shot_InstructUIE/"
            )
            output_dir = Path(output_path)
            output_dir.mkdir(exist_ok=True, parents=True)
            output_file = dataset[0] + ".json"

            Fewshot = True

            with open(input_path, "r", encoding="utf-8") as reader:
                d = json.load(reader)
                reader.close()

            unified_data = []
            for i, vert in enumerate(d):
                # fewshot
                formatted_text = ""
                if Fewshot == True:
                    for j, hd in enumerate(vert["history"]):
                        if j == 0:
                            text = hd[0].split("Text: ")[1]
                            formatted_text += "Text: " + text + "\n"
                        else:
                            formatted_text += hd[0] + "\n"
                        formatted_text += (
                            "Answer: " + hd[1].split("[Answer]: ")[1] + "\n"
                        )
                # eae
                if "eae" in dataset:
                    roleset = vert["history"][0][0].split("[")[1]
                    roleset = roleset.split("]")[0]
                    instruction = EAE_Zeroshot.format(options=roleset) + formatted_text
                else:
                    instruction = dataset[1] + formatted_text
                    # print("=====================")
                    # print(roleset)

                unified_instance = {
                    "prompt": {
                        "instructions": instruction,
                        "input_prefix": "",
                        "input_suffix": "\n",
                        "output_prefix": "",
                        "output_suffix": "\n",
                    },
                    "request_states": [
                        {
                            "instance": {
                                "input": {"text": vert["instruction"] + "\nAnswer:"},
                                "references": [{"output": {"text": vert["output"]}}],
                                "split": "test",
                                "id": i,
                            },
                        },
                    ],
                }
                unified_data.append(unified_instance)
            out_file = open(os.path.join(output_dir, output_file), "w")
            json.dump(unified_data, out_file, indent=2)
            out_file.close()
