---
slug: /
title: Pro-Log
description: Research notes on machine learning, neural networks, and optimization.
canonical_url: "https://www.protimroy.com/pro-log/"
allow_html: true
template: page.html
---

<style>
  .prolog-index { --index-line: rgba(60,75,95,.18); --index-hover: rgba(90,110,140,.045); --index-feature: transparent; --index-feature-hover: rgba(90,110,140,.045); --index-accent: #304d72; --index-muted: #526071; }
  @media (prefers-color-scheme: dark) { .prolog-index { --index-line: rgba(190,204,226,.22); --index-hover: rgba(180,200,230,.065); --index-feature: transparent; --index-feature-hover: rgba(180,200,230,.065); --index-accent: #9fc4f4; --index-muted: #b7c3d2; } }
  .date { font-family: 'Inter', sans-serif; }

  /* Keep table rows in the table formatting model; style cells instead. */
  .prolog-index { width: 100%; border-collapse: collapse; table-layout: fixed; }
  .prolog-index .postcontainer { display: table-row; height: auto; background: transparent; }
  .prolog-index .postcontainer > td {
    padding: 11px 0;
    vertical-align: middle;
    border-bottom: 1px solid var(--index-line);
    overflow-wrap: anywhere;
  }
  .prolog-index .postcontainer:hover > td { background: var(--index-hover); }
  .prolog-index .post_title,
  .prolog-index .post_text { display: block; font-family: 'Inter', sans-serif; margin: 0; }
  .prolog-index .post_title { font-size: 16px; font-style: normal; font-weight: 600; line-height: 1.4; }
  .prolog-index .post_text { font-size: 13px; line-height: 1.55; margin-top: 2px; }
  .prolog-index .post_date { display: block; margin-top: 3px; font: 400 12px/1.5 'Inter', sans-serif; color: var(--index-muted); }
  .prolog-index .post_title a { color: inherit; text-decoration: none; }
  .prolog-index .post_title a:hover,
  .prolog-index .post_title a:focus-visible { text-decoration: underline; }

  .prolog-index .research-series-head > td {
    padding: 17px 0 10px;
    background: var(--index-feature);
    border-left: none;
  }
  .prolog-index .research-series-head:hover > td { background: var(--index-feature-hover); }
  .prolog-index .research-series-head .post_title {
    font-size: 19px;
    font-weight: 650;
    line-height: 1.25;
  }
  .prolog-index .research-series-label {
    display: block;
    font: 700 11px 'Inter', sans-serif;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 4px;
  }
  .prolog-index .research-series-chapter > td {
    padding: 9px 0 9px 18px;
    border-left: none;
  }
  .prolog-index .research-series-chapter .post_title { font-size: 15px; font-weight: 500; }
  .prolog-index .research-series-chapter .post_text { font-size: 12px; }
  .prolog-index .research-series-chapter .post_title::before {
    content: '↳';
    margin-right: 7px;
    opacity: .6;
  }
  @media (max-width: 600px) {
    .prolog-index .postcontainer > td { padding: 10px 0; }
    .prolog-index .research-series-head > td { padding: 15px 0 9px; }
    .prolog-index .research-series-head .post_title { font-size: 19px; }
    .prolog-index .research-series-chapter > td { padding: 9px 0 9px 12px; }
    .prolog-index .research-series-chapter .post_title { font-size: 16px; }
  }
</style>

<table class="prolog-index">
  <tbody>
    <tr class="postcontainer research-series-head">
      <td>
        <span class="research-series-label">Research series</span>
        <span class="post_title"><a href="/pro-log/function-space-programming-thread/">Function Space Programming</a></span>
        <span class="post_text">Research questions, chapter map, and evidence status</span>
        <time class="post_date" datetime="2026-11-22">Updated November 22, 2026</time>
      </td>
    </tr>
    <tr class="postcontainer research-series-chapter">
      <td>
        <span class="post_title"><a href="/pro-log/function-space-programming/">Part I · Constructing Functions</a></span>
        <span class="post_text">XOR, MNIST, LLM-proposed edits, and compiled Transformer functions</span>
        <time class="post_date" datetime="2026-11-22">Updated November 22, 2026</time>
      </td>
    </tr>
    <tr class="postcontainer research-series-chapter">
      <td>
        <span class="post_title"><a href="/pro-log/function-space-programming-shared-functions/">Part II · Shared Functions, Lost Information</a></span>
        <span class="post_text">R12–R13: KL clustering, sparse corrections, and negative results</span>
        <time class="post_date" datetime="2026-11-22">Updated November 22, 2026</time>
      </td>
    </tr>
    <tr class="postcontainer research-series-head">
      <td>
        <span class="research-series-label">Research series</span>
        <span class="post_title"><a href="/pro-log/alopex-thread/">ALOPEX</a></span>
        <span class="post_text">Correlative learning, activation-space credit, and scaling limitations</span>
        <time class="post_date" datetime="2026-11-22">Updated November 22, 2026</time>
      </td>
    </tr>
    <tr class="postcontainer research-series-chapter">
      <td>
        <span class="post_title"><a href="/pro-log/activation-space-alopex/">Activation-Space ALOPEX</a></span>
        <span class="post_text">Hidden-activation interventions and measured local-credit experiments</span>
        <time class="post_date" datetime="2026-11-22">Updated November 22, 2026</time>
      </td>
    </tr>
    <tr class="postcontainer research-series-chapter">
      <td>
        <span class="post_title"><a href="/pro-log/alopex-partial-negative-result/">ALOPEX: A Partial Negative Result</a></span>
        <span class="post_text">Historical reconstruction, scaling evidence, and unresolved limitations</span>
        <time class="post_date" datetime="2026-11-22">Updated November 22, 2026</time>
      </td>
    </tr>
  </tbody>
</table>

<table class="table prolog-index">
  <thead>
    <tr>
      <th><div class="date">June 2025</div></th>
    </tr>
  </thead>
  <tbody>
    <tr class="postcontainer">
      <td>
        <span class="post_title"><a href="https://github.com/protimroy/basis">Basis</a></span>
        <span class="post_text">Laboratory version for building neural networks from scratch in low-level PyTorch</span>
      </td>
    </tr>
  </tbody>
</table>

#### About

Inspired by [1],[2],[3],[4].<br>
This is an ever growing list.<br>

<a href="https://distill.pub/2020/circuits/">[1]https://distill.pub/2020/circuits/</a><br>
<a href="https://worldmodels.github.io">[2]https://worldmodels.github.io</a><br>
<a href="https://transformer-circuits.pub/">[3]https://transformer-circuits.pub/</a><br>
<a href="https://lilianweng.github.io">[4]https://lilianweng.github.io</a><br>

<a href="https://protimroy.com">Protim Roy</a> &copy; 2024<br>
Made with <a href="https://github.com/sea-grass/goku">Goku</a> &copy; 2024