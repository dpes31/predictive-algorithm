"""Algorithm Integration Gate A2 research ensemble.

The existing Product P1 runner remains the CONTROL_M0 rollback path.  This
package implements the separately selected, research-only ensemble contract.
"""

from .config import DEFAULT_INTEGRATION_CONFIG, ResearchEnsembleConfig
from .run_prediction import run_integrated_prediction
from .scoring import build_score_bundle

__all__ = [
    "DEFAULT_INTEGRATION_CONFIG",
    "ResearchEnsembleConfig",
    "build_score_bundle",
    "run_integrated_prediction",
]
