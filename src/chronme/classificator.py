import json
import glob
import os
import re

from aw_core.models import Event
from collections import defaultdict
from typing import Any, Dict, List

class YamlReaderError(Exception):
    pass

def data_merge(dest, src):
    """Merges b into a and return merged result
    Stolen from https://stackoverflow.com/a/15836901/2687601

    NOTE: tuples and arbitrary objects are not handled as it is totally ambiguous what should happen"""
    key = None
    try:
        if dest is None or isinstance(dest, (str, int, float)):
            # border case for first run or if a is a primitive
            dest = src
        elif isinstance(dest, list):
            # lists can be only appended
            if isinstance(src, list):
                # merge lists
                dest.extend(src)
            else:
                # append to list
                dest.append(src)
        elif isinstance(dest, dict):
            # dicts must be merged
            if isinstance(src, dict):
                for key in src:
                    if key in dest:
                        dest[key] = data_merge(dest[key], src[key])
                    else:
                        dest[key] = src[key]
            else:
                raise YamlReaderError('Cannot merge non-dict "%s" into dict "%s"' % (src, dest))
        else:
            raise YamlReaderError('NOT IMPLEMENTED "%s" into "%s"' % (src, dest))
    except TypeError as e:
        raise YamlReaderError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, src, dest))
    return dest

class Classificator:

    UNKNOWN_CATEGORY = "UNKNOWN"

    def __init__(self, productivity_map=None, rulespath="rules"):

        self.productivity_map = productivity_map
        if self.productivity_map is None:
            self.productivity_map = self.load_productivity_map(rulespath)
        self.rules_for_categories = self.parse_productivity_map(self.productivity_map)

    @staticmethod
    def load_productivity_map(dirpath=None):
        prod_map = {}
        for filepath in glob.glob(os.path.join(dirpath, "*.json")):
            print("filePath: ", filepath)
            with open(filepath) as file:
                f_json = json.load(file)
                data_merge(prod_map, f_json)
        return prod_map
    
    @staticmethod
    def compiled_regex(rules):
        out = []
        for rule in rules:
            compiled_rule = {}
            for key, value in rule.items():
                compiled_rule[key] = re.compile(value)
            out.append(compiled_rule)
        return out

    def parse_productivity_map(self, categories_and_rules) -> Dict[str, Any]:
        parsed = defaultdict(list)
        for category_name, category_entry in categories_and_rules.items():
            for subcategory_name, entry in category_entry.items():
                productivity = entry["Productivity"]
                parsed[productivity] += self.compiled_regex(entry["Rules"])
        return parsed

    def _check_category(self, compiled_rules: list, test_entry):
        for compiled_rule in compiled_rules:
            if self._match_rules(compiled_rule, test_entry):
                return True
        return False

    @staticmethod
    def _match_rules(compiled_rule, test_entry):
        for key, value in compiled_rule.items():
            if (key not in test_entry) or (not value.search(test_entry[key])):
                return False
        return True
    
    def check_productivity(self, event: Event):
        data = event['data']

        for category, compiled_rules in self.rules_for_categories.items():
            if self._check_category(compiled_rules, data):
                return category

        return self.UNKNOWN_CATEGORY 
        