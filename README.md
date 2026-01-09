# Zolo Monorepo

Monorepo for the Zolo ecosystem - four independent projects that work together.

---

## Projects

### 🔧 [zSys](./zSys/)
System foundation utilities shared across the ecosystem.

- Bootstrap logging, terminal formatting, error handling
- CLI command handlers for the `zolo` terminal command
- Standalone package: `zsys`

### 📝 [zLSP](./zLSP/)
Language Server Protocol implementation for `.zolo` files.

- Parser for the `.zolo` file format
- IDE integration (syntax highlighting, completion, diagnostics)
- Standalone package: `zolo`

### ⚡ [zKernel](./zKernel/)
Declarative Python kernel - orchestrates 17 subsystems across Terminal and Web contexts.

- YAML-driven application framework
- 4-layer architecture (Foundation → Core → Abstraction → Orchestration)
- Standalone package: `zkernel`

### 🎨 [zTheme](./zTheme/)
Modern CSS framework with handwritten typography.

- CSS component library
- CDN-ready distribution
- Standalone package: `ztheme`

### 🌉 [bifrost](./bifrost/)
WebSocket client for real-time browser ↔ kernel communication.

- JavaScript client library
- Pairs with zKernel's zBifrost server
- Standalone package: `bifrost-client`

---

## Development

Each project is independent with its own:
- Package configuration (`pyproject.toml` or `package.json`)
- Documentation
- Build process
- Release cycle

See individual project READMEs for setup and usage.

---

## License

MIT License - See [LICENSE](./LICENSE) for details.
