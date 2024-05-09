### Prepare annotation files
""" Rules for creating dataset:
    Retain at most 3 sentences with heuristic segmentation method:
      (1) For a pair of two sentences s1,s2 having the highest BLEU score in the remaining set:
          a. if the length of one of them is less than 2/3 of original sentence, remove this one;
          a. otherwise, remove the one with highest sum of BLEU scores with all other sentences.
      (2) Remain at least 3 sentences.
          
      
"""
SELF_IDS = list(range(10,1282,1282//20))
n_sents = 0
n_sents_para = 0
ann_para = []
ann_para_records = []
ann_para_self = []
for i, x in enumerate(result):
    # paraphrase sample
    x_para = {
        "ori_sent": x["ori_sent"],
        "paraphrases": [
            p["sent"] for p in x["paraphrases"]
        ]
    }
    
    x_para_record = {
        "ori_sent": x["ori_sent"],
        "paraphrases": [],
        "bleus": None
    }
    
    # apply heuristic rules
    _all_sents = sorted([p["sent"] for p in x["paraphrases"]], key=lambda _ss:len(_ss.split()))
    _all_sents_records =sorted([p["sent"] for p in x["paraphrases"]], key=lambda _ss:len(_ss.split()))
    ## length rule
    for _s in _all_sents:
        if len(_s.split()) < len(x["ori_sent"].split())*(2/3) and len(_all_sents)>3:
            _all_sents_records[_all_sents.index(_s)] = (_s, 'discard_length', len(_s.split()))
            _all_sents.pop(_all_sents.index(_s))
    ## bleu score rule
    if len(_all_sents) > 3:
        _sents_bleu = np.zeros([len(_all_sents),len(_all_sents)])
        for ii in range(len(_all_sents)):
            for iii in range(ii+1, len(_all_sents)):
                _b1 = sacrebleu.corpus_bleu([_all_sents[ii]], [[_all_sents[iii]]])
                _b2 = sacrebleu.corpus_bleu([_all_sents[iii]], [[_all_sents[ii]]])
                _sents_bleu[ii][iii] = _b1.score
                _sents_bleu[iii][ii] = _b2.score
        x_para_record["bleus"] = copy.copy(_sents_bleu).tolist()
        while len(_all_sents) > 3:
            _m1, _m2 = [_[0] for _ in np.where(_sents_bleu==_sents_bleu.max())]
            _sum_m1 = (_sents_bleu[_m1,:].sum() + _sents_bleu[:,_m1].sum()) / 2
            _sum_m2 = (_sents_bleu[_m2,:].sum() + _sents_bleu[:,_m2].sum()) / 2
            if _sum_m1 > _sum_m2:
                _all_sents.pop(_m1)
                _sents_bleu = np.delete(_sents_bleu, _m1, axis=0)
                _sents_bleu = np.delete(_sents_bleu, _m1, axis=1)
                _all_sents_records[_m1] = (_all_sents_records[_m1], 'discard_bleu', _sum_m1)
            else:
                _all_sents.pop(_m2)
                _sents_bleu = np.delete(_sents_bleu, _m2, axis=0)
                _sents_bleu = np.delete(_sents_bleu, _m2, axis=1)
                _all_sents_records[_m2] = (_all_sents_records[_m2], 'discard_bleu', _sum_m2)
    x_para["paraphrases"] = _all_sents
    x_para_record["paraphrases"] = _all_sents_records
    ann_para.append(x_para)
    ann_para_records.append(x_para_record)
    
    # paraphrase self-annotation sample
    if i in SELF_IDS:
        x_para_self = {
            "ori_sent": x["ori_sent"],
            "paraphrases":[
                {
                    "sent":_s,
                    "annotation_sent": " ",
                    "annotation_args": [
                        {"arg1":" ", "pred": " ", "arg2": " "},
                        {"arg1":" ", "pred": " ", "arg2": " "}
                    ]
                } for _s in _all_sents
            ]
        }
        ann_para_self.append(x_para_self)
    n_sents += 1
    n_sents_para += len(x_para["paraphrases"])
    
# prepare shuffled all samples
np.random.shuffle(ann_para)
np.random.shuffle(ann_para_self)
# save
with open(result_ann_para, "w") as f:
    json.dump(ann_para, f, indent=4)
with open(result_ann_para[:-4]+'records.json', "w") as f:
    json.dump(ann_para_records, f, indent=4)
with open(result_ann_para_self, "w") as f:
    json.dump(ann_para_self, f, indent=4)
print(f"total # of instances: {n_sents}")
print(f"total # of paraphrases: {n_sents_para}")