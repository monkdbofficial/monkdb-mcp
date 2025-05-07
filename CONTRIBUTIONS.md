# MonkDB MCP Server Contributor Guide: Work In Progress

## Introduction

### What is MonkDB and its MCP Support?

MonkDB is a unified OLAP AI native database which supports timeseries, vector, full text search, geospatial, nosql, and streaming sql data workloads. This project gives first class support to MCP server. This project aims to seamlessly connect LLMs, Pipelines like LangChain, and MonkDB datastore via MCP. 


### What is this guide?

This guide is for anyone who wants to contribute to MonkDB-MCP Server. It's a work in progress, and will be updated regularly.

### How can I contribute?

There are many ways to contribute to MonkDB. You can:

- Report a bug by mailing to [security@monkdb.com](mailto:security@monkdb.com)
- [Suggest a feature (via email)][support@monkdb.com](mailto:support@monkdb.com) or by raising a new issue in this GitHub project.
- Submit a PR

### Development Requirements

Before anything else, make sure you have the following installed:

- Node Version 20+
- Python 3 >= 3.13
- NPM > 10.9+

### General Setup

Configure the necessary environment variables by copying the `.env.example` file in `example_env` directory to `.env`. Replace the `ip_address` with an `ip_address` where MonkDB's docker image is provisioned. Replace `username` and `password` with the values of your environment. The other two variable (`port` and `schema`) values need not be changed. 

You may `pip` or `poetry` or any other package manager to install our [python package](https://pypi.org/project/mcp-monkdb/). If your stack is based on typescript, you may use `npm` or `npx` or `yarn` or any other package manager to install our [npm package](https://www.npmjs.com/package/@monkdb/monkdb-mcp).

## Connect with us

For any other information, please connect with us at [support@monkdb.com](mailto:support@monkdb.com).