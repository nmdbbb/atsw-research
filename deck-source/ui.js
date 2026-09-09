const deck=document.getElementById('deck');
deck.innerHTML=slides.map((s,i)=>`<section class="slide ${s.cls||''}" id="slide-${i+1}" aria-labelledby="title-${i+1}"><div class="eyebrow"><span>${s.ch}</span><span class="source"><a href="paper.pdf#page=${s.page}" target="_blank" rel="noopener">${s.section} · PDF tr. ${s.page} ↗</a></span></div><h1 id="title-${i+1}">${s.title}</h1><div class="essence"><div class="zone-label"><span class="index">01</span> Bản chất · hiểu cách nó hoạt động</div><div class="essence-grid"><div class="prose">${s.body}</div><div class="visual">${s.visual}</div></div></div><div class="traits"><div class="zone-label"><span class="index">02</span> Đặc điểm · hệ quả, điều kiện, giới hạn</div><div class="traits-grid">${s.ts.map(t=>`<div class="trait"><h3>${t.h}</h3><p>${t.p}</p></div>`).join('')}</div></div></section>`).join('');
const sections=[...document.querySelectorAll('.slide')],toc=document.getElementById('toc'),pageInput=document.getElementById('page-number');
let current=0,reading=false;
const clamp=(n,a,b)=>Math.min(b,Math.max(a,n));
const fmt=(n,d=2)=>n.toLocaleString('vi-VN',{minimumFractionDigits:d,maximumFractionDigits:d});
function setToc(open){toc.hidden=!open;document.getElementById('toc-toggle').setAttribute('aria-expanded',open);if(open)document.getElementById('search').focus();}
function renderToc(query=''){
 let prev=''; const q=query.toLocaleLowerCase('vi');
 document.getElementById('toc-list').innerHTML=slides.map((s,i)=>{
  if(q&&!`${s.ch} ${s.title} ${s.body} ${s.ts.map(x=>x.p).join(' ')}`.toLocaleLowerCase('vi').includes(q))return '';
  let group=s.ch!==prev?`<div class="toc-group">${s.ch}</div>`:'';prev=s.ch;
  return group+`<a class="toc-link ${i===current?'current':''}" href="#${i+1}" data-goto="${i}"><span>${String(i+1).padStart(2,'0')}</span>${s.title}</a>`;
 }).join('')||'<p class="subtitle">Không tìm thấy slide phù hợp.</p>';
}
function updateNav(){pageInput.value=current+1;document.getElementById('page-total').textContent='/ '+slides.length;pageInput.max=slides.length;document.getElementById('chapter-name').textContent=slides[current].ch;document.getElementById('progress').style.width=((current+1)/slides.length*100)+'%';document.getElementById('prev').disabled=current===0;document.getElementById('next').disabled=current===slides.length-1;document.querySelectorAll('.toc-link').forEach(a=>a.classList.toggle('current',Number(a.dataset.goto)===current));}
function go(n,changeHash=true){current=clamp(Number(n)||0,0,slides.length-1);sections.forEach((s,j)=>{s.classList.toggle('active',j===current);s.setAttribute('aria-hidden',!reading&&j!==current?'true':'false');});updateNav();if(changeHash)history.replaceState(null,'','#'+(current+1));if(reading)sections[current].scrollIntoView({behavior:'auto',block:'start'});else window.scrollTo({top:0,behavior:'instant'});}
renderToc();
document.getElementById('toc-toggle').onclick=()=>setToc(toc.hidden);
document.getElementById('toc-close').onclick=()=>{setToc(false);document.getElementById('toc-toggle').focus()};
document.getElementById('search').oninput=e=>renderToc(e.target.value);
document.getElementById('toc-list').onclick=e=>{const a=e.target.closest('[data-goto]');if(a){e.preventDefault();go(+a.dataset.goto);setToc(false)}};
document.getElementById('next').onclick=()=>go(current+1);
document.getElementById('prev').onclick=()=>go(current-1);
pageInput.onchange=()=>go(+pageInput.value-1);
document.getElementById('reading-toggle').onclick=()=>{reading=!reading;document.body.classList.toggle('reading',reading);const b=document.getElementById('reading-toggle');b.textContent=reading?'Trình chiếu':'Đọc liền';b.setAttribute('aria-pressed',reading);go(current)};
document.getElementById('print').onclick=()=>window.print();
addEventListener('hashchange',()=>go((parseInt(location.hash.slice(1),10)||1)-1,false));
addEventListener('keydown',e=>{
 if(e.key==='Escape'){setToc(false);return}
 if(e.ctrlKey||e.metaKey||e.altKey||e.target.closest('input,textarea,select,summary,a')||document.querySelector('dialog[open]'))return;
 if(e.target.closest('button')&&[' ','Enter'].includes(e.key))return;
 if(['ArrowRight','PageDown'].includes(e.key)||(!reading&&e.key===' ')){e.preventDefault();go(current+1)}
 else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();go(current-1)}
 else if(e.key==='Home'){e.preventDefault();go(0)}else if(e.key==='End'){e.preventDefault();go(slides.length-1)}
 else if(e.key.toLowerCase()==='m'){e.preventDefault();setToc(toc.hidden)}
});
let scrollScheduled=false;
addEventListener('scroll',()=>{if(!reading||scrollScheduled)return;scrollScheduled=true;requestAnimationFrame(()=>{scrollScheduled=false;let best=0;sections.forEach((s,i)=>{if(s.getBoundingClientRect().top<innerHeight*.42)best=i});if(best!==current){current=best;updateNav();history.replaceState(null,'','#'+(current+1));}})});
let touchStart=null;
deck.addEventListener('touchstart',e=>{if(e.target.closest('input,button,a,.table-wrap')){touchStart=null;return}touchStart={x:e.touches[0].clientX,y:e.touches[0].clientY}},{passive:true});
deck.addEventListener('touchend',e=>{if(!touchStart||reading)return;const dx=e.changedTouches[0].clientX-touchStart.x,dy=e.changedTouches[0].clientY-touchStart.y;touchStart=null;if(Math.abs(dx)>80&&Math.abs(dx)>Math.abs(dy)*2)go(current+(dx<0?1:-1))},{passive:true});

function information(t){let out='';const paths=['(0, 0)','(0, 2)','(1, 0)','(1, 2)'];
 for(let i=0;i<4;i++){const x=20+i*135;out+=`<rect x="${x}" y="60" width="120" height="70" rx="9" fill="${i<2?'#dcebe3':'#f3e7d7'}"/>`+txt(x+60,102,paths[i],'#172d2b',19,'middle');}
 if(t===1){out+=`<rect x="13" y="48" width="262" height="98" rx="12" fill="none" stroke="#126b59" stroke-width="2"/><rect x="283" y="48" width="262" height="98" rx="12" fill="none" stroke="#b7502f" stroke-width="2"/>`+txt(145,181,'Biết X₁ = 0','#126b59',15,'middle')+txt(415,181,'Biết X₁ = 1','#b7502f',15,'middle');}
 else{for(let i=0;i<4;i++)out+=`<rect x="${18+i*135}" y="53" width="124" height="87" rx="10" fill="none" stroke="#126b59" stroke-width="2"/>`;out+=txt(280,182,'Biết (X₁, X₂): phân biệt được cả bốn paths','#126b59',15,'middle')}
 out+=txt(280,25,t===1?'Hai nhóm chưa phân biệt được bên trong':'Bốn nhóm riêng biệt','#52635e',14,'middle');document.getElementById('information-viz').innerHTML=svg(out,205);document.querySelectorAll('[data-info]').forEach(b=>b.classList.toggle('selected',+b.dataset.info===t));}
document.querySelectorAll('[data-info]').forEach(b=>b.onclick=()=>information(+b.dataset.info));information(1);

function coupling(){const a=+document.getElementById('coupling-a').value,b=.5-a;document.getElementById('coupling-a-out').textContent=fmt(a);document.getElementById('coupling-matrix').innerHTML=matrix(['','Y = −1','Y = +1','Tổng hàng'],[['X = −1',fmt(a),fmt(b),'0,50'],['X = +1',fmt(b),fmt(a),'0,50'],['Tổng cột','0,50','0,50','1,00']]);document.getElementById('coupling-result').textContent=`Với cost |X−Y|: E[cost] = 2 × ${fmt(b)} + 2 × ${fmt(b)} = ${fmt(4*b)}.`;}
document.getElementById('coupling-a').oninput=coupling;coupling();

function epsilon(){const e=+document.getElementById('epsilon').value;document.getElementById('epsilon-out').textContent=fmt(e);document.getElementById('epsilon-viz').innerHTML=`<div class="bar-chart"><div class="bar-item"><span>Static W₁</span><div class="bar-track"><div class="bar-fill" style="width:${e/2*100}%"></div></div><strong>${fmt(e)}</strong></div><div class="bar-item"><span>Adapted AW₁</span><div class="bar-track"><div class="bar-fill orange" style="width:${(e+1)/2*100}%"></div></div><strong>${fmt(e+1)}</strong></div></div>`;document.getElementById('epsilon-result').textContent=`ε = ${fmt(e)} > 0: X vẫn biết dấu cuối. Chênh lệch AW₁ − W₁ luôn bằng 1.`;}
document.getElementById('epsilon').oninput=epsilon;epsilon();

const qcP=[.2,.5,.3],qcQ=[.2,.6,.2],colors=['#c3ddbd','#7fb89c','#236f5a'];
function probabilityStrip(probs,y,which){let a=0;let out=txt(20,y+27,which,'#172d2b',15);probs.forEach((p,i)=>{out+=`<rect x="${65+a*455}" y="${y}" width="${p*455}" height="43" fill="${colors[i]}" stroke="#fffefa" stroke-width="2"/>`+txt(65+(a+p/2)*455,y+27,String(i),i===2?'white':'#172d2b',17,'middle');a+=p;out+=txt(65+a*455,y+60,fmt(a,1),'#52635e',11,'middle');});return out;}
function quantile(){let u=+document.getElementById('quantile-u').value;const x=u<=.2?0:u<=.7?1:2,y=u<=.2?0:u<=.8?1:2;let out=probabilityStrip(qcP,40,'p')+probabilityStrip(qcQ,125,'q');out+=line(65+u*455,24,65+u*455,180,'#b7502f',3)+txt(65+u*455,16,'U','#b7502f',12,'middle');document.getElementById('quantile-u-viz').innerHTML=svg(out,200);document.getElementById('quantile-u-out').textContent=fmt(u,3);document.getElementById('quantile-u-result').textContent=`U = ${fmt(u,3)} → X = ${x}, Y = ${y}; cost |X−Y| = ${Math.abs(x-y)}.`;}
document.getElementById('quantile-u').oninput=quantile;quantile();

function grid(){const x=+document.getElementById('grid-x').value,c=Math.floor(x/.5),r=.5*(c+.5),X=v=>45+(v+1)/2.5*470;let out='';for(let j=-2;j<=2;j++){const a=j*.5;out+=`<rect x="${X(a)}" y="70" width="94" height="70" fill="${j===c?'#d2e7d5':'#edf0e7'}" stroke="#fff" stroke-width="2"/>`+txt(X(a+.25),116,'C = '+j,'#52635e',13,'middle')+txt(X(a),162,fmt(a,1),'#52635e',11,'middle');}out+=txt(X(1.5),162,'1,5','#52635e',11,'middle')+line(X(x),42,X(x),69,'#b7502f',3)+`<circle cx="${X(x)}" cy="41" r="6" fill="#b7502f"/>`+txt(X(x),23,'x = '+fmt(x),'#b7502f',13,'middle')+`<circle cx="${X(r)}" cy="184" r="6" fill="#126b59"/>`+txt(X(r),207,'tâm '+fmt(r),'#126b59',13,'middle');document.getElementById('grid-viz').innerHTML=svg(out,224);document.getElementById('grid-x-out').textContent=fmt(x);document.getElementById('grid-result').textContent=`C = floor(${fmt(x)}/0,5) = ${c}; r = ${fmt(r)}; |x−r| = ${fmt(Math.abs(x-r))} ≤ 0,25.`;}
document.getElementById('grid-x').oninput=grid;grid();

function shift(){const s=+document.getElementById('grid-shift').value*.5,X=v=>50+(v+.7)/1.4*460,pts=[-.1,.1];let out='';for(let j=-3;j<=2;j++){const a=s+j*.5,b=a+.5;if(b<-.7||a>.7)continue;out+=`<rect x="${X(Math.max(-.7,a))}" y="70" width="${(Math.min(.7,b)-Math.max(-.7,a))/1.4*460}" height="65" fill="${j%2===0?'#dcebe3':'#ecede3'}" stroke="#fff" stroke-width="2"/>`;if(a>-.7&&a<.7)out+=txt(X(a),158,fmt(a),'#52635e',11,'middle');}pts.forEach((p,i)=>{out+=`<circle cx="${X(p)}" cy="102" r="8" fill="${i?'#b7502f':'#126b59'}"/>`+txt(X(p),48,i?'+0,1':'−0,1',i?'#b7502f':'#126b59',15,'middle');});document.getElementById('shift-viz').innerHTML=svg(out,185);document.getElementById('grid-shift-out').textContent=fmt(s/.5);const a=Math.floor((pts[0]-s)/.5+1e-12),b=Math.floor((pts[1]-s)/.5+1e-12);document.getElementById('shift-result').textContent=`s = ${fmt(s)}: hai tín hiệu ${a===b?'cùng ô → bị gộp':'khác ô → còn phân biệt được'}.`;}
document.getElementById('grid-shift').oninput=shift;shift();

function windowViz(k){const h=[[0,1,0],[2,1,0]];let out='';h.forEach((row,i)=>{out+=txt(20,52+i*80,'h'+(i+1),'#52635e',14);row.forEach((v,j)=>{const retained=j>=3-k;out+=`<rect x="${75+j*105}" y="${22+i*80}" width="82" height="50" rx="6" fill="${retained?'#dcebe3':'#f0f0e8'}" stroke="${retained?'#126b59':'#e0e3d9'}"/>`+txt(116+j*105,54+i*80,String(v),retained?'#126b59':'#abb2a5',21,'middle');});out+=txt(409,52+i*80,'→ '+(i?2:0),'#b7502f',19);});out+=txt(420,195,'Bước kế tiếp','#52635e',12,'middle');document.getElementById('window-viz').innerHTML=svg(out,218);document.getElementById('window-result').textContent=k<3?`k = ${k}: hai histories cùng cửa sổ (${h[0].slice(-k).join(', ')}). Nếu đếm bằng nhau: law gộp cho 0 và 2, mỗi khả năng 1/2.`:'k = 3: hai histories khác cửa sổ. Tại h₁, bước tiếp là 0; tại h₂, bước tiếp là 2.';document.querySelectorAll('[data-window]').forEach(b=>b.classList.toggle('selected',+b.dataset.window===k));}
document.querySelectorAll('[data-window]').forEach(b=>b.onclick=()=>windowViz(+b.dataset.window));windowViz(2);

function counts(){const n=+document.getElementById('count-one').value;let out='';for(let i=0;i<10;i++){const one=i>=10-n,x=40+(i%5)*103,y=45+Math.floor(i/5)*70;out+=`<rect x="${x}" y="${y}" width="78" height="48" rx="7" fill="${one?'#126b59':'#e7dfcb'}"/>`+txt(x+39,y+30,one?'1':'0',one?'#fff':'#6d6247',20,'middle');}document.getElementById('counts-viz').innerHTML=svg(out,184);document.getElementById('count-one-out').textContent=n;document.getElementById('counts-result').textContent=`K̂(u,0) = ${10-n}/10 = ${fmt((10-n)/10,1)}; K̂(u,1) = ${n}/10 = ${fmt(n/10,1)}. Tổng hàng = 1.`;}
document.getElementById('count-one').oninput=counts;counts();

function kink(){const h=+document.getElementById('kink-h').value,X=v=>280+v*2400,Y=v=>178-v*1450;let out=line(40,178,520,178)+line(280,24,280,196)+`<polyline points="${X(-.08)},${Y(.08)} 280,178 ${X(.08)},${Y(.08)}" fill="none" stroke="#126b59" stroke-width="3"/><circle cx="${X(h)}" cy="${Y(Math.abs(h))}" r="7" fill="#b7502f"/>`+txt(301,25,'|h|','#126b59',15)+txt(500,200,'h','#52635e',14)+txt(68,202,'−0,08','#52635e',12)+txt(450,202,'+0,08','#52635e',12)+txt(269,200,'0','#52635e',12);document.getElementById('kink-viz').innerHTML=svg(out,218);document.getElementById('kink-h-out').textContent=fmt(h,3);document.getElementById('kink-result').textContent=`h = ${fmt(h,3)}: tại tie, cost tăng |h| = ${fmt(Math.abs(h),3)}; tại d = −0,1, cost đổi −h = ${fmt(-h,3)}.`;}
document.getElementById('kink-h').oninput=kink;kink();

function limitChart(){let seed=927461;const rand=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return(seed+.5)/4294967296};const bins=50,lo=-2.5,hi=3.5,counts=Array(bins).fill(0),N=80000,sdA=Math.sqrt(.32),coef=-.1/sdA,sdR=Math.sqrt(.37-coef*coef);let sum=0;
 for(let i=0;i<N;i++){let r=Math.sqrt(-2*Math.log(rand())),t=2*Math.PI*rand(),z1=r*Math.cos(t),z2=r*Math.sin(t),value=Math.abs(sdA*z1)+coef*z1+sdR*z2;sum+=value;let b=Math.floor((value-lo)/(hi-lo)*bins);if(b>=0&&b<bins)counts[b]++;}
 const X=x=>45+(x-lo)/(hi-lo)*475,Y=y=>200-y*250,bw=(hi-lo)/bins;let out=line(45,200,520,200);counts.forEach((n,i)=>{let y=n/N/bw;out+=`<rect x="${X(lo+i*bw)}" y="${Y(y)}" width="${475/bins-.6}" height="${200-Y(y)}" fill="#126b59" opacity=".8"/>`;});
 let d='',variance=.37+.32*(1-2/Math.PI);for(let i=0;i<=180;i++){let x=lo+(hi-lo)*i/180,y=Math.exp(-x*x/(2*variance))/Math.sqrt(2*Math.PI*variance);d+=`${i?'L':'M'}${X(x)},${Y(y)} `;}out+=`<path d="${d}" fill="none" stroke="#b7502f" stroke-width="2.5"/>`;for(let i=-2;i<=3;i++)out+=txt(X(i),221,i,'#52635e',11,'middle');out+=line(X(.45135),25,X(.45135),201,'#689844',1.5)+txt(315,20,'Mean lý thuyết ≈ 0,4514','#126b59',12)+txt(46,20,'Mật độ','#52635e',11);document.getElementById('limit-viz').innerHTML=svg(out,240);window.limitSimulation={mean:sum/N,N};}
limitChart();

document.querySelectorAll('.quiz').forEach(q=>q.querySelectorAll('[data-choice]').forEach(b=>b.onclick=()=>{const ok=b.dataset.choice===q.dataset.answer;q.querySelectorAll('button').forEach(x=>x.classList.remove('selected'));b.classList.add('selected');const f=q.querySelector('.quiz-feedback');f.textContent=ok?'Đúng. Hãy nối kết luận với công thức và các đặc điểm phía dưới.':q.dataset.answer==='1'?'Chưa đúng. Biên đúng chưa đủ, và bicausal không buộc độc lập. Hãy so P(Y₂ | Y₁) với P(Y₂ | Y₁, X₁).':'Chưa đúng. Định lý chỉ làm kernel ước lượng tiến tới kernel thật của mô hình đã chọn. Quy tắc coupling và biểu diễn vẫn giữ nguyên.';f.style.color=ok?'var(--green)':'var(--orange)';}));

const tablesDialog=document.createElement('dialog');tablesDialog.id='tables-dialog';tablesDialog.innerHTML=`<div class="toc-head"><h2>Bảng gốc · chỉ để tra cứu</h2><button id="tables-close" aria-label="Đóng các bảng">×</button></div><p class="subtitle">Số liệu chép từ PDF được cung cấp; chưa chạy lại thực nghiệm. Dấu thập phân trong bảng dùng quy ước của paper.</p><label for="table-select" class="sr-only">Chọn bảng</label><select id="table-select">${paperTables.map((t,i)=>`<option value="${i}">Bảng ${i+1}: ${t.name}</option>`).join('')}</select><div id="paper-table-body"></div>`;document.body.appendChild(tablesDialog);
function showTable(i){const t=paperTables[i];document.getElementById('paper-table-body').innerHTML=`<p class="subtitle">${t.note} <a href="paper.pdf#page=${t.page}" target="_blank">PDF tr. ${t.page} ↗</a></p>${table(t.head,t.rows)}`;}
document.querySelectorAll('.open-tables').forEach(b=>b.onclick=()=>{showTable(0);document.getElementById('table-select').value=0;tablesDialog.showModal();});document.getElementById('tables-close').onclick=()=>tablesDialog.close();document.getElementById('table-select').onchange=e=>showTable(+e.target.value);tablesDialog.onclick=e=>{if(e.target===tablesDialog){const r=tablesDialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)tablesDialog.close();}};
go((parseInt(location.hash.slice(1),10)||1)-1,false);
