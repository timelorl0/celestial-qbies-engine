# coordinator/modules/knowledge_map.py
"""
Knowledge map: lưu các tri thức, phiên bản công pháp, records.
"""
MAP = {}

def init(app=None, config=None):
    print("[KnowledgeMap] ready")

def record_concept(namespace, concept):
    lst = MAP.setdefault(namespace, [])
    entry = {"time": int(time.time()), "concept": concept}
    lst.append(entry)
    return entry

def list_concepts(namespace):
    return MAP.get(namespace, [])[-50:]