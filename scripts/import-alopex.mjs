import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { cp, mkdir, readFile, writeFile } from 'node:fs/promises';
import { dirname, extname, join, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const site = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const source = resolve(process.env.ALOPEX_SOURCE || join(site, '../alopex_article'));
const require = createRequire(join(source, 'package.json'));
const { createServer } = require('vite');
const React = require('react');
const { renderToStaticMarkup } = require('react-dom/server');
const { parseFragment, serializeOuter } = await import(pathToFileURL(require.resolve('parse5')).href);
const hash = value => createHash('sha256').update(value).digest('hex');
const fingerprint = (name, value) => {
  const extension = extname(name);
  return `${name.slice(0, -extension.length)}-${createHash('md5').update(value).digest('hex').slice(0, 12)}${extension}`;
};
const input = await readFile(join(source, 'src/content/paper.mdx'), 'utf8');

const vite = await createServer({
  root: source,
  configFile: join(source, 'vite.config.js'),
  appType: 'custom',
  server: { middlewareMode: true },
  logLevel: 'error',
  plugins: [{
    name: 'pro-log-static-reader',
    enforce: 'pre',
    transform(code, id) {
      const path = id.split('?')[0];
      if (path.endsWith('/src/content/paper.mdx')) {
        return code
          .replace("from '../components/DeferredChapterExperiments.jsx'", "from '../components/StaticChapterExperiments.jsx'")
          .replace('The missing MSc thesis and exact submitted TensorFlow implementation prevent thesis-level attribution.', 'The MSc thesis is available as a primary source, but the exact submitted TensorFlow implementation remains unresolved.')
          .replace('Claims about the thesis require recovery of the thesis or submitted notebook.', 'The written thesis supports thesis-level claims; implementation-specific claims require the submitted notebook.')
          .replace('Every empirical figure in the final publication discloses or links to:', 'The publication evidence pipeline aims to retain the following provenance for empirical results:');
      }
      if (path.endsWith('/src/components/InteractiveDataTable.jsx')) {
        return code
          .replace("<div className={'interactive-data '+(compact?'compact':'')}>", "<div className={'interactive-data '+(compact?'compact':'')} data-records={JSON.stringify(rows.map(row=>({id:String(rowKey(row)),values:row})))} data-columns={JSON.stringify(columns.map(column=>({key:column.key,label:column.label})))} data-filters={JSON.stringify(filterColumns)} data-chart={chart?JSON.stringify({xKey:chart.xKey,ariaLabel:chart.ariaLabel,series:chart.series.map(item=>({key:item.key,label:item.label}))}):undefined}>")
          .replace('<tr\n                key={key}', '<tr\n                data-row-id={String(key)}\n                key={key}')
          .replace('className={sort?.key===column.key?', 'disabled className={sort?.key===column.key?');
      }
      if (path.endsWith('/src/experiments/evidence/ScaleTrajectory.jsx')) {
        return code.replace('onClick={()=>setSelected(row.id)} role="button" tabIndex="0"', 'data-scale={JSON.stringify(row)}');
      }
    },
  }],
});

let html;
let evidence;
try {
  const paper = await vite.ssrLoadModule('/src/content/paper.mdx');
  html = renderToStaticMarkup(React.createElement(paper.default));
  const scientific = await vite.ssrLoadModule('/src/data/scientificEvidence.js');
  const replay = await vite.ssrLoadModule('/src/data/chapterCloseEvidence.js');
  const scale = await vite.ssrLoadModule('/src/data/scaleTrajectory.js');
  evidence = { scientificEvidence: scientific.scientificEvidence, chapterCloseEvidence: replay.chapterCloseEvidence, evidenceReplaySource: replay.evidenceReplaySource, scaleMilestones: scale.scaleMilestones, depthMilestones: scale.depthMilestones, scaleSummary: scale.scaleSummary };
} finally {
  await vite.close();
}

const fragment = parseFragment(html);
const getAttr = (node, name) => node.attrs?.find(attr => attr.name === name)?.value;
const hasClass = (node, name) => (getAttr(node, 'class') || '').split(/\s+/).includes(name);
const nodes = [];
const visit = node => { nodes.push(node); (node.childNodes || []).forEach(visit); };
visit(fragment);
const references = new Map(nodes.filter(node => node.tagName === 'li' && getAttr(node, 'id')?.startsWith('ref-')).map(node => [getAttr(node, 'id'), node]));
const citations = new Map();
for (const node of nodes.filter(node => node.tagName === 'a' && hasClass(node, 'citation'))) {
  const reference = getAttr(node, 'href')?.slice(1);
  if (!references.has(reference)) throw new Error(`Missing citation destination: ${reference}`);
  const index = (citations.get(reference) || 0) + 1;
  citations.set(reference, index);
  const id = `citation-${reference.slice(4)}-${index}`;
  node.attrs.push({ name: 'id', value: id });
  const backlink = parseFragment(`<a class="citation-return" href="#${id}" aria-label="Return to citation ${index}">↩${index}</a>`).childNodes[0];
  backlink.parentNode = references.get(reference);
  references.get(reference).childNodes.push(backlink);
}
const sections = fragment.childNodes.filter(node => hasClass(node, 'paper-section'));
if (sections.length !== 12 || html.includes('citation-missing')) throw new Error('Article sections or citations are incomplete');
if ((html.match(/class="reference-main"/g) || []).length < 60) throw new Error('Bibliography is incomplete');
const lists = [...html.matchAll(/<ol class="equation-list">([\s\S]*?)<\/ol>/g)];
if (lists.length !== 6 || lists.reduce((count, match) => count + (match[1].match(/<li(?:\s|>)/g) || []).length, 0) !== 38) throw new Error('Equation appendix is incomplete');
const parts = [];
for (const section of sections) {
  const id = getAttr(section, 'id');
  const heading = section.childNodes.find(node => hasClass(node, 'paper-section-heading'));
  const titleNode = heading?.childNodes.find(node => node.tagName === 'h2');
  if (!id || !titleNode) throw new Error('Missing section title or anchor');
  const title = titleNode.childNodes.map(node => node.value || '').join('');
  section.attrs = section.attrs.filter(attr => attr.name !== 'aria-labelledby');
  section.attrs.push({ name: 'aria-label', value: title });
  section.childNodes = section.childNodes.filter(node => node !== heading && !hasClass(node, 'section-plate'));
  parts.push(`###### ${title}\n\n${serializeOuter(section)}`);
}
const frontmatter = `---\nslug: /alopex-partial-negative-result\ntitle: "ALOPEX: A Partial Negative Result"\ndescription: From correlative neural learning to an unresolved small-language-model scale test.\ncanonical_url: "https://www.protimroy.com/pro-log/alopex-partial-negative-result/"\nallow_html: true\noptions_toc: true\ntemplate: article.html\n---\n\n`;
const assetDir = join(site, 'assets/alopex');
await mkdir(assetDir, { recursive: true });
const katexDir = dirname(require.resolve('katex/dist/katex.min.css'));
await cp(join(katexDir, 'fonts'), join(assetDir, 'fonts'), { recursive: true });
let katexCss = await readFile(join(katexDir, 'katex.min.css'), 'utf8');
const fontNames = [...new Set([...katexCss.matchAll(/url\(fonts\/([^)]*)\)/g)].map(match => match[1]))];
for (const name of fontNames) {
  const font = await readFile(join(katexDir, 'fonts', name));
  katexCss = katexCss.replaceAll(`fonts/${name}`, `fonts/${fingerprint(name, font)}`);
}
await writeFile(join(assetDir, 'katex.min.css'), katexCss);
const stylesheet = await readFile(join(assetDir, 'article.css'));
const script = await readFile(join(assetDir, 'article.js'));
const assetUrl = (name, content) => `/pro-log/assets/alopex/${fingerprint(name, content)}`;
const evidenceJson = JSON.stringify({ schema_version: 1, status: 'reader-replay-not-independent-reproduction', ...evidence }, null, 2) + '\n';
const report = await readFile(join(source, 'reference_notebooks_with_scripts/backprop_free_blog_v1/backprop_free_blog_v1/VERIFIED_REPORT.md'));
await writeFile(join(assetDir, 'evidence.json'), evidenceJson);
await writeFile(join(assetDir, 'archived-verification.md'), report);
const componentMarkup = `<div class="alopex-native"><p class="alopex-source-links"><a href="${assetUrl('evidence.json', evidenceJson)}" download>Reader evidence data</a> <span> · </span><a href="${assetUrl('archived-verification.md', report)}" download>Archived verification report</a></p><p class="alopex-source-note">The verification report is an archived record, not a local rerun. Its historical early-HFD recovery status was later updated; see the recovery section below. The separate schema-v2 campaign remains staging: it cannot support new headline performance, causal, or multiseed conclusions until complete and its release checks pass.</p></div>`;
await writeFile(join(site, 'components/alopex-reader.js'), `export const render = () => ${JSON.stringify(componentMarkup)};\nexport const script = ${JSON.stringify(script.toString())};\n`);
const intro = `<link rel="stylesheet" href="${assetUrl('katex.min.css', katexCss)}"><link rel="stylesheet" href="${assetUrl('article.css', stylesheet)}">\n\n`;
parts.splice(1, 0, ':::interactive alopex-reader.js Evidence and provenance\n:::');
const page = frontmatter + intro + parts.join('\n\n') + '\n';
await writeFile(join(site, 'pages/alopex-partial-negative-result.md'), page);
await writeFile(join(assetDir, 'import-manifest.json'), JSON.stringify({ source: 'alopex_article/src/content/paper.mdx', source_sha256: hash(input), page_sha256: hash(page), evidence_sha256: hash(evidenceJson), archived_report_sha256: hash(report), sections: sections.length, equation_families: lists.length, equations: 38 }, null, 2) + '\n');
console.log(`Imported ${sections.length} sections, 38 appendix equations, and ${((html.match(/class="reference-main"/g)) || []).length} bibliography records.`);