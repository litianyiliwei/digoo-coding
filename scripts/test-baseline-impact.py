#!/usr/bin/env python3
"""Regression checks for detailed-design versus implementation impact gates."""
import subprocess
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name('check-baseline-impact.py')
HEADINGS = '''## 1. Baseline Status Snapshot
## 2. Fixed-Read Verification
## 3. Impact-Based Read Verification
## 4. Reuse and Consistency Mapping
## 5. Change Ownership Classification
## 6. Baseline Conflicts, Gaps, and Candidate Amendments
## 7. In-Flight Change Version Review
## 8. Conclusion and Gates
'''


def record(implementation):
    implementation_line = '' if implementation is None else f'- Allowed to enter implementation: {implementation}\n'
    return HEADINGS + '''
- Status: APPROVED
- Current baseline version: test
- This Change baseline classification: CHANGE_ONLY
- Overall conclusion: COMPATIBLE
- Allowed to enter detailed design: YES
- Change ID: demo
- Approver and evidence: owner / evidence
''' + implementation_line


class BaselineImpactGateTests(unittest.TestCase):
    def run_checker(self, content):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'demo' / 'design' / 'baseline-impact.md'
            path.parent.mkdir(parents=True)
            path.write_text(content, encoding='utf-8')
            return subprocess.run(
                ['python', str(CHECKER), str(path), '--implementation'],
                capture_output=True, text=True, check=False)

    def test_implementation_gate_rejects_missing_explicit_decision(self):
        result = self.run_checker(record(None))
        self.assertNotEqual(0, result.returncode)
        self.assertIn('implementation gate recorded', result.stdout)

    def test_implementation_gate_rejects_explicit_no_even_when_design_is_allowed(self):
        result = self.run_checker(record('NO'))
        self.assertNotEqual(0, result.returncode)
        self.assertIn('blocks implementation', result.stdout)


if __name__ == '__main__':
    unittest.main()
