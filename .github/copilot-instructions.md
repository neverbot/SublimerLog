# Copilot Instructions for Sublimer Log

## Python Guidelines

**Version**: Python 3.8+ (Sublime Text embedded Python)

**Avoid**:
- None (All Python 3.8 features are supported)

**Use**:
- f-strings for string formatting: `f"Hello, {name}!"`
- Type hints for better code clarity
- `pathlib` for file operations
- Modern async/await syntax
- Walrus operator `:=`
- `sublime` and `sublime_plugin` modules

## File Naming

**Markdown files**: Always lowercase with hyphens
- ✅ `readme.md`, `changelog.md`, `api-reference.md`
- ❌ `README.md`, `API_Reference.md`
