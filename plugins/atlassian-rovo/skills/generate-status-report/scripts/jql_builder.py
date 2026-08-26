#!/usr/bin/env python3
"""
JQL Query Builder Utility

Helper functions for building common JQL queries for status reports.
"""

from typing import List, Optional
import re


def sanitize_jql_value(value: str) -> str:
    """
    Sanitize a value for use in JQL to prevent injection attacks.
    
    Args:
        value: The input value to sanitize
        
    Returns:
        Sanitized value safe for JQL queries
    """
    if not value:
        return value
    
    # Remove or escape potentially dangerous characters
    # Allow alphanumeric, spaces, hyphens, underscores, dots, @
    safe_pattern = re.compile(r'^[a-zA-Z0-9\s\-_.@]+$')
    
    if not safe_pattern.match(value):
        raise ValueError(
            f"Invalid characters in input: '{value}'. "
            f"Only alphanumeric characters, spaces, hyphens, underscores, dots, and @ are allowed."
        )
    
    # Escape double quotes by doubling them (JQL escaping)
    return value.replace('"', '""')


def sanitize_jql_list(values: List[str]) -> List[str]:
    """
    Sanitize a list of values for use in JQL.
    
    Args:
        values: List of input values to sanitize
        
    Returns:
        List of sanitized values
    """
    return [sanitize_jql_value(v) for v in values]


def build_project_query(
    project_key: str,
    statuses: Optional[List[str]] = None,
    exclude_done: bool = True,
    priorities: Optional[List[str]] = None,
    days_back: Optional[int] = None,
    assignee: Optional[str] = None,
    order_by: str = "priority DESC, updated DESC"
) -> str:
    """
    Build a JQL query for project status.
    
    Args:
        project_key: The Jira project key
        statuses: List of statuses to include (e.g., ["To Do", "In Progress"])
        exclude_done: Whether to exclude Done status (default True)
        priorities: List of priorities to include (e.g., ["Highest", "High"])
        days_back: Number of days to look back for updates (e.g., 7)
        assignee: Specific assignee email or "EMPTY" for unassigned
        order_by: JQL order by clause (default: "priority DESC, updated DESC")
    
    Returns:
        JQL query string
    """
    # Sanitize inputs to prevent JQL injection
    project_key = sanitize_jql_value(project_key)
    conditions = [f'project = "{project_key}"']
    
    if statuses:
        statuses = sanitize_jql_list(statuses)
        status_list = '", "'.join(statuses)
        conditions.append(f'status IN ("{status_list}")')
    elif exclude_done:
        conditions.append('status != Done')
    
    if priorities:
        priorities = sanitize_jql_list(priorities)
        priority_list = '", "'.join(priorities)
        conditions.append(f'priority IN ("{priority_list}")')
    
    if days_back:
        if not isinstance(days_back, int) or days_back < 0:
            raise ValueError(f"days_back must be a non-negative integer, got: {days_back}")
        conditions.append(f'updated >= -{days_back}d')
    
    if assignee:
        if assignee.upper() == "EMPTY":
            conditions.append('assignee is EMPTY')
        else:
            assignee = sanitize_jql_value(assignee)
            conditions.append(f'assignee = "{assignee}"')
    
    query = " AND ".join(conditions)
    
    if order_by:
        # Validate order_by contains only safe keywords
        order_by = sanitize_jql_value(order_by)
        query += f' ORDER BY {order_by}'
    
    return query


def build_blocked_query(
    project_key: str,
    high_priority_only: bool = False
) -> str:
    """Build query for blocked issues."""
    project_key = sanitize_jql_value(project_key)
    query = f'project = "{project_key}" AND status = Blocked'
    
    if high_priority_only:
        query += ' AND priority IN (Highest, High)'
    
    query += ' ORDER BY priority DESC, created ASC'
    return query


def build_completed_query(
    project_key: str,
    days_back: int = 7
) -> str:
    """Build query for recently completed issues."""
    project_key = sanitize_jql_value(project_key)
    
    if not isinstance(days_back, int) or days_back < 0:
        raise ValueError(f"days_back must be a non-negative integer, got: {days_back}")
    
    return (
        f'project = "{project_key}" AND '
        f'status = Done AND '
        f'resolved >= -{days_back}d '
        f'ORDER BY resolved DESC'
    )


def build_in_progress_query(
    project_key: str,
    priorities: Optional[List[str]] = None
) -> str:
    """Build query for in-progress issues."""
    project_key = sanitize_jql_value(project_key)
    query = f'project = "{project_key}" AND status IN ("In Progress", "In Review")'
    
    if priorities:
        priorities = sanitize_jql_list(priorities)
        priority_list = '", "'.join(priorities)
        query += f' AND priority IN ("{priority_list}")'
    
    query += ' ORDER BY priority DESC, updated DESC'
    return query


def build_risk_query(
    project_key: str,
    include_overdue: bool = True
) -> str:
    """Build query for risk items (blocked or overdue high priority)."""
    project_key = sanitize_jql_value(project_key)
    conditions = [f'project = "{project_key}"']
    
    risk_conditions = ['status = Blocked']
    if include_overdue:
        risk_conditions.append('(duedate < now() AND status != Done)')
    
    conditions.append(f'({" OR ".join(risk_conditions)})')
    conditions.append('priority IN (Highest, High)')
    
    query = " AND ".join(conditions)
    query += ' ORDER BY priority DESC, duedate ASC'
    return query


def build_unassigned_query(
    project_key: str,
    exclude_done: bool = True
) -> str:
    """Build query for unassigned issues."""
    project_key = sanitize_jql_value(project_key)
    query = f'project = "{project_key}" AND assignee is EMPTY'
    
    if exclude_done:
        query += ' AND status != Done'
    
    query += ' ORDER BY priority DESC, created ASC'
    return query


# Example usage
if __name__ == "__main__":
    # Example queries
    project = "PROJ"
    
    print("Open Issues Query:")
    print(build_project_query(project))
    print()
    
    print("High Priority In Progress:")
    print(build_in_progress_query(project, priorities=["Highest", "High"]))
    print()
    
    print("Blocked Issues:")
    print(build_blocked_query(project, high_priority_only=True))
    print()
    
    print("Completed Last Week:")
    print(build_completed_query(project, days_back=7))
    print()
    
    print("Risk Items:")
    print(build_risk_query(project))
    print()
    
    print("Unassigned Open Issues:")
    print(build_unassigned_query(project))
