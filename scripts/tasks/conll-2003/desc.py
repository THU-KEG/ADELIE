OPTIONS = {
    "conll-2003": "Person, Organization, Location, Miscellaneous",
}

JSON_BASE = "Please give the answer in json format."
# (prefix,to_type,summary): prefix+ (multi) to_type+summary+[Answer]:+output_base
# {entity}, {stype}, {type}
# OUTPUT_EXPLAN=[
#     ('Based on the given predefined entity type and text: ','"{entity}" is the {stype} entity representing the "{type}". ','To sum up, '),
#     ('Given the provided predefined entity type and text, ','"{entity}" is identified as the {stype} entity categorized under the type "{type}" entity. ','In summary, '),
#     ('In accordance with the specified entity type and text, ','"{entity}" is recognized as the {stype} entity with the classification "{type}". ','To recap, '),
#     ('Based on the predefined entity type and text, ','"{entity}" is acknowledged as the {stype} entity falling under the "{type}" category. ','To summarize, '),
#     ('According to the given entity type and text, ','"{entity}" is identified as the {stype} entity, specifically categorized as "{type}". ','In brief, ')
# ]
OUTPUT_BASE = [
    (
        'Please give the answer in the form "[Answer]: {entity}: {type}; ".',
        "{entity}: {type}; ",
    ),
    (
        "Please give the answer in natural language.",
        '"{entity}" is classified as a "{type}"; ',
    ),
    (
        'Please give the answer in the form "[Answer]: ({entity}, {type}); ".',
        "({entity}, {type}); ",
    ),
    (
        "Please give the answer in natural language.",
        '"{entity}" signifies a "{type}"; ',
    ),
    (
        "Please give the answer in natural language.",
        '"{entity}" represents a "{type}"; ',
    ),
    (
        "Identify and classify the entities mentioned.",
        'The term "{entity}" is a "{type}". ',
    ),
    (
        "What entities are present, and how are they categorized?",
        'Entity: "{entity}", Category: "{type}". ',
    ),
    (
        "List the entities with their respective types.",
        '"{entity}" falls under the "{type}" category. ',
    ),
    (
        "Highlight the entities in the text and specify their types.",
        'Identified: "{entity}" as Type: "{type}". ',
    ),
    (
        "Can you extract the named entities and their respective categories from the given text?",
        'Extracted Entity: "{entity}", Classified under: "{type}". ',
    ),
    (
        "List all entities found in the text along with their classification.",
        'Entity Found: "{entity}", Classified As: "{type}". ',
    ),
    (
        "Identify and categorize the entities mentioned.",
        'The term "{entity}" is identified as a "{type}". ',
    ),
    (
        "What types of entities are present in this text?",
        'Within this context, "{entity}" is a "{type}". ',
    ),
    (
        "Can you classify the entities found in the document?",
        '"{entity}" pertains to the "{type}" category. ',
    ),
    (
        "Highlight the entities and their classifications.",
        'Entity "{entity}" belongs to the "{type}" class. ',
    ),
]
# (prefix,to_type,summary): prefix+ (multi) to_type+summary+[Answer]:+output_base
# {stype}, {type}
OUTPUT_EXPLAN = [
    (
        "Based on the given predefined entity type and text: ",
        '"{entity}" represents the "{type}". ',
        "To sum up, ",
    ),
    (
        "Given the provided predefined entity type and text, ",
        '"{entity}" is identified as the "{type}" entity. ',
        "In summary, ",
    ),
    (
        "In accordance with the specified entity type and text, ",
        '"{entity}" is recognized as the "{type}". ',
        "To recap, ",
    ),
    (
        "Based on the predefined entity type and text, ",
        '"{entity}" is acknowledged as the "{type}" category. ',
        "To summarize, ",
    ),
    (
        "According to the given entity type and text, ",
        '"{entity}" is identified as the "{type}". ',
        "In brief, ",
    ),
    [
        "Upon analyzing the context, ",
        '"{entity}" is categorized under "{type}". ',
        "Summarizing, ",
    ],
    [
        "After a thorough examination, ",
        'the entity "{entity}" has been classified as "{type}". ',
        "Conclusively, ",
    ],
    [
        "Following the clues provided, ",
        '"{entity}" is detected as a "{type}". ',
        "In conclusion, ",
    ],
    [
        "Upon investigation, ",
        '"{entity}" is found and categorized as "{type}". ',
        "Overall, ",
    ],
    [
        "After examining the context, ",
        '"{entity}" has been classified as a "{type}". ',
        "To encapsulate, ",
    ],
    [
        "Following the analysis of the text, ",
        '"{entity}" is determined to be of the "{type}" type. ',
        "Conclusively, ",
    ],
    [
        "After parsing the given text, ",
        '"{entity}" is placed under the "{type}" category. ',
        "In conclusion, ",
    ],
    [
        "Upon dissecting the text, ",
        '"{entity}" has been labelled as "{type}". ',
        "Overall, ",
    ],
    [
        "During the analysis, ",
        'it was observed that "{entity}" belongs to the "{type}" classification. ',
        "Summing up, ",
    ],
    [
        "Upon thorough examination, ",
        '"{entity}" has been classified as a "{type}". ',
        "To summarize, ",
    ],
]

RANDOM_SYMBOLS = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "LABEL_1",
    "LABEL_2",
    "LABEL_3",
    "LABEL_4",
    "LABEL_5",
    "LABEL_6",
]
