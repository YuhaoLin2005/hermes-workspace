"""Pre-register Causal Swap v2 experiment protocol.

Usage: python pre_register.py
Output: SHA256 hash of protocol.md → stored in pre_reg_hash.txt
Do NOT modify protocol.md after this step.
"""
import hashlib
from pathlib import Path
from datetime import datetime

PROTOCOL = Path(__file__).parent / "protocol.md"
HASH_FILE = Path(__file__).parent / "pre_reg_hash.txt"

content = PROTOCOL.read_text(encoding="utf-8")
digest = hashlib.sha256(content.encode("utf-8")).hexdigest()

HASH_FILE.write_text(
    f"# Pre-Registration Hash\n"
    f"# Generated: {datetime.now().isoformat()}\n"
    f"# File hashed: protocol.md\n"
    f"# DO NOT MODIFY protocol.md AFTER THIS POINT\n"
    f"SHA256: {digest}\n",
    encoding="utf-8"
)

seed = int(digest[:16], 16)

print(f"SHA256: {digest}")
print(f"Random seed (from hash): {seed}")
print(f"Hash saved to: {HASH_FILE}")
print("\n⚠️  protocol.md is now FROZEN. Do not edit before running the experiment.")
