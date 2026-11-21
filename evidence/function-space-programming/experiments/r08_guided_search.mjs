import { readFileSync } from 'node:fs'
import { compile, score } from './r06_zero_training.mjs'

const N = 7
const domain = Array.from({ length: N }, (_, x) => x)
const families = ['cubic', 'parity', 'step']
const mod = value => ((value % N) + N) % N
const feature = (family, x) => family === 'parity' ? x % 2 : Number(family === 'step' && x >= 2)
const apply = ({ family, coeff: [a, b, c, d, e] }, x) =>
  mod(a + b*x + c*x*x + d*x*x*x + e*feature(family, x))

function* enumerate() {
  for (const family of families) {
    for (const a of domain) for (const b of domain) for (const c of domain) for (const d of domain) {
      for (const e of (family === 'cubic' ? [0] : domain.slice(1))) {
        yield { family, coeff: [a,b,c,d,e] }
      }
    }
  }
}

function fit(family, labels) {
  const width = family === 'cubic' ? 4 : 5
  const matrix = labels.map((y, x) => [1,x,x*x,x*x*x,feature(family,x)].slice(0,width).concat(y).map(mod))
  for (let col = 0; col < width; col++) {
    const pivot = matrix.findIndex((row,i) => i >= col && row[col] !== 0)
    if (pivot < 0) throw Error('Rank deficient family')
    const swap = matrix[col]
    matrix[col] = matrix[pivot]
    matrix[pivot] = swap
    const inverse = domain.find(a => mod(a*matrix[col][col]) === 1)
    matrix[col] = matrix[col].map(v => mod(v*inverse))
    for (let row = 0; row < matrix.length; row++) {
      if (row === col) continue
      const scale = matrix[row][col]
      matrix[row] = matrix[row].map((v,i) => mod(v-scale*matrix[col][i]))
    }
  }
  const program = { family, coeff: matrix.slice(0,width).map(row => row[width]) }
  if (width === 4) program.coeff.push(0)
  if (width === 5 && program.coeff[4] === 0) return null
  return labels.every((y,x) => apply(program,x) === y) ? program : null
}

function signature(labels) {
  const delta = i => mod(labels[i] - 4*labels[i+1] + 6*labels[i+2] - 4*labels[i+3] + labels[i+4])
  const [a,b] = [delta(0),delta(1)]
  if (a === 0 && b === 0) return 'cubic'
  if (a !== 0 && mod(a+b) === 0) return 'parity'
  if (a !== 0 && mod(2*a-b) === 0) return 'step'
  throw Error('No matching family signature')
}

function search(order, labels) {
  for (const [index,family] of order.entries()) {
    const program = fit(family,labels)
    if (program) return { program, familyFits:index+1 }
  }
  throw Error('No matching family')
}

const { seed, truth, packets, teacher } = JSON.parse(
  readFileSync(new URL('../runs/r08-guided-search/tasks.json', import.meta.url), 'utf8'),
)
let state = seed
function draw(n) {
  state = (Math.imul(1664525,state)+1013904223) >>> 0
  return (state >>> 8) % n
}
const generated = Array.from({length:12}, (_,i) => ({
  family:families[i%3], coeff:[draw(7),draw(7),draw(7),draw(7),i%3 ? 1+draw(6) : 0],
}))
for (let i = generated.length-1; i > 0; i--) {
  const j = draw(i+1), swap = generated[i]
  generated[i] = generated[j]
  generated[j] = swap
}
if (JSON.stringify(generated) !== JSON.stringify(truth)) throw Error('Task generation mismatch')

const identity = {family:'cubic',coeff:[0,1,0,0,0]}
const shift = {family:'cubic',coeff:[1,1,0,0,0]}
const compose = (ops,a,b,x) => apply(ops[b],apply(ops[a],x))
const grammar = [...enumerate()]
const summaries = packets.map(({id,labels}) => {
  const target = truth[id]
  if (!labels.every((y,x)=>apply(target,x)===y)) throw Error('Labels do not match generated task')
  const observed = program => labels.every((y,x) => apply(program,x) === y)
  const first = grammar.findIndex(observed)
  if (first === -1 || grammar.slice(first+1).some(observed)) throw Error('Expected one matching program')
  const nominated = teacher.families[id]
  if (!families.includes(nominated)) throw Error('Invalid family nomination')
  const symbolicFamily = signature(labels)
  const arms = {
    exhaustive:{program:grammar[first], candidatesTested:first+1},
    fixedOrder:search(families,labels),
    teacher:search([nominated,...families.filter(f=>f!==nominated)],labels),
    symbolicSignature:search([symbolicFamily],labels),
    oracle:{program:target},
  }
  const targetOps = [identity,target,shift]
  const heldOut = [[0,1,6],...[[1,1],[1,2],[2,1]].flatMap(([a,b])=>domain.map(x=>[a,b,x]))]
    .map(([a,b,x])=>[a,b,x,compose(targetOps,a,b,x)])
  for (const arm of Object.values(arms)) {
    const model = compile([identity,arm.program,shift],compose)
    arm.predictions = score(model,heldOut)
    arm.exact = domain.every(x=>apply(arm.program,x)===apply(target,x))
  }
  return {id,nominated,arms}
})

const summary = Object.fromEntries(Object.keys(summaries[0].arms).map(name => {
  const rows = summaries.map(task=>task.arms[name])
  const sum = f => rows.reduce((total,row)=>total+f(row),0)
  return [name,{exact:sum(row=>Number(row.exact)),correct:sum(row=>row.predictions.correct),
    total:sum(row=>row.predictions.total),familyFits:sum(row=>row.familyFits??0),
    candidatesTested:sum(row=>row.candidatesTested??0)}]
}))
console.log(JSON.stringify({tasks:summaries,updates:0,grammarSize:grammar.length,summary},null,2))
