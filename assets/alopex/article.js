(() => {
  if (!document.querySelector('.alopex-native')) return;
  const svgNamespace = 'http://www.w3.org/2000/svg';
  const svgElement = (name, attributes, text) => {
    const element = document.createElementNS(svgNamespace, name);
    Object.entries(attributes).forEach(([key, value]) => element.setAttribute(key, value));
    if (text !== undefined) element.textContent = text;
    return element;
  };

  const contents = document.querySelector('.article-toc .table-of-contents');
  if (contents) {
    const list = contents.querySelector('ul');
    const label = contents.querySelector('.menu-label');
    if (list && label) {
      const details = document.createElement('details');
      const summary = document.createElement('summary');
      summary.textContent = label.textContent;
      details.open = matchMedia('(min-width: 701px)').matches;
      details.append(summary, list);
      label.replaceWith(details);
    }
  }

  document.querySelectorAll('.interactive-data[data-records]').forEach(root => {
    const records = JSON.parse(root.dataset.records);
    const columns = JSON.parse(root.dataset.columns);
    const filters = JSON.parse(root.dataset.filters);
    const chart = root.dataset.chart ? JSON.parse(root.dataset.chart) : null;
    const table = root.querySelector('table');
    const body = table?.querySelector('tbody');
    if (!body) return;
    const rows = new Map(Array.from(body.rows, row => [row.dataset.rowId, row]));
    if (records.some(record => !rows.has(record.id))) return;
    const toolbar = root.querySelector('.data-toolbar');
    const search = toolbar.querySelector('input');
    const selects = Array.from(toolbar.querySelectorAll('select'));
    const count = toolbar.querySelector('.data-count');
    const buttons = Array.from(root.querySelectorAll('thead button'));
    const viewButtons = Array.from(toolbar.querySelectorAll('.data-view-switch button'));
    const tableWrap = root.querySelector('.data-table-wrap');
    const chartContainer = document.createElement('div');
    chartContainer.className = 'alopex-chart';
    chartContainer.hidden = true;
    tableWrap.after(chartContainer);
    let order = null;
    let view = 'table';

    function renderChart(visible) {
      chartContainer.replaceChildren();
      if (!visible.length) {
        chartContainer.textContent = 'No rows match the current filters.';
        return;
      }
      const values = visible.flatMap(record => chart.series.map(series => Number(record.values[series.key])).filter(Number.isFinite));
      const max = Math.max(1, ...values);
      const width = Math.max(620, visible.length * 120);
      const height = 320;
      const left = 55;
      const top = 25;
      const bottom = 105;
      const plotHeight = height - top - bottom;
      const groupWidth = (width - left - 20) / visible.length;
      const barWidth = Math.min(35, groupWidth / (chart.series.length + 1));
      const svg = svgElement('svg', { viewBox: `0 0 ${width} ${height}`, role: 'img', 'aria-label': chart.ariaLabel || 'Chart of the visible table rows' });
      for (let tick = 0; tick <= 4; tick += 1) {
        const value = max * tick / 4;
        const y = top + plotHeight * (1 - tick / 4);
        svg.append(svgElement('line', { x1: left, x2: width - 20, y1: y, y2: y, class: 'chart-grid' }));
        svg.append(svgElement('text', { x: left - 8, y: y + 4, 'text-anchor': 'end', class: 'chart-axis' }, value.toFixed(max < 10 ? 1 : 0)));
      }
      visible.forEach((record, rowIndex) => {
        const center = left + groupWidth * (rowIndex + 0.5);
        chart.series.forEach((series, seriesIndex) => {
          const value = Number(record.values[series.key]);
          if (!Number.isFinite(value)) return;
          const barHeight = Math.max(0, value / max * plotHeight);
          const bar = svgElement('rect', { x: center - chart.series.length * barWidth / 2 + seriesIndex * barWidth, y: top + plotHeight - barHeight, width: barWidth - 2, height: barHeight, class: `chart-series-${seriesIndex + 1}` });
          bar.append(svgElement('title', {}, `${series.label}: ${value}`));
          svg.append(bar);
        });
        const label = String(record.values[chart.xKey] ?? '');
        const labelNode = svgElement('text', { x: center, y: top + plotHeight + 20, 'text-anchor': 'end', transform: `rotate(-35 ${center} ${top + plotHeight + 20})`, class: 'chart-axis' }, label);
        svg.append(labelNode);
      });
      const legend = document.createElement('div');
      legend.className = 'alopex-chart-legend';
      chart.series.forEach((series, index) => {
        const label = document.createElement('span');
        const swatch = document.createElement('i');
        swatch.className = `chart-series-${index + 1}`;
        label.append(swatch, document.createTextNode(series.label));
        legend.append(label);
      });
      chartContainer.append(svg, legend);
    }

    function update() {
      const query = search.value.trim().toLowerCase();
      const visible = records.filter(record => {
        const matchesSearch = !query || columns.some(column => String(record.values[column.key] ?? '').toLowerCase().includes(query));
        return matchesSearch && filters.every((key, index) => !selects[index].value || String(record.values[key] ?? '') === selects[index].value);
      });
      if (order) visible.sort((first, second) => {
        const firstValue = first.values[order.key];
        const secondValue = second.values[order.key];
        const comparison = typeof firstValue === 'number' && typeof secondValue === 'number'
          ? firstValue - secondValue
          : String(firstValue ?? '').localeCompare(String(secondValue ?? ''), undefined, { numeric: true, sensitivity: 'base' });
        return order.direction * comparison;
      });
      const included = new Set(visible.map(record => record.id));
      records.forEach(record => { rows.get(record.id).hidden = !included.has(record.id); });
      visible.forEach(record => body.append(rows.get(record.id)));
      count.textContent = `${visible.length} / ${records.length} rows`;
      buttons.forEach((button, index) => {
        const sorted = order?.key === columns[index].key;
        button.parentElement.setAttribute('aria-sort', sorted ? (order.direction === 1 ? 'ascending' : 'descending') : 'none');
        const indicator = button.querySelector('span');
        if (indicator) indicator.textContent = sorted ? (order.direction === 1 ? ' ↑' : ' ↓') : ' ↕';
      });
      if (chart && view === 'chart') renderChart(visible);
    }

    search.addEventListener('input', update);
    selects.forEach(select => select.addEventListener('change', update));
    buttons.forEach((button, index) => button.addEventListener('click', () => {
      const key = columns[index].key;
      order = { key, direction: order?.key === key ? -order.direction : 1 };
      update();
    }));
    buttons.forEach(button => { button.disabled = false; });
    viewButtons.forEach((button, index) => button.addEventListener('click', () => {
      view = index === 0 ? 'table' : 'chart';
      tableWrap.hidden = view !== 'table';
      chartContainer.hidden = view !== 'chart';
      viewButtons.forEach((item, itemIndex) => item.setAttribute('aria-pressed', String(index === itemIndex)));
      update();
    }));
    root.classList.add('is-ready');
    update();
  });

  const scale = document.querySelector('.scale-trajectory');
  if (scale) {
    const selected = scale.querySelector('.scale-selected');
    scale.querySelectorAll('[data-scale]').forEach(point => {
      const item = JSON.parse(point.dataset.scale);
      const update = () => {
        const panels = selected.children;
        panels[0].querySelector('span').textContent = item.experiment;
        panels[0].querySelector('strong').textContent = item.label;
        panels[0].querySelector('small').textContent = item.architecture;
        panels[1].querySelector('strong').textContent = item.parameters.toLocaleString();
        panels[1].querySelector('small').textContent = item.method;
        panels[2].querySelector('p').textContent = item.result;
        panels[2].querySelector('small').textContent = item.evidence;
        scale.querySelectorAll('[data-scale]').forEach(other => other.setAttribute('aria-pressed', String(other === point)));
      };
      point.setAttribute('role', 'button');
      point.setAttribute('tabindex', '0');
      point.setAttribute('aria-pressed', String(item.id === 'p113m'));
      point.addEventListener('click', update);
      point.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); update(); }
      });
    });
  }

  const bibliography = document.querySelector('.bibliography-browser');
  if (bibliography) {
    const search = bibliography.querySelector('input');
    const buttons = Array.from(bibliography.querySelectorAll('.bibliography-scopes button'));
    const references = Array.from(bibliography.querySelectorAll('.references-list > li'));
    const count = bibliography.querySelector('.bibliography-count');
    let scope = 0;
    const update = () => {
      const query = search.value.trim().toLowerCase();
      let shown = 0;
      references.forEach(reference => {
        const background = Boolean(reference.querySelector('.background'));
        const visible = (scope === 0 || (scope === 1 ? !background : background)) && reference.textContent.toLowerCase().includes(query);
        reference.hidden = !visible;
        if (visible) shown += 1;
      });
      count.textContent = `Showing ${shown} of ${references.length} records.`;
      buttons.forEach((button, index) => button.setAttribute('aria-pressed', String(index === scope)));
    };
    search.addEventListener('input', update);
    buttons.forEach((button, index) => button.addEventListener('click', () => { scope = index; update(); }));
    bibliography.classList.add('is-ready');
    update();
  }
})();