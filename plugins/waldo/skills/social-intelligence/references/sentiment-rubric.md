# Sentiment Rubric

Classify every organic post as **Positive**, **Neutral**, or **Negative**.

## Positive

- Explicit praise, recommendation, or endorsement
- Loyalty, repeat purchase intent, or personal attachment
- Positive experience tied to the brand/product
- Defending the brand or comparing it favorably to competitors

## Neutral

- Factual mention without evaluative language
- Questions or information requests without opinion
- Balanced takes weighing pros and cons equally
- News sharing or reposting without personal commentary

## Negative

- Explicit complaint, dissatisfaction, or criticism
- Reporting a problem: defect, poor service, unmet expectations
- Warning others away or recommending competitors
- Frustration, disappointment, anger, or regret about the brand

## Edge Cases

- **Sarcasm**: Look for exaggerated praise, contradictory context, or `/s` markers. Classify by *intended* sentiment and flag as sarcastic.
- **Mixed Sentiment**: Classify by the **dominant** sentiment — whichever occupies more of the post's content and carries stronger language intensity. Note the secondary sentiment.
- **Comparative**: "X is better than Y" is positive for X, negative for Y — classify relative to the brand being analyzed.

## Engagement Weighting

Not all posts carry equal weight. Use engagement signals to prioritize significance:

| Tier | Criteria | Weight |
|---|---|---|
| High | Top 10% by likes/comments/shares for that platform search | 3x |
| Medium | Middle 50% | 1x |
| Low | Bottom 40% or zero engagement | 0.5x |

- Apply weights when calculating sentiment percentages and identifying dominant themes.
- **User override**: If the user specifies equal weighting or a different methodology, use theirs.
- Always state in the report whether engagement weighting was applied.

## Content Safety

- Exclude posts containing nudity, hate speech, graphic violence, or sexually explicit content from direct quotes and embedded visuals.
- Casual profanity is acceptable in quotes — redact only slurs and highly offensive language.
- Still count all classifiable posts toward sentiment totals.
- Flag excluded content: *"X posts excluded from quotes due to content policy."*
