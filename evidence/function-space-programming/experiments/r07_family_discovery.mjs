import { readFileSync } from 'node:fs'
import { compile, score } from './r06_zero_training.mjs'

const modulus = 7
const values = Array.from({ length: modulus }, (_, i) => i)
const families = ['affine', 'quadratic', 'parity']
const mod = n => ((n % modulus) + modulus) % modulus

function apply([family, a, b, c], x) {
  const term = family === 'quadratic' ? x * x : family === 'parity' ? x % 2 : 0
  return mod(a * x + b + c * term)
}

function compose(ops, a, b, x) {
  return apply(ops[b], apply(ops[a], x))
}

function enumerate() {
  return families.flatMap(family => values.flatMap(a => values.flatMap(b => {
    const coefficients = family === 'affine' ? [0] : values.slice(1)
    return coefficients.map(c => [family, a, b, c])
  })))
}

const { seed, truth, packets, proposals } = JSON.parse(
  readFileSync(new URL('../runs/r07-family-discovery/tasks.json', import.meta.url), 'utf8'),
)
// Reproduce the pre-proposal task draw and check the archived observations.
let state = seed
function draw(n) {
  state = (Math.imul(1664525, state) + 1013904223) >>> 0
  return (state >>> 8) % n
}

const generated = Array.from({ length: 12 }, (_, i) => {
  const family = families[i % families.length]
  return [family, draw(7), draw(7), family === 'affine' ? 0 : 1 + draw(6)]
})
for (let i = generated.length - 1; i > 0; i--) {
  const j = draw(i + 1)
  ;[generated[i], generated[j]] = [generated[j], generated[i]]
}
const generatedPackets = generated.map((program, id) => ({
  id, rows: [0, 1, 2, 3].map(x => [x, apply(program, x)]),
}))
if (JSON.stringify(generated) !== JSON.stringify(truth) ||
    JSON.stringify(generatedPackets) !== JSON.stringify(packets))
  throw Error('Archived tasks disagree with the seed')

const identity = ['affine', 1, 0, 0]
const shift = ['affine', 1, 1, 0]
const candidates = enumerate()
if (new Set(candidates.map(program => values.map(x => apply(program, x)).join(','))).size !== candidates.length)
  throw Error('Duplicate candidate functions')

function evaluate(program, target) {
  const ops = [identity, program, shift]
  const targetOps = [identity, target, shift]
  const primitive = [4, 5, 6].map(x => [0, 1, x, apply(target, x)])
  const pairs = [[1, 1], [1, 2], [2, 1]]
  const composition = pairs.flatMap(([a,b]) => values.map(x => [a,b,x,compose(targetOps,a,b,x)]))
  const model = compile(ops, compose)
  return {
    exact: values.every(x => apply(program, x) === apply(target, x)),
    primitive: score(model, primitive),
    composition: score(model, composition),
  }
}

const stages = [2, 3, 4].map(budget => {
  const tasks = packets.map(({ id, rows }) => {
    const labels = rows.slice(0, budget)
    const fits = program => labels.every(([x,y]) => apply(program,x) === y)
    const possible = candidates.filter(fits)
    const teacher = proposals[budget][id]
    if (!possible.length || !fits(truth[id])) throw Error('Invalid benchmark data')
    return {
      id,
      consistent: possible.length,
      teacherFits: fits(teacher),
      teacher: evaluate(teacher, truth[id]),
      symbolic: evaluate(possible[0], truth[id]),
      oracle: evaluate(truth[id], truth[id]),
    }
  })
  return {
    labels: budget,
    tasks,
    summary: Object.fromEntries(['teacher','symbolic','oracle'].map(arm => [arm, {
      exact: tasks.filter(t => t[arm].exact).length,
      primitive: tasks.reduce((sum,t) => sum+t[arm].primitive.correct,0),
      composition: tasks.reduce((sum,t) => sum+t[arm].composition.correct,0),
    }])),
  }
})
console.log(JSON.stringify({ seed, candidateFunctions: candidates.length, steps: 0, stages }, null, 2))
