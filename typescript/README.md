# @monkdb/monkdb-mcp

> Modular Command Protocol (MCP) Server for **MonkDB** – enabling LLMs to interact with MonkDB securely and efficiently using standardized tools like `run_select_query`, `describe_table`, `health_check`, and more.

![npm](https://img.shields.io/npm/v/@monkdb/monkdb-mcp)
![license](https://img.shields.io/npm/l/@monkdb/monkdb-mcp)
![typescript](https://img.shields.io/badge/TypeScript-ESM-blue)
![build](https://img.shields.io/badge/build-passing-brightgreen)
![tests](https://img.shields.io/badge/tests-passed-brightgreen)
![status](https://img.shields.io/badge/project-stable-blue)

---

## ✨ What is This?

This is an **MCP server implementation in TypeScript** for [MonkDB](https://monkdb.com), enabling:
- LLM frameworks like **Claude**, **LangChain**, **CrewAI**, and others to interact with MonkDB.
- Secure, controlled SQL access to MonkDB clusters.
- Extensible plug-and-play architecture to add new tools and utilities.

---

## 🚀 Features

- ✅ Supports `SELECT` queries with parameterized inputs
- 📋 Lists and describes MonkDB tables
- 🩺 Provides health and version check utilities
- 🔐 Uses environment-based credentials for safety
- 📦 Exports a clean API with `startMonkDBMCPServer()` entry point
- 🧪 Production-ready with Jest-style unit tests

---

## 📦 Installation

```bash
npm install @monkdb/monkdb-mcp
```

## 🛠️ Usage

As a CLI (via stdio transport)

```ts
// server.mts
import { startMonkDBMCPServer } from '@monkdb/monkdb-mcp';

await startMonkDBMCPServer();
```

Run the server with:

```bash
node build/server.mjs
```

Or use in your MCP host like Claude Desktop, LangChain, etc.

## 🔧 Configuration

Create a `.env` file or use environment variables:

```text
MONKDB_HOST=127.0.0.1
MONKDB_API_PORT=4200
MONKDB_USER=your_user
MONKDB_PASSWORD=your_password
MONKDB_SCHEMA=monkdb  # Optional (defaults to monkdb)
```

## 🧰 Supported Tools

| Tool Name            | Description                                         |
|----------------------|-----------------------------------------------------|
| `list_tables`          | Lists tables under `MONKDB_SCHEMA`                    |
| `run_select_query`     | Executes `SELECT` queries (**others are blocked**)        |
| `health_check`         | Runs `SELECT 1` to verify DB connectivity             |
| `get_server_version`   | Returns server version using `SELECT version()`        |
| `describe_table`       | Lists columns and types of a table                  |


## 🧪 Running Tests

This package includes unit tests using vitest. To run:

```bash
npm install
npm run build
npm vitest
```

## 🧩 Integrations

Can be used with:

- ✅ Claude Desktop (via stdio)
- ✅ LangChain or equivalents (as a tool or plugin)
- ✅ CrewAI or equivalents (via custom agent tools)
- ✅ CLI scripts or microservices needing DB interface

## 📄 License

This project is licensed under Apache-2.0.

## Contact Us

You may reach out to us at [support@monkdb.com](mailto:support@monkdb.com)