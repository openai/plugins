#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'USAGE'
Usage: heapprofd_reports.sh <native-alloc.pftrace> [output-dir]

Generates text reports from a Perfetto trace captured with the heapprofd data
source enabled.
USAGE
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

trace="${1:-}"
if [[ -z "$trace" ]]; then
  usage
  exit 2
fi

if [[ ! -f "$trace" ]]; then
  echo "Trace not found: $trace" >&2
  exit 1
fi

if [[ "$trace" != /* ]]; then
  trace="$(cd "$(dirname "$trace")" && pwd)/$(basename "$trace")"
fi

output_dir="${2:-$(dirname "$trace")}"
mkdir -p "$output_dir"
if [[ "$output_dir" != /* ]]; then
  output_dir="$(cd "$output_dir" && pwd)"
fi

trace_processor="${TRACE_PROCESSOR_SHELL:-}"
if [[ -z "$trace_processor" ]]; then
  if command -v trace_processor_shell >/dev/null 2>&1; then
    trace_processor="trace_processor_shell"
  elif command -v trace_processor >/dev/null 2>&1; then
    trace_processor="trace_processor"
  fi
fi

if [[ -z "$trace_processor" ]] || ! command -v "$trace_processor" >/dev/null 2>&1; then
  echo "Perfetto trace processor not found. Set TRACE_PROCESSOR_SHELL or install trace_processor_shell/trace_processor." >&2
  exit 1
fi

run_query() {
  "$trace_processor" -Q "$1" "$trace"
}

summary_report="$output_dir/heapprofd-summary.txt"
top_allocations_report="$output_dir/heapprofd-top-allocations.txt"
top_stack_report="$output_dir/heapprofd-top-stack.txt"
health_report="$output_dir/heapprofd-health.txt"

run_query "
select count(*) as allocation_rows, sum(size) as net_size
from __intrinsic_heap_profile_allocation;
" > "$summary_report"

run_query "
with alloc as (
  select callsite_id, sum(size) as net_size, sum(count) as net_count
  from __intrinsic_heap_profile_allocation
  group by callsite_id
  having net_size > 0
)
select
  alloc.callsite_id,
  alloc.net_size,
  alloc.net_count,
  frame.name as leaf_frame,
  mapping.name as leaf_mapping
from alloc
join __intrinsic_stack_profile_callsite callsite on callsite.id = alloc.callsite_id
join __intrinsic_stack_profile_frame frame on frame.id = callsite.frame_id
join __intrinsic_stack_profile_mapping mapping on mapping.id = frame.mapping
order by alloc.net_size desc
limit 30;
" > "$top_allocations_report"

top_callsite="$(
  run_query "
  select callsite_id
  from __intrinsic_heap_profile_allocation
  group by callsite_id
  having sum(size) > 0
  order by sum(size) desc
  limit 1;
  " | awk -F, 'NR > 1 { gsub(/"/, "", $1); print $1; exit }'
)"

if [[ "$top_callsite" =~ ^[0-9]+$ ]]; then
  run_query "
  with recursive stack(id, depth, parent_id, frame_id) as (
    select id, depth, parent_id, frame_id
    from __intrinsic_stack_profile_callsite
    where id = $top_callsite
    union all
    select callsite.id, callsite.depth, callsite.parent_id, callsite.frame_id
    from __intrinsic_stack_profile_callsite callsite
    join stack on callsite.id = stack.parent_id
  )
  select stack.depth, frame.name as frame, mapping.name as mapping
  from stack
  join __intrinsic_stack_profile_frame frame on frame.id = stack.frame_id
  join __intrinsic_stack_profile_mapping mapping on mapping.id = frame.mapping
  order by stack.depth;
  " > "$top_stack_report"
else
  printf 'No positive net allocation callsite found.\n' > "$top_stack_report"
fi

run_query "
select name, idx, severity, source, value, description
from stats
where lower(name) like '%heapprofd%'
   or lower(name) like 'traced_buf%'
   or lower(name) like '%packet_loss%'
   or lower(name) like '%overrun%'
order by name, idx;
" > "$health_report"

printf 'Wrote: %s\n' "$summary_report"
printf 'Wrote: %s\n' "$top_allocations_report"
printf 'Wrote: %s\n' "$top_stack_report"
printf 'Wrote: %s\n' "$health_report"
