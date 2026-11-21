import { readFileSync } from 'node:fs'

// R06 CPU reference. ES module, no dependencies.
const N = 7, V = 10, D = 26, H = 13, M = 63
const offset = 13, result = 19
const mod = n => ((n % N) + N) % N
const zeros = n => new Float64Array(n)
function create(seed) {
  const p = Object.fromEntries(Object.entries({E:V*D,P:3*D,Q:D*D,K:D*D,V:D*D,O:D*D,U:M*D,b:M,W:D*M,C:N*D}).map(([k,n])=>[k,zeros(n)]))
  if (seed === null) return p
  let s = seed
  for (const [name, weights] of Object.entries(p)) {
    if (name === 'b') continue
    for (let i=0;i<weights.length;i++) {
      s = (Math.imul(1664525,s)+1013904223) >>> 0
      weights[i] = ((s / 2**32)*2-1)*.22
    }
  }
  return p
}
function mat(w,x,n) {
  const y=zeros(n)
  for(let i=0;i<n;i++) for(let j=0;j<x.length;j++) y[i]+=w[i*x.length+j]*x[j]
  return y
}
function back(w,g,x,dy) {
  const dx=zeros(x.length)
  for(let i=0;i<dy.length;i++) for(let j=0;j<x.length;j++){
    const k=i*x.length+j
    g[k]+=dy[i]*x[j]
    dx[j]+=w[k]*dy[i]
  }
  return dx
}
function dot(a,b){let n=0;for(let i=0;i<a.length;i++)n+=a[i]*b[i];return n}
function softmax(x){
  const max=Math.max(...x), y=x.map(v=>Math.exp(v-max))
  const sum=y.reduce((a,b)=>a+b,0)
  return y.map(v=>v/sum)
}
function forward(p,row) {
  const ids=[N+row[0],N+row[1],row[2]]
  const x=ids.map((id,i)=>p.E.slice(id*D,(id+1)*D).map((v,j)=>v+p.P[i*D+j]))
  const q=mat(p.Q,x[2],D), k=x.map(v=>mat(p.K,v,D)), v=x.map(z=>mat(p.V,z,D))
  const a=zeros(D), probs=[]
  for(let h=0;h<2;h++){
    const at=h*H
    const qs=q.subarray(at,at+H)
    const prob=softmax(k.map(ks=>dot(qs,ks.subarray(at,at+H))/Math.sqrt(H)))
    probs.push(prob)
    for(let j=at;j<at+H;j++) for(let t=0;t<3;t++) a[j]+=prob[t]*v[t][j]
  }
  const z=mat(p.O,a,D).map((v,j)=>v+x[2][j])
  const u=mat(p.U,z,M).map((v,j)=>v+p.b[j])
  const r=u.map(v=>Math.max(v,0))
  const out=mat(p.W,r,D).map((v,j)=>v+z[j])
  return {ids,x,q,k,v,a,probs,z,u,r,out,logits:mat(p.C,out,N)}
}
function backward(p,g,row) {
  const {ids,x,q,k,v,a,probs,z,u,r,out,logits}=forward(p,row)
  const dlogits=softmax(logits)
  dlogits[row[3]]-=1
  const dout=back(p.C,g.C,out,dlogits)
  const du=back(p.W,g.W,r,dout).map((v,i)=>u[i]>0?v:0)
  for(let i=0;i<M;i++)g.b[i]+=du[i]
  const dz=back(p.U,g.U,z,du).map((v,i)=>v+dout[i])
  const da=back(p.O,g.O,a,dz), dq=zeros(D)
  const dk=x.map(()=>zeros(D)), dv=x.map(()=>zeros(D))
  for(let h=0;h<2;h++){
    const at=h*H,end=at+H, prob=probs[h]
    const dprob=v.map(row=>dot(da.subarray(at,end),row.subarray(at,end)))
    const center=dot(prob,dprob)
    for(let j=at;j<end;j++) for(let t=0;t<3;t++){
      const ds=prob[t]*(dprob[t]-center)/Math.sqrt(H)
      dq[j]+=ds*k[t][j]
      dk[t][j]+=ds*q[j]
      dv[t][j]+=prob[t]*da[j]
    }
  }
  const dxq=back(p.Q,g.Q,x[2],dq)
  for(let t=0;t<3;t++){
    const dxk=back(p.K,g.K,x[t],dk[t])
    const dxv=back(p.V,g.V,x[t],dv[t])
    for(let j=0;j<D;j++){
      const d=dxk[j]+dxv[j]+(t===2?dz[j]+dxq[j]:0)
      g.E[ids[t]*D+j]+=d
      g.P[t*D+j]+=d
    }
  }
}
function label(ops,a,b,x) {
  const [s,t]=ops[a], [u,v]=ops[b]
  return mod(u*mod(s*x+t)+v)
}
function compile(ops) {
  const p=create(null)
  for(let i=0;i<V;i++)p.E[i*D+i]=1
  for(let t=0;t<3;t++)p.P[t*D+V+t]=1
  for(let h=0;h<2;h++){
    const at=h*H
    p.Q[at*D+V+2]=16
    p.K[at*D+V+h]=16
    for(let op=0;op<3;op++){
      p.V[(at+op)*D+N+op]=1
      p.O[(offset+h*3+op)*D+at+op]=1
    }
  }
  let n=0
  for(let a=0;a<3;a++)for(let b=0;b<3;b++)for(let x=0;x<N;x++){
    for(const j of [x,offset+a,offset+3+b])p.U[n*D+j]=1
    p.b[n]=-2.5
    p.W[(result+label(ops,a,b,x))*M+n]=2
    n++
  }
  for(let y=0;y<N;y++)p.C[y*D+result+y]=12
  return p
}
function score(p,rows){
  let correct=0,loss=0
  for(const row of rows){
    const {logits}=forward(p,row)
    correct+=logits.indexOf(Math.max(...logits))===row[3]
    loss-=Math.log(softmax(logits)[row[3]])
  }
  return {correct,total:rows.length,ce:loss/rows.length}
}
function gradientCheck(){
  const p=create(991), g=create(null), row=[0,1,2,4]
  backward(p,g,row)
  let maxError=0
  for(const name of Object.keys(p)){
    let i=0
    for(let j=1;j<g[name].length;j++)if(Math.abs(g[name][j])>Math.abs(g[name][i]))i=j
    const before=p[name][i], eps=1e-5
    p[name][i]=before+eps
    const plus=score(p,[row]).ce
    p[name][i]=before-eps
    const minus=score(p,[row]).ce
    p[name][i]=before
    maxError=Math.max(maxError,Math.abs((plus-minus)/(2*eps)-g[name][i]))
  }
  if(maxError>1e-7)throw new Error('Gradient check failed '+maxError)
  return maxError
}
function train(rows,seed,steps){
  const p=create(seed), m=create(null), v=create(null)
  for(let s=1;s<=steps;s++){
    const g=create(null)
    for(const r of rows)backward(p,g,r)
    const c1=1-.9**s,c2=1-.999**s
    for(const k of Object.keys(p))for(let i=0;i<p[k].length;i++){
      const d=g[k][i]/rows.length
      m[k][i]=.9*m[k][i]+.1*d
      v[k][i]=.999*v[k][i]+.001*d*d
      p[k][i]-=.003*(m[k][i]/c1)/(Math.sqrt(v[k][i]/c2)+1e-8)
    }
  }
  return p
}
function evaluate({truth,packets,proposals}){
  const steps=250
  const gradientMaxError=gradientCheck()
  const tasks=[]
  for(const {id,ops} of truth){
    const rows=packets[id].examples
    const symbolic=[[1,0],...[1,2].map(o=>{
      const [zero,one]=rows.filter(r=>r[1]===o)
      return [mod(one[3]-zero[3]),zero[3]]
    })]
    const primitive=[1,2].flatMap(o=>[2,4,5,6].map(x=>[0,o,x,label(ops,0,o,x)]))
    const composition=[1,2].flatMap(a=>[1,2].flatMap(b=>Array.from({length:N},(_,x)=>[a,b,x,label(ops,a,b,x)])))
    const arms={}
    for(const [name,program] of Object.entries({teacher:proposals[id],symbolic,oracle:ops})){
      const p=compile(program)
      arms[name]={updates:0,train:score(p,rows),primitive:score(p,primitive),composition:score(p,composition)}
    }
    arms.backprop=[17,31,57].map(seed=>{
      const p=train(rows,seed,steps)
      return {seed,updates:steps,train:score(p,rows),primitive:score(p,primitive),composition:score(p,composition)}
    })
    const p=create(17)
    arms.random={updates:0,train:score(p,rows),primitive:score(p,primitive),composition:score(p,composition)}
    tasks.push({id,arms})
  }
  return {stepsPerBaseline:steps,parameters:Object.values(create(null)).reduce((n,x)=>n+x.length,0),gradientMaxError,tasks}
}

const input = JSON.parse(readFileSync(new URL('../runs/r06-zero-training/tasks.json', import.meta.url), 'utf8'))
console.log(JSON.stringify(evaluate(input), null, 2))
