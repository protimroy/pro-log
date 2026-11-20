export const render = () => `
<div class="family-evidence">
  <div class="family-evidence-control" hidden>
    <label>Experiment cohort
      <select aria-label="Experiment cohort">
        <option value="all">All cohorts</option>
        <option value="mnist">MNIST activation-space</option>
        <option value="pilot">Sensor-control pilot</option>
        <option value="cifar">Learned-credit CIFAR-10</option>
      </select>
    </label>
  </div>
  <section class="family-cohort" data-cohort="mnist" aria-labelledby="family-mnist">
    <h3 id="family-mnist">Activation-space on MNIST</h3>
    <p>784 → 1024 → 10 · 1 seed · 8 epochs · best test accuracy</p>
    <table><thead><tr><th scope="col">Method</th><th scope="col">Accuracy</th><th scope="col">Recorded time</th></tr></thead><tbody>
      <tr><th scope="row">AdamW</th><td><meter min="0" max="100" value="97.80">97.80%</meter> 97.80%</td><td>29.5 s</td></tr>
      <tr><th scope="row">Activation-Space · hybrid head</th><td><meter min="0" max="100" value="97.21">97.21%</meter> 97.21%</td><td>205.6 s</td></tr>
      <tr><th scope="row">Activation-Space · full probes</th><td><meter min="0" max="100" value="96.87">96.87%</meter> 96.87%</td><td>180.1 s</td></tr>
    </tbody></table>
  </section>
  <section class="family-cohort" data-cohort="pilot" aria-labelledby="family-pilot">
    <h3 id="family-pilot">Short sensor-control pilot</h3>
    <p>390 steps · 2 seeds · held-out training validation · mean accuracy</p>
    <table><thead><tr><th scope="col">Method</th><th scope="col">Accuracy</th></tr></thead><tbody>
      <tr><th scope="row">Two-Timescale Activation-Space</th><td><meter min="0" max="100" value="29.70">29.70%</meter> 29.70%</td></tr>
      <tr><th scope="row">Matched-JVP Control</th><td><meter min="0" max="100" value="28.75">28.75%</meter> 28.75%</td></tr>
      <tr><th scope="row">Learned Credit-Map Hybrid</th><td><meter min="0" max="100" value="44.14">44.14%</meter> 44.14%</td></tr>
      <tr><th scope="row">AdamW</th><td><meter min="0" max="100" value="42.61">42.61%</meter> 42.61%</td></tr>
    </tbody></table>
  </section>
  <section class="family-cohort" data-cohort="cifar" aria-labelledby="family-cifar">
    <h3 id="family-cifar">Learned-credit hybrid on CIFAR-10</h3>
    <p>W512 / d7 residual MLP · 3 paired seeds · 50 epochs · mean accuracy</p>
    <table><thead><tr><th scope="col">Method</th><th scope="col">Accuracy</th></tr></thead><tbody>
      <tr><th scope="row">Learned Credit-Map Hybrid</th><td><meter min="0" max="100" value="57.79">57.79%</meter> 57.79%</td></tr>
      <tr><th scope="row">AdamW</th><td><meter min="0" max="100" value="60.93">60.93%</meter> 60.93%</td></tr>
    </tbody></table>
  </section>
</div>`;

export const style = `
body:has(.family-evidence) .article-shell { max-width: 72rem; }
body:has(.family-evidence) .article-header { max-width: 54rem; margin-bottom: 3rem; }
body:has(.family-evidence) .article-title { font-family: Georgia, serif; font-size: 3rem; line-height: 1.08; font-weight: 600; }
body:has(.family-evidence) .article-kicker { color: #1d6659; letter-spacing: 0; }
body:has(.family-evidence) .article-toc { padding: 0; border: 0; border-top: 2px solid #1d2926; background: transparent; }
body:has(.family-evidence) .article-toc summary { cursor: pointer; padding: .8rem 0; font-size: .8rem; font-weight: 700; text-transform: uppercase; }
body:has(.family-evidence) .article-toc a { display: block; color: #596a64; font-size: .85rem; line-height: 1.4; }
body:has(.family-evidence) .article-content .content { color: #1d2926; line-height: 1.8; }
body:has(.family-evidence) .article-content .content > h6 { font-family: Georgia, serif; font-size: 1.65rem; line-height: 1.25; letter-spacing: 0; text-transform: none; border-top: 1px solid #d7ded9; padding-top: 1.75rem; margin-top: 3rem; }
body:has(.family-evidence) .article-content .content a { color: #1d6659; }
body:has(.family-evidence) .article-content .content table { display: block; max-width: 100%; overflow-x: auto; }
@media (min-width: 1024px) { body:has(.family-evidence) .article-grid { grid-template-columns: minmax(0, 14rem) minmax(0, 1fr); gap: 3rem; } body:has(.family-evidence) .article-toc { position: sticky; top: 1.5rem; max-height: calc(100vh - 3rem); overflow-y: auto; } }
@media (max-width: 600px) { body:has(.family-evidence) .article-title { font-size: 2.25rem; } body:has(.family-evidence) .article-content .content > h6 { font-size: 1.4rem; } }
.family-evidence-control { margin-bottom: 1.5rem; }
.family-evidence-control label { display: grid; gap: .4rem; max-width: 20rem; font-size: .85rem; font-weight: 700; }
.family-evidence-control select { width: 100%; padding: .5rem; border: 1px solid #9faea6; background: white; color: #1d2926; font: inherit; }
.family-cohort + .family-cohort { margin-top: 1.75rem; }
.family-cohort h3 { margin: 0 0 .25rem; font-size: 1.05rem; }
.family-cohort p { margin: 0 0 .65rem; color: #596a64; font-size: .85rem; }
.family-cohort table { width: 100%; font-size: .85rem; }
.family-cohort th, .family-cohort td { padding: .5rem; vertical-align: middle; }
.family-cohort meter { display: block; width: 100%; min-width: 4rem; height: .65rem; accent-color: #1d6659; }
.family-cohort[hidden] { display: none; }
`;

export const script = `
document.querySelectorAll('.family-evidence').forEach(function(root) {
  var contents = document.querySelector('.article-toc .table-of-contents');
  if (contents) {
    var list = contents.querySelector('ul');
    var label = contents.querySelector('.menu-label');
    if (list && label) {
      var details = document.createElement('details');
      var summary = document.createElement('summary');
      summary.textContent = label.textContent;
      details.open = matchMedia('(min-width: 701px)').matches;
      details.append(summary, list);
      label.replaceWith(details);
    }
  }
  var control = root.querySelector('.family-evidence-control');
  var select = control.querySelector('select');
  var cohorts = root.querySelectorAll('.family-cohort');
  select.addEventListener('change', function() {
    cohorts.forEach(function(cohort) {
      cohort.hidden = select.value !== 'all' && cohort.dataset.cohort !== select.value;
    });
  });
  control.hidden = false;
});
`;