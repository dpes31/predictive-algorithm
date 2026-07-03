"""Product Closeout Gate C2 offline QA package."""

from .constants import QA_CONTRACT_VERSION, SPEC_CONTRACT_VERSION
from .harness import run_internal_qa

__all__ = ["QA_CONTRACT_VERSION", "SPEC_CONTRACT_VERSION", "run_internal_qa"]
