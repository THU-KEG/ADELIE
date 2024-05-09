Prompt = """Please provide an explanation of the [Answer] based on [Question]. 
The generated explanation should make use of the content in the [Question] as much as possible, and must be consistent with the [Answer]. 
It will eventually be provided at the front of the answer. 
No more than {words_number} words."""

Content = """
[Question]: {input}

[Answer]: {output}
[Explanation]:
"""

Demo = []
