import argparse
from collections import Counter
import json

parser = argparse.ArgumentParser()
parser.add_argument("enriched_events", help="Enriched events file")
args = parser.parse_args()

selectors = []

with open(args.enriched_events) as ifp:
    for line in ifp:
        event = json.loads(line.strip())
        if len(event["input"]) >= 10:
            selector = event["input"][:10]
            selectors.append(selector)

selector_counter = Counter(selectors)
print(json.dumps(selector_counter.most_common()))
