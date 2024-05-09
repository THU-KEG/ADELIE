import sys
import json
import evaluate
from tqdm import tqdm

def load_json(path):
    with open(path) as f:
        data = json.loads(f.read())
    return data

def extract_markdown(s, output=False):
    first_index = s.find("|") # the index for the first |
    # last_index = s.rfind("|") # the index for the last |
    last_index = len(s) - 1
    if first_index != -1 and last_index != -1:
        table = s[first_index: last_index + 1]
    else:
        return ""
    # post processing
    table = table.replace("| |", "| N/A |")
    table = table.replace("|  |", "| N/A |")
    table = table.replace("|   |", "| N/A |")
    table = table.replace("|-|", "| N/A |")
    table = table.replace("| - |", "| N/A |")
    table = table.replace("| Not specified |", "| N/A |")
    table = table.replace("| not specified |", "| N/A |")
    table = table.replace("| Not Specified |", "| N/A |")
    table = table.replace("| None |", "| N/A |")
    table = table.replace("| none |", "| N/A |")

    return table


def get_score(pred, gold, metric):
    return 100 * metric.compute(predictions=pred,references=gold)['rougeLsum']

def group_by_tag(data, score, tag):
    dic, cnt = {}, {}
    for i in range(len(data)):
        tag_value = data[i][tag]
        if tag_value not in dic:
            dic[tag_value] = score[i]
            cnt[tag_value] = 1
        else:
            dic[tag_value] += score[i]
            cnt[tag_value] += 1 
    print('\n' + tag)
    for key in dic:
        print(f"{key}: {dic[key] / cnt[key]} ({cnt[key]})")

def main(path):
    # if len(sys.argv) < 2:
    #     path = 'model_output/ODIE-7b-filter.json'
    # else: 
    #     path = sys.argv[1]
    print(f"model output file: {path}")

    data = load_json(path)
    metric = evaluate.load('rouge')
    score = []
    
    for i in tqdm(range(len(data))):
        pred = [extract_markdown(data[i]['output'], output=True)]
        gold = [extract_markdown(data[i]['gold'])]
        cur_score = get_score(pred, gold, metric)
        score.append(cur_score)
    
    print(f'Overall:\n{sum(score) / len(score)}')
    group_by_tag(data, score, "difficulty")
    group_by_tag(data, score, "category")
    group_by_tag(data, score, "source_type")

if __name__ == "__main__":
    main("test_data.json")
