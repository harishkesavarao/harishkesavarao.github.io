---
layout: page
title: technical notes
permalink: /technical_notes/
description: Short-form technical observations on data engineering, infrastructure, and systems.
nav: true
nav_order: 5
---

{% assign notes_sorted = site.technical_notes | sort: "date" | reverse %}

{% if notes_sorted.size > 0 %}
<ul class="post-list">
  {% for note in notes_sorted %}
  {% assign read_time = note.content | number_of_words | divided_by: 180 | plus: 1 %}
  <li>
    <h3><a class="post-title" href="{{ note.url | relative_url }}">{{ note.title }}</a></h3>
    <p>{{ note.description }}</p>
    <p class="post-meta">
      {{ note.date | date: "%B %-d, %Y" }} &nbsp;&middot;&nbsp; {{ read_time }} min read
    </p>
  </li>
  {% endfor %}
</ul>
{% else %}
<p>No notes yet.</p>
{% endif %}
