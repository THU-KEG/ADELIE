import os, re
from sklearn.decomposition import PCA
from typing import Counter
from sklearn import cluster
import json
import numpy
import matplotlib.pyplot as plt
# from random import sample
import random
import argparse
import tqdm
import stanza

TAG_DICT = "./tag_dict.json"

with open(TAG_DICT) as f:
    tag_dict = json.load(f)


def serialize_tree_with_fo(tree:dict, pure_parse:list, parse:list):
        """Recursively traverse the tree in the first-order."""
        if tree is not None:
            if len(tree.children)!=0:
                pure_parse.append(f" ({tree.label}")
                parse.append(f" ({tree.label}")
            else:
                pure_parse.append(" ")
                parse.append(f" {tree.label}")
            for i in range(len(tree.children)):
                serialize_tree_with_fo(tree.children[i], pure_parse, parse)
            if len(tree.children)!=0:
                pure_parse.append(")")
                parse.append(")")
        return pure_parse, parse


def seq2dict(seq, max_level):
    root = {'value': seq.split(" ")[0]}
    if max_level == 1:
        return root
    child = []
    stack = 0
    begin = -1
    for i in range(0, len(seq)):
        if seq[i] == '(':
            if stack == 0:
                begin = i
            stack += 1
        elif seq[i] == ')':
            stack -= 1
            if stack == 0:
                child.append(seq2dict(seq[begin+1:i], max_level-1))
    if child:
        root['child'] = child
    return root


def dict2bag(root, bag):
    bag[tag_dict[root['value']]] += 1
    if 'child' in root:
        for child in root['child']:
            dict2bag(child, bag)


def bags_algorithm(k):
    bags = []
    for line in tqdm(lines):
        parseTree = line.split(' <sep> ')[1].strip()[1:-1]
        root = seq2dict(parseTree, 4)
        bag = [0]*len(tag_dict)
        dict2bag(root, bag)
        bag[0] -= 1
        bag[1] -= 1
        bags.append(bag)

    x = numpy.array(bags)
    features = x/x.sum(1)[:, None]

    model = cluster.KMeans(n_clusters=k, max_iter=1000,
                           n_jobs=4, init="k-means++")
    model.fit(features)
    cnt = Counter(model.labels_)
    files = []
    for i in range(k):
        files.append(open(f"clusters/{i}.txt", "w"))
    for i in range(len(model.labels_)):
        files[model.labels_[i]].write(lines[i])
    for i in range(k):
        files[i].close()

    with open(train_data) as f:
        samples = random.sample(f.readlines(), 20000)

    distances = []
    for i in range(k):
        center = model.cluster_centers_[i]
        temp = 0
        for line in samples:
            parseTree = line.split(' <sep> ')[1].strip()[1:-1]
            root = seq2dict(parseTree, 4)
            bag = [0]*len(tag_dict)
            dict2bag(root, bag)
            bag[0] -= 1
            bag[1] -= 1
            feature = numpy.array(bag)
            temp = numpy.sqrt(((center-feature)**2).sum())
        temp /= len(samples)
        distances.append(temp)
    for i in cnt.most_common():
        print(f'{i[0]}: cnt={i[1]},dis={distances[i[0]]}')


def preorderTraversal(root, nums):
    nums.append(tag_dict[root['value']])
    if 'child' in root:
        for child in root['child']:
            preorderTraversal(child, nums)


def levelorderTraversal(root, nums):
    queue = [root]
    while queue:
        cur = queue.pop(0)
        nums.append(tag_dict[cur['value']])
        if 'child' in cur:
            for child in cur['child']:
                queue.append(child)



def lcs_distance_qiji1(s1, s2, weight_decay=0.5):
    dp = [[0]*(len(s2)) for _ in range(len(s1))]
    # dp = np.zeros([len(s1), len(s2)], dtype=int)
    for i in range(len(s2)):
        if s1[0] == s2[i]:
            dp[0][i] = 1

    for i in range(len(s1)):
        if s1[i] == s2[0]:
            dp[i][0] = 1

    b_span = 0
    for i in range(1, len(s1)):
        for j in range(1, len(s2)):
            if s1[i]==s2[j]:
                if s1[i-1]==s2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = dp[i-1][j-1] + 1
                    b_span = i
            else:
                dp[i][j] = max((dp[i-1][j-1], dp[i][j-1], dp[i-1][j]))
                if s1[i-1] == s2[j-1]:
                    m = len(re.findall(r".*?{}.*?".format(s1[b_span: i+1]), str(s1)))
                    dp[i][j] = min(m, max((dp[i-1][j-1], dp[i][j-1], dp[i-1][j])))

    tot_m = max(dp[len(s1)-1])
    # import ipdb
    # ipdb.set_trace()
    # tot_m = dp[len(s1)-1].max()
    tot_len = sum([weight_decay**m for m in range(tot_m)])
    return 1-tot_len/min(len(s1), len(s2))


def cal_hws_distance(parses_pairs, weight_decay=0.95, idx=0):
    """Calculate HWS-distance for all pairs of parses.
    """
    rt_dists = []
    if idx == 0:
        data = tqdm.tqdm(enumerate(parses_pairs), total=len(parses_pairs))
    else:
        data = enumerate(parses_pairs)
    for i, (parse1,parse2) in data:
        seqs = []
        for parse in (parse1, parse2):
            root = seq2dict(parse[1:-1], 4)
            seq = []
            levelorderTraversal(root, seq)
            seqs.append(seq)
        dist = lcs_distance_qiji1(seqs[0][1:], seqs[1][1:], weight_decay)
        rt_dists.append(dist)
    return rt_dists


if __name__ == "__main__":
    parser = parser = argparse.ArgumentParser()
    parser.add_argument("--sent1", type=str)
    parser.add_argument("--sent2", type=str)
    parser.add_argument("--tag_dict", default="./tag_dict.json", type=str)
    parser.add_argument("--decay", type=float, default=0.5)
    args = parser.parse_args()


    with open(args.tag_dict) as f:
        tag_dict = json.load(f)


    stanford_parser = stanza.Pipeline(lang='en', processors='tokenize,pos,constituency',
                                  use_gpu=False, download_method=None)

    parse1 = stanford_parser(args.sent1).sentences[0].constituency.__str__()
    parse2 = stanford_parser(args.sent2).sentences[0].constituency.__str__()

#     # bags_algorithm(k)
    dists = cal_hws_distance([(parse1,parse2)], args.decay, idx=0)

    print("The syntactic distance between sent1 and setn2 is: ",dists[0])

