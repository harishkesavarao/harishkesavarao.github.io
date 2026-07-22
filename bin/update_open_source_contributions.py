#!/usr/bin/env python3
"""Regenerate _pages/open_source.md from live GitHub PR data.

Queries the GitHub GraphQL API for pull requests authored by the configured
accounts, drops PRs against the accounts' own repos/forks (personal work),
and writes out an auto-generated summary grouped by repository.
"""
import os
import sys
import urllib.request
import json
from datetime import datetime

USERS = ["harishkesavarao", "harishkrao"]
OWN_ACCOUNTS = {u.lower() for u in USERS}
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "_pages", "open_source.md")

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


def parse_date(iso_str):
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))


def build_markdown(grouped):
    lines = [
        "---",
        "layout: page",
        "title: open source",
        "permalink: /open_source/",
        "description: Live snapshot of open, in-review, and merged pull requests to repositories outside my own projects.",
        "nav: true",
        "nav_order: 2",
        "---",
        "",
        "This page is generated automatically from GitHub pull request activity across "
        + ", ".join(f"@{u}" for u in USERS)
        + ". It excludes personal repositories and personal forks, and only lists pull "
        "requests that are open, in review, or merged.",
        "",
    ]
    for repo in sorted(grouped):
        lines.append(f"#### {repo}")
        lines.append("")
        for pr in sorted(grouped[repo], key=lambda p: p["createdAt"], reverse=True):
            date_str = parse_date(pr["createdAt"]).strftime("%b %d, %Y")
            lines.append(f"- [{pr['title']}]({pr['url']}) — {status_label(pr)} ({date_str})")
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
