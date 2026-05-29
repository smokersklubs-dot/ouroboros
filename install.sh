#!/usr/bin/env bash
# Ouroboros — Local Installer
# Usage: bash install.sh
# Supports: Linux, macOS

set -euo pipefail

# ── colours ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; BOLD='\033[1m'; NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $*"; }
warn() { echo -e "${YELLOW}⚠${NC}  $*"; }
err()  { echo -e "${RED}✗${NC} $*" >&2; }
info() { echo -e "${BLUE}→${NC} $*"; }
hr()   { echo -e "${BLUE}────────────────────────────────────────────────────${NC}"; }

# ── banner ───────────────────────────────────────────────────────────────────
clear
echo -e "${BOLD}"
echo "  ██████╗ ██╗   ██╗██████╗  ██████╗ ██████╗  ██████╗ ██████╗  ██████╗ ███████╗"
echo "  ██╔══██╗██║   ██║██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗██╔══██╗██╔═══██╗██╔════╝"
echo "  ██║  ██║██║   ██║██████╔╝██║   ██║██████╔╝██║   ██║██████╔╝██║   ██║███████╗"
echo "  ██║  ██║██║   ██║██╔══██╗██║   ██║██╔══██╗██║   ██║██╔══██╗██║   ██║╚════██║"
echo "  ██████╔╝╚██████╔╝██║  ██║╚██████╔╝██████╔╝╚██████╔╝██║  ██║╚██████╔╝███████║"
echo "  ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝"
echo -e "${NC}"
echo -e "${BOLD}  Self-creating AI agent — Local Installer${NC}"
hr
echo ""

# ── prereq checks ────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}Checking prerequisites…${NC}"
hr

PYTHON=""
for cmd in python3.12 python3.11 python3.10 python3 python; do
    if command -v "$cmd" &>/dev/null; then
        ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "0.0")
        maj=$(echo "$ver" | cut -d. -f1)
        min=$(echo "$ver" | cut -d. -f2)
        if [ "$maj" -ge 3 ] && [ "$min" -ge 10 ]; then
            PYTHON="$cmd"
            ok "Python $ver  ($cmd)"
            break
        fi
    fi
done
if [ -z "$PYTHON" ]; then
    err "Python 3.10+ is required but was not found."
    echo "  Install it from https://www.python.org/downloads/"
    exit 1
fi

if ! command -v git &>/dev/null; then
    err "git is not installed."
    exit 1
fi
ok "git $(git --version | awk '{print $3}')"

if command -v node &>/dev/null; then
    ok "Node.js $(node --version)  (optional, for Claude Code CLI)"
    HAS_NODE=1
else
    warn "Node.js not found — Claude Code CLI (optional) won't be installed."
    HAS_NODE=0
fi
echo ""

# ── venv setup ───────────────────────────────────────────────────────────────
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$INSTALL_DIR/.venv"

hr
echo -e "${BOLD}Setting up Python virtual environment…${NC}"
hr

if [ -d "$VENV_DIR" ]; then
    warn "Virtual environment already exists at .venv — reusing."
else
    "$PYTHON" -m venv "$VENV_DIR"
    ok "Created .venv"
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
ok "Activated .venv"

pip install --quiet --upgrade pip
pip install --quiet -r "$INSTALL_DIR/requirements.txt"
ok "Python dependencies installed"
echo ""

# ── Claude Code CLI (optional) ───────────────────────────────────────────────
if [ "$HAS_NODE" -eq 1 ]; then
    hr
    echo -e "${BOLD}Claude Code CLI (optional)${NC}"
    hr
    echo "Claude Code enables AI-powered code editing inside Ouroboros."
    echo -n "Install Claude Code CLI? [y/N] "
    read -r INSTALL_CLAUDE
    if [[ "$INSTALL_CLAUDE" =~ ^[Yy]$ ]]; then
        if npm install -g @anthropic-ai/claude-code &>/dev/null 2>&1; then
            ok "Claude Code CLI installed"
        else
            warn "Claude Code CLI install failed — continuing without it."
        fi
    fi
    echo ""
fi

# ── API key collection ────────────────────────────────────────────────────────
hr
echo -e "${BOLD}API Keys & Configuration${NC}"
hr
echo "All values are saved to ${BOLD}.env${NC} in this directory."
echo "You can edit .env manually at any time."
echo ""

prompt_secret() {
    local var="$1" label="$2" required="$3" hint="$4"
    local existing=""
    [ -f "$INSTALL_DIR/.env" ] && existing=$(grep "^${var}=" "$INSTALL_DIR/.env" 2>/dev/null | cut -d= -f2-)
    echo -e "${BOLD}$label${NC}"
    [ -n "$hint" ] && echo -e "  ${BLUE}$hint${NC}"
    if [ -n "$existing" ]; then
        echo -n "  Value [press Enter to keep existing]: "
        read -r input
        [ -z "$input" ] && input="$existing"
    else
        echo -n "  Value: "
        read -r input
    fi
    if [ "$required" = "required" ] && [ -z "$input" ]; then
        err "$var is required."
        exit 1
    fi
    # write/update .env
    if [ -f "$INSTALL_DIR/.env" ] && grep -q "^${var}=" "$INSTALL_DIR/.env"; then
        # replace existing line (portable sed)
        sed -i.bak "s|^${var}=.*|${var}=${input}|" "$INSTALL_DIR/.env" && rm -f "$INSTALL_DIR/.env.bak"
    else
        echo "${var}=${input}" >> "$INSTALL_DIR/.env"
    fi
    echo ""
}

# Create .env if missing
[ -f "$INSTALL_DIR/.env" ] || touch "$INSTALL_DIR/.env"
chmod 600 "$INSTALL_DIR/.env"  # secrets — owner-readable only

echo -e "${BOLD}── Required keys ──${NC}"
echo ""

prompt_secret "OPENROUTER_API_KEY" "OpenRouter API Key" "required" \
    "Get one at https://openrouter.ai/keys (free tier available)"

prompt_secret "TELEGRAM_BOT_TOKEN" "Telegram Bot Token" "required" \
    "Create a bot via @BotFather on Telegram, then paste the token"

prompt_secret "TOTAL_BUDGET" "Spending Limit (USD)" "required" \
    "Maximum amount Ouroboros may spend on LLM calls (e.g. 10)"

prompt_secret "GITHUB_TOKEN" "GitHub Personal Access Token" "required" \
    "github.com/settings/tokens → classic token with 'repo' scope"

prompt_secret "GITHUB_USER" "GitHub Username" "required" \
    "Your GitHub username (used to push commits to your fork)"

prompt_secret "GITHUB_REPO" "GitHub Repository Name" "required" \
    "Repository name of your forked Ouroboros (default: ouroboros)"

echo -e "${BOLD}── Optional keys ──${NC}"
echo ""

prompt_secret "OPENAI_API_KEY" "OpenAI API Key (optional)" "optional" \
    "Enables the web_search tool — platform.openai.com/api-keys"

prompt_secret "ANTHROPIC_API_KEY" "Anthropic API Key (optional)" "optional" \
    "Enables Claude Code CLI code editing — console.anthropic.com/settings/keys"

# ── model config ─────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}Model Configuration (press Enter to use defaults)${NC}"
hr

prompt_secret "OUROBOROS_MODEL" "Primary LLM model" "optional" \
    "Default: anthropic/claude-sonnet-4.6  (via OpenRouter)"
prompt_secret "OUROBOROS_MODEL_CODE" "Code editing model" "optional" \
    "Default: anthropic/claude-sonnet-4.6"
prompt_secret "OUROBOROS_MODEL_LIGHT" "Lightweight model (consciousness/dedup)" "optional" \
    "Default: google/gemini-3-pro-preview"
prompt_secret "OUROBOROS_MAX_WORKERS" "Max parallel workers" "optional" \
    "Default: 5"

# ── data directory ────────────────────────────────────────────────────────────
hr
echo -e "${BOLD}Local Data Directory${NC}"
hr
echo "Ouroboros stores state, logs, and memory here (replaces Google Drive)."
echo -n "Data directory [~/.ouroboros]: "
read -r DATA_DIR
DATA_DIR="${DATA_DIR:-$HOME/.ouroboros}"
DATA_DIR="${DATA_DIR/#\~/$HOME}"  # expand tilde

# persist to .env
if grep -q "^OUROBOROS_DATA_DIR=" "$INSTALL_DIR/.env" 2>/dev/null; then
    sed -i.bak "s|^OUROBOROS_DATA_DIR=.*|OUROBOROS_DATA_DIR=${DATA_DIR}|" "$INSTALL_DIR/.env" && rm -f "$INSTALL_DIR/.env.bak"
else
    echo "OUROBOROS_DATA_DIR=${DATA_DIR}" >> "$INSTALL_DIR/.env"
fi

mkdir -p "$DATA_DIR"/{state,logs,memory,index,locks,archive}
ok "Data directory: $DATA_DIR"
echo ""

# ── write run script ──────────────────────────────────────────────────────────
RUN_SCRIPT="$INSTALL_DIR/run.sh"
cat > "$RUN_SCRIPT" <<'RUNSCRIPT'
#!/usr/bin/env bash
# Run Ouroboros locally.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DIR/.venv/bin/activate"

# Load .env
set -o allexport
source "$DIR/.env"
set +o allexport

exec python "$DIR/local_launcher.py" "$@"
RUNSCRIPT
chmod +x "$RUN_SCRIPT"
ok "Created run.sh"

# ── summary ───────────────────────────────────────────────────────────────────
echo ""
hr
echo -e "${BOLD}${GREEN}Installation complete!${NC}"
hr
echo ""
echo -e "  Start Ouroboros:  ${BOLD}bash run.sh${NC}"
echo ""
echo -e "  Config file:      ${BOLD}.env${NC}   (edit to change keys/models)"
echo -e "  Data directory:   ${BOLD}$DATA_DIR${NC}"
echo ""
echo -e "  First run: open your Telegram bot and send any message."
echo -e "  The first person to write becomes the owner."
echo ""
hr
