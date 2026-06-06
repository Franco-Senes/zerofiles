# ZeroFiles (`.zr`) - Python Parser & Formatter

**ZeroFiles (`.zr`)** is a lightweight, developer-friendly data serialization format designed as a flexible alternative to JSON. It combines the simplicity of object and array structures with features like header metadata, multiple comment styles that are preserved during formatting, and unquoted object keys.

This repository contains the reference Python implementation for the lexer (tokenizer), parser, AST (Abstract Syntax Tree) generator, formatter, and a static linter.

---

## Core Features

* **Native Comments:** Supports single-line comments (`#` and `//`) as well as block comments (`/* ... */`).
* **Comment Preservation:** The AST-based formatter organizes code structure without stripping away or destroying explanatory comments.
* **Header Metadata:** Allows you to define special directives at the top of the file using the `# @key: value` syntax.
* **Clean Syntax:** Object keys can be valid identifiers without requiring quotes, similar to JavaScript or YAML.
* **Built-in Linter:** Automatically detects style warnings—such as single-quote usage or unnecessary quotes on keys—and reports syntax errors with precise line and column numbers.

---

## File Format Example

Here is a standard `.zr` file:

```json
# @version: 1.0
# @author: Dev
# @project: Global Configuration

{
    // Server data
    server: {
        host: "127.0.0.1",
        port: 8080, /* Default port */
        debug_mode: true
    },
    
    # List of administrators
    admins: [
        "admin_user",
        "root"
    ]
}

```