# Visualization Style

Use a warm editorial style with a large serif headline that states the finding.
Place the key value beside the primary chart where space allows, and stack them
in a narrow pane. Add supporting charts below when they answer distinct
questions.

- **Chart choice.** Use lines or columns for trends and grouped bars for
  comparisons. Use a waterfall only when the movements reconcile the starting
  and ending totals.
- **Palette.** Use a warm off-white surface, faint gridlines, and a subtle
  peach-to-lavender glow around the headline and primary chart. Use copper
  (`#B27055`) for the focus series or selection, lavender for comparison, and
  quiet neutral axes. Adapt contrast to the host theme and identify series with
  labels as well as color.
- **First view.** Show the main finding, units, time range, source, and visible
  or inspectable values. Check that the initial view stands on its own before
  interaction and remains legible in a narrow conversation pane.
- **Selection controls.** Prefer a native HTML range input for continuous
  numeric exploration when data or a validated model supports its full domain.
  Use a stepped slider for a small ordered numeric or time domain when adjacent
  values are meaningful to compare. Snap to exact available values, such as
  queried amount tiers. Use a labeled dropdown or other choice control for
  unordered categories. Update charts from retrieved results as the slider
  moves. Preserve native keyboard controls and show the selected value and
  unit. If the input stores an index, use `aria-valuetext` to announce the
  actual value and unit.
- **Interaction.** Filter and select locally within the retrieved results. When
  the host supports follow-ups, offer a labeled drill-down for a question that
  needs a different grain or source. Carry the selected entity, periods, metric,
  and existing authorized source into the follow-up and apply the analysis
  workflow to any new query. In a static host, show the chart and its source
  information directly.
