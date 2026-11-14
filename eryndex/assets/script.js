const toggle=document.getElementById('menuToggle');const nav=document.getElementById('nav');toggle?.addEventListener('click',()=>{const open=nav.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open));});nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{nav.classList.remove('open');toggle?.setAttribute('aria-expanded','false');}));const progress=document.getElementById('progress');window.addEventListener('scroll',()=>{const max=document.documentElement.scrollHeight-window.innerHeight;progress.style.width=(max>0?window.scrollY/max*100:0)+'%';},{passive:true});const year=document.getElementById('year');if(year) year.textContent=new Date().getFullYear();
const contactForm=document.getElementById('contactForm');
contactForm?.addEventListener('submit',async event=>{
 event.preventDefault();
 const status=document.getElementById('formStatus');
 if(!contactForm.reportValidity()) return;
 if(document.getElementById('website')?.value) return;
 const data=Object.fromEntries(new FormData(contactForm).entries());
 if(data.name.trim().length<2||data.message.trim().length<20||data.message.length>3000){status.textContent='Please check the name and project brief.';return;}
 const endpoint=window.ERYNDEX_CONTACT_ENDPOINT||'';
 if(!endpoint){
  const subject=encodeURIComponent('Project inquiry — ERYNDEX');
  const body=encodeURIComponent('Name: '+data.name+'\nEmail: '+data.email+'\nCompany: '+data.company+'\nService: '+data.service+'\n\nBrief:\n'+data.message);
  window.location.href='mailto:eryndexco@gmail.com?subject='+subject+'&body='+body;
  status.textContent='Your email app should open with the inquiry details. Online form delivery will be enabled after the secure backend is deployed.';
  return;
 }
 const button=contactForm.querySelector('button[type="submit"]');button.disabled=true;status.textContent='Sending…';
 try{
  const response=await fetch(endpoint,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
  const result=await response.json();
  if(!response.ok) throw new Error(result.error||'Submission failed');
  contactForm.reset();status.textContent=result.reference?'Request received. Your tracking code is '+result.reference+'. Save it and track your request at '+new URL('requests/',window.location.href).href:'Thank you. Your inquiry has been received.';
 }catch(error){status.textContent='We could not send the inquiry. Please email eryndexco@gmail.com.';}
 finally{button.disabled=false;}
});


/* Procedural galaxy canvas + lightweight guided navigation */
(()=>{
 const canvas=document.getElementById('cosmosCanvas');
 if(canvas){
  const ctx=canvas.getContext('2d',{alpha:true});
  const reduced=window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let w=0,h=0,dpr=1,stars=[],raf=0,px=0,py=0;
  const seed=()=>{stars=Array.from({length:Math.min(190,Math.floor(w*h/6500))},()=>({x:Math.random()*w,y:Math.random()*h,r:Math.random()*1.25+.25,a:Math.random()*.65+.2,s:Math.random()*.012+.002,p:Math.random()*6.28}));};
  const resize=()=>{const box=canvas.getBoundingClientRect();w=box.width;h=box.height;dpr=Math.min(devicePixelRatio||1,1.7);canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);ctx.setTransform(dpr,0,0,dpr,0,0);seed();draw(0);};
  let tick=0;
  const draw=()=>{
   ctx.clearRect(0,0,w,h);tick+=reduced?0:.012;
   for(const s of stars){const tw=reduced?s.a:s.a*(.72+.28*Math.sin(tick+s.p));ctx.beginPath();ctx.fillStyle='rgba(205,225,255,'+tw+')';ctx.arc(s.x+px*s.r*3,s.y+py*s.r*3,s.r,0,Math.PI*2);ctx.fill();}
   const cx=w*.74,cy=h*.5;
   const g=ctx.createRadialGradient(cx,cy,0,cx,cy,Math.min(w,h)*.42);g.addColorStop(0,'rgba(91,116,230,.08)');g.addColorStop(.55,'rgba(74,110,180,.035)');g.addColorStop(1,'rgba(0,0,0,0)');
   ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
   if(!reduced)raf=requestAnimationFrame(draw);
  };
  const pointer=e=>{const r=canvas.getBoundingClientRect();px=(e.clientX-r.left-r.width/2)/r.width;py=(e.clientY-r.top-r.height/2)/r.height;};
  resize();if(!reduced)raf=requestAnimationFrame(draw);
  window.addEventListener('resize',resize,{passive:true});window.addEventListener('pointermove',pointer,{passive:true});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)cancelAnimationFrame(raf);else if(!reduced)raf=requestAnimationFrame(draw);});
 }
 const toggle=document.getElementById('guideToggle'),panel=document.getElementById('guidePanel'),answer=document.getElementById('guideAnswer');
 toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));panel.hidden=!open;toggle.querySelector('b').textContent=open?'−':'+';});
 document.querySelectorAll('[data-guide]').forEach(button=>button.addEventListener('click',()=>{
  const target=button.dataset.guide;const labels={services:['Services','خدمات'],work:['Selected work','نمونه‌کارها'],contact:['Contact','ارتباط']};
  const el=document.getElementById(target);if(el){answer.textContent=(document.documentElement.lang==='fa'?'در حال انتقال به بخش ':'Taking you to ')+(document.documentElement.lang==='fa'?labels[target][1]:labels[target][0])+'.';el.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth'});}
 }));
})();
