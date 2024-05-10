# ner task evaluate

from sys import argv
import json
import argparse

# turn the output string into dictionary form in order to make comparison
OPTIONS = "art-broadcastprogram, art-film, art-music, art-other, art-painting, art-writtenart, building-airport, building-hospital, building-hotel, building-library, building-other, building-restaurant, building-sportsfacility, building-theater, event-attack/battle/war/militaryconflict, event-disaster, event-election, event-other, event-protest, event-sportsevent, location-bodiesofwater, location-GPE, location-island, location-mountain, location-other, location-park, location-road/railway/highway/transit, O, organization-company, organization-education, organization-government/governmentagency, organization-media/newspaper, organization-other, organization-politicalparty, organization-religion, organization-showorganization, organization-sportsleague, organization-sportsteam, other-astronomything, other-award, other-biologything, other-chemicalthing, other-currency, other-disease, other-educationaldegree, other-god, other-language, other-law, other-livingthing, other-medical, person-actor, person-artist/author, person-athlete, person-director, person-other, person-politician, person-scholar, person-soldier, product-airplane, product-car, product-food, product-game, product-other, product-ship, product-software, product-train, product-weapon"

Env_type_convert = []
Env_type_convert = OPTIONS.split(", ")
Env_type_convert = [vert.replace("-", "_") for vert in Env_type_convert]


def turn_into_dict(ans: str):
    res_dict = {}
    for pair in ans.split(";"):
        pair_split = pair.split(":")
        if len(pair_split) == 2:
            entity, type_ent = pair_split[0].strip().lower(), pair_split[
                1
            ].strip().removesuffix(".")
            if type_ent in Env_type_convert:
                res_dict[entity] = type_ent
    return res_dict


def safe_division(a, b) -> float:
    return a / b if b != 0 else 0


def evaluate(input_path: str):
    # input_data = json.load(open(input_path, "r", encoding='utf-8'))
    golden, predict, correct = 0, 0, 0
    # ... by entity level

    with open(input_path) as f:
        for line in f.readlines():
            data = json.loads(line.strip())

            ref_ans = str(data["messages"][-1]["content"]).strip().lower()
            mod_ans = ""
            if "[Answer]:" in data["output"]:
                mod_ans = (
                    str(data["output"]).strip().split("[Answer]:")[1].strip().lower()
                )
            else:
                mod_ans = data["output"].lower()

            ref_dict, mod_dict = turn_into_dict(ref_ans), turn_into_dict(mod_ans)
            golden += len(ref_dict)
            predict += len(mod_dict)
            for entity in ref_dict:
                if entity in mod_dict and ref_dict[entity] == mod_dict[entity]:
                    correct += 1
    precision = safe_division(correct, predict)
    recall = safe_division(correct, golden)
    f1_score = safe_division(2 * precision * recall, precision + recall)
    return {
        "golden": golden,
        "predict": predict,
        "correct": correct,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
    }


if __name__ == "__main__":
    # assert(len(argv) == 3)
    parser = argparse.ArgumentParser(description="Evaluate Event Detection")
    # IO
    parser.add_argument(
        "--input_dir",
        type=str,
        default="/SSD_DATA/qyj/open-instruct-main/saves/llama_v2_7B/full/no_output_desc/predict/zeroshot/RichERE-ed.jsonl",
    )
    parser.add_argument("--output_dir", type=str, default="result.json")

    args = parser.parse_args()

    input_path = args.input_dir
    result = evaluate(input_path)
    print(result)
    # json.dump(result, fp=open(output_path, "w", encoding='utf-8'), indent=4)
