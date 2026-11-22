---
slug: /
title: Pro-Log
description: Hi, this is Protim. I am documenting most of my learnings in the fields of artificial intelligence, machine learning, deep learning, generative ai, ..etc, here.
canonical_url: "https://www.protimroy.com/pro-log/"
allow_html: true
template: page.html
---

<style>
  .date { font-family: 'Inter', sans-serif; }

  /* Keep table rows in the table formatting model; style cells instead. */
  .prolog-index { width: 100%; border-collapse: collapse; table-layout: fixed; }
  .prolog-index .postcontainer { display: table-row; height: auto; background: transparent; }
  .prolog-index .postcontainer > td {
    padding: 15px 20px;
    vertical-align: middle;
    border-bottom: 1px solid rgba(90, 100, 115, .16);
    overflow-wrap: anywhere;
  }
  .prolog-index .postcontainer:hover > td { background: rgba(90, 110, 140, .055); }
  .prolog-index .post_title,
  .prolog-index .post_text { display: block; font-family: 'Inter', sans-serif; margin: 0; }
  .prolog-index .post_title { font-size: 19px; font-style: normal; font-weight: 600; line-height: 1.4; }
  .prolog-index .post_text { font-size: 14px; line-height: 1.6; margin-top: 4px; }
  .prolog-index .post_date { display: block; margin-top: 5px; font: 500 12px/1.5 'Inter', sans-serif; opacity: .72; }
  .prolog-index .post_title a { color: inherit; text-decoration: none; }
  .prolog-index .post_title a:hover,
  .prolog-index .post_title a:focus-visible { text-decoration: underline; }

  .prolog-index .research-series-head > td {
    padding: 22px 24px;
    background: rgba(35, 55, 85, .10);
    border-left: 4px solid #304d72;
  }
  .prolog-index .research-series-head:hover > td { background: rgba(35, 55, 85, .15); }
  .prolog-index .research-series-head .post_title {
    font-size: 26px;
    font-weight: 750;
    line-height: 1.25;
  }
  .prolog-index .research-series-label {
    display: block;
    font: 700 11px 'Inter', sans-serif;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .prolog-index .research-series-chapter > td {
    padding: 14px 20px 14px 40px;
    border-left: 2px solid rgba(48, 77, 114, .30);
  }
  .prolog-index .research-series-chapter .post_title { font-size: 17px; font-weight: 600; }
  .prolog-index .research-series-chapter .post_text { font-size: 13px; }
  .prolog-index .research-series-chapter .post_title::before {
    content: '↳';
    margin-right: 9px;
    opacity: .6;
  }
  @media (max-width: 600px) {
    .prolog-index .postcontainer > td { padding: 13px 12px; }
    .prolog-index .research-series-head > td { padding: 18px 15px; }
    .prolog-index .research-series-head .post_title { font-size: 22px; }
    .prolog-index .research-series-chapter > td { padding: 13px 12px 13px 23px; }
    .prolog-index .research-series-chapter .post_title { font-size: 16px; }
  }
</style>

<table class="table prolog-index">
  <thead>
    <tr>
      <th><div class="date">RESEARCH</div></th>
    </tr>
  </thead>
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

#### About this Thread Project

Inspired by [1],[2],[3],[4].<br>
This is an ever growing list.<br>

<a href="https://distill.pub/2020/circuits/">[1]https://distill.pub/2020/circuits/</a><br>
<a href="https://worldmodels.github.io">[2]https://worldmodels.github.io</a><br>
<a href="https://transformer-circuits.pub/">[3]https://transformer-circuits.pub/</a><br>
<a href="https://lilianweng.github.io">[4]https://lilianweng.github.io</a><br>

<a href="https://protimroy.com">Protim Roy</a> &copy; 2024<br>
Made with <a href="https://github.com/sea-grass/goku">Goku</a> &copy; 2024