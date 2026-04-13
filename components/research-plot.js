const markup = [
  '<div class="rp-root">',
  '  <div class="rp-controls">',
  '    <label class="rp-label">Decision threshold',
  '      <input type="range" class="rp-slider" min="0.05" max="0.95" step="0.01" value="0.50">',
  '      <span class="rp-val">0.50</span>',
  '    </label>',
  '  </div>',
  '  <div class="rp-chart"></div>',
  '  <div class="rp-metrics">',
  '    <div class="rp-metric"><span class="rp-metric-label">Precision</span><span class="rp-metric-value rp-precision">-</span></div>',
  '    <div class="rp-metric"><span class="rp-metric-label">Recall</span><span class="rp-metric-value rp-recall">-</span></div>',
  '    <div class="rp-metric"><span class="rp-metric-label">F1 Score</span><span class="rp-metric-value rp-f1">-</span></div>',
  '    <div class="rp-metric"><span class="rp-metric-label">Accuracy</span><span class="rp-metric-value rp-accuracy">-</span></div>',
  '  </div>',
  '</div>'
].join('');

export const render = () => markup;

export const style = `
.rp-controls {
  margin-bottom: 1rem;
}

.rp-label {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.9rem;
  font-weight: 600;
}

.rp-slider {
  flex: 1;
}

.rp-val {
  min-width: 2.5em;
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.rp-chart {
  margin-bottom: 1rem;
}

.rp-chart figure {
  margin: 0;
}

.rp-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: 0.75rem;
}

.rp-metric {
  padding: 0.7rem 0.8rem;
  border: 1px solid #dbdbdb;
  background: #fafaf8;
}

.rp-metric-label {
  display: block;
  margin-bottom: 0.2rem;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #5c5c5c;
}

.rp-metric-value {
  display: block;
  font-size: 1.1rem;
  font-variant-numeric: tabular-nums;
}
`;

export const script = `
(function() {
  var data = [
    {score: 0.05, label: 0, jy: -0.12},
    {score: 0.12, label: 0, jy: 0.08},
    {score: 0.18, label: 0, jy: -0.06},
    {score: 0.23, label: 0, jy: 0.14},
    {score: 0.29, label: 0, jy: -0.10},
    {score: 0.34, label: 0, jy: 0.05},
    {score: 0.40, label: 0, jy: -0.15},
    {score: 0.44, label: 0, jy: 0.11},
    {score: 0.51, label: 0, jy: -0.07},
    {score: 0.57, label: 0, jy: 0.03},
    {score: 0.63, label: 0, jy: -0.13},
    {score: 0.72, label: 0, jy: 0.09},
    {score: 0.31, label: 1, jy: 0.12},
    {score: 0.38, label: 1, jy: -0.08},
    {score: 0.45, label: 1, jy: 0.15},
    {score: 0.50, label: 1, jy: -0.11},
    {score: 0.55, label: 1, jy: 0.06},
    {score: 0.61, label: 1, jy: -0.14},
    {score: 0.66, label: 1, jy: 0.10},
    {score: 0.73, label: 1, jy: -0.04},
    {score: 0.78, label: 1, jy: 0.13},
    {score: 0.83, label: 1, jy: -0.09},
    {score: 0.88, label: 1, jy: 0.07},
    {score: 0.93, label: 1, jy: -0.12}
  ];

  document.querySelectorAll('.rp-root').forEach(function(root) {
    if (root.dataset.bound) return;
    root.dataset.bound = 'true';

    var slider = root.querySelector('.rp-slider');
    var valEl = root.querySelector('.rp-val');
    var chartEl = root.querySelector('.rp-chart');

    function classify(d, t) {
      var predicted = d.score >= t ? 1 : 0;
      if (predicted === 1 && d.label === 1) return 'True Positive';
      if (predicted === 1 && d.label === 0) return 'False Positive';
      if (predicted === 0 && d.label === 0) return 'True Negative';
      return 'False Negative';
    }

    function update() {
      var t = Number(slider.value);
      valEl.textContent = t.toFixed(2);
      chartEl.innerHTML = '';

      var classified = data.map(function(d) {
        return {score: d.score, y: d.label + d.jy, outcome: classify(d, t)};
      });

      var w = chartEl.clientWidth || 560;
      var chart = Plot.plot({
        width: w,
        height: 260,
        marginLeft: 60,
        marginBottom: 40,
        marginTop: 30,
        style: {fontSize: '13px', background: 'transparent'},
        x: {label: 'Model score \\u2192', domain: [0, 1]},
        y: {label: null, domain: [-0.35, 1.35], ticks: [0, 1], tickFormat: function(d) { return d === 0 ? 'Negative' : 'Positive'; }},
        color: {
          domain: ['True Positive', 'True Negative', 'False Positive', 'False Negative'],
          range: ['#2563eb', '#6b7280', '#ef4444', '#f59e0b'],
          legend: true
        },
        marks: [
          Plot.ruleX([t], {stroke: '#111827', strokeDasharray: '6 4', strokeWidth: 1.5}),
          Plot.dot(classified, {x: 'score', y: 'y', fill: 'outcome', r: 5.5, stroke: '#fff', strokeWidth: 1})
        ]
      });

      chartEl.appendChild(chart);

      var tp = 0, fp = 0, tn = 0, fn = 0;
      classified.forEach(function(d) {
        if (d.outcome === 'True Positive') tp++;
        else if (d.outcome === 'False Positive') fp++;
        else if (d.outcome === 'True Negative') tn++;
        else fn++;
      });

      var precision = tp + fp > 0 ? tp / (tp + fp) : 0;
      var recall = tp + fn > 0 ? tp / (tp + fn) : 0;
      var f1 = precision + recall > 0 ? 2 * precision * recall / (precision + recall) : 0;
      var accuracy = (tp + tn) / data.length;

      root.querySelector('.rp-precision').textContent = precision.toFixed(2);
      root.querySelector('.rp-recall').textContent = recall.toFixed(2);
      root.querySelector('.rp-f1').textContent = f1.toFixed(2);
      root.querySelector('.rp-accuracy').textContent = accuracy.toFixed(2);
    }

    slider.addEventListener('input', update);
    update();
  });
})();
`;