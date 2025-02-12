import{_ as L}from"./LogoDark.vue.5d837e0c.js";import{q as N,r as y,s as V,v as M,x as P,y as A,z as F,A as T,B as U,a,o as r,g as u,w as t,b as c,e,t as b,E as D,c as x,G as j,f as _,k as H,_ as S,d as I,m as R,i as g,U as E,M as O,L as G,H as W,I as q,J,K,N as Q,O as X,P as Y,Q as Z,R as ee,S as te,F as w,j as ne,T as ae,p as oe}from"./entry.31107928.js";function se(n,i={}){const o=i.head||N();if(o)return o.ssr?o.push(n,i):ie(o,n,i)}function ie(n,i,o={}){const d=y(!1),s=y({});V(()=>{s.value=d.value?{}:M(i)});const l=n.push(s.value,o);return P(s,p=>{l.patch(p)}),U()&&(A(()=>{l.dispose()}),F(()=>{d.value=!0}),T(()=>{d.value=!1})),l}const le={class:"mini-icon"},ce={class:"mini-text font-weight-semibold pl-2 text-medium-emphasis text-uppercase"},re={__name:"index",props:{item:Object},setup(n){const i=n;return(o,d)=>{const s=a("DotsIcon"),l=a("v-list-subheader");return r(),u(l,{class:"smallCap text-capitalize text-subtitle-1 mt-5 d-flex align-items-center"},{default:t(()=>[c("span",le,[e(s,{size:"16","stroke-width":"1.5",class:"iconClass"})]),c("span",ce,b(i.item.header),1)]),_:1})}}},de={__name:"Icon",props:{item:Object,level:Number},setup(n){return(i,o)=>n.level>0?(r(),u(D(n.item),{key:0,size:"5",fill:"currentColor","stroke-width":"1.5",class:"iconClass"})):(r(),u(D(n.item),{key:1,size:"20","stroke-width":"1.5",class:"iconClass"}))}},me={class:"mb-1"},_e={class:"navbox bg-hover-primary"},ue={class:"icon-box"},pe={__name:"index",props:{item:Object,level:Number},setup(n){return(i,o)=>{const d=a("v-list-item-title"),s=a("v-list-item-subtitle"),l=a("v-chip"),m=a("v-list-item");return r(),x("div",me,[e(m,{to:n.item.type==="external"?"":n.item.to,href:n.item.type==="external"?n.item.to:"",rounded:"",class:"bg-hover-primary",color:"primary",ripple:!1,disabled:n.item.disabled,target:n.item.type==="external"?"_blank":""},j({prepend:t(()=>[c("div",_e,[c("span",ue,[e(de,{item:n.item.icon,level:n.level,class:"position-relative z-index-2 texthover-primary"},null,8,["item","level"])])])]),default:t(()=>[e(d,{class:"text-subtitle-1 font-weight-medium",color:"primary"},{default:t(()=>[_(b(n.item.title),1)]),_:1}),n.item.subCaption?(r(),u(s,{key:0,class:"text-caption mt-n1 hide-menu"},{default:t(()=>[_(b(n.item.subCaption),1)]),_:1})):H("",!0)]),_:2},[n.item.chip?{name:"append",fn:t(()=>[e(l,{color:n.item.chipColor,class:"sidebarchip hide-menu",size:(n.item.chipIcon,"x-small"),variant:n.item.chipVariant,"prepend-icon":n.item.chipIcon},{default:t(()=>[_(b(n.item.chip),1)]),_:1},8,["color","size","variant","prepend-icon"])]),key:"0"}:void 0]),1032,["to","href","disabled","target"])])}}},ve={};function fe(n,i){const o=a("BellRingingIcon"),d=a("v-badge"),s=a("v-btn");return r(),u(s,{icon:"",variant:"text",class:"custom-hover-primary ml-0 ml-md-5 text-muted"},{default:t(()=>[e(d,{dot:"",color:"primary","offset-x":"-5","offset-y":"-3"},{default:t(()=>[e(o,{"stroke-width":"1.5",size:"22"})]),_:1})]),_:1})}const he=S(ve,[["render",fe]]),be=""+globalThis.__publicAssetsURL("images/profile/user-1.jpg"),xe=c("img",{src:be,height:"35",alt:"user"},null,-1),ge={class:"pt-4 pb-4 px-5 text-center"},ye=I({__name:"ProfileDD",setup(n){return(i,o)=>{const d=a("v-avatar"),s=a("v-btn"),l=a("v-list-item-title"),m=a("v-list-item"),p=a("v-list"),h=a("v-sheet"),v=a("v-menu");return r(),u(v,{"close-on-content-click":!1},{activator:t(({props:k})=>[e(s,R({class:"",variant:"text"},k,{icon:""}),{default:t(()=>[e(d,{size:"35"},{default:t(()=>[xe]),_:1})]),_:2},1040)]),default:t(()=>[e(h,{rounded:"xl",width:"200",elevation:"10",class:"mt-2"},{default:t(()=>[e(p,{class:"py-0",lines:"one",density:"compact"},{default:t(()=>[e(m,{value:"item1",color:"primary"},{prepend:t(()=>[e(g(E),{"stroke-width":"1.5",size:"20"})]),default:t(()=>[e(l,{class:"pl-4 text-body-1"},{default:t(()=>[_("My Profile")]),_:1})]),_:1}),e(m,{value:"item2",color:"primary"},{prepend:t(()=>[e(g(O),{"stroke-width":"1.5",size:"20"})]),default:t(()=>[e(l,{class:"pl-4 text-body-1"},{default:t(()=>[_("My Account")]),_:1})]),_:1}),e(m,{value:"item3",color:"primary"},{prepend:t(()=>[e(g(G),{"stroke-width":"1.5",size:"20"})]),default:t(()=>[e(l,{class:"pl-4 text-body-1"},{default:t(()=>[_("My Task")]),_:1})]),_:1})]),_:1}),c("div",ge,[e(s,{to:"",color:"primary",variant:"outlined",class:"rounded-pill",block:""},{default:t(()=>[_("Logout")]),_:1})])]),_:1})]),_:1})}}}),ke=[{header:"Home"},{title:"Dashboard",icon:W,to:"/"},{header:"ui"},{title:"Alert",icon:q,to:"/ui-components/alerts"},{title:"Button",icon:J,to:"/ui-components/buttons"},{title:"Cards",icon:K,to:"/ui-components/cards"},{title:"Tables",icon:Q,to:"/ui-components/tables"},{header:"Auth"},{title:"Login",icon:X,to:"/auth/login"},{title:"Register",icon:Y,to:"/auth/register"},{header:"Extra"},{title:"Icons",icon:Z,to:"/pages/icons"},{title:"Sample Page",icon:ee,to:"/pages/sample-page"}],we={class:"pa-5 pl-4"},Ie={class:"py-0 px-6"},De={class:"container verticalLayout"},Ce={class:"maxWidth"},$e={class:"d-flex align-center justify-space-between w-100"},ze=I({__name:"Main",setup(n){const i=te(ke),o=y(!0);return(d,s)=>{const l=L,m=re,p=pe,h=a("v-list"),v=a("v-btn"),k=a("perfect-scrollbar"),C=a("v-navigation-drawer"),$=he,z=ye,B=a("v-app-bar");return r(),x(w,null,[e(C,{left:"",modelValue:o.value,"onUpdate:modelValue":s[0]||(s[0]=f=>o.value=f),app:"",class:"leftSidebar ml-sm-5 mt-sm-5 bg-containerBg",elevation:"10",width:"270"},{default:t(()=>[c("div",we,[e(l)]),e(k,{class:"scrollnavbar bg-containerBg overflow-y-hidden"},{default:t(()=>[e(h,{class:"py-4 px-4 bg-containerBg"},{default:t(()=>[(r(!0),x(w,null,ne(i.value,(f,Le)=>(r(),x(w,null,[f.header?(r(),u(m,{item:f,key:f.title},null,8,["item"])):(r(),u(p,{key:1,item:f,class:"leftPadding"},null,8,["item"]))],64))),256))]),_:1}),c("div",Ie,[e(v,{class:"mr-2 bg-primary rounded-pill",size:"large",href:"https://www.wrappixel.com/templates/spike-nuxtjs-admin-template/?ref=33",block:"",target:"_blank"},{default:t(()=>[_("Upgrade to Pro")]),_:1})])]),_:1})]),_:1},8,["modelValue"]),c("div",De,[c("div",Ce,[e(B,{elevation:"0",height:"70"},{default:t(()=>[c("div",$e,[c("div",null,[e(v,{class:"hidden-lg-and-up text-muted",onClick:s[1]||(s[1]=f=>o.value=!o.value),icon:"",variant:"flat",size:"small"},{default:t(()=>[e(g(ae),{size:"20","stroke-width":"1.5"})]),_:1}),e($)]),c("div",null,[e(v,{class:"mr-2 bg-primary rounded-pill",href:"https://www.wrappixel.com/templates/spike-nuxtjs-admin-template/?ref=33",target:"_blank"},{default:t(()=>[_("Upgrade to Pro")]),_:1}),e(z)])])]),_:1})])])],64)}}}),Be={class:"maxWidth"},Me=I({__name:"default",setup(n){const i=y("spikeadmin Nuxt 3 - Vuetify 3 - vite - Typescript Based Free Dashboard");return se({meta:[{content:i}],titleTemplate:o=>o?`${o} - Nuxt3 Typescript based Free Admin Dashboard Template`:"spikeadmin Nuxt 3 - Vuetify 3 - vite - Typescript Based Free Dashboard"}),(o,d)=>{const s=ze,l=oe,m=a("v-container"),p=a("v-main"),h=a("v-app"),v=a("v-locale-provider");return r(),u(v,null,{default:t(()=>[e(h,null,{default:t(()=>[e(s),e(p,null,{default:t(()=>[e(m,{fluid:"",class:"page-wrapper bg-background px-sm-5 px-4 pt-12 rounded-xl"},{default:t(()=>[c("div",Be,[e(l)])]),_:1})]),_:1})]),_:1})]),_:1})}}});export{Me as default};
