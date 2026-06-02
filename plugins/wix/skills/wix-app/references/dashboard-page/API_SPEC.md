# API Spec Reference

Guide for using API specifications in dashboard pages.

## Overview

You will be given an API specification under the "API SPEC" spec. The dashboard page code you generate can make API calls to these endpoints to read and write data. You cannot write the API calls yourself, you must use the API calls provided in the API SPEC.

## Example API Spec

```json
{
  "name": "Todo Management API",
  "description": "A simple API for managing todo items with CRUD operations",
  "endpoints": [
    {
      "id": "get-todos",
      "path": "/api/todos",
      "method": "GET",
      "name": "Get All Todos",
      "description": "Retrieve all todo items",
      "parameters": [],
      "response": {
        "statusCode": 200,
        "type": "array"
      }
    },
    {
      "id": "create-todo",
      "path": "/api/todos",
      "method": "POST",
      "name": "Create Todo",
      "description": "Create a new todo item",
      "parameters": [
        {
          "name": "todo",
          "type": "object",
          "required": true,
          "location": "body"
        }
      ],
      "response": {
        "statusCode": 201,
        "type": "object"
      }
    },
    {
      "id": "update-todo",
      "path": "/api/todos/[id]",
      "method": "PUT",
      "name": "Update Todo",
      "description": "Update an existing todo item",
      "parameters": [
        {
          "name": "id",
          "type": "string",
          "required": true,
          "location": "path"
        },
        {
          "name": "todo",
          "type": "object",
          "required": true,
          "location": "body"
        }
      ],
      "response": {
        "statusCode": 200,
        "type": "object"
      }
    }
  ],
  "dataModels": [
    {
      "name": "Todo",
      "properties": {
        "id": {
          "type": "string",
          "required": true
        },
        "title": {
          "type": "string",
          "required": true
        },
        "description": {
          "type": "string",
          "required": false
        },
        "completed": {
          "type": "boolean",
          "required": true
        },
        "createdAt": {
          "type": "string",
          "required": true
        }
      }
    }
  ]
}
```

## Example Output Code

```typescript
// Reading data - GET request
async function getTodos(): Promise<Todo[]> {
  const response = await fetch('/api/todos');
  const data = await response.json();
  return data;
}

// Writing data - POST request with data model entity
async function createTodo(todo: Omit<Todo, 'id' | 'createdAt'>): Promise<Todo> {
  const response = await fetch('/api/todos', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(todo),
  });
  const data = await response.json();
  return data;
}

// Writing data - PUT request with data model entity
async function updateTodo(id: string, todo: Partial<Todo>): Promise<Todo> {
  const response = await fetch(`/api/todos/${id}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(todo),
  });
  const data = await response.json();
  return data;
}
```
