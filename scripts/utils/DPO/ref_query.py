QUERY = {
    # NER
    "conll-2003": (
        'Please give the answer in the form "[Answer]: {entity}: {type}; ".',
        "{entity}: {type}; ",
    ),
    "ontonote5": (
        'Please give the answer in the form "[Answer]: {entity}: {type}; ".',
        "{entity}: {type}; ",
    ),
    "ace2005-ner": (
        'Please give the answer in the form "[Answer]: {entity}: {type}; ".',
        "{entity}: {type}; ",
    ),
    # RC
    "tacred": (
        'Please give the answer in the tuple form "[Answer]: ({subject}; {relation}; {object})\n".',
        "({head}; {type}; {tail})\n",
    ),
    "fewrel": (
        'Please give the answer in the tuple form "[Answer]: ({subject}; {relation}; {object})\n".',
        "({head}; {type}; {tail})\n",
    ),
    # ED
    "ace2005-ed": (
        'Please give the answer in the form "[Answer]: {event}: {class}; ".',
        "{word}: {type}; ",
    ),
    "maven-ed": (
        'Please give the answer in the form "[Answer]: {event}: {class}; ".',
        "{word}: {type}; ",
    ),
    # EAE
    "ace2005-eae": (
        'Please give the answer in the form "[Answer]: {word}: {role}; ".',
        "{word}: {type}; ",
    ),
    "maven-eae": (
        'Please give the answer in the form "[Answer]: {word}: {role}; ".',
        "{word}: {type}; ",
    ),
    "RAMS-eae": (
        'Please give the answer in the form "[Answer]: {word}: {role}; ".',
        "{word}: {type}; ",
    ),
    # ERE -- 需要进一步处理一下
    "MAVEN-ERE": (
        'Please give the answer in the list form "[Answer]: [{relation}]".',
        "[{type}]",
    ),
    # OPENIE -- 需要进一步处理一下
    "openie4": (
        'Please give the answer in the tuple form "[Answer]: ({predicate}; {subject}; {object}; {time}; {location})\n". If one or more of the last three elements does not exist, it can be omitted.',
        "",
    ),
    # OndemandIE 数据集不处理
}
