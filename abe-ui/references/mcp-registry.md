Read when using the shadcn MCP server or publishing/consuming a custom registry.

## MCP Server (AI Integration)

```json
// .mcp.json (Claude Code)
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

```json
// .cursor/mcp.json (Cursor)
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

```json
// .vscode/mcp.json (VS Code / Kiro)
{
  "servers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    }
  }
}
```

Quick setup: `npx shadcn@latest mcp init --client vscode`

## Registry System

### Custom Registries

```json
// components.json
{
  "registries": {
    "@acme": "https://acme.com/r/{name}.json",
    "@internal": {
      "url": "https://internal.company.com/{name}.json",
      "headers": {
        "Authorization": "Bearer ${REGISTRY_TOKEN}"
      }
    }
  }
}
```

```bash
npx shadcn@latest add @acme/hero
npx shadcn@latest add @internal/auth-form
```
