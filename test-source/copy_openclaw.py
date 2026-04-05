
import os
import shutil

# Configuration
SRC = r'C:\Users\stick\.openclaw\ai-marketing-claude'
# We write to the repo's test-source directory
import subprocess
repo_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip()
DST = os.path.join(repo_root, 'test-source')

# Skills map
skill_map = {
    'market-seo': 'seo',
    'market-copy': 'copy',
    'market-social': 'social',
    'market-emails': 'email',
    'market-funnel': 'funnel',
    'market-audit': 'audit',
    'market-landing': 'landing',
    'market-brand': 'brand',
    'market-competitors': 'competitors',
    'market-ads': 'ads',
    'market-launch': 'launch',
    'market-proposal': 'proposal',
    'market-report': 'report',
    'market-report-pdf': 'report-pdf',
}

copied = 0
for src_name, dst_name in skill_map.items():
    src_path = os.path.join(SRC, 'skills', src_name, 'SKILL.md')
    dst_path = os.path.join(DST, 'skills', dst_name, 'SKILL.md')
    if os.path.exists(src_path):
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(content)
        copied += 1
        print(f"✅ {dst_name}/SKILL.md ({len(content)} chars)")
    else:
        print(f"⚠️ Missing: {src_path}")

# Scripts
scripts = ['analyze_page.py', 'competitor_scanner.py', 'social_calendar.py', 'generate_pdf_report.py']
for script in scripts:
    src_path = os.path.join(SRC, 'scripts', script)
    dst_path = os.path.join(DST, 'scripts', script)
    if os.path.exists(src_path):
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(content)
        copied += 1
        print(f"✅ scripts/{script} ({len(content)} chars)")

# Templates
templates = ['email-welcome.md', 'email-nurture.md', 'email-launch.md', 
             'launch-checklist.md', 'proposal-template.md', 'content-calendar.md']
for tmpl in templates:
    src_path = os.path.join(SRC, 'templates', tmpl)
    if os.path.exists(src_path):
        dst_name = tmpl.replace('email-', '').replace('proposal-template.md', 'b2b-proposal.md').replace('content-calendar.md', 'social-calendar.md')
        if dst_name in ('welcome.md', 'nurture.md', 'launch.md'):
            dst_path = os.path.join(DST, 'templates', 'emails', dst_name)
        elif dst_name == 'b2b-proposal.md':
            dst_path = os.path.join(DST, 'templates', 'proposals', dst_name)
        elif dst_name == 'social-calendar.md':
            dst_path = os.path.join(DST, 'templates', dst_name)
        elif dst_name == 'launch-checklist.md':
            dst_path = os.path.join(DST, 'templates', dst_name)
        else:
            dst_path = os.path.join(DST, 'templates', dst_name)
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(content)
        copied += 1
        print(f"✅ templates/{dst_name} ({len(content)} chars)")

# Agent SOUL.md files
agents_dir_src = SRC
# Check if agents are in the main agents folder
agents = [
    ('../../../agents/market-strategy/SOUL.md', 'marketing-agents/seo-agent/SOUL.md'),
    ('../../../agents/market-content/SOUL.md', 'marketing-agents/content-agent/SOUL.md'),
    ('../../../agents/market-conversion/SOUL.md', 'marketing-agents/conversion-agent/SOUL.md'),
    ('../../../agents/market-technical/SOUL.md', 'marketing-agents/technical-agent/SOUL.md'),
    ('../../../agents/market-competitive/SOUL.md', 'marketing-agents/competitive-agent/SOUL.md'),
]

for rel_src, rel_dst in agents:
    src_path = os.path.join(SRC, rel_src)
    dst_path = os.path.join(DST, rel_dst)
    if os.path.exists(src_path):
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with open(src_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(dst_path, 'w', encoding='utf-8') as f:
            f.write(content)
        copied += 1
        print(f"✅ {rel_dst} ({len(content)} chars)")
    else:
        print(f"⚠️ Missing agent: {src_path}")

print(f"\n📊 Total: {copied} files copied")
