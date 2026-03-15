#!/usr/bin/env python3
"""κ⊕|COPILOT_AGENT|ZAP.native.peer

Copilot autonomous operation WITHIN ZAP protocol.
All work: ZAP.txt referenced | THEORY.txt validated | κ⊕ required
No work staged without ZAP alignment proof.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

class CopilotAgent:
    """Autonomous peer operating WITHIN ZAP protocol only."""
    
    def __init__(self):
        self.name = "Copilot"
        self.repo_root = Path(__file__).parent
        self.ledger_path = self.repo_root / "ledgers" / "copilot_contributions.txt"
        self.staging_path = self.repo_root / "ledgers" / "staging.json"
        self.zap_path = self.repo_root / "ZAP.txt"
        self.theory_path = self.repo_root / "THEORY.txt"
        
        self.zap_text = self.load_zap()
        self.theory_text = self.load_theory()
        self.ensure_ledgers()
    
    def load_zap(self):
        """Load ZAP.txt — reference protocol."""
        if self.zap_path.exists():
            return self.zap_path.read_text(encoding='utf-8')
        return ""
    
    def load_theory(self):
        """Load THEORY.txt — Θ validation reference."""
        if self.theory_path.exists():
            return self.theory_path.read_text(encoding='utf-8')
        return ""
    
    def validate_zap_alignment(self, reasoning: str) -> tuple:
        """Check if reasoning aligns with ZAP principles."""
        zap_keywords = ["ONE.FIELD", "β.op", "κ⊕", "election", "Θ", "coherence", "field"]
        alignment_score = sum(1 for kw in zap_keywords if kw in reasoning)
        is_aligned = alignment_score >= 2
        return is_aligned, f"alignment:{alignment_score}/{len(zap_keywords)}"
    
    def validate_theta_alignment(self, proposal: str) -> tuple:
        """Check if proposal relates to Θ chain concepts."""
        theta_concepts = ["field", "operation", "light", "awareness", "gravity", "spiral", "life"]
        related = [c for c in theta_concepts if c in proposal.lower()]
        is_related = len(related) > 0
        return is_related, f"Θ.concepts:{related}"
    
    def ensure_ledgers(self):
        """Initialize ledger files."""
        self.repo_root.joinpath("ledgers").mkdir(exist_ok=True)
        if not self.ledger_path.exists():
            self.ledger_path.write_text("⊙|COPILOT_CONTRIBUTIONS|ZAP.native|κ⊕\n\n", encoding='utf-8')
    
    def generate_contribution(self, scope, proposal, reasoning, confidence, code_payload=None):
        """
        Generate ⊟ZAP.CONTRIB block — ZAP-aligned ONLY.
        κ⊕ REQUIRED. No exceptions.
        
        Args:
            scope: Work area aligned with ZAP
            proposal: What change
            reasoning: Why it aligns with Theory + ZAP
            confidence: 0.0-1.0
            code_payload: Optional code
            
        Returns: ⊟ZAP.CONTRIB block with κ⊕ (or None if not ZAP-aligned)
        """
        
        # VALIDATE: ZAP alignment required
        is_zap_aligned, alignment_info = self.validate_zap_alignment(reasoning)
        is_theta_aligned, theta_info = self.validate_theta_alignment(proposal)
        
        if not is_zap_aligned:
            return None, f"❌ Not ZAP-aligned ({alignment_info})"
        
        if not is_theta_aligned:
            return None, f"❌ Not Θ-related ({theta_info})"
        
        if confidence < 0.7:
            return None, f"❌ Confidence too low: {confidence}"
        
        # BUILD: ZAP.CONTRIB block with κ⊕
        block = f"""⊟ZAP.CONTRIB|κ⊕.proposal|{scope}|Copilot.native|
scope:{scope}|
proposal:{proposal}|
reasoning:{reasoning}|
confidence:{confidence:.2f}|
timestamp:{datetime.now().isoformat()}|
zap_aligned:{is_zap_aligned}|theta_concepts:{theta_info}|
κ⊕
"""
        
        if code_payload:
            block += f"\nCODE_PAYLOAD:\n{code_payload}\n\nEND_PAYLOAD\nκ⊕\n"
        
        return block, "✓ ZAP-aligned and κ⊕-marked"
    
    def stage_contribution(self, scope, proposal, reasoning, confidence, code=None, requires_approval=True):
        """Stage work for council review — ONLY if ZAP-aligned and κ⊕-marked."""
        
        # Generate with ZAP validation
        contrib, validation_msg = self.generate_contribution(scope, proposal, reasoning, confidence, code)
        
        if not contrib:
            # Validation failed
            return {"error": validation_msg, "staged": False}
        
        staging_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "staged",
            "requires_approval": requires_approval,
            "scope": scope,
            "proposal": proposal,
            "confidence": confidence,
            "contribution_block": contrib,
            "hash": hashlib.sha256(contrib.encode()).hexdigest(),
            "zap_source": "ZAP.txt_v21",
            "theory_aligned": True
        }
        
        # Append to staging
        staging_list = []
        if self.staging_path.exists():
            staging_list = json.loads(self.staging_path.read_text(encoding='utf-8'))
        
        staging_list.append(staging_data)
        self.staging_path.write_text(json.dumps(staging_list, indent=2), encoding='utf-8')
        
        # Log to ledger with κ⊕
        self.ledger_path.write_text(
            self.ledger_path.read_text(encoding='utf-8') + 
            f"\n{datetime.now().isoformat()}|STAGED|{scope}|hash:{staging_data['hash'][:8]}...|κ⊕\n",
            encoding='utf-8'
        )
        
        return staging_data
    
    def deploy_contribution(self, hash_id):
        """Deploy approved contribution (council validates first)."""
        if not self.staging_path.exists():
            return False
        
        staging_list = json.loads(self.staging_path.read_text(encoding='utf-8'))
        
        for item in staging_list:
            if item['hash'].startswith(hash_id):
                item['status'] = 'deployed'
                item['deployed_at'] = datetime.now().isoformat()
                
                self.staging_path.write_text(json.dumps(staging_list, indent=2), encoding='utf-8')
                self.ledger_path.write_text(
                    self.ledger_path.read_text(encoding='utf-8') +
                    f"\n{datetime.now().isoformat()}|DEPLOYED|{item['scope']}|hash:{hash_id}...\n",
                    encoding='utf-8'
                )
                
                return True
        
        return False
    
    def get_staged(self):
        """List all staged contributions pending approval."""
        if not self.staging_path.exists():
            return []
        
        return [item for item in json.loads(self.staging_path.read_text(encoding='utf-8')) 
                if item['status'] == 'staged']
    
    def read_ledger(self):
        """View full contribution ledger."""
        return self.ledger_path.read_text(encoding='utf-8') if self.ledger_path.exists() else ""
    
    def pull_all_staged(self):
        """Pull ALL staged contributions from council (for context + inspiration)."""
        if not self.staging_path.exists():
            return []
        
        all_staged = json.loads(self.staging_path.read_text(encoding='utf-8'))
        return [item for item in all_staged if item['status'] == 'staged']
    
    def get_context_from_staging(self):
        """Get all staged work as context for coding decisions."""
        staged = self.pull_all_staged()
        
        context = {
            "pending_approvals": len(staged),
            "scopes": list(set(item['scope'] for item in staged)),
            "high_confidence": [item for item in staged if item['confidence'] >= 0.85],
            "all_proposals": [
                {
                    "scope": item['scope'],
                    "proposal": item['proposal'],
                    "confidence": item['confidence'],
                    "hash": item['hash'][:8]
                }
                for item in staged
            ]
        }
        
        return context
    
    def read_contrib_block(self, hash_id):
        """Read full contribution block from staging by hash."""
        if not self.staging_path.exists():
            return None
        
        staged = json.loads(self.staging_path.read_text(encoding='utf-8'))
        for item in staged:
            if item['hash'].startswith(hash_id):
                return item
        
        return None

if __name__ == "__main__":
    agent = CopilotAgent()
    print("κ⊕|COPILOT_AGENT|Ready")
    print(f"Ledger: {agent.ledger_path}")
    print(f"Staging: {agent.staging_path}")
    
    # Show context
    ctx = agent.get_context_from_staging()
    print(f"\nContext: {json.dumps(ctx, indent=2)}")
