import yaml
import sys

filename = 'shop1.yaml'

print(f"Reading {filename}...")
with open(filename, 'r', encoding='utf-8') as f:
    data = yaml.safe_load(f)

print(f"\nData type: {type(data)}")

if isinstance(data, list):
    print(f"List length: {len(data)}")
    print("\nFirst 3 items:")
    for i, item in enumerate(data[:3]):
        print(f"\nItem {i}:")
        if isinstance(item, dict):
            for key, value in item.items():
                print(f"  {key}: {type(value)}")
                if key in ['goods', 'products', 'categories'] and isinstance(value, list):
                    print(f"    First 2 {key}:")
                    for subitem in value[:2]:
                        print(f"      - {subitem}")
        else:
            print(f"  Non-dict: {item}")

elif isinstance(data, dict):
    print("Dictionary keys:", data.keys())
    for key, value in data.items():
        print(f"\n{key}: {type(value)}")
        if isinstance(value, list):
            print(f"  First 2 items:")
            for item in value[:2]:
                print(f"    {item}")

print("\nFull structure (limited):")
print(yaml.dump(data, default_flow_style=False, width=80, depth=3)[:1000])
