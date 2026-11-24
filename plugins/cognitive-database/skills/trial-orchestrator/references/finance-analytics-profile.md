# Finance Analytics Profile (DABstep)

Read this file when the resolved trial profile is `dabstep` (DABStep Payment
Analytics). It supplies the introduction template, the built-in question list
without answers.

## Opening Introduction Template

```text
🎯 Welcome to DABStep Payment Analytics!

Explore payments, fraud, merchants, fees, and what-if scenarios with live data
analysis. Built on the DABStep benchmark: 450 grounded questions over governed
2023 payment data.

[What I can help you see]
💳 Payment insights — volume, amounts, credit/debit, domestic/cross-border
🕵️ Fraud analysis — fraud rates and distributions by channel / card scheme / time
🏪 Merchant profiling — account types, MCC industries, monthly volume & fraud tiers
💰 Fee analytics — fee-rule matching, effective rates, fee composition
🔮 What-if analysis — card-scheme routing, rule-change impact simulations

👇 Start with one of these popular questions!
```

## Built-in Questions (answers are NOT in this file)

Each line is one question. Offer the `question` text verbatim as the option
label — never the `guidelines` or any answer-type hint; apply the
`guidelines` output-format requirements to the answer value. Experience copy
and explicit reply-only requests follow SKILL.md Core Instructions.

```jsonl
{"task_id": "30", "question": "Is the fraud rate for ecommerce transactions higher than in-store transactions during the year 2023?", "guidelines": "Answer must either yes or no. If a question does not have a relevant or applicable answer for the task, please respond with 'Not Applicable'."}
{"task_id": "64", "question": "What are the possible values for the field aci?", "guidelines": "Answer must be a list of values in comma separated list, eg: A, B, C. If the answer is an empty list, reply with an empty string. If a question does not have a relevant or applicable answer for the task, please respond with 'Not Applicable'."}
{"task_id": "6", "question": "What percentage of the transactions are made using credit cards?", "guidelines": "Answer must be just a number rounded to 3 decimals. If a question does not have a relevant or applicable answer for the task, please respond with 'Not Applicable'."}
{"task_id": "24", "question": "Which device type is most commonly used in fraudulent transactions?", "guidelines": "Answer must be just the name of the device category. If a question does not have a relevant or applicable answer for the task, please respond with 'Not Applicable'."}
{"task_id": "42", "question": "Are there any duplicate (by all columns) transactions in the payments dataset?", "guidelines": "Answer must either yes or no. If a question does not have a relevant or applicable answer for the task, please respond with 'Not Applicable'."}
{"task_id": "23", "question": "What is the fraud rate for in-person transactions for the year 2023?", "guidelines": "Answer must be just a number. If a question does not have a relevant or applicable answer for the task, please respond with 'Not Applicable'."}
```

## Analysis

Use `cognitivedb-data-analysis` for source discovery, approval, read-only SQL,
and result validation.
Answer from the authorized data and established definitions. If a material
business rule remains unclear, ask for clarification before reporting a value.
