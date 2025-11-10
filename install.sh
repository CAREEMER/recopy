#!/bin/bash

set -e

REPO="CAREEMER/recopy"
INSTALL_DIR="$HOME/.local/bin"
SCRIPT_NAME="recopy"

echo "🚀 Installing Recopy..."

# Проверяем Python 3
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

# Создаем директорию для установки
mkdir -p "$INSTALL_DIR"

# Скачиваем скрипт
echo "📥 Downloading from GitHub..."
curl -fsSL "https://raw.githubusercontent.com/$REPO/main/recopy.py" -o "$INSTALL_DIR/$SCRIPT_NAME"

# Делаем исполняемым
chmod +x "$INSTALL_DIR/$SCRIPT_NAME"

# Проверяем, есть ли PATH в системе
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo ""
    echo "⚠️  Warning: $INSTALL_DIR is not in your PATH"
    echo "   Add this to your ~/.bashrc, ~/.zshrc, or ~/.profile:"
    echo ""
    echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
    echo ""
fi

# Проверяем установку
if [ -f "$INSTALL_DIR/$SCRIPT_NAME" ]; then
    echo "✅ Recopy installed successfully!"
    echo ""
    echo "Usage:"
    echo "  $SCRIPT_NAME              # Collect files and copy to clipboard"
    echo "  $SCRIPT_NAME --help       # Show help"
    echo ""
    echo "Create a 'recopy.ignore' file to exclude patterns (like .gitignore)"
else
    echo "❌ Installation failed"
    exit 1
fi
