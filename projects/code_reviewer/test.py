import re
import json

last = ('  ```json {"a": 1, "b": "abcdefg"} ``` ')

cleaned = re.sub(r"^```json\s*|\s*```$", "", last.strip(), flags=re.M)

print(cleaned)

review = json.loads(cleaned)

print(review)