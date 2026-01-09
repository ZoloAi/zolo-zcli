# Zolo Monorepo

Monorepo for the Zolo ecosystem - four independent projects that work together.

---

## Projects

### 📝 [zLSP](./zLSP/)
Language Server Protocol implementation for `.zolo` files.

- Parser for the `.zolo` file format
- IDE integration (syntax highlighting, completion, diagnostics)
- Standalone package: `zolo`

### ⚡ [zCLI](./zCLI/)
Context Layer Interface - declarative Python CLI framework.

- YAML-driven application framework
- Multi-layer architecture (Foundation → Core → Business → Orchestration)
- Standalone package: `zolo-zcli`

### 🎨 [zTheme](./zTheme/)
Modern CSS framework with handwritten typography.

- CSS component library
- CDN-ready distribution
- Standalone package: `ztheme`

### 🌉 [bifrost](./bifrost/)
WebSocket client for real-time browser ↔ CLI communication.

- JavaScript client library
- Pairs with zCLI's zBifrost server
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
