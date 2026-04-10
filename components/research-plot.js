const markup = [
  '<div class="research-plot" data-threshold="0.50">',
  '  <div class="research-plot-controls">',
  '    <label>',
  '      Decision threshold',
  '      <input class="research-threshold" type="range" min="0.10" max="0.90" step="0.01" value="0.50" />',
  '    </label>',
  '  </div>',
  '  <div class="research-plot-frame">',
  '    <svg viewBox="0 0 400 240" role="img" aria-label="Synthetic threshold sweep plot">',
  '      <rect x="40" y="20" width="320" height="180" fill="#fcfcfb" stroke="#d4d4d4"></rect>',
  '      <line x1="40" y1="200" x2="360" y2="200" stroke="#666"></line>',
  '      <line x1="40" y1="20" x2="40" y2="200" stroke="#666"></line>',
  '      <line class="threshold-line" x1="200" y1="20" x2="200" y2="200" stroke="#111827" stroke-dasharray="6 4"></line>',
  '      <circle class="research-point" cx="78" cy="74" r="6" fill="#2563eb" opacity="0.9"></circle>',
  '      <circle class="research-point" cx="118" cy="92" r="6" fill="#2563eb" opacity="0.9"></circle>',
  '      <circle class="research-point" cx="152" cy="110" r="6" fill="#2563eb" opacity="0.9"></circle>',
  '      <circle class="research-point" cx="196" cy="122" r="6" fill="#2563eb" opacity="0.9"></circle>',
  '      <circle class="research-point" cx="234" cy="146" r="6" fill="#ef4444" opacity="0.9"></circle>',
  '      <circle class="research-point" cx="274" cy="162" r="6" fill="#ef4444" opacity="0.9"></circle>',
  '      <circle class="research-point" cx="306" cy="178" r="6" fill="#ef4444" opacity="0.9"></circle>',
  '      <circle class="research-point" cx="338" cy="196" r="6" fill="#ef4444" opacity="0.9"></circle>',
  '      <text x="360" y="225" text-anchor="end">feature score</text>',
  '      <text x="12" y="24" text-anchor="start">confidence</text>',
  '    </svg>',
  '  </div>',
  '  <div class="plot-summary">',
  '    <div><strong>threshold</strong><span class="metric-threshold">0.50</span></div>',
  '    <div><strong>true positives</strong><span class="metric-tp">4</span></div>',
  '    <div><strong>false positives</strong><span class="metric-fp">0</span></div>',
  '    <div><strong>true negatives</strong><span class="metric-tn">4</span></div>',
  '    <div><strong>false negatives</strong><span class="metric-fn">0</span></div>',
  '  </div>',
  '</div>',
].join('');

export const render = () => markup;

export const style = `
.research-plot-controls {
  margin-bottom: 1rem;
}

.research-plot-controls label {
  display: grid;
  gap: 0.45rem;
  font-size: 0.9rem;
  font-weight: 600;
}

.research-plot-frame {
  margin-bottom: 1rem;
}

.research-plot-frame svg {
  width: 100%;
  height: auto;
}

.plot-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(8rem, 1fr));
  gap: 0.75rem;
}

.plot-summary div {
  padding: 0.7rem 0.8rem;
  border: 1px solid #dbdbdb;
  background: #fafaf8;
}

.plot-summary strong,
.plot-summary span {
  display: block;
}

.plot-summary strong {
  margin-bottom: 0.2rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #5c5c5c;
}

.plot-summary span {
  font-size: 1.1rem;
}
`;

export const script = `
Array.from(document.querySelectorAll('.research-plot')).forEach(function (root) {
  if (root.dataset.bound === 'true') return;
  root.dataset.bound = 'true';

  var slider = root.querySelector('.research-threshold');
  var thresholdValue = root.querySelector('.metric-threshold');
  var line = root.querySelector('.threshold-line');
  var tpNode = root.querySelector('.metric-tp');
  var fpNode = root.querySelector('.metric-fp');
  var tnNode = root.querySelector('.metric-tn');
  var fnNode = root.querySelector('.metric-fn');
  var points = Array.from(root.querySelectorAll('.research-point'));

  function updateMetrics() {
    var threshold = Number(slider.value);
    var lineX = 40 + threshold * 320;
    var tp = 0;
    var fp = 0;
    var tn = 0;
    var fn = 0;

    thresholdValue.textContent = threshold.toFixed(2);
    line.setAttribute('x1', String(lineX));
    line.setAttribute('x2', String(lineX));

    points.forEach(function (point, index) {
      var cx = Number(point.getAttribute('cx'));
      var normalizedX = (cx - 40) / 320;
      var predictedPositive = normalizedX <= threshold;
      var actualPositive = index < 4;

      if (predictedPositive && actualPositive) tp += 1;
      else if (predictedPositive && !actualPositive) fp += 1;
      else if (!predictedPositive && actualPositive) fn += 1;
      else tn += 1;

      point.setAttribute('fill', predictedPositive ? '#2563eb' : '#ef4444');
    });

    tpNode.textContent = String(tp);
    fpNode.textContent = String(fp);
    tnNode.textContent = String(tn);
    fnNode.textContent = String(fn);
  }

  slider.addEventListener('input', updateMetrics);
  updateMetrics();
});
`;