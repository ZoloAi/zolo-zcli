# zData Guide

## Introduction

**zData** is the unified data management subsystem of `zolo-zcli`. It consolidates schema parsing, database operations, and multi-backend support into a single, cohesive architecture.

---

## zData Architecture

### Core Components

### Adapter Pattern

### Module Organization

---

## Multi-Backend Support

### Supported Backends

### Backend Selection

### Connection Management

---

## SQLite Backend

### Configuration

### Features

### Type Mapping

### Transactions

### Limitations

---

## CSV Backend

### Configuration

### Features

### Type Mapping

### Transactions

### Limitations

---

## Schema Management

### Schema Loading

### Field Parsing

### Type System

### Foreign Keys

### RGB Columns

---

## CRUD Operations

### CREATE

### READ

### UPDATE

### DELETE

### UPSERT

### ALTER TABLE

---

## Query Building

### WHERE Clauses

### JOIN Operations

### ORDER BY

### LIMIT & OFFSET

---

## Validation

### Field Validation

### Type Validation

### Required Fields

### Custom Rules

---

## Infrastructure Functions

### zDataConnect

### zEnsureTables

### zTables

### resolve_source

### build_order_clause

---

## Migration & RGB Tracking

### Auto-Migration

### RGB Weak Nuclear Force

### Migration History

---

## Advanced Features

### Connection Pooling

### Caching

### Transaction Management

### Error Handling

---

## Usage Examples

### Basic CRUD with SQLite

### Basic CRUD with CSV

### Switching Backends

### Complex Queries

### Validation Rules

---

## API Reference

### ZData Class

### handle_zData Function

### handle_zCRUD Function

### load_schema_ref Function

---

## Best Practices

### Schema Design

### Backend Selection

### Performance Optimization

### Error Handling

---

## Troubleshooting

### Common Issues

### Debug Mode

### Error Messages

---

## Migration from Legacy

### From zCRUD

### From zSchema

### Import Changes

---

## Appendix

### Supported Data Types

### Operator Reference

### Configuration Options