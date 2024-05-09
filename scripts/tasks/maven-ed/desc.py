JSON_BASE = "Please give the answer in json format."

OUTPUT_BASE = [
    (
        'Please give the answer in the form "[Answer]: {event}: {class}; ".',
        "{word}: {type}; ",
    ),
    (
        'Please give the answer in the form "[Answer]: ({event}, {class}); ".',
        "({word}, {type}); ",
    ),
    (
        'Please give the answer in the form "[Answer]: (event trigger: {event}, class: {class}); ".',
        "(event trigger: {word}, class: {type}); ",
    ),
    (
        "Please give the answer in natural language.",
        '"{word}" is linked to the "{type}" event. ',
    ),
    (
        "Please give the answer in natural language.",
        '"{word}" triggers an event identified as "{type}". ',
    ),
    (
        "Identify the event and its type from the text.",
        'The event "{word}" falls under the category "{type}".',
    ),
    (
        "What event is described, and how can it be classified?",
        'Event: "{word}", Type: "{type}".',
    ),
    (
        "Extract the key event and its corresponding type from the provided text.",
        '"{word}" is an event that is categorized as "{type}".',
    ),
    (
        "From the given text, identify the event trigger and its type.",
        'Trigger: "{word}", Classified as: "{type}".',
    ),
    (
        "Identify the event and its category from the given text.",
        'Event identified: "{word}", Category: "{type}".',
    ),
    (
        "Describe the event and determine its classification.",
        'Described Event: "{word}", Classification: "{type}".',
    ),
    (
        "What type of event does this scenario depict?",
        'Depicted Event: "{word}", Event Type: "{type}".',
    ),
    (
        "Identify the event and its category from the description.",
        'Identified Event: "{word}", Category: "{type}".',
    ),
    (
        "Highlight the key event and its corresponding classification from the text.",
        'Key Event: "{word}", Classification: "{type}".',
    ),
    (
        "From the given narrative, extract the event and its type.",
        'Extracted Event: "{word}", Type: "{type}".',
    ),
]
# (prefix,to_type,summary): prefix+ (multi) to_type+summary+[Answer]:+output_base
# {word}, {btype},{stype},{type}
OUTPUT_EXPLAN = [
    (
        "Based on the given predefined event type and text: ",
        '"{word}" is an event trigger word, which triggers an event of type "{type}". ',
        "To sum up, ",
    ),
    (
        "In consideration of the provided predefined event type and text, ",
        '"{word}" is specifically linked to the category "{type}". ',
        "In brief, ",
    ),
    (
        "Given the predefined event type and text, ",
        '"{word}" triggers an event classified as "{type}". ',
        "To summarize, ",
    ),
    (
        "According to the provided event type and text, ",
        '"{word}" serves as an event trigger word, instigating an event classified under "{type}". ',
        "In conclusion, ",
    ),
    (
        "Based on the given predefined event type and text, ",
        '"{word}" operates as an event trigger word, initiating an event categorized as "{type}". ',
        "Hence, ",
    ),
    [
        "Upon analyzing the context, ",
        '"{word}" is pinpointed as the catalyst for an event, which is best described by the category "{type}". ',
        "In conclusion, ",
    ],
    [
        "After a thorough examination of the context, ",
        'it\'s evident that "{word}" serves as the trigger for an event, which can be classified under "{type}". ',
        "Therefore, ",
    ],
    [
        "Following a detailed analysis, ",
        'the term "{word}" emerges as a significant event trigger, falling into the "{type}" category. ',
        "As a result, ",
    ],
    [
        "Upon close inspection of the text, ",
        '"{word}" is identified as the trigger for an event, which is classified under the type "{type}". ',
        "Summarily, ",
    ],
    [
        "Upon examining the context, ",
        'it becomes clear that "{word}" is identified as the pivotal event, which is best categorized under "{type}". ',
        "This leads to the conclusion that ",
    ],
    [
        "After a thorough review of the context, ",
        'the descriptor "{word}" is pinpointed as an event, which is aptly classified under "{type}". ',
        "This analysis brings us to understand that ",
    ],
    [
        "Through the lens of the scenario provided, ",
        '"{word}" is highlighted as the event in question, with its type being "{type}". ',
        "This delineation makes it clear that ",
    ],
    [
        "Upon analyzing the description, ",
        '"{word}" emerges as the pivotal event, falling under the category of "{type}". ',
        "Therefore, ",
    ],
    [
        "In dissecting the text, ",
        '"{word}" is pinpointed as the key event, which is classified under "{type}". ',
        "In essence, ",
    ],
    [
        "Delving into the narrative provided, ",
        '"{word}" is extracted as the significant event, with its type being "{type}". ',
        "Conclusively, ",
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
