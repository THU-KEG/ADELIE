import sys
import json
import torch
# import evaluate
from tqdm import tqdm
from sentence_transformers import SentenceTransformer, util

def load_json(path):
    with open(path) as f:
        data = json.loads(f.read())
    return data

def extract_header(s):
    first_index = s.find("|") # the index for the first |
    last_index = s.rfind("|") # the index for the last |

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
    table = table.replace("| not specified |", "| N/A |")
    table = table.replace("| none |", "| N/A |")
    
    # get header
    header = table.split('\n')[0]
    header = header.strip('|').strip()
    header = header.split(' | ')

    return header

def soft_match(query, value, sim_model):
    device = torch.device("cuda:0") # specify CPU as device
    sim_model = sim_model.to(device) # move model to CPU
    embedding_1 = sim_model.encode(query, convert_to_tensor=True, device=device) # encode on CPU
    embedding_2 = sim_model.encode(value, convert_to_tensor=True, device=device) # encode on CPU
    sim_matrix = util.pytorch_cos_sim(embedding_1, embedding_2)
    return sim_matrix

def header_soft_score(pred_list, gold_list):
    device = torch.device("cpu")
    gold_n, pred_n, pred_in_gold_n, gold_in_pred_n = 0, 0, 0, 0
    sim_model = SentenceTransformer('/home/qyj/.cache/huggingface/hub/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/44eb4044493a3c34bc6d7faae1a71ec76665ebc6')
    sim_model = sim_model.to(device)
    for gold, pred in zip(gold_list, pred_list):
        gold_n += len(gold) 
        pred_n += len(pred)
        scores = soft_match(gold, pred, sim_model)
        max_gold_score = torch.max(scores, dim=0).values
        pred_in_gold_n += torch.sum(max_gold_score)
        max_pred_score = torch.max(scores, dim=1).values
        gold_in_pred_n += torch.sum(max_pred_score)
    try:
        pre, rec, f1 = 0, 0, 0
        pre = 100.0 * pred_in_gold_n / pred_n
        rec = 100.0 * gold_in_pred_n / gold_n
        f1 = 2 * pre * rec / (pre + rec)
    except:
        pre = rec = f1 = 0

    return pre, rec, f1

def calculate_by_tag(data, tag, metrics):
    dic = {}
    for i in range(len(data)):
        cur_tag = data[i][tag]
        if cur_tag not in dic:
            dic[cur_tag] = 1
    print(tag)
    for key in dic:
        pred_list, gold_list = [], []
        for i in range(len(data)):
            if data[i][tag] == key:
                pred_header = extract_header(data[i]['output'].lower())
                gold_header = extract_header(data[i]['gold'].lower())
                pred_list.append(pred_header)
                gold_list.append(gold_header)
        P, R, F = metrics(pred_list, gold_list)
        print(f"{key}: {F}")
    print()

def main(path):
    # if len(sys.argv) < 2:
    #     path = 'model_output/ODIE-7b-filter.json'
    # else: 
    #     path = sys.argv[1]
    print(f"model output file: {path}")

    metrics = header_soft_score

    data = load_json(path)
    
    pred_list, gold_list = [], []

    for i in tqdm(range(len(data))):
        pred_header = extract_header(data[i]['output'].lower())
        gold_header = extract_header(data[i]['gold'].lower())
        
        pred_list.append(pred_header)
        gold_list.append(gold_header)
        
    
    P, R, F = metrics(pred_list, gold_list)
    print(f"Overall\n{F}")
    
    calculate_by_tag(data, 'source_type', metrics)
    calculate_by_tag(data, 'category', metrics)
    calculate_by_tag(data, 'difficulty', metrics)

if __name__ == "__main__":
    main('test_data.json')
