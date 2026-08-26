# Data Preparation

## Data Cleaning Checklist

Before analysis, check for and handle:

- Missing values (nulls, empty strings, "N/A", "-")
- Duplicate rows
- Inconsistent date formats
- Numeric columns stored as strings (currency symbols, commas, %)
- Trailing whitespace and mixed case in categorical columns

## File Retrieval from Waldo Workspace

Users store files (reports, spreadsheets, research documents, brand assets) in the Waldo workspace. Users typically say "files," "documents," "reports," "saved docs," "saved research," "library," or "brand files."

When the user asks to find or analyze a stored file:

1. Confirm this is a file request, not a feed/signal request. If the user is asking about signals, insights, or feed items, use the Archival Knowledge skill instead.
2. Use `search_documents` or `feed_get_items` to locate the file in the workspace.
3. If multiple matches, present options and ask which one they want.
