;(function() {
  'use strict';

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

}())