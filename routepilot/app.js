const API=window.ROUTEPILOT_API||"http://127.0.0.1:8000";

let accessToken=sessionStorage.getItem("demo_access_token")||"";
function apiFetch(url,options={}){
  const headers=new Headers(options.headers||{});
  if(accessToken)headers.set("Authorization","Bearer "+accessToken);
  return fetch(url,{...options,headers});
}
async function ensureAuth(){
  if(accessToken){
    const check=await apiFetch(API+"/auth/me");
    if(check.ok)return;
    accessToken="";sessionStorage.removeItem("demo_access_token");
  }
  return new Promise(resolve=>{
    const overlay=document.createElement("div");
    overlay.style.cssText="position:fixed;inset:0;z-index:9999;background:#08111eeF;display:grid;place-items:center;padding:20px";
    overlay.innerHTML='<form style="width:min(420px,100%);background:#fff;color:#142033;padding:28px;border-radius:16px;display:grid;gap:12px;font:14px system-ui"><h2 style="margin:0">Sign in to the demo</h2><p style="margin:0 0 8px;color:#526071">Use the administrator account configured in the local .env file.</p><label>Organization<input name="organization_name" required minlength="2" style="display:block;width:100%;padding:10px;margin-top:5px"></label><label>Email<input name="email" type="email" required style="display:block;width:100%;padding:10px;margin-top:5px"></label><label>Password<input name="password" type="password" required style="display:block;width:100%;padding:10px;margin-top:5px"></label><button style="padding:12px;background:#172c4b;color:white;border:0;border-radius:8px">Sign in</button><p data-error role="alert" style="color:#b42318;margin:0"></p></form>';
    document.body.appendChild(overlay);
    overlay.querySelector("form").addEventListener("submit",async event=>{
      event.preventDefault();const form=event.currentTarget;const data=Object.fromEntries(new FormData(form).entries());const button=form.querySelector("button");button.disabled=true;
      try{
        const response=await apiFetch(API+"/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
        const result=await response.json();if(!response.ok)throw Error(result.detail||"Sign-in failed");
        accessToken=result.access_token;sessionStorage.setItem("demo_access_token",accessToken);overlay.remove();resolve();
      }catch(error){form.querySelector("[data-error]").textContent=error.message;button.disabled=false;}
    });
  });
}
const filter=document.querySelector("#statusFilter");
const escapeHTML=value=>String(value??"").replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[char]));
async function loadDeliveries(){
  try{
    await ensureAuth();
    const status=filter.value==="all"?"":filter.value.toLowerCase().replace(" ","_");
    const res=await apiFetch(API+"/deliveries"+(status?"?status="+encodeURIComponent(status):""));
    if(!res.ok)throw Error("Could not load deliveries");
    const rows=await res.json();
    document.querySelector("#jobs").innerHTML=rows.map(d=>{
      const label={in_transit:"In transit",delivered:"Delivered",attention:"Attention",scheduled:"Scheduled",cancelled:"Cancelled"}[d.status]||d.status;
      const cls=d.status==="delivered"?"green":d.status==="attention"?"amber":"blue";
      return `<tr><td>${escapeHTML(d.id)}</td><td>${escapeHTML(d.recipient)}</td><td>${escapeHTML(d.route_id)}</td><td>${escapeHTML(d.eta||"—")}</td><td><span class="tag ${cls}">${label}</span></td><td>${d.proof_count?"Recorded":"Pending"}</td><td><button class="proof-action" data-proof="${escapeHTML(d.id)}" ${d.proof_count?"disabled":""}>${d.proof_count?"Proof saved":"Record proof"}</button></td></tr>`;
    }).join("");
    document.querySelectorAll("[data-proof]").forEach(button=>button.addEventListener("click",()=>recordProof(button)));
  }catch(error){console.error(error);document.querySelector("#jobs").innerHTML="<tr><td colspan='7'>API unavailable. Start the RoutePilot backend and refresh.</td></tr>";}
}
async function recordProof(button){
  const picker=document.createElement("input");picker.type="file";picker.accept="image/jpeg,image/png,application/pdf";picker.capture="environment";picker.hidden=true;document.body.appendChild(picker);picker.click();
  await new Promise(resolve=>picker.addEventListener("change",resolve,{once:true}));
  const file=picker.files[0];picker.remove();if(!file)return;
  const recipient_name=prompt("Name of the person receiving the delivery:");if(!recipient_name)return;
  const form=new FormData();form.append("recipient_name",recipient_name);form.append("file",file);form.append("note",prompt("Delivery note (optional):")||"");
  try{const response=await apiFetch(API+"/deliveries/"+encodeURIComponent(button.dataset.proof)+"/proof/upload",{method:"POST",body:form});const data=await response.json();if(!response.ok)throw Error(data.detail||"Could not upload proof");await loadDeliveries();}
  catch(error){alert(error.message);}
}

filter.addEventListener("change",loadDeliveries);
document.querySelector("#newDeliveryForm").addEventListener("submit",async event=>{
  event.preventDefault();const form=event.currentTarget;const data=Object.fromEntries(new FormData(form).entries());
  if(!data.vehicle_id)delete data.vehicle_id;
  if(data.eta)data.eta=new Date(data.eta).toISOString();else delete data.eta;
  const message=document.querySelector("#deliveryMessage");message.textContent="Creating…";
  try{const response=await apiFetch(API+"/deliveries",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});const result=await response.json();if(!response.ok)throw Error(result.detail||"Could not create delivery");message.textContent="Created "+result.id;form.reset();await loadDeliveries();}
  catch(error){message.textContent=error.message;}
});
document.querySelector("#generate").addEventListener("click",async()=>{
  const button=document.querySelector("#generate");
  try{const res=await apiFetch(API+"/deliveries/DL-2083/note");if(!res.ok)throw Error("API unavailable");const data=await res.json();button.textContent="Delivery note preview loaded";const paper=document.querySelector("#paper");paper.dataset.document=JSON.stringify(data);paper.querySelector(".paper-head span").textContent="API PREVIEW · NOT LEGAL";
  }catch(error){button.textContent="Start API to generate note";}
});
loadDeliveries();


let gpsWatchId=null;
const gpsStart=document.querySelector("#gpsStart");
const gpsStop=document.querySelector("#gpsStop");
const gpsStatus=document.querySelector("#gpsStatus");
if(gpsStart&&gpsStop){
  gpsStart.addEventListener("click",()=>{
    if(!("geolocation" in navigator)){gpsStatus.textContent="This browser does not support geolocation.";return;}
    if(!window.isSecureContext && location.hostname!=="localhost" && location.hostname!=="127.0.0.1"){gpsStatus.textContent="GPS requires HTTPS (or localhost).";return;}
    gpsStatus.textContent="Waiting for location permission…";
    gpsWatchId=navigator.geolocation.watchPosition(async position=>{
      const vehicle=document.querySelector("#gpsVehicle").value;
      try{
        const response=await apiFetch(API+"/vehicles/"+encodeURIComponent(vehicle)+"/positions",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({latitude:position.coords.latitude,longitude:position.coords.longitude,recorded_at:new Date(position.timestamp).toISOString()})});
        if(!response.ok)throw Error("GPS update rejected by API");
        gpsStatus.textContent="Location sent · "+new Date(position.timestamp).toLocaleTimeString();
      }catch(error){gpsStatus.textContent=error.message;}
    },error=>{gpsStatus.textContent=error.message;},{enableHighAccuracy:true,maximumAge:10000,timeout:20000});
    gpsStart.disabled=true;gpsStop.disabled=false;
  });
  gpsStop.addEventListener("click",()=>{
    if(gpsWatchId!==null)navigator.geolocation.clearWatch(gpsWatchId);
    gpsWatchId=null;gpsStart.disabled=false;gpsStop.disabled=true;gpsStatus.textContent="Location sharing stopped.";
  });
  window.addEventListener("pagehide",()=>{if(gpsWatchId!==null)navigator.geolocation.clearWatch(gpsWatchId);});
}
