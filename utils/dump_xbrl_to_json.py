#!/usr/bin/env python3
"""
SEC XBRL instance (.xml) to sec-api-style JSON extractor (fully dynamic, year-agnostic).
Usage:
    Place your .xml file in ./input/
    python3 xbrl_to_secapi_json.py aapl-20200926
Output:
    ./output/aapl-20200926_secapi.json
"""

import xml.etree.ElementTree as ET
import json
import os
import re
from pathlib import Path

class XBRLToSecAPIJSON:
    def __init__(self, file_prefix: str):
        self.file_prefix = file_prefix
        self.prefix_to_uri = {}
        self.uri_to_prefix = {}
        self.contexts = {}

    def load_namespaces(self, instance_file: str):
        """Extract namespaces (prefix <-> URI) from the root element, fully dynamic/year-agnostic."""
        path = os.path.join("input", instance_file)
        with open(path, 'r', encoding='utf-8') as f:
            content = ''
            for line in f:
                content += line
                if '>' in line:
                    break
        self.prefix_to_uri.clear()
        self.uri_to_prefix.clear()
        # Extract xmlns:prefix="url"
        for m in re.findall(r'xmlns:([a-zA-Z0-9_\-]+)="([^"]+)"', content):
            prefix, uri = m
            self.prefix_to_uri[prefix] = uri
            self.uri_to_prefix[uri] = prefix
        # Extract default xmlns (rare)
        m = re.search(r'xmlns="([^"]+)"', content)
        if m:
            self.prefix_to_uri['default'] = m.group(1)
            self.uri_to_prefix[m.group(1)] = 'default'

    def parse_contexts(self, root):
        """Parse all <context> elements for entity/period info."""
        # Find the correct 'xbrli' URI for this file
        xbrli_uri = self.prefix_to_uri.get('xbrli', 'http://www.xbrl.org/2003/instance')
        context_tag = f'{{{xbrli_uri}}}context'
        entity_tag = f'{{{xbrli_uri}}}entity'
        identifier_tag = f'{{{xbrli_uri}}}identifier'
        period_tag = f'{{{xbrli_uri}}}period'
        instant_tag = f'{{{xbrli_uri}}}instant'
        start_tag = f'{{{xbrli_uri}}}startDate'
        end_tag = f'{{{xbrli_uri}}}endDate'

        for context in root.findall(f'.//{context_tag}'):
            context_id = context.get('id')
            entity_elem = context.find(entity_tag)
            identifier = entity_elem.find(identifier_tag) if entity_elem is not None else None
            entity_info = {}
            if identifier is not None:
                entity_info = {
                    'identifier': identifier.text,
                    'scheme': identifier.get('scheme')
                }
            period_elem = context.find(period_tag)
            period_info = {}
            if period_elem is not None:
                instant = period_elem.find(instant_tag)
                start_date = period_elem.find(start_tag)
                end_date = period_elem.find(end_tag)
                if instant is not None:
                    period_info = {'instant': instant.text}
                elif start_date is not None and end_date is not None:
                    period_info = {'startDate': start_date.text, 'endDate': end_date.text}
            self.contexts[context_id] = {
                'entity': entity_info,
                'period': period_info
            }

    def extract_facts_secapi(self, root):
        """Extract all facts (tags with contextRef) with correct <prefix>:<TagName> keys."""
        facts = {}
        for elem in root.iter():
            if 'contextRef' in elem.attrib:
                # {namespace}TagName → prefix:TagName, always dynamic
                if elem.tag.startswith('{'):
                    uri, local = elem.tag[1:].split('}', 1)
                    prefix = self.uri_to_prefix.get(uri)
                    # Fallback: accept any us-gaap/dei patterns not declared as prefix
                    if not prefix:
                        if uri.startswith('http://fasb.org/us-gaap/'):
                            prefix = 'us-gaap'
                            self.uri_to_prefix[uri] = prefix
                        elif uri.startswith('http://xbrl.sec.gov/dei/'):
                            prefix = 'dei'
                            self.uri_to_prefix[uri] = prefix
                        else:
                            continue  # unknown tag, skip
                    tag = f"{prefix}:{local}"
                else:
                    tag = elem.tag  # fallback, rare
                context_ref = elem.get('contextRef')
                fact = {
                    "value": elem.text,
                    "decimals": elem.get('decimals'),
                    "unitRef": elem.get('unitRef'),
                    "contextRef": context_ref,
                    "period": self.contexts.get(context_ref, {}).get('period', {}),
                    "entity": self.contexts.get(context_ref, {}).get('entity', {}),
                    "dimensions": {}
                }
                facts.setdefault(tag, []).append(fact)
        return facts

    def run(self):
        self.load_namespaces(self.file_prefix + ".xml")
        tree = ET.parse(os.path.join("input", self.file_prefix + ".xml"))
        root = tree.getroot()
        self.parse_contexts(root)
        facts = self.extract_facts_secapi(root)
        print(f"Extracted {sum(len(v) for v in facts.values())} facts, {len(facts)} unique keys")
        return facts

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 xbrl_to_secapi_json.py <file_prefix>")
        print("E.g.: python3 xbrl_to_secapi_json.py aapl-20200926")
        exit(1)
    file_prefix = sys.argv[1]
    
    # Create output directory within utils package
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    converter = XBRLToSecAPIJSON(file_prefix)
    facts = converter.run()
    output_file = output_dir / f"{file_prefix}_secapi.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2, ensure_ascii=False)
    print(f"Wrote: {output_file}")

if __name__ == "__main__":
    main()
