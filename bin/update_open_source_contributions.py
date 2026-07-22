#!/usr/bin/env python3
"""Regenerate _projects/open_source_contributions.md from live GitHub PR data.

Queries the GitHub GraphQL API for pull requests authored by the configured
accounts, drops PRs against the accounts' own repos/forks (personal work),
and writes out an auto-generated summary grouped by repository.
"""
import os
import sys
import urllib.request
import json
from datetime import datetime, timezone
from html import escape

USERS = ["harishkesavarao", "harishkrao"]
OWN_ACCOUNTS = {u.lower() for u in USERS}
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "_projects", "open_source_contributions.md")

GRAPHQL_URL = "https://api.github.com/graphql"

QUERY = """
query($searchQuery: String!, $after: String) {
  search(query: $searchQuery, type: ISSUE, first: 100, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on PullRequest {
        title
        url
        state
        reviewDecision
        createdAt
        repository {
          nameWithOwner
          isFork
          owner { login }
        }
      }
    }
  }
}
"""


def graphql_request(query, variables, token):
    body = json.dumps({"query": query, "variables": variables}).encode("utf-8")
    req = urllib.request.Request(
        GRAPHQL_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "open-source-contributions-updater",
        },
        method="POST",
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_prs(user, token):
    prs = []
    after = None
    search_query = f"type:pr author:{user}"
    while True:
        data = graphql_request(QUERY, {"searchQuery": search_query, "after": after}, token)
        if "errors" in data:
            raise RuntimeError(data["errors"])
        result = data["data"]["search"]
        prs.extend(n for n in result["nodes"] if n)
        if result["pageInfo"]["hasNextPage"]:
            after = result["pageInfo"]["endCursor"]
        else:
            break
    return prs


def status_label(pr):
    if pr["state"] == "MERGED":
        return "merged"
    if pr["state"] == "OPEN":
        decision = pr.get("reviewDecision")
        if decision == "APPROVED":
            return "open, approved — pending merge"
        if decision == "REVIEW_REQUIRED":
            return "open, in review"
        if decision == "CHANGES_REQUESTED":
            return "open, changes requested"
        return "open"
    return None  # CLOSED (unmerged) - excluded


# Status palette: fixed, reserved for state - never themed or reused as a
# categorical series color. See dataviz skill references/palette.md.
STATUS_STYLE = {
    "merged": ("#0ca30c", "#0ca30c", "Merged"),
    "changes_requested": ("#d03b3b", "#e66767", "Changes requested"),
    "open": ("#fab219", "#fab219", "Open / in review"),
}


def status_class(pr):
    label = status_label(pr)
    if label is None:
        return None
    if label == "merged":
        return "merged"
    if label == "open, changes requested":
        return "changes_requested"
    return "open"  # open, approved, or in review


def parse_date(iso_str):
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))


def build_timeline_svg(grouped):
    all_prs = [(repo, pr) for repo, prs in grouped.items() for pr in prs]
    if not all_prs:
        return ""

    repos = sorted(grouped, key=lambda r: min(parse_date(p["createdAt"]) for p in grouped[r]))
    dates = [parse_date(pr["createdAt"]) for _, pr in all_prs]
    min_date, max_date = min(dates), max(dates)
    today = datetime.now(timezone.utc)
    if max_date < today:
        max_date = today
    span = (max_date - min_date).days or 1
    # pad both ends slightly so dots at the extremes aren't clipped
    pad_days = max(span * 0.04, 5)
    range_start = min_date - _days(pad_days)
    range_end = max_date + _days(pad_days)
    total_days = (range_end - range_start).days or 1

    longest_label = max(len(r) for r in repos)
    margin_left = min(280, max(168, 60 + longest_label * 6))
    margin_right = 24
    margin_top, margin_bottom = 16, 36
    row_height = 34
    width = 860
    plot_width = width - margin_left - margin_right
    height = margin_top + margin_bottom + row_height * len(repos)

    def x_for(date):
        return margin_left + (date - range_start).days / total_days * plot_width

    def y_for(i):
        return margin_top + i * row_height + row_height / 2

    # year/quarter-ish ticks: pick up to 6 evenly spaced points across the range
    tick_count = min(6, max(2, total_days // 60))
    ticks = []
    for i in range(tick_count + 1):
        d = range_start + _days(total_days * i / tick_count)
        ticks.append(d)

    parts = []
    parts.append(
        f'<svg class="osc-timeline-svg" viewBox="0 0 {width} {height}" '
        f'role="img" aria-label="Timeline of open source pull requests">'
    )

    # gridlines + tick labels
    for d in ticks:
        x = x_for(d)
        parts.append(
            f'<line x1="{x:.1f}" y1="{margin_top}" x2="{x:.1f}" y2="{height - margin_bottom:.1f}" '
            f'class="osc-grid" />'
        )
        parts.append(
            f'<text x="{x:.1f}" y="{height - margin_bottom + 18:.1f}" class="osc-axis-label" '
            f'text-anchor="middle">{d.strftime("%b %Y")}</text>'
        )

    # baseline
    parts.append(
        f'<line x1="{margin_left}" y1="{height - margin_bottom:.1f}" x2="{width - margin_right}" '
        f'y2="{height - margin_bottom:.1f}" class="osc-baseline" />'
    )

    # repo lanes: label + row divider + dots
    for i, repo in enumerate(repos):
        y = y_for(i)
        parts.append(
            f'<text x="{margin_left - 12}" y="{y + 4:.1f}" class="osc-repo-label" '
            f'text-anchor="end">{escape(repo)}</text>'
        )
        if i > 0:
            row_top = margin_top + i * row_height
            parts.append(
                f'<line x1="{margin_left}" y1="{row_top}" x2="{width - margin_right}" y2="{row_top}" '
                f'class="osc-grid" />'
            )
        for pr in sorted(grouped[repo], key=lambda p: p["createdAt"]):
            cls = status_class(pr)
            if cls is None:
                continue
            fill_light, fill_dark, status_text = STATUS_STYLE[cls]
            x = x_for(parse_date(pr["createdAt"]))
            title = f"{pr['title']} — {status_text}, {parse_date(pr['createdAt']).strftime('%b %d, %Y')}"
            parts.append(
                f'<a href="{escape(pr["url"])}" target="_blank" rel="noopener">'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" class="osc-dot osc-dot-{cls}">'
                f'<title>{escape(title)}</title>'
                f'</circle></a>'
            )

    parts.append("</svg>")
    svg = "".join(parts)

    legend_items = "".join(
        f'<span class="osc-legend-item"><span class="osc-legend-swatch osc-dot-{cls}"></span>{text}</span>'
        for cls, (_, _, text) in STATUS_STYLE.items()
    )

    style = """
<style>
.osc-timeline { margin: 1.5rem 0 2rem; }
.osc-timeline-svg { width: 100%; height: auto; display: block; font-family: system-ui, -apple-system, "Segoe UI", sans-serif; }
.osc-timeline-svg { --osc-surface: #fcfcfb; --osc-grid: #e1e0d9; --osc-baseline: #c3c2b7; --osc-muted: #898781; --osc-ink: #52514e; }
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .osc-timeline-svg { --osc-surface: #1a1a19; --osc-grid: #2c2c2a; --osc-baseline: #383835; --osc-muted: #898781; --osc-ink: #c3c2b7; }
}
:root[data-theme="dark"] .osc-timeline-svg { --osc-surface: #1a1a19; --osc-grid: #2c2c2a; --osc-baseline: #383835; --osc-muted: #898781; --osc-ink: #c3c2b7; }
.osc-grid { stroke: var(--osc-grid); stroke-width: 1; }
.osc-baseline { stroke: var(--osc-baseline); stroke-width: 1; }
.osc-axis-label, .osc-repo-label { fill: var(--osc-muted); font-size: 11px; }
.osc-repo-label { fill: var(--osc-ink); }
.osc-dot { stroke: var(--osc-surface); stroke-width: 2; cursor: pointer; }
.osc-dot-merged { fill: #0ca30c; }
.osc-dot-open { fill: #fab219; }
.osc-dot-changes_requested { fill: #d03b3b; }
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) .osc-dot-changes_requested { fill: #e66767; }
}
:root[data-theme="dark"] .osc-dot-changes_requested { fill: #e66767; }
.osc-legend { display: flex; flex-wrap: wrap; gap: 1rem; margin-top: 0.5rem; font-size: 0.85rem; color: var(--osc-ink, #52514e); }
.osc-legend-item { display: inline-flex; align-items: center; gap: 0.4rem; }
.osc-legend-swatch { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
</style>
"""

    return (
        f'{style}\n<div class="osc-timeline">\n{svg}\n'
        f'<div class="osc-legend">{legend_items}</div>\n</div>\n'
    )


def _days(n):
    from datetime import timedelta

    return timedelta(days=n)


def build_markdown(grouped):
    lines = [
        "---",
        "layout: page",
        "title: Open Source Contributions",
        "description: Live snapshot of open, in-review, and merged pull requests to repositories outside my own projects.",
        "importance: 2",
        "category: side-projects",
        "---",
        "",
        "This page is generated automatically from GitHub pull request activity across "
        + ", ".join(f"@{u}" for u in USERS)
        + ". It excludes personal repositories and personal forks, and only lists pull "
        "requests that are open, in review, or merged.",
        "",
    ]
    timeline = build_timeline_svg(grouped)
    if timeline:
        lines.append(timeline)
        lines.append("")
    for repo in sorted(grouped):
        lines.append(f"#### {repo}")
        lines.append("")
        for pr in sorted(grouped[repo], key=lambda p: p["createdAt"], reverse=True):
            lines.append(f"- [{pr['title']}]({pr['url']}) — {status_label(pr)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("GITHUB_TOKEN environment variable is required", file=sys.stderr)
        sys.exit(1)

    grouped = {}
    for user in USERS:
        for pr in fetch_prs(user, token):
            repo = pr["repository"]
            owner = repo["owner"]["login"].lower()
            if owner in OWN_ACCOUNTS:
                continue  # personal repo or personal fork
            label = status_label(pr)
            if label is None:
                continue  # closed, unmerged
            grouped.setdefault(repo["nameWithOwner"], []).append(pr)

    markdown = build_markdown(grouped)
    with open(OUTPUT_PATH, "w") as f:
        f.write(markdown)
    print(f"Wrote {sum(len(v) for v in grouped.values())} PR(s) across {len(grouped)} repo(s) to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
