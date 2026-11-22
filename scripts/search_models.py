#!/usr/bin/env python3
"""
CLI helper to quickly search, filter, and inspect mental models in Charlie's latticework.
Usage:
    python search_models.py --query "incentives"
    python search_models.py --category economics
    python search_models.py --list
    python search_models.py --model "First-Principle Thinking"
"""
import os
import sys
import re
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'references'))

def load_models():
    models = []
    if not os.path.exists(REF_DIR):
        print(f"Error: references directory not found at {REF_DIR}")
        return models
    
    for cat in os.listdir(REF_DIR):
        cat_path = os.path.join(REF_DIR, cat)
        if not os.path.isdir(cat_path):
            continue
        for fname in os.listdir(cat_path):
            if not fname.endswith('.md'):
                continue
            fpath = os.path.join(cat_path, fname)
            with open(fpath, 'r', encoding='utf-8') as fp:
                text = fp.read()
            
            name_m = re.search(r'## Mental Model\s*=\s*([^\r\n]+)', text)
            name = name_m.group(1).strip() if name_m else fname
            
            desc_m = re.search(r'\*\*Description:\*\*\s*\n([^\r\n]+)', text)
            desc = desc_m.group(1).strip() if desc_m else ''
            
            kw_m = re.search(r'\*\*Keywords for Situations:\*\*\s*\n([^\r\n]+)', text)
            kw = kw_m.group(1).strip() if kw_m else ''
            
            models.append({
                'name': name,
                'category': cat,
                'file': fname,
                'path': fpath,
                'rel_path': f"{cat}/{fname}",
                'description': desc,
                'keywords': kw,
                'full_text': text
            })
    return models

def main():
    parser = argparse.ArgumentParser(description="Search and explore mental models.")
    parser.add_argument('-q', '--query', type=str, help="Search query (matches name, description, keywords, and text)")
    parser.add_argument('-c', '--category', type=str, help="Filter by category (general, economics, human_nature, systems_thinking, science, math, war, art)")
    parser.add_argument('-l', '--list', action='store_true', help="List all models")
    parser.add_argument('-m', '--model', type=str, help="Inspect a specific model by name or filename")
    
    args = parser.parse_args()
    models = load_models()
    
    if args.list:
        print(f"Total Mental Models: {len(models)}")
        for m in sorted(models, key=lambda x: (x['category'], x['name'])):
            print(f"[{m['category']}] {m['name']} -> {m['rel_path']}")
        return
        
    if args.model:
        query_m = args.model.lower()
        matched = [m for m in models if query_m in m['name'].lower() or query_m in m['file'].lower()]
        if not matched:
            print(f"No model found matching '{args.model}'")
            return
        for m in matched:
            print("="*70)
            print(f"Model: {m['name']} ({m['category']})")
            print(f"File: {m['rel_path']}")
            print("="*70)
            print(m['full_text'])
        return
        
    results = models
    if args.category:
        cat_q = args.category.lower().strip()
        results = [m for m in results if cat_q in m['category'].lower()]
        
    if args.query:
        words = args.query.lower().split()
        def score(m):
            s = 0
            text_lower = (m['name'] + " " + m['description'] + " " + m['keywords'] + " " + m['full_text']).lower()
            for w in words:
                if w in m['name'].lower():
                    s += 10
                elif w in m['keywords'].lower():
                    s += 5
                elif w in m['description'].lower():
                    s += 3
                elif w in text_lower:
                    s += 1
            return s
        
        scored = [(m, score(m)) for m in results]
        scored = [item for item in scored if item[1] > 0]
        scored.sort(key=lambda x: x[1], reverse=True)
        results = [item[0] for item in scored]
        
    print(f"Found {len(results)} matching mental model(s):")
    print("-" * 70)
    for m in results[:15]:
        print(f"* [{m['category']}] {m['name']} ({m['rel_path']})")
        print(f"  Description: {m['description'][:110]}...")
        if m['keywords']:
            print(f"  Keywords: {m['keywords']}")
        print()
    if len(results) > 15:
        print(f"... and {len(results) - 15} more. Refine your query or category.")

if __name__ == '__main__':
    main()
