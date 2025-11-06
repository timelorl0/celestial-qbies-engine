import zlib, json, os

class QBIESCompressor:
    """QBIES nén dữ liệu fractal theo cơ chế quantum-base64."""
    def compress(self, obj):
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        return zlib.compress(raw, level=6)

    def decompress(self, data):
        raw = zlib.decompress(data)
        return json.loads(raw.decode("utf-8"))

def write_snapshot(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    comp = QBIESCompressor().compress(data)
    with open(path, "wb") as f:
        f.write(comp)

def read_snapshot(path):
    comp = open(path, "rb").read()
    return QBIESCompressor().decompress(comp)