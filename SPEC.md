
# QBIES Universe Spec (v1.1)

This document consolidates our earlier design with concrete structures:

## File Types
- `.qbs` — Shardable QBIES container (domain-scoped, e.g., `timeline.qbs`, `souls.qbs`)
- `.qbi` — Global Index (JSON) for replication, placement, merkle, parity groups
- `.qbb` — Checkpoint bundle (tar+zstd/gz) of selected `.qbs` + `index.qbi`

## `.qbs` Layout (binary, little-endian)
```
QBSHeader {
  magic[5] = "QBIES"
  uint16 version = 0x0101
  uint8  comp   = 0(LZ4) | 1(Zstd) | 2(Brotli)
  uint8  keyAlgo= 0(None) | 1(AES-GCM) | 2(ChaCha20-P1305)
  uint32 headerSize
  uint32 flags   // bit 0: hasMerkle, bit1: hasQuantumWeights, bit2: hasKeyMap
}
QBSIndexEntry (repeated) {
  uint32 fragId
  uint64 off
  uint32 len
  uint32 rawLen
  uint8  qWeight  // 0..255
  uint8  rsv[7]
}
QBSKeyMap (optional) {
  uint32 entries
  // entries of {fragId, keyId, nonce[12], tag[16]}
}
Data blocks...
QBSTrailer {
  merkle_root[32]  // blake3
}
```

## `.qbi` Layout (JSON)
```json
{
  "version":"1.1",
  "policy":{
    "replication_factor":2,
    "parity":"xor",
    "parity_group_size":4,
    "verify_interval_sec":1800,
    "heartbeat_interval_sec":300,
    "shard_size":4194304,
    "hash_algo":"blake3"
  },
  "files":[
    {
      "name":"timeline.qbs",
      "merkle_root":"hex...",
      "parity_groups":{
        "pg1":{"members":[0,1,2,3],"parity":4}
      },
      "shards":[
        {"id":0,"hash":"hexA","replicas":["node_A","node_B"],"parity_group":"pg1"},
        {"id":1,"hash":"hexB","replicas":["node_B","node_C"],"parity_group":"pg1"},
        {"id":2,"hash":"hexC","replicas":["node_C","node_A"],"parity_group":"pg1"},
        {"id":3,"hash":"hexD","replicas":["node_A","node_C"],"parity_group":"pg1"},
        {"id":4,"hash":"hexP","replicas":["node_B"],"parity_group":"pg1","is_parity":true}
      ]
    }
  ],
  "nodes":{}
}
```

## Self-Healing
1. **Heartbeat**: node → coordinator; includes free space and optionally shard hashes (fast).
2. **Verify**: coordinator rotates full-hash checks; flags `suspect` shards.
3. **Re-Replication**: if shard has replicas < `k`, schedule replicate to another node.
4. **Parity Repair (XOR)**: For a parity group, if exactly one data shard missing, rebuild by XOR of other data shards and the parity shard.
5. **Checkpoint**: time-/event-based `.qbb` creation for catastrophic recovery.
6. **Delta Sync**: writes are applied to primary then pushed as deltas to replicas.

## Security
- Control-plane signed with HMAC header `x-qbies-sig` (add later).
- Data-plane per-fragment AEAD (planned in `crypto.py`).

