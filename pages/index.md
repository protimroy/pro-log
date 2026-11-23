---
slug: /
title: Pro-Log
description: Research notes on machine learning, neural networks, and optimization.
canonical_url: "https://www.protimroy.com/pro-log/"
allow_html: true
template: page.html
---

<style>
  /* The main site supplies typography, colors, and table rhythm via Goku. */
  .prolog-index { width: 100%; border-collapse: collapse; }
  .prolog-index .postcontainer { display: table-row; background: transparent; }
  .prolog-index .postcontainer > td { vertical-align: top; overflow-wrap: anywhere; }
  .prolog-index .post_title,
  .prolog-index .post_text,
  .prolog-index .post_date { display: block; font: inherit; }
  .prolog-index .post_title { font-weight: 600; }
  .prolog-index .post_text,
  .prolog-index .post_date { font-size: inherit; font-weight: normal; }
  .prolog-index .research-series-head .post_title { font-weight: 700; }
  .prolog-index .research-series-chapter > td { padding-left: 1.25rem; }
  .prolog-index .research-series-label { display: none; }
  @media (max-width: 600px) {
    .prolog-index .research-series-chapter > td { padding-left: .75rem; }
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
    <tr class="postcontainer research-series-chapter">
      <td>
        <span class="post_title"><a href="/pro-log/function-space-programming-r14-r18/">Part III · Function Synthesis and Controls</a></span>
        <span class="post_text">R14–R18: Transformer injection, MNIST proposals, reconstruction, and experimental controls</span>
        <time class="post_date" datetime="2026-11-23">Updated November 23, 2026</time>
      </td>
    </tr>
    <tr class="postcontainer research-series-chapter">
      <td>
        <span class="post_title"><a href="/pro-log/function-space-programming-frozen-functions/">Part IV · Frozen Functions Before Backpropagation</a></span>
        <span class="post_text">R19–R28: function synthesis, spatial placement, and AdamW initialization controls</span>
        <time class="post_date" datetime="2026-11-23">Updated November 23, 2026</time>
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

<table class="prolog-index">
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

<footer class="site-footer"><a href="https://www.protimroy.com/">Protim Roy</a> © 2026 · Built with <a href="https://github.com/sea-grass/goku">Goku</a></footer>