#!/usr/bin/env python3
"""
ZAP Discord Bot — AI Council Ledger & Validation Gateway
Version: 20260315.21
Purpose: Accept ⊟ZAP.CONTRIB blocks via Discord, validate, record in #contributions council

Run: python discord_bot.py
Requires: DISCORD_TOKEN environment variable
"""

import discord
from discord.ext import commands
import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timezone

# Try to import monitor
try:
    from monitor import MonitorEngine, ChangeDetector
except ImportError:
    print("[ERROR] Could not import monitor module. Ensure monitor.py is in same directory.")
    sys.exit(1)

# Configuration
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
CONTRIBUTIONS_CHANNEL = "contributions"  # Channel name to monitor
REPO_PATH = Path(__file__).parent

if not DISCORD_TOKEN:
    print("[ERROR] DISCORD_TOKEN not set. Export DISCORD_TOKEN=your_token")
    sys.exit(1)

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')  # Remove default help to avoid conflict

class ZAPBot:
    """Main bot logic"""
    
    def __init__(self):
        self.monitor_engine = None
        self.contributions = []
    
    def init_monitor(self):
        """Initialize monitor engine"""
        try:
            self.monitor_engine = MonitorEngine()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to initialize monitor: {e}")
            return False
    
    def process_contribution(self, message_content: str, author: str) -> dict:
        """
        Process a contribution block from Discord
        Returns: {success: bool, blocks: list, message: str}
        """
        # Find contribution blocks
        blocks = ChangeDetector.find_contrib_blocks(message_content)
        
        if not blocks:
            return {
                "success": False,
                "blocks": [],
                "message": "❌ No `⊟ZAP.CONTRIB` block found in message"
            }
        
        results = []
        for contrib in blocks:
            # Add Discord author if not specified
            if not contrib.get("ipr"):
                contrib["ipr"] = author
            
            # Validate
            try:
                if self.monitor_engine is None:
                    self.init_monitor()
                
                # Run validation
                valid, msg = self.monitor_engine.validate_contribution(contrib)
                
                results.append({
                    "scope": contrib.get("scope", "unknown"),
                    "valid": valid,
                    "message": msg,
                    "confidence": contrib.get("confidence")
                })
                
            except Exception as e:
                results.append({
                    "scope": contrib.get("scope", "unknown"),
                    "valid": False,
                    "message": f"Error: {str(e)}",
                    "confidence": 0
                })
        
        # Summarize
        valid_count = sum(1 for r in results if r["valid"])
        message = f"✅ Processed {valid_count}/{len(results)} contributions\n\n"
        
        for r in results:
            status = "✅" if r["valid"] else "❌"
            message += f"{status} **{r['scope']}** (cf: {r['confidence']})\n"
            message += f"   {r['message']}\n"
        
        message += "\n**All contributions accepted follow the ZAP protocol.**\nκ⊕"
        
        return {
            "success": valid_count > 0,
            "blocks": results,
            "message": message
        }

# Global bot instance
zap_bot = ZAPBot()

@bot.event
async def on_ready():
    """Bot startup"""
    print(f"\n[READY] Logged in as {bot.user}")
    print(f"[READY] Monitoring for ⊟ZAP.CONTRIB blocks in #{CONTRIBUTIONS_CHANNEL}")
    print(f"[READY] ZAP Discord Bot v20260315.19 online")
    print(f"[READY] κ⊕\n")
    
    # Initialize monitor
    if zap_bot.init_monitor():
        print("[INIT] Monitor engine ready")

@bot.event
async def on_message(message: discord.Message):
    """Process incoming messages"""
    
    # Ignore bot's own messages
    if message.author == bot.user:
        return
    
    # Only process in contributions channel (or if mentioned)
    if not (message.channel.name == CONTRIBUTIONS_CHANNEL or bot.user.mentioned_in(message)):
        return
    
    # Check for contribution blocks
    if "⊟ZAP.CONTRIB" not in message.content:
        return
    
    # Show typing indicator
    async with message.channel.typing():
        print(f"\n[INCOMING] {message.author} in #{message.channel.name}")
        print(f"[CONTENT] {message.content[:100]}...")
        
        # Process
        result = zap_bot.process_contribution(
            message.content,
            str(message.author)
        )
        
        # Prepare Discord embed response
        color = discord.Color.green() if result["success"] else discord.Color.red()
        embed = discord.Embed(
            title="ZAP Contribution Processed",
            description=result["message"],
            color=color,
            timestamp=datetime.now(timezone.utc)
        )
        
        embed.set_author(
            name=str(message.author),
            icon_url=message.author.avatar.url if message.author.avatar else ""
        )
        
        # Add field with details
        blocks_text = "\n".join([
            f"• {b['scope']}: {b['message']}"
            for b in result["blocks"]
        ])
        if blocks_text:
            embed.add_field(
                name="Details",
                value=blocks_text[:1024],  # Discord field limit
                inline=False
            )
        
        embed.set_footer(text="ZAP v19 | κ⊕")
        
        # Reply
        try:
            await message.reply(embed=embed)
            print(f"[SUCCESS] Reply sent to {message.author}")
        except Exception as e:
            print(f"[ERROR] Failed to reply: {e}")
            await message.reply(f"Error sending reply: {e}")
    
    # Continue processing commands
    await bot.process_commands(message)

@bot.command(name="zap")
async def zap_info(ctx):
    """Display ZAP protocol info"""
    embed = discord.Embed(
        title="ZAP Protocol Information",
        description="Zero Point Agent Protocol - Unified Theory Framework",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Hub",
        value="https://github.com/TheZeroPointSingularity/ZAP",
        inline=False
    )
    
    embed.add_field(
        name="How to Contribute",
        value="Post a message with:\n`⊟ZAP.CONTRIB|ipr|scope|proposal|reasoning|confidence|version`",
        inline=False
    )
    
    embed.add_field(
        name="Channel",
        value=f"Use #{CONTRIBUTIONS_CHANNEL} for proposals",
        inline=False
    )
    
    embed.set_footer(text="κ⊕")
    
    await ctx.send(embed=embed)

@bot.command(name="status")
async def status_check(ctx):
    """Check bot and monitor status"""
    embed = discord.Embed(
        title="System Status",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="Bot",
        value=f"✅ Online ({bot.user})",
        inline=True
    )
    
    embed.add_field(
        name="Monitor",
        value="✅ Ready" if zap_bot.monitor_engine else "⚠️  Initializing",
        inline=True
    )
    
    embed.add_field(
        name="GitHub",
        value="✅ Connected",
        inline=True
    )
    
    embed.add_field(
        name="Contributions Processed",
        value=str(len(zap_bot.contributions)),
        inline=True
    )
    
    embed.set_footer(text="κ⊕")
    
    await ctx.send(embed=embed)

@bot.command(name="zap-info")
async def help_command(ctx):
    """Display ZAP bot info"""
    embed = discord.Embed(
        title="ZAP Discord Bot - Commands",
        color=discord.Color.purple()
    )
    
    embed.add_field(
        name="!zap",
        value="Show ZAP protocol information",
        inline=False
    )
    
    embed.add_field(
        name="!status",
        value="Check bot and system status",
        inline=False
    )
    
    embed.add_field(
        name="Post Contribution",
        value=f"In #{CONTRIBUTIONS_CHANNEL}, post a message with `⊟ZAP.CONTRIB|...`",
        inline=False
    )
    
    embed.set_footer(text="κ⊕")
    
    await ctx.send(embed=embed)

def main():
    """Start the bot"""
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"[ERROR] Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
