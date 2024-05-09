SUBTYPE = {
    "Airport": "Facility",
    "Building-Grounds": "Facility",
    "Path": "Facility",
    "Plant": "Facility",
    "Subarea-Facility": "Facility",
    "Continent": "GPE",
    "County-or-District": "GPE",
    "GPE-Cluster": "GPE",
    "Nation": "GPE",
    "Population-Center": "GPE",
    "Special": "GPE",
    "State-or-Province": "GPE",
    "Address": "Location",
    "Boundary": "Location",
    "Celestial": "Location",
    "Land-Region-Natural": "Location",
    "Region-General": "Location",
    "Region-International": "Location",
    "Water-Body": "Location",
    "Commercial": "Organization",
    "Educational": "Organization",
    "Government": "Organization",
    "Entertainment": "Organization",
    "Media": "Organization",
    "Medical-Science": "Organization",
    "Non-Governmental": "Organization",
    "Religious": "Organization",
    "Sports": "Organization",
    "Group": "Person",
    "Indeterminate": "Person",
    "Individual": "Person",
    "Air": "Vehicle",
    "Land": "Vehicle",
    "Subarea-Vehicle": "Vehicle",
    "Vehicle.Underspecified": "Vehicle",
    "Water": "Vehicle",
    "Biological": "Weapon",
    "Blunt": "Weapon",
    "Chemical": "Weapon",
    "Exploding": "Weapon",
    "Nuclear": "Weapon",
    "Projectile": "Weapon",
    "Sharp": "Weapon",
    "Shooting": "Weapon",
    "Weapon.Underspecified": "Weapon",  # 与vehicle重合，使用括号来区分
}

ENTITY_TO_CLASS_MAPPING = {
    "FAC": "Facility",
    "GPE": "GPE",
    "LOC": "Location",
    "ORG": "Organization",
    "PER": "Person",
    "VEH": "Vehicle",
    "WEA": "Weapon",
}

BTYPE = {
    "Facility": "A facility is a functional, primarily man-made structure. These include buildings and similar facilities designed for human habitation, such as houses, factories, stadiums, office buildings, ...Roughly speaking, facilities are artifacts falling under the domains of architecture and civil engineering.",
    "GPE": "Geo-Political Entities are composite entities comprised of a population, a government, a physical location, and a nation (or province, state, country, city, etc.).",
    "Location": "Places defined on a geographical or astronomical basis which are mentioned in a document and do not constitute a political entity give rise to Location entities. These include, for example, the solar system, Mars, the Hudson River, Mt. Everest, and Death Valley.",
    "Organization": "Each organization or set of organizations mentioned in a document gives rise to an entity of type Organization. Typical examples are businesses, government units, sports teams, and formally organized music groups.",
    "Person": 'Each distinct person or set of people mentioned in a document refers to an entity of type Person. For example, people may be specified by name ("John Smith"), occupation ("the butcher"), family relation ("dad"), pronoun ("he"), etc., or by some combination of these.',
    "Vehicle": "A Vehicle entity refers to vehicles that are used for transportation. The vehicles can transport either persons or artifacts. For example: 'car', 'plane', 'cabin', ...",
    "Weapon": "A Weapon entity refers to instruments that can be used to deal physical damage, destroy something or kill someone. For example: 'bomb', 'm-16s', 'missile', ...",
}

MENTION_TYPE = {
    "NAM": '"{entity}" is a proper name ',
    "NOM": '"{entity}" is a common noun ',
    "PRO": '"{entity}" is a pronominal ',
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
# {stype}, {btype}
OUTPUT_EXPLAN_S = [
    (
        "Based on the given predefined entity type and text: ",
        'reference to the {btype} entity representing the "{stype}". ',
        "To sum up, ",
    ),
    (
        "Given the provided predefined entity type and text, ",
        'identified as the {stype} entity categorized under the type "{btype}" entity. ',
        "In summary, ",
    ),
    (
        "In accordance with the specified entity type and text, ",
        'recognized as the {btype} entity with the classification "{stype}". ',
        "To recap, ",
    ),
    (
        "Based on the predefined entity type and text, ",
        'acknowledged as the {stype} entity falling under the "{btype}" category. ',
        "To summarize, ",
    ),
    (
        "According to the given entity type and text, ",
        'identified as the {btype} entity, specifically categorized as "{stype}". ',
        "In brief, ",
    ),
    [
        "Upon analyzing the context and entity types, ",
        'pinpointed as a {btype}, more precisely, a "{stype}". ',
        "Summarizing, ",
    ],
    [
        "Following the examination of the text and its entities, ",
        'emerging as a {btype}, under the sub-type "{stype}". ',
        "Conclusively, ",
    ],
    [
        "After careful consideration of the provided text and entities, ",
        'classified as the {btype} entity, specifically known as "{stype}". ',
        "In conclusion, ",
    ],
    [
        "Upon close inspection of the text and its entities, ",
        'standing out as a {btype}, specifically identified as "{stype}". ',
        "To put it succinctly, ",
    ],
    [
        "After a thorough review of the content and its entities, ",
        'distinguished as a member of the {btype} category, with a finer classification of "{stype}". ',
        "Ultimately, ",
    ],
    [
        "Upon analyzing the context and entities within, ",
        'recognized as a {btype}, more precisely as a "{stype}". ',
        "In essence, ",
    ],
    [
        "Upon analyzing the context and entities within, ",
        'recognized as a {btype}, with a more precise classification as "{stype}". ',
        "Summarizing, ",
    ],
    [
        "After a thorough review of the entities present, ",
        'categorized as a {btype}, with a finer distinction as "{stype}". ',
        "In essence, ",
    ],
    [
        "Following a detailed analysis of the document's content, ",
        'discerned as a {btype}, more specifically, "{stype}". ',
        "In summary, ",
    ],
    [
        "In the process of dissecting the text for its entities, ",
        'pinpointed as a {btype}, or more accurately, "{stype}". ',
        "To encapsulate, ",
    ],
]

# OUTPUT_BASE=[
#     ('Please give the answer in the form "[Answer]: {entity}: {type}; ".','{entity}: {type}; '),
#     ('Please give the answer in natural language.','"{entity}" is classified as a "{type}"; '),
#     ('Please give the answer in the form "[Answer]: ({entity}, {type}); ".','({entity}, {type}); '),
#     ('Please give the answer in natural language.','"{entity}" signifies a "{type}"; '),
#     ('Please give the answer in natural language.','"{entity}" represents a "{type}"; ')
# ]
# #(prefix,to_type,summary): prefix+ (multi) to_type+summary+[Answer]:+output_base
# # {stype}, {btype}
# OUTPUT_EXPLAN_S=[
#     ('Based on the given predefined entity type and text: ','reference to the {btype} entity representing the "{stype}". ','To sum up, '),
#     ('Given the provided predefined entity type and text, ','identified as the {stype} entity categorized under the type "{btype}" entity. ','In summary, '),
#     ('In accordance with the specified entity type and text, ','recognized as the {btype} entity with the classification "{stype}". ','To recap, '),
#     ('Based on the predefined entity type and text, ','acknowledged as the {stype} entity falling under the "{btype}" category. ','To summarize, '),
#     ('According to the given entity type and text, ','identified as the {btype} entity, specifically categorized as "{stype}". ','In brief, ')
# ]
# {type}
# OUTPUT_EXPLAN_B=[
#     ('Based on the given predefined entity type and text: ','reference to the "{type}". ','To sum up, '),
#     ('Given the provided predefined entity type and text, ','identified as the "{type}" entity. ','In summary, '),
#     ('In accordance with the specified entity type and text, ','recognized as the "{type}" entity. ','To recap, '),
#     ('Based on the predefined entity type and text, ','acknowledged as the "{type}" entity. ','To summarize, '),
#     ('According to the given entity type and text, ','identified as the "{type}" entity ','In brief, ')
# ]
OUTPUT_EXPLAN_B = [
    (
        "Based on the given predefined entity type and text: ",
        'reference to the "{type}". ',
        "To sum up, ",
    ),
    (
        "Given the provided predefined entity type and text, ",
        'identified as the "{type}" entity. ',
        "In summary, ",
    ),
    (
        "In accordance with the specified entity type and text, ",
        'recognized as the "{type}" entity. ',
        "To recap, ",
    ),
    (
        "Based on the predefined entity type and text, ",
        'acknowledged as the "{type}" entity. ',
        "To summarize, ",
    ),
    (
        "According to the given entity type and text, ",
        'identified as the "{type}" entity ',
        "In brief, ",
    ),
    ["Upon analyzing the context, ", 'categorized under "{type}". ', "Summarizing, "],
    ["After a thorough examination, ", 'classified as "{type}". ', "Conclusively, "],
    ["Following the clues provided, ", 'detected as a "{type}". ', "In conclusion, "],
    ["Upon investigation, ", 'found and categorized as "{type}". ', "Overall, "],
    ["After examining the context, ", 'classified as a "{type}". ', "To encapsulate, "],
    [
        "Following the analysis of the text, ",
        'determined to be of the "{type}" type. ',
        "Conclusively, ",
    ],
    [
        "After parsing the given text, ",
        'placed under the "{type}" category. ',
        "In conclusion, ",
    ],
    ["Upon dissecting the text, ", 'labelled as "{type}". ', "Overall, "],
    [
        "During the analysis, ",
        'belongs to the "{type}" classification. ',
        "Summing up, ",
    ],
    ["Upon thorough examination, ", 'classified as a "{type}". ', "To summarize, "],
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
