# This code modified from: https://github.com/hitz-zentroa/GoLLIE/tree/main/src/tasks/ontonotes

OPTIONS = {
    "PERSON": ("Person", "People, including fictional."),
    "NORP": ("NORP", "Nationalities or religious or political groups."),
    "FAC": ("Facility", "Buildings, airports, highways, bridges, etc."),
    "ORG": ("Organization", "Companies, agencies, institutions, etc."),
    "GPE": ("GPE", "Countries, cities, states."),
    "LOC": ("Location", "Non-GPE locations, mountain ranges, bodies of water."),
    "PRODUCT": ("Product", "Objects, vehicles, foods, etc. (Not services)."),
    "DATE": ("Date", "Absolute or relative dates or periods."),
    "TIME": ("Time", "Times smaller than a day."),
    "PERCENT": ("Percentage", "Percentage, including ”%“."),
    "MONEY": ("Money", "Monetary values, including unit."),
    "QUANTITY": ("Quantity", "Measurements, as of weight or distance."),
    "ORDINAL": (
        "Ordinal",
        "first, second, third, First, fourth, fifth, Second, seventh, eighth, sixth.",
    ),
    "CARDINAL": (
        "Cardinal",
        "two, one, three, One, four, five, six, seven, Two, half.",
    ),
    "EVENT": ("Event", "Named hurricanes, battles, wars, sports events, etc."),
    "WORK_OF_ART": ("WorkOfArt", "Titles of books, songs, etc."),
    "LAW": ("Law", "Named documents made into laws."),
    "LANGUAGE": ("Language", "Any named language."),
}
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
        'The entity "{entity}" falls under the category of "{type}"; ',
    ),
    (
        "Highlight the entities and their types as found in the text.",
        'Entity identified: "{entity}", Type: "{type}"; ',
    ),
    (
        "Can you point out the entities and specify their categories?",
        'Detected "{entity}" as a "{type}"; ',
    ),
    (
        "List all entities with their corresponding types.",
        'Found: "{entity}", categorized as "{type}"; ',
    ),
    ("Highlight the entities and their types.", '"{entity}" is a "{type}". '),
    (
        "What are the types of the mentioned entities?",
        'The type of "{entity}" is "{type}". ',
    ),
    (
        "Categorize each entity found in the text.",
        'Under the category "{type}", "{entity}" is listed. ',
    ),
    (
        "Extract and label the entities from the provided text.",
        'Labelled: "{entity}" as "{type}". ',
    ),
    (
        "Identify all entities and their types within the text.",
        'Entity "{entity}" falls under "{type}" category; ',
    ),
    (
        "Highlight the entities and classify them accordingly.",
        'Classification: "{entity}" is a "{type}"; ',
    ),
]
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
