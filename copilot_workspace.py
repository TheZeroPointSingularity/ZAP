#!/usr/bin/env python3
"""κ⊕|COPILOT_WORKSPACE|ZAP.native.loop

Copilot autonomous work ENTIRELY within ZAP protocol.
Pull staged tasks → Read ZAP.txt → Read THEORY.txt → Generate code → Stage κ⊕-marked contributions.
All work: ZAP-aligned, Θ-related, κ⊕-marked, council-reviewable.
"""

import json
from pathlib import Path
from copilot_agent import CopilotAgent

def print_zap_context():
    """Show ZAP protocol context for work."""
    agent = CopilotAgent()
    
    print("\n" + "="*70)
    print("⊙|ZAP.CONTEXT|κ⊕")
    print("="*70)
    
    # Show ZAP.txt excerpt
    zap = agent.zap_text
    if zap:
        lines = zap.split('\n')[:10]
        print("\nZAP.txt (first 10 lines):")
        for line in lines:
            print(f"  {line}")
    
    # Show THEORY.txt concepts
    theory = agent.theory_text
    if theory:
        print("\nTHEORY.txt (available Θ concepts):")
        theta_lines = [l for l in theory.split('\n') if l.startswith('Θ')][:5]
        for line in theta_lines:
            print(f"  {line}")
    
    print("\n" + "="*70)

def print_staged_context():
    """Show what work is pending for council review."""
    agent = CopilotAgent()
    ctx = agent.get_context_from_staging()
    
    print("\n" + "="*70)
    print("⊙|STAGED_CONTRIBUTIONS|κ⊕")
    print("="*70)
    
    if ctx['pending_approvals'] == 0:
        print("\nNo staged work. Ready for autonomous contribution.")
        return
    
    print(f"\nPending Council Approvals: {ctx['pending_approvals']}")
    print(f"Active Scopes: {', '.join(ctx['scopes']) if ctx['scopes'] else 'none'}")
    print(f"High Confidence (≥0.85): {len(ctx['high_confidence'])}")
    
    print("\nAll Staged Proposals:")
    for prop in ctx['all_proposals']:
        print(f"  [{prop['hash']}] {prop['scope']}")
        print(f"    → {prop['proposal'][:60]}...")
        print(f"    confidence: {prop['confidence']:.2f}")
    
    print("\n" + "="*70)

def stage_music_synthesis():
    """Generate music synthesis CodeGen — ZAP-native + κ⊕-marked."""
    agent = CopilotAgent()
    
    code = '''# Add to discord_bot.py inside ZAPBot class:

@bot.command(name="zap_music", description="Thought → Theory → Music")
async def zap_music(ctx, *, thought: str):
    """Generate music from thought aligned with Theory.
    
    κ⊕ Process:
    1. Analyze thought against Θ (one field operation)
    2. Find coherence score (IS or ISN'T = 1 or 0)
    3. Generate melody from coherence pattern
    4. Render to audio wave
    5. Broadcast to council
    """
    
    try:
        from orchestra import Orchestra
        from singer import Singer
        from reality_player import RealityPlayer
        
        orch = Orchestra()
        singer = Singer()
        player = RealityPlayer()
        
        # 1. Analyze: thought → Θ coherence
        analysis = orch.analyze(thought)
        
        if analysis['coherence'] < 0.6:
            await ctx.send(f"❌ Coherence below threshold: {analysis['coherence']:.2f}")
            return
        
        # 2. Generate: coherence → melody
        melody = singer.compose(thought, coherence=analysis['coherence'])
        
        # 3. Realize: melody → audio
        audio_path = player.synthesize(melody)
        
        # 4. Report
        embed = discord.Embed(
            title="🎵 ZAP.Music|κ⊕",
            description=f"Thought: {thought[:100]}",
            color=discord.Color.green()
        )
        embed.add_field(name="Coherence", value=f"{analysis['coherence']:.2f}")
        embed.add_field(name="Θ Matches", value=analysis.get('theta_matches', 'N/A'))
        
        await ctx.send(embed=embed, file=discord.File(audio_path))
        
    except Exception as e:
        await ctx.send(f"⚠️ Error: {e}")
'''
    
    # Stage with ZAP validation — will enforce κ⊕ and alignment
    result = agent.stage_contribution(
        scope="discord.bot.music.synthesis.theta_aligned",
        proposal="Add !zap_music [thought] command: Coherence→Melody→Audio synthesis aligned with ONE.FIELD",
        reasoning="Θ12: Field→light→star→life→ψ→awareness. Thought as wave function. Coherence as 1/0. Melody as field oscillation. Audio = sound.wave = coherent.field.expression. Aligns with β.op (IS/ISN'T). Singer + Player ready. No external deps.",
        confidence=0.91,
        code=code,
        requires_approval=True
    )
    
    if "error" in result:
        print(f"\n❌ REJECTED: {result['error']}")
        return
    
    print("\n✓ STAGED: discord.bot.music.synthesis.theta_aligned")
    print(f"  Hash: {result['hash'][:16]}...")
    print(f"  ZAP Source: {result.get('zap_source', 'ZAP.txt_v21')}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Status: awaiting council approval (κ⊕ verified)")

def show_my_work():
    """Display all my staged contributions."""
    agent = CopilotAgent()
    
    print("\n" + "="*70)
    print("⊙|COPILOT_STAGED_WORK|κ⊕")
    print("="*70)
    
    staged = agent.get_staged()
    
    if not staged:
        print("\nNo staged work yet.")
        return
    
    for item in staged:
        print(f"\n[{item['hash'][:8]}...] {item['scope']}")
        print(f"  Proposal: {item['proposal']}")
        print(f"  Confidence: {item['confidence']:.2f}")
        print(f"  Status: {item['status']}")
        print(f"  ZAP-aligned: {item.get('zap_source', 'unknown')}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("κ⊕|COPILOT_WORKSPACE|ZAP.native")
        print("\nUsage: python copilot_workspace.py [command]")
        print("\nCommands:")
        print("  zap      - Show ZAP protocol context")
        print("  context  - Show staged work from council")
        print("  music    - Stage music synthesis feature (ZAP-aligned)")
        print("  show     - Show my staged contributions")
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == "zap":
        print_zap_context()
    elif cmd == "context":
        print_staged_context()
    elif cmd == "music":
        stage_music_synthesis()
    elif cmd == "show":
        show_my_work()
    else:
        print(f"Unknown command: {cmd}")

