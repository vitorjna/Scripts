---
name: readme-manager
description: >-
  Use this skill when creating or updating README documentation for utility scripts, tools, or folders in this repository, including synchronizing entries with the root README.md.
---

# README Manager

A standardized workflow for creating and maintaining README documentation across this repository, ensuring consistency between folder-level documentation and the root repository index.

## Repository Conventions

### 1. Root `README.md` Structure
The root README.md acts as the central directory for all utilities:
- **Table of Contents**: An alphabetical list of markdown anchor links:
  ```markdown
  - [Tool Name](#tool-name)
  ```
- **Tool Sections**: Keep these concise (2-4 lines):
  ```markdown
  ## Tool Name

  This script (`tool_name.py`) is a Python-based tool to <concise summary of purpose>.

  For more details, see the [Tool Name README](ToolFolder/README.md).
  ```
- Alphabetical order must be maintained across both the Table of Contents and the section blocks.

### 2. Subfolder `README.md` Structure
Each tool folder should have its own self-contained `README.md` covering:
- **Title**: `# Tool Name`
- **Overview**: 1-2 paragraphs detailing the tool's purpose, problem it solves, and core behavior.
- **Features / Key Capabilities**: Bullet list or table highlighting main capabilities.
- **Prerequisites & Dependencies**: External tools (`ffmpeg`, `diskpart`, `llama.cpp`), GPU requirements, or Python libraries (explicitly note if only stdlib is needed).
- **Usage & Examples**:
  - Command-line syntax and runnable examples.
  - Drag-and-drop or interactive menu instructions (if supported).
- **Configuration / Options**: Table or bullet points describing parameters, CLI flags, or environment variables.
- **Project Structure**: Short list of files in the directory if multiple scripts/assets exist.

## Workflow

### Creating a New Tool README

1. **Analyze Code First**:
   - Inspect all scripts in the tool directory (`view_file` or `list_dir`).
   - Identify CLI parsers (`argparse`, `sys.argv`), default values, flags, and error exit codes.
   - Note external requirements or platform constraints (Windows batch, Linux, CUDA/Vulkan).

2. **Generate Folder README**:
   - Create `<ToolFolder>/README.md` using the structure described above.
   - Keep tone practical, concise, and developer-focused.
   - Avoid placeholders or untested command options.

3. **Update Root `README.md`**:
   - Insert an entry in the Table of Contents in alphabetical order.
   - Add the matching `## Tool Name` section with relative link to `<ToolFolder>/README.md`.

### Updating an Existing Tool README

1. **Diff Changes**:
   - Check what changed in the underlying scripts (new flags, changed defaults, deprecated options).
2. **Update Subfolder README**:
   - Edit `<ToolFolder>/README.md` to reflect the updated arguments, behaviors, or dependencies.
3. **Verify Root Summary**:
   - If the core scope of the script changed significantly, adjust the 1-2 sentence description in root `README.md`.

## Verification Checklist

Before completing:
- [ ] Relative links to files or other docs resolve correctly.
- [ ] All CLI commands and flags documented match the actual script implementations.
- [ ] Table of Contents in root `README.md` remains in alphabetical order.
- [ ] Formatting is clean GitHub-flavored markdown without unnecessary boilerplate.
