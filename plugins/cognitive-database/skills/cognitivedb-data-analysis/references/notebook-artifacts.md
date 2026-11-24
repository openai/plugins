# Analysis Notebook Artifacts

Apply this guidance when the user requests an `.ipynb` analysis artifact in the
Agent working environment or as a downloadable attachment. Creating the local
file does not authorize running its cells, importing it into CognitiveDB, or
changing CognitiveDB resources.

## Cell Language and Execution Scope

- Generate a valid nbformat 4 document. Executable cells use `cell_type: code`;
  SQL is a language, not a Jupyter cell type.
- Mark each SQL cell with `metadata.language: sql` and each Python cell with
  `metadata.language: python`. CognitiveDB import uses cell language metadata
  before the notebook kernel default. This also preserves SQL cells in a mixed
  notebook whose kernel is Python. Do not infer language from SQL-looking text.
- Reuse verified Catalog, Schema, table names, and SQL from the analysis. Fully
  qualify persistent objects in SQL so the notebook does not depend on the
  importing user's default Schema or an earlier transient SQL session.
- Keep Markdown explanations in Markdown cells. Put Python code only in Python
  cells; do not place bare SQL in Python or claim that a notebook-wide SQL
  kernel alone gives individual cells their correct type.

## Validate and Deliver

- Parse the generated JSON and verify nbformat, cells, source strings, and every
  executable cell's declared language against its contents before delivery.
  Use an available nbformat validator in addition to these semantic checks.
- Save the validated notebook to the user's requested workspace path, or deliver
  it through the host's supported attachment mechanism. Return the actual local
  file or attachment reference; do not invent a download URL.
- Preserve the analysis metric definitions, filters, precision, and ordering.
  Include the intended execution context and required existing Compute in a
  Markdown cell. Do not embed credentials or authentication state.
- Distinguish local artifact creation and validation, local cell execution,
  CognitiveDB import, and CognitiveDB execution. Claim successful
  CognitiveDB import or execution only after independently observing it; when
  the live tool contract lacks that operation, deliver the validated local file or attachment
  and state the unverified step instead of substituting another interface.
