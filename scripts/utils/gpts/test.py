import re
import pprint
import json

result = """
```json
{
  "Step-by-Step Explanation": [
    "Step 1: Identify the 'head event' and 'tail event' from the question. The 'head event' is the first event or 'Timex' mentioned, which is '1952'. The 'tail event' is the second event or 'Timex' mentioned, which is 'promising'.",
    "Step 2: Understand the context of both events within the text. '1952' refers to the year Dwight D. Eisenhower was elected U.S. President, and 'promising' refers to Eisenhower's campaign promise to take a harder line against communism.",
    "Step 3: Determine the relationship between the two events based on their context in the text. Since Eisenhower's campaign promise occurred within the year 1952, the 'head event' (1952) contains the 'tail event' (promising).",
    "Step 4: Choose the correct relation from the given options [before, overlap, contains, simultaneous, begins-on, ends-on] that best describes the temporal relationship between the 'head event' and 'tail event'. The correct relation is 'contains' because the event of Eisenhower promising to take a harder line against communism is encompassed within the year 1952.",
    "Step 5: Formulate the answer in the required format, confirming that the 'head event' ('1952') contains the 'tail event' ('promising'), consistent with the context provided in the text."
  ]
}
```
"""

pattern = r"{[^{}]*}"
matches = re.findall(pattern, result)
d = eval(matches[0])
print(type(d))
print(d)
# str= result.split(matches[0])[1]
# print(str)
# json_string = result.replace('\"', '\\"')
# print(json_string)
# d=json.loads(json_string)
# print(d)
# for match in matches:
#     input = match[0]
#     answer = match[1]
#     print("---")
#     print("input template:", input)
#     print("answer templat:", answer)
#     # print("explanation templat:", explain)
#     OUTPUT_BASE.append((input,answer))
#     # OUTPUT_EXPLAN.append(explain)


# print("=============OUTPUT_BASE=============")
# pprint.pprint(OUTPUT_BASE,width=400)
# print("=============OUTPUT_EXPLAN=============")
# pprint.pprint(OUTPUT_EXPLAN,width=400)
