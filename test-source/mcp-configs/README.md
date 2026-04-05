# MCP Servers Configuration for SKLUBS

## 1. WordPress MCP (sklubs.fr)

**Purpose**: Modifier le site WordPress directement (SEO, contenu, pages)

**Setup:**
```bash
# Installer le plugin sur WordPress
# WP Admin → Plugins → Ajouter → "WPGraphQL" + "WPGraphQL JWT Auth"
# Activer les deux plugins
# Générer un token JWT :
curl -X POST https://sklubs.fr/wp-json/jwt-auth/v1/token \
  -d "username=admin&password=VOTRE_PASSWORD"
```

**MCP Config (openclaw.json) :**
```json
{
  "mcpServers": {
    "wordpress": {
      "command": "npx",
      "args": ["-y", "@openclaw/mcp-wordpress"],
      "env": {
        "WORDPRESS_URL": "https://sklubs.fr",
        "WORDPRESS_TOKEN": "VOTRE_JWT_TOKEN",
        "WORDPRESS_USER": "admin"
      }
    }
  }
}
```

**Capabilités:**
- Créer/modifier des pages et articles
- Mettre à jour meta SEO (title, description, schema)
- Gérer les médias (upload images)
- Modifier le contenu Elementor
- Extraire analytics (via plugins compatibles)
- Gérer les catégories et tags

**Commandes utiles:**
- `mcp.wordpress.page.create(title, content, status)`
- `mcp.wordpress.page.update(id, updates)`
- `mcp.wordpress.seo.update(id, metaTitle, metaDescription)`
- `mcp.wordpress.media.upload(file, title)`
- `mcp.wordpress.post.list(category, count)`

---

## 2. Nano Banana MCP (Image Generation)

**Purpose**: Générer des visuels pour SKLUBS (product shots, social media, ads)

**Setup:**
```bash
# Clé API Gemini requise
# Obtenir sur: https://aistudio.google.com/apikey
export GEMINI_API_KEY="sk-..."
```

**MCP Config :**
```json
{
  "mcpServers": {
    "nano-banana": {
      "command": "npx",
      "args": ["-y", "@openclaw/mcp-nano-banana"],
      "env": {
        "GEMINI_API_KEY": "VOTRE_CLE_API"
      }
    }
  }
}
```

**Prompts pour SKLUBS:**
```
# Product photography
"Professional product photography of a customized black canvas bag 
with gold foil logo 'SKLUBS', white marble background, natural lighting, 
shot on Hasselblad, editorial style"

# Social media visual
"Instagram post showing a hand holding a customized tote bag with 
colorful abstract design, urban Paris background, lifestyle photography, 
warm tones, 1:1 ratio"

# Ad creative
"Facebook ad image: before/after split screen. Left: plain white mug. 
Right: same mug with vibrant 'SKLUBS' logo and pattern. Clean white 
background, professional product photography style."

# Hero banner
"Hero banner image for SKLUBS website. Wide 16:9. Collection of 
personalized products (bag, jar, tote, pins, business cards, stickers, 
t-shirt) arranged artistically on dark background with warm accent 
lighting. Modern, premium, minimalist aesthetic."
```

---

## 3. Blender MCP

**Purpose**: Création 3D de mockups produits et animations

**Setup:**
```bash
# Blender doit être installé sur la machine
# Path vers Blender: c:\Users\stick\Documents\blender\blender-mcp
# Démarrer le serveur MCP Blender avant utilisation

# Config openclaw.json
```

**MCP Config :**
```json
{
  "mcpServers": {
    "blender": {
      "command": "python",
      "args": ["-m", "blender_mcp"],
      "cwd": "c:\\Users\\stick\\Documents\\blender\\blender-mcp"
    }
  }
}
```

**Use Cases pour SKLUBS:**
- Mockups 3D des configurateurs (rotation 360°)
- Animations produits pour les landing pages
- Visuels hero en 3D
- Packaging renders

---

## 4. Filesystem MCP

**Purpose**: Accès aux fichiers locaux pour lecture/écriture

**MCP Config :**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", 
               "C:\\Users\\stick", "D:\\MES LOGICIEL\\ourobouros"],
      "env": {}
    }
  }
}
```

**Capabilités:**
- Lire et écrire des fichiers
- Lister des répertoires
- Rechercher dans les fichiers
- Copier/déplacer des fichiers

---

## 5. Browser Automation MCP

**Purpose**: Navigation web et screenshots automatiques

**Setup:**
```json
{
  "mcpServers": {
    "browser": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-browser"],
      "env": {
        "DISPLAY": ":99" # Si Linux, ou utiliser puppeteer directement
      }
    }
  }
}
```

**Use Cases SKLUBS:**
- Screenshots des 7 configurateurs pour monitoring
- Test de responsive (mobile/tablet/desktop)
- Capture de concurrents
- Monitoring de disponibilité

---

## 6. OpenClaw Complete Configuration

Voici la configuration complète pour `openclaw.json` :

```json
{
  "openclaw": {
    "version": "2026.3.31"
  },
  "mcpServers": {
    "wordpress": {
      "command": "npx",
      "args": ["-y", "@openclaw/mcp-wordpress"],
      "env": {
        "WORDPRESS_URL": "https://sklubs.fr",
        "WORDPRESS_TOKEN": "VOTRE_JWT_TOKEN",
        "WORDPRESS_USER": "admin"
      }
    },
    "nano-banana": {
      "command": "npx",
      "args": ["-y", "@openclaw/mcp-nano-banana"],
      "env": {
        "GEMINI_API_KEY": "VOTRE_CLE_API"
      }
    },
    "blender": {
      "command": "python",
      "args": ["-m", "blender_mcp"],
      "cwd": "c:\\Users\\stick\\Documents\\blender\\blender-mcp"
    },
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem",
               "C:\\Users\\stick", "D:\\MES LOGICIEL\\ourobouros"]
    }
  },
  "models": {
    "default": "ollama/gemma4",
    "providers": {
      "ollama": {
        "baseUrl": "http://localhost:11434",
        "models": ["gemma4", "qwen2.5-coder:7b", "qwen3-coder:480b-cloud"]
      },
      "openrouter": {
        "apiKey": "VOTRE_OPENROUTER_KEY",
        "models": ["qwen3-coder:free", "openai/gpt-oss-20b:free", "openrouter/free"]
      },
      "openai-codex": {
        "oauth": true
      }
    }
  },
  "agents": [
    "seo-master",
    "social-media-manager",
    "video-creative-director",
    "configurators-admin",
    "market-strategy",
    "market-content",
    "market-conversion",
    "market-technical",
    "market-competitive"
  ]
}
```
