# Zotero local API and connector routes

Base URL: `http://127.0.0.1:23119`.

## Desktop local API

The local API is under `/api/`. It implements Zotero Web API v3 for the local logged-in desktop user.

Important constraints:

- Use `/api/users/0/...` for the local user by default.
- Local API reads do not require an API key.
- The local API is read-only; write requests are not supported there.
- Atom output is not supported locally.
- Attachment file URLs and full text can expose local file paths or document text; only retrieve them when the user asks.

Safe read routes:

```text
/api/
/api/schema
/api/itemTypes
/api/itemFields
/api/itemTypeFields?itemType=journalArticle
/api/itemTypeCreatorTypes?itemType=journalArticle
/api/creatorFields
/api/users/0/collections
/api/users/0/collections/top
/api/users/0/items
/api/users/0/items/top
/api/users/0/items/trash
/api/users/0/items/<itemKey>
/api/users/0/items/<itemKey>/children
/api/users/0/items?format=keys
/api/users/0/items?format=versions
/api/users/0/items?format=bibtex
/api/users/0/items?include=data,citation&style=apa
/api/users/0/items?q=<query>
/api/users/0/tags
/api/users/0/searches
/api/users/0/searches/<searchKey>/items
/api/users/0/groups
/api/users/0/fulltext?since=0
/api/users/0/items/<attachmentKey>/fulltext
/api/users/0/items/<attachmentKey>/file/view/url
```

## Connector server

The Zotero Connector server shares port `23119` and is used for desktop writes/imports.

Useful routes:

```text
GET  /connector/ping
POST /connector/ping
POST /connector/getSelectedCollection
POST /connector/import?session=<uuid>
POST /connector/saveItems
POST /connector/saveSnapshot
```

Use `/connector/import` for importing BibTeX/RIS strings into the currently selected Zotero library or collection. Treat connector writes as Zotero library modifications and confirm with the user before doing them.
