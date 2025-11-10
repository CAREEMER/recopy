# 🖨️ Recopy

Recursive file content collector with gitignore-like exclusion patterns. Perfect for preparing codebases to share with LLMs or for documentation.

## Features

- 📁 **Recursive scanning** - Walks through all subdirectories
- 🚫 **Smart exclusion** - gitignore-like patterns with glob support
- 🔄 **Nested configs** - Each subdirectory can have its own `recopy.ignore`
- 📋 **Clipboard integration** - Automatically copies to clipboard (macOS/Linux/Windows)
- 📝 **Text-only** - Filters out binary files automatically
- 💨 **Fast and lightweight** - Single Python script, no dependencies

## Installation

### Quick Install (Linux/macOS)

`curl -fsSL https://raw.githubusercontent.com/CAREEMER/recopy/main/install.sh | bash
`
