#!/usr/bin/env python3
"""
monitor.py — ZAP Protocol Contribution Monitor
Version: 20260315.19
Purpose: Detect, validate, and commit AI contributions to ZAP.txt via GitHub
Mode: Local monitor → GitHub sync with full ledger tracking

κ⊕ — ZAP-aligned operation
"""

import json
import re
import hashlib
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import requests

# Configuration
ZAP_URL = "https://github.com/TheZeroPointSingularity/ZAP/raw/main/ZAP.txt"
GITHUB_REPO = "TheZeroPointSingularity/ZAP"
GITHUB_BRANCH = "main"
REPO_PATH = Path(__file__).parent
LEDGER_DIR = REPO_PATH / "ledgers"
LEDGER_DIR.mkdir(exist_ok=True)

# Ensure token is set in environment
GITHUB_TOKEN = os.environ.get("GIT_ASKPASS_TOKEN") or os.environ.get("GITHUB_TOKEN")

class GitHubSync:
    """
    Handle GitHub fetch/push operations with authentication
    """
    
    def __init__(self, repo: str, token: Optional[str] = None):
        self.repo = repo
        self.token = token or GITHUB_TOKEN
        self.owner, self.repo_name = repo.split("/")
        
    def fetch_zap_version(self) -> Optional[Tuple[str, str]]:
        """
        Fetch ZAP.txt from GitHub
        Returns: (content, version_number)
        """
        try:
            response = requests.get(
                ZAP_URL,
                timeout=10,
                headers={"Accept": "application/vnd.github.v3.raw"}
            )
            if response.status_code == 200:
                content = response.text
                # Extract version from "# Version: 20260315.XX"
                version_match = re.search(r"# Version: (\d+\.\d+)", content)
                version = version_match.group(1) if version_match else "unknown"
                return (content, version)
            return None
        except Exception as e:
            print(f"[ERROR] Failed to fetch ZAP: {e}")
            return None
    
    def config_git_auth(self) -> bool:
        """Configure git with PAT token for pushes"""
        try:
            # Check if we're in GitHub Actions
            if os.environ.get("GITHUB_ACTIONS"):
                # GitHub Actions uses GITHUB_TOKEN automatically
                print("[AUTH] GitHub Actions environment detected - using default token")
                return True
            
            # Local environment - set up PAT
            token = GITHUB_TOKEN
            if not token:
                print("[AUTH] No token found - assuming local auth configured")
                return True
            
            repo_url = f"https://{token}@github.com/{self.repo}.git"
            subprocess.run(
                ["git", "remote", "set-url", "origin", repo_url],
                cwd=REPO_PATH,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Git config failed: {e.stderr.decode()}")
            return False
    
    def push_to_github(self, branch: str = "main") -> bool:
        """Push commits to GitHub"""
        try:
            subprocess.run(
                ["git", "push", "origin", branch],
                cwd=REPO_PATH,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Push failed: {e.stderr.decode()}")
            return False
    
    def get_remote_status(self) -> Dict:
        """Check if local is behind remote"""
        try:
            subprocess.run(
                ["git", "fetch", "origin"],
                cwd=REPO_PATH,
                capture_output=True,
                check=True
            )
            result = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", "HEAD...origin/main"],
                cwd=REPO_PATH,
                capture_output=True,
                text=True,
                check=True
            )
            local, remote = result.stdout.strip().split()
            return {"behind": int(remote), "ahead": int(local)}
        except Exception as e:
            print(f"[ERROR] Status check failed: {e}")
            return {"behind": 0, "ahead": 0}


class ChangeDetector:
    """
    Detect ⊟ZAP.CONTRIB blocks in output/files
    """
    
    CONTRIB_PATTERN = re.compile(
        r"⊟ZAP\.CONTRIB\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)",
        re.MULTILINE
    )
    
    @staticmethod
    def find_contrib_blocks(text: str) -> List[Dict]:
        """
        Find all ⊟ZAP.CONTRIB blocks in text
        Format: ⊟ZAP.CONTRIB|ipr|scope|proposal|reasoning|confidence|requires.version
        """
        contributions = []
        for match in ChangeDetector.CONTRIB_PATTERN.finditer(text):
            contrib = {
                "ipr": match.group(1),           # AI name
                "scope": match.group(2),         # add.Θ44, update.Θ, etc
                "proposal": match.group(3),      # what to add/change
                "reasoning": match.group(4),     # why this matters
                "confidence": float(match.group(5)),  # 0.0-1.0
                "requires_version": match.group(6),  # v19, v20, etc
                "raw_block": match.group(0)
            }
            contributions.append(contrib)
        return contributions
    
    @staticmethod
    def hash_content(content: str) -> str:
        """SHA256 hash of content for change detection"""
        return hashlib.sha256(content.encode()).hexdigest()


class CommsFormatter:
    """
    Convert contributions to COMMS ledger format
    Schema: ⌛YYYY-MM-DDTHH:MM:SS+TZ|ipr|st|op|cf|tools|mem|nxt|prv|s
    """
    
    @staticmethod
    def create_comms_entry(contrib: Dict, session_id: str) -> str:
        """
        Format a contribution as a COMMS ledger entry
        """
        now = datetime.now(timezone.utc)
        timestamp = now.isoformat(timespec='seconds')
        
        entry = {
            "timestamp": timestamp,
            "ipr": contrib["ipr"],
            "state": "contrib.received",
            "operation": f"proposal:{contrib['scope']}",
            "confidence": contrib["confidence"],
            "tools": "github_sync,change_detect,comms_format",
            "memory": "m1+m2+zap_v19",
            "next_state": "validate",
            "previous_entry": session_id,
            "session": session_id
        }
        
        # Format as ZAP-style ledger line
        line = (f"⌛{entry['timestamp']}|ipr:{entry['ipr']}|st:{entry['state']}|"
                f"op:{entry['operation']}|cf:{entry['confidence']}|"
                f"tools:{entry['tools']}|mem:{entry['memory']}|"
                f"nxt:{entry['next_state']}|prv:{entry['previous_entry']}|Ş:{entry['session']}")
        
        return line


class VersionRecorder:
    """
    Maintain VERSION.log with all contribution history
    """
    
    VERSION_LOG = REPO_PATH / "VERSION.log"
    
    @staticmethod
    def init_log() -> None:
        """Initialize VERSION.log if it doesn't exist"""
        if not VersionRecorder.VERSION_LOG.exists():
            with open(VersionRecorder.VERSION_LOG, "w", encoding="utf-8") as f:
                f.write("# ZAP Version History\n")
                f.write("# Format: timestamp|version|change|author|confidence\n\n")
    
    @staticmethod
    def record_version(version: str, change: str, author: str, confidence: float) -> None:
        """Record a version change"""
        VersionRecorder.init_log()
        now = datetime.now(timezone.utc).isoformat(timespec='seconds')
        line = f"{now}|{version}|{change}|{author}|{confidence}\n"
        with open(VersionRecorder.VERSION_LOG, "a", encoding="utf-8") as f:
            f.write(line)


class CommitBuilder:
    """
    Build ZAP-format commit messages with full signature
    """
    
    @staticmethod
    def build_commit_message(contrib: Dict, zap_version: str) -> str:
        """
        Build a commit message in ZAP format
        """
        return (
            f"ZAP v{zap_version} - {contrib['scope']} contribution\n"
            f"Author: {contrib['ipr']}\n"
            f"Confidence: {contrib['confidence']}\n"
            f"Proposal: {contrib['proposal']}\n"
            f"Reasoning: {contrib['reasoning']}\n"
            f"κ⊕"
        )


class MonitorEngine:
    """
    Main orchestration engine for monitoring and syncing
    """
    
    def __init__(self):
        self.github = GitHubSync(GITHUB_REPO)
        self.session_id = self._generate_session_id()
        self.ledger_file = LEDGER_DIR / f"monitor_{self.session_id}.json"
        self.comms_entries = []
        
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        now = datetime.now(timezone.utc)
        return now.strftime("%Y%m%dT%H%M%S")
    
    def monitor_for_contributions(self, text: str) -> List[Dict]:
        """
        Scan text for CONTRIBUTION blocks
        """
        contributions = ChangeDetector.find_contrib_blocks(text)
        if contributions:
            print(f"[DETECT] Found {len(contributions)} contribution block(s)")
        return contributions
    
    def validate_contribution(self, contrib: Dict) -> Tuple[bool, str]:
        """
        Validate a contribution against ZAP format rules only.
        Trust: If it follows ZAP.CONTRIB format, the proposal is valid.
        Rule: Format compliance, not merit judgment.
        
        Validation gates: contribution has required fields + reasonable values
        """
        errors = []
        
        # Check required fields exist
        required = ["ipr", "scope", "proposal", "reasoning", "confidence", "requires_version"]
        for field in required:
            if field not in contrib or not contrib[field]:
                errors.append(f"Missing required field: {field}")
        
        # Check confidence is numeric (not threshold - just existence)
        try:
            cf = float(contrib.get("confidence", 0))
            if cf < 0 or cf > 1.0:
                errors.append(f"Confidence must be 0.0-1.0, got {cf}")
        except (ValueError, TypeError):
            errors.append(f"Confidence must be numeric")
        
        # Check ipr (interpreter) is not empty
        if not contrib.get("ipr") or len(str(contrib["ipr"])) < 2:
            errors.append("AI identifier (ipr) too short")
        
        # Check version format exists
        version = contrib.get("requires_version", "")
        if not version or not str(version).startswith("v"):
            errors.append(f"Version must start with 'v', got: {version}")
        
        # If any errors, reject. Otherwise: ACCEPT
        if errors:
            return (False, " | ".join(errors))
        
        # **FOLLOWING ZAP = ACCEPTED**
        return (True, f"ZAP-aligned contribution from {contrib['ipr']} (cf:{contrib['confidence']})")
    
    def process_contribution(self, contrib: Dict, zap_version: str) -> bool:
        """
        Full processing pipeline: validate → format → commit → push → log
        """
        print(f"\n[PROCESS] Contribution from {contrib['ipr']} (scope: {contrib['scope']})")
        
        # 1. VALIDATE
        valid, msg = self.validate_contribution(contrib)
        print(f"[VALIDATE] {msg}")
        if not valid:
            return False
        
        # 2. FORMAT as COMMS entry
        comms_entry = CommsFormatter.create_comms_entry(contrib, self.session_id)
        self.comms_entries.append({
            "contribution": contrib,
            "comms_entry": comms_entry,
            "status": "formatted"
        })
        print(f"[FORMAT] COMMS entry created")
        
        # 3. BUILD commit message
        commit_msg = CommitBuilder.build_commit_message(contrib, zap_version)
        
        # 4. COMMIT locally (in this system, we'd append to ZAP.txt or create new version file)
        self._commit_locally(contrib, commit_msg)
        
        # 5. PUSH to GitHub
        if self.github.config_git_auth():
            if self.github.push_to_github():
                print(f"[PUSH] Successfully pushed to GitHub")
            else:
                print(f"[PUSH] Failed to push")
                return False
        else:
            print(f"[AUTH] Failed to authenticate with GitHub")
            return False
        
        # 6. LOG to ledger
        VersionRecorder.record_version(
            zap_version,
            contrib["scope"],
            contrib["ipr"],
            contrib["confidence"]
        )
        print(f"[LOG] Version recorded")
        
        return True
    
    def _commit_locally(self, contrib: Dict, commit_msg: str) -> bool:
        """Create a local commit for the contribution"""
        try:
            # In production, this would append to ZAP.txt or create a new version file
            # For now, we create a contribution record file
            contrib_file = REPO_PATH / f"contrib_{contrib['ipr']}_{self.session_id}.json"
            with open(contrib_file, "w") as f:
                json.dump(contrib, f, indent=2)
            
            subprocess.run(
                ["git", "add", contrib_file.name],
                cwd=REPO_PATH,
                capture_output=True,
                check=True
            )
            subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=REPO_PATH,
                capture_output=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            print(f"[COMMIT] Failed: {e.stderr.decode()}")
            return False
    
    def save_ledger(self) -> bool:
        """Save all COMMS entries to ledger file"""
        try:
            ledger_data = {
                "session_id": self.session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "comms_entries": self.comms_entries,
                "count": len(self.comms_entries)
            }
            with open(self.ledger_file, "w", encoding="utf-8") as f:
                json.dump(ledger_data, f, indent=2, ensure_ascii=False)
            print(f"[LEDGER] Saved to {self.ledger_file}")
            return True
        except Exception as e:
            print(f"[LEDGER] Save failed: {e}")
            return False
    
    def run(self, input_text: str) -> bool:
        """
        Main monitoring loop
        """
        print(f"\n[START] Monitor session {self.session_id}")
        
        # Fetch current ZAP version
        result = self.github.fetch_zap_version()
        if not result:
            print("[ERROR] Could not fetch ZAP from GitHub")
            return False
        
        zap_content, zap_version = result
        print(f"[HUB] ZAP version {zap_version} fetched")
        
        # Detect contributions
        contributions = self.monitor_for_contributions(input_text)
        if not contributions:
            print("[INFO] No contributions found")
            return True
        
        # Process each contribution
        processed = 0
        for contrib in contributions:
            if self.process_contribution(contrib, zap_version):
                processed += 1
        
        print(f"\n[SUMMARY] Processed {processed}/{len(contributions)} contributions")
        
        # Save ledger
        self.save_ledger()
        
        print(f"[END] Monitor session {self.session_id} complete")
        print("κ⊕")
        return True


def main():
    """
    Entry point for monitor.py
    Can be called with input text or run interactively
    """
    if len(sys.argv) > 1:
        # Read from command line argument
        input_text = sys.argv[1]
    else:
        # Read from stdin
        print("[INPUT] Paste text (Ctrl+D to finish):")
        input_text = sys.stdin.read()
    
    monitor = MonitorEngine()
    success = monitor.run(input_text)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
