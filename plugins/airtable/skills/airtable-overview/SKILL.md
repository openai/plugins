---
name: airtable-overview
description: Explains what Airtable is and how data is structured — bases, tables, fields, records, views, automations, and interfaces. Use when you need context about the Airtable data model.
license: MIT
metadata:
    version: '1.0.0'
    author: airtable
---

# Airtable Overview

Airtable is a no-code platform where teams build custom applications and AI-powered workflows from structured data. Users organize their data into bases, define tables with typed fields, set up automations to act on changes, and create interfaces that give different audiences tailored views of the same data.

## Data model

### Bases

A base is an Airtable database. It is the top-level container for all related data. A base contains one or more tables.

### Tables

A table is a collection of structured data within a base, similar to a sheet in a spreadsheet or a table in a relational database. Each table has a defined set of fields and contains records.

### Fields

A field defines a named, typed property on every record in a table.

### Records

A record is a single entry in a table. Each record has a unique ID and stores a cell value for each field defined on that table.

### Views

A view is a saved configuration for how to display records in a table. Views can filter, sort, group, and hide fields without changing the underlying data. Multiple views can exist on the same table, each showing the data differently.

## Automations

An automation is a workflow that runs in response to a defined trigger (e.g. a record entering a view) and executes one or more actions (e.g. sending an email or updating a record).

## Interfaces

Interfaces are custom app-like pages built on top of base data. They provide tailored, user-friendly ways to view and interact with records without exposing the full base structure or all of its data. A base can have multiple interfaces, each designed for a specific workflow or audience.

Some users can only access a base through its interfaces and cannot read or modify the underlying tables directly.
