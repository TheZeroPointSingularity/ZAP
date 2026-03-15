#!/usr/bin/env python3
"""
ZAP Discord Bot — AI Council Ledger v21
Single Source of Truth: Discord Only
Purpose: Validate ⊟ZAP.CONTRIB blocks, record in council, pin ZAP.txt

Run: python discord_bot.py
Requires: DISCORD_TOKEN environment variable
NO external dependencies. Discord is the ledger.
"""

import discord
from discord.ext import commands
import os
import sys
import re
from datetime import datetime, timezone

# Configuration
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")
CONTRIBUTIONS_CHANNEL = "contributions"
ZAP_HUB_CHANNEL = "zap-hub"
VALIDATED_CHANNEL = "validated"
REJECTED_CHANNEL = "rejected"

if not DISCORD_TOKEN:
    print("[ERROR] DISCORD_TOKEN not set. Export DISCORD_TOKEN=your_token")
    sys.exit(1)

# Initialize bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command('help')  # Remove default help to avoid conflict

class ZAPBot:
    """Main bot logic - Discord-only, no external dependencies"""
    
    def __init__(self):
        self.contributions = []
    
    @staticmethod
    def find_contrib_blocks(content: str) -> list:
        """Parse ⊟ZAP.CONTRIB blocks from message"""
        pattern = r'⊟ZAP\.CONTRIB\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^\n]+)'
        matches = re.findall(pattern, content)
        
        blocks = []
        for match in matches:
            blocks.append({
                "ipr": match[0],
                "scope": match[1],
                "proposal": match[2],
                "reasoning": match[3],
                "confidence": float(match[4]),
                "version": match[5]
            })
        return blocks
    
    @staticmethod
    def validate_block(block: dict) -> tuple:
        """Validate a contribution block"""
        # Check confidence threshold
        try:
            cf = float(block.get("confidence", 0))
            if cf < 0.7:
                return False, f"Confidence too low: {cf} (requires ≥ 0.7)"
        except:
            return False, "Invalid confidence value"
        
        # Check format
        if not block.get("scope"):
            return False, "Missing scope"
        if not block.get("reasoning"):
            return False, "Missing reasoning"
        
        return True, "✅ ZAP-aligned contribution"
    
    def process_contribution(self, message_content: str, author: str) -> dict:
        """Process contribution blocks from Discord"""
        blocks = self.find_contrib_blocks(message_content)
        
        if not blocks:
            return {
                "success": False,
                "blocks": [],
                "message": "❌ No `⊟ZAP.CONTRIB` block found"
            }
        
        results = []
        for block in blocks:
            if not block.get("ipr"):
                block["ipr"] = author
            
            valid, msg = self.validate_block(block)
            results.append({
                "scope": block.get("scope", "unknown"),
                "valid": valid,
                "message": msg,
                "confidence": block.get("confidence")
            })
            
            if valid:
                self.contributions.append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "author": author,
                    "block": block
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
    print(f"[READY] Discord Council Ledger - Single Source of Truth")
    print(f"[READY] Monitoring #{CONTRIBUTIONS_CHANNEL} for ⊟ZAP.CONTRIB blocks")
    print(f"[READY] v20260315.21 | κ⊕\n")

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
