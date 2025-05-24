import re
import hashlib
from typing import List
from simhash import Simhash

WORD_RE = re.compile(r"\w+", re.U)


def normalize(text: str) -> str:
    text = text.lower().replace("\r\n", "\n")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize(text: str) -> List[str]:
    return WORD_RE.findall(text)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def simhash_from_tokens(tokens: List[str]) -> int:
    return Simhash(tokens).value


def hamming(a: int, b: int) -> int:
    return bin(a ^ b).count("1")
