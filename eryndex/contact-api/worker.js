const STATUSES = new Set(["submitted","under_review","needs_information","proposal_sent","awaiting_approval","approved","in_progress","completed","declined"]);
const json = (body, status=200, headers={}) => new Response(JSON.stringify(body), {status, headers:{"Content-Type":"application/json; charset=utf-8","Cache-Control":"no-store","X-Content-Type-Options":"nosniff",...headers}});
const clean = (v,max) => typeof v === "string" && v.trim().length <= max ? v.trim() : null;
const now = () => new Date().toISOString();
const reference = () => "ERX-" + new Date().getUTCFullYear() + "-" + crypto.randomUUID().replace(/-/g,"").slice(0,8).toUpperCase();
const statusLabels = {submitted:"Request submitted",under_review:"Under review",needs_information:"More information needed",proposal_sent:"Proposal sent",awaiting_approval:"Awaiting your approval",approved:"Approved",in_progress:"In progress",completed:"Completed",declined:"Closed"};
export default {
 async fetch(request, env) {
  const allowed=(env.ALLOWED_ORIGINS||"").split(",").map(x=>x.trim()).filter(Boolean), origin=request.headers.get("Origin")||"";
  const cors=allowed.includes(origin)?{"Access-Control-Allow-Origin":origin,"Access-Control-Allow-Methods":"GET, POST, PATCH, OPTIONS","Access-Control-Allow-Headers":"Content-Type, Authorization","Vary":"Origin"}:{};
  if(request.method==="OPTIONS") return new Response(null,{status:204,headers:cors});
  const url=new URL(request.url), path=url.pathname.replace(/\/$/,""), reply=(body,status=200)=>json(body,status,cors);
  if(path==="/health"&&request.method==="GET") return reply({ok:true,service:"eryndex-request-api"});
  if(!allowed.includes(origin)) return reply({error:"Origin not allowed"},403);
  if(path==="/api/requests"&&request.method==="POST"){
   if(!env.DB)return reply({error:"Database is not configured"},503);
   if(Number(request.headers.get("Content-Length")||0)>9000)return reply({error:"Request too large"},413);
   let d;try{d=await request.json()}catch{return reply({error:"Invalid JSON"},400)}
   const name=clean(d.name,80),email=clean(d.email,254)?.toLowerCase(),company=clean(d.company||"",100),service=clean(d.service,100),message=clean(d.message,3000);
   if(clean(d.website||"",200))return reply({ok:true});
   if(d.consent!=="true"||!name||name.length<2||!email||!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)||!service||!message||message.length<20)return reply({error:"Please check the submitted fields"},400);
   const id=crypto.randomUUID(),ref=reference(),stamp=now();
   await env.DB.prepare("INSERT INTO requests (id,reference,name,email,company,service,message,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?,'submitted',?,?)").bind(id,ref,name,email,company,service,message,stamp,stamp).run();
   await env.DB.prepare("INSERT INTO request_events (request_id,status,public_message,created_at) VALUES (?, 'submitted', 'Your request has been received.', ?)").bind(id,stamp).run();
   if(env.RESEND_API_KEY&&env.CONTACT_TO&&env.CONTACT_FROM){const body=["New ERYNDEX collaboration request","Reference: "+ref,"Name: "+name,"Email: "+email,"Company: "+company,"Service: "+service,"","Brief:",message].join("\n");try{await fetch("https://api.resend.com/emails",{method:"POST",headers:{"Authorization":"Bearer "+env.RESEND_API_KEY,"Content-Type":"application/json"},body:JSON.stringify({from:env.CONTACT_FROM,to:[env.CONTACT_TO],reply_to:email,subject:"New ERYNDEX request "+ref,text:body})})}catch{}}
   return reply({ok:true,reference:ref,status:"submitted",trackingUrl:"/requests/"},201);
  }
  if(path==="/api/track"&&request.method==="POST"){
   if(!env.DB)return reply({error:"Database is not configured"},503);
   let d;try{d=await request.json()}catch{return reply({error:"Invalid JSON"},400)}
   const ref=clean(d.reference,32)?.toUpperCase(),email=clean(d.email,254)?.toLowerCase();
   if(!ref||!email)return reply({error:"Reference and email are required"},400);
   const row=await env.DB.prepare("SELECT reference,status,service,created_at,updated_at FROM requests WHERE reference=? AND email=?").bind(ref,email).first();
   if(!row)return reply({error:"No matching request was found. Check the reference and email."},404);
   const events=await env.DB.prepare("SELECT status,public_message,created_at FROM request_events WHERE request_id=(SELECT id FROM requests WHERE reference=?) ORDER BY id ASC").bind(ref).all();
   return reply({ok:true,request:{...row,statusLabel:statusLabels[row.status]||row.status,history:events.results||[]}});
  }
  if(path.startsWith("/api/admin/")){
   if(!env.ADMIN_API_TOKEN||request.headers.get("Authorization")!=="Bearer "+env.ADMIN_API_TOKEN)return reply({error:"Unauthorized"},401);
   if(!env.DB)return reply({error:"Database is not configured"},503);
   if(path==="/api/admin/requests"&&request.method==="GET"){
    const rows=await env.DB.prepare("SELECT id,reference,name,email,company,service,message,status,priority,admin_note,proposal_amount,proposal_timeline,created_at,updated_at FROM requests ORDER BY created_at DESC LIMIT 200").all();
    return reply({ok:true,requests:rows.results||[]});
   }
   const match=path.match(/^\/api\/admin\/requests\/([A-Fa-f0-9-]+)$/);
   if(match&&request.method==="PATCH"){
    let d;try{d=await request.json()}catch{return reply({error:"Invalid JSON"},400)}
    const id=match[1],status=clean(d.status,40),priority=clean(d.priority,20),note=clean(d.admin_note||"",2000),amount=clean(d.proposal_amount||"",80),timeline=clean(d.proposal_timeline||"",120),publicMessage=clean(d.public_message||"",500);
    if(!status||!STATUSES.has(status)||!priority||!["low","normal","high"].includes(priority)||note===null||amount===null||timeline===null||publicMessage===null)return reply({error:"Invalid update"},400);
    const stamp=now(),exists=await env.DB.prepare("SELECT id FROM requests WHERE id=?").bind(id).first();
    if(!exists)return reply({error:"Request not found"},404);
    await env.DB.prepare("UPDATE requests SET status=?,priority=?,admin_note=?,proposal_amount=?,proposal_timeline=?,updated_at=? WHERE id=?").bind(status,priority,note,amount,timeline,stamp,id).run();
    await env.DB.prepare("INSERT INTO request_events (request_id,status,public_message,created_at) VALUES (?,?,?,?)").bind(id,status,publicMessage,stamp).run();
    return reply({ok:true});
   }
  }
  return reply({error:"Not found"},404);
 }
};
