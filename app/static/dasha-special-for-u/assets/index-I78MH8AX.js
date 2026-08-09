var im=Object.defineProperty;var rm=(r,e,t)=>e in r?im(r,e,{enumerable:!0,configurable:!0,writable:!0,value:t}):r[e]=t;var Ee=(r,e,t)=>rm(r,typeof e!="symbol"?e+"":e,t);(function(){const e=document.createElement("link").relList;if(e&&e.supports&&e.supports("modulepreload"))return;for(const i of document.querySelectorAll('link[rel="modulepreload"]'))n(i);new MutationObserver(i=>{for(const s of i)if(s.type==="childList")for(const o of s.addedNodes)o.tagName==="LINK"&&o.rel==="modulepreload"&&n(o)}).observe(document,{childList:!0,subtree:!0});function t(i){const s={};return i.integrity&&(s.integrity=i.integrity),i.referrerPolicy&&(s.referrerPolicy=i.referrerPolicy),i.crossOrigin==="use-credentials"?s.credentials="include":i.crossOrigin==="anonymous"?s.credentials="omit":s.credentials="same-origin",s}function n(i){if(i.ep)return;i.ep=!0;const s=t(i);fetch(i.href,s)}})();function Ri(r){if(r===void 0)throw new ReferenceError("this hasn't been initialised - super() hasn't been called");return r}function qf(r,e){r.prototype=Object.create(e.prototype),r.prototype.constructor=r,r.__proto__=e}/*!
 * GSAP 3.15.0
 * https://gsap.com
 *
 * @license Copyright 2008-2026, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/var Hn={autoSleep:120,force3D:"auto",nullTargetWarn:1,units:{lineHeight:""}},So={duration:.5,overwrite:!1,delay:0},wu,en,wt,Zn=1e8,xt=1/Zn,uc=Math.PI*2,sm=uc/4,om=0,$f=Math.sqrt,am=Math.cos,lm=Math.sin,jt=function(e){return typeof e=="string"},Pt=function(e){return typeof e=="function"},Oi=function(e){return typeof e=="number"},Au=function(e){return typeof e>"u"},Mi=function(e){return typeof e=="object"},En=function(e){return e!==!1},Ru=function(){return typeof window<"u"},ko=function(e){return Pt(e)||jt(e)},Kf=typeof ArrayBuffer=="function"&&ArrayBuffer.isView||function(){},ln=Array.isArray,cm=/random\([^)]+\)/g,um=/,\s*/g,ch=/(?:-?\.?\d|\.)+/gi,Zf=/[-+=.]*\d+[.e\-+]*\d*[e\-+]*\d*/g,_s=/[-+=.]*\d+[.e-]*\d*[a-z%]*/g,pl=/[-+=.]*\d+\.?\d*(?:e-|e\+)?\d*/gi,jf=/[+-]=-?[.\d]+/,hm=/[^,'"\[\]\s]+/gi,fm=/^[+\-=e\s\d]*\d+[.\d]*([a-z]*|%)\s*$/i,Rt,di,hc,Cu,Gn={},ka={},Jf,Qf=function(e){return(ka=Ps(e,Gn))&&Rn},Pu=function(e,t){return console.warn("Invalid property",e,"set to",t,"Missing plugin? gsap.registerPlugin()")},Mo=function(e,t){return!t&&console.warn(e)},ed=function(e,t){return e&&(Gn[e]=t)&&ka&&(ka[e]=t)||Gn},yo=function(){return 0},dm={suppressEvents:!0,isStart:!0,kill:!1},Ea={suppressEvents:!0,kill:!1},pm={suppressEvents:!0},Du={},nr=[],fc={},td,Nn={},ml={},uh=30,Ta=[],Lu="",Iu=function(e){var t=e[0],n,i;if(Mi(t)||Pt(t)||(e=[e]),!(n=(t._gsap||{}).harness)){for(i=Ta.length;i--&&!Ta[i].targetTest(t););n=Ta[i]}for(i=e.length;i--;)e[i]&&(e[i]._gsap||(e[i]._gsap=new Ed(e[i],n)))||e.splice(i,1);return e},Lr=function(e){return e._gsap||Iu(jn(e))[0]._gsap},nd=function(e,t,n){return(n=e[t])&&Pt(n)?e[t]():Au(n)&&e.getAttribute&&e.getAttribute(t)||n},Tn=function(e,t){return(e=e.split(",")).forEach(t)||e},Ut=function(e){return Math.round(e*1e5)/1e5||0},At=function(e){return Math.round(e*1e7)/1e7||0},Ss=function(e,t){var n=t.charAt(0),i=parseFloat(t.substr(2));return e=parseFloat(e),n==="+"?e+i:n==="-"?e-i:n==="*"?e*i:e/i},mm=function(e,t){for(var n=t.length,i=0;e.indexOf(t[i])<0&&++i<n;);return i<n},Ha=function(){var e=nr.length,t=nr.slice(0),n,i;for(fc={},nr.length=0,n=0;n<e;n++)i=t[n],i&&i._lazy&&(i.render(i._lazy[0],i._lazy[1],!0)._lazy=0)},Uu=function(e){return!!(e._initted||e._startAt||e.add)},id=function(e,t,n,i){nr.length&&!en&&Ha(),e.render(t,n,!!(en&&t<0&&Uu(e))),nr.length&&!en&&Ha()},rd=function(e){var t=parseFloat(e);return(t||t===0)&&(e+"").match(hm).length<2?t:jt(e)?e.trim():e},sd=function(e){return e},Vn=function(e,t){for(var n in t)n in e||(e[n]=t[n]);return e},_m=function(e){return function(t,n){for(var i in n)i in t||i==="duration"&&e||i==="ease"||(t[i]=n[i])}},Ps=function(e,t){for(var n in t)e[n]=t[n];return e},hh=function r(e,t){for(var n in t)n!=="__proto__"&&n!=="constructor"&&n!=="prototype"&&(e[n]=Mi(t[n])?r(e[n]||(e[n]={}),t[n]):t[n]);return e},Ga=function(e,t){var n={},i;for(i in e)i in t||(n[i]=e[i]);return n},ao=function(e){var t=e.parent||Rt,n=e.keyframes?_m(ln(e.keyframes)):Vn;if(En(e.inherit))for(;t;)n(e,t.vars.defaults),t=t.parent||t._dp;return e},gm=function(e,t){for(var n=e.length,i=n===t.length;i&&n--&&e[n]===t[n];);return n<0},od=function(e,t,n,i,s){var o=e[i],a;if(s)for(a=t[s];o&&o[s]>a;)o=o._prev;return o?(t._next=o._next,o._next=t):(t._next=e[n],e[n]=t),t._next?t._next._prev=t:e[i]=t,t._prev=o,t.parent=t._dp=e,t},il=function(e,t,n,i){n===void 0&&(n="_first"),i===void 0&&(i="_last");var s=t._prev,o=t._next;s?s._next=o:e[n]===t&&(e[n]=o),o?o._prev=s:e[i]===t&&(e[i]=s),t._next=t._prev=t.parent=null},ar=function(e,t){e.parent&&(!t||e.parent.autoRemoveChildren)&&e.parent.remove&&e.parent.remove(e),e._act=0},Ir=function(e,t){if(e&&(!t||t._end>e._dur||t._start<0))for(var n=e;n;)n._dirty=1,n=n.parent;return e},vm=function(e){for(var t=e.parent;t&&t.parent;)t._dirty=1,t.totalDuration(),t=t.parent;return e},dc=function(e,t,n,i){return e._startAt&&(en?e._startAt.revert(Ea):e.vars.immediateRender&&!e.vars.autoRevert||e._startAt.render(t,!0,i))},xm=function r(e){return!e||e._ts&&r(e.parent)},fh=function(e){return e._repeat?Ds(e._tTime,e=e.duration()+e._rDelay)*e:0},Ds=function(e,t){var n=Math.floor(e=At(e/t));return e&&n===e?n-1:n},Va=function(e,t){return(e-t._start)*t._ts+(t._ts>=0?0:t._dirty?t.totalDuration():t._tDur)},rl=function(e){return e._end=At(e._start+(e._tDur/Math.abs(e._ts||e._rts||xt)||0))},sl=function(e,t){var n=e._dp;return n&&n.smoothChildTiming&&e._ts&&(e._start=At(n._time-(e._ts>0?t/e._ts:((e._dirty?e.totalDuration():e._tDur)-t)/-e._ts)),rl(e),n._dirty||Ir(n,e)),e},ad=function(e,t){var n;if((t._time||!t._dur&&t._initted||t._start<e._time&&(t._dur||!t.add))&&(n=Va(e.rawTime(),t),(!t._dur||Do(0,t.totalDuration(),n)-t._tTime>xt)&&t.render(n,!0)),Ir(e,t)._dp&&e._initted&&e._time>=e._dur&&e._ts){if(e._dur<e.duration())for(n=e;n._dp;)n.rawTime()>=0&&n.totalTime(n._tTime),n=n._dp;e._zTime=-xt}},_i=function(e,t,n,i){return t.parent&&ar(t),t._start=At((Oi(n)?n:n||e!==Rt?Yn(e,n,t):e._time)+t._delay),t._end=At(t._start+(t.totalDuration()/Math.abs(t.timeScale())||0)),od(e,t,"_first","_last",e._sort?"_start":0),pc(t)||(e._recent=t),i||ad(e,t),e._ts<0&&sl(e,e._tTime),e},ld=function(e,t){return(Gn.ScrollTrigger||Pu("scrollTrigger",t))&&Gn.ScrollTrigger.create(t,e)},cd=function(e,t,n,i,s){if(Fu(e,t,s),!e._initted)return 1;if(!n&&e._pt&&!en&&(e._dur&&e.vars.lazy!==!1||!e._dur&&e.vars.lazy)&&td!==On.frame)return nr.push(e),e._lazy=[s,i],1},Sm=function r(e){var t=e.parent;return t&&t._ts&&t._initted&&!t._lock&&(t.rawTime()<0||r(t))},pc=function(e){var t=e.data;return t==="isFromStart"||t==="isStart"},Mm=function(e,t,n,i){var s=e.ratio,o=t<0||!t&&(!e._start&&Sm(e)&&!(!e._initted&&pc(e))||(e._ts<0||e._dp._ts<0)&&!pc(e))?0:1,a=e._rDelay,l=0,c,u,f;if(a&&e._repeat&&(l=Do(0,e._tDur,t),u=Ds(l,a),e._yoyo&&u&1&&(o=1-o),u!==Ds(e._tTime,a)&&(s=1-o,e.vars.repeatRefresh&&e._initted&&e.invalidate())),o!==s||en||i||e._zTime===xt||!t&&e._zTime){if(!e._initted&&cd(e,t,i,n,l))return;for(f=e._zTime,e._zTime=t||(n?xt:0),n||(n=t&&!f),e.ratio=o,e._from&&(o=1-o),e._time=0,e._tTime=l,c=e._pt;c;)c.r(o,c.d),c=c._next;t<0&&dc(e,t,n,!0),e._onUpdate&&!n&&zn(e,"onUpdate"),l&&e._repeat&&!n&&e.parent&&zn(e,"onRepeat"),(t>=e._tDur||t<0)&&e.ratio===o&&(o&&ar(e,1),!n&&!en&&(zn(e,o?"onComplete":"onReverseComplete",!0),e._prom&&e._prom()))}else e._zTime||(e._zTime=t)},ym=function(e,t,n){var i;if(n>t)for(i=e._first;i&&i._start<=n;){if(i.data==="isPause"&&i._start>t)return i;i=i._next}else for(i=e._last;i&&i._start>=n;){if(i.data==="isPause"&&i._start<t)return i;i=i._prev}},Ls=function(e,t,n,i){var s=e._repeat,o=At(t)||0,a=e._tTime/e._tDur;return a&&!i&&(e._time*=o/e._dur),e._dur=o,e._tDur=s?s<0?1e10:At(o*(s+1)+e._rDelay*s):o,a>0&&!i&&sl(e,e._tTime=e._tDur*a),e.parent&&rl(e),n||Ir(e.parent,e),e},dh=function(e){return e instanceof yn?Ir(e):Ls(e,e._dur)},Em={_start:0,endTime:yo,totalDuration:yo},Yn=function r(e,t,n){var i=e.labels,s=e._recent||Em,o=e.duration()>=Zn?s.endTime(!1):e._dur,a,l,c;return jt(t)&&(isNaN(t)||t in i)?(l=t.charAt(0),c=t.substr(-1)==="%",a=t.indexOf("="),l==="<"||l===">"?(a>=0&&(t=t.replace(/=/,"")),(l==="<"?s._start:s.endTime(s._repeat>=0))+(parseFloat(t.substr(1))||0)*(c?(a<0?s:n).totalDuration()/100:1)):a<0?(t in i||(i[t]=o),i[t]):(l=parseFloat(t.charAt(a-1)+t.substr(a+1)),c&&n&&(l=l/100*(ln(n)?n[0]:n).totalDuration()),a>1?r(e,t.substr(0,a-1),n)+l:o+l)):t==null?o:+t},lo=function(e,t,n){var i=Oi(t[1]),s=(i?2:1)+(e<2?0:1),o=t[s],a,l;if(i&&(o.duration=t[1]),o.parent=n,e){for(a=o,l=n;l&&!("immediateRender"in a);)a=l.vars.defaults||{},l=En(l.vars.inherit)&&l.parent;o.immediateRender=En(a.immediateRender),e<2?o.runBackwards=1:o.startAt=t[s-1]}return new kt(t[0],o,t[s+1])},fr=function(e,t){return e||e===0?t(e):t},Do=function(e,t,n){return n<e?e:n>t?t:n},on=function(e,t){return!jt(e)||!(t=fm.exec(e))?"":t[1]},Tm=function(e,t,n){return fr(n,function(i){return Do(e,t,i)})},mc=[].slice,ud=function(e,t){return e&&Mi(e)&&"length"in e&&(!t&&!e.length||e.length-1 in e&&Mi(e[0]))&&!e.nodeType&&e!==di},bm=function(e,t,n){return n===void 0&&(n=[]),e.forEach(function(i){var s;return jt(i)&&!t||ud(i,1)?(s=n).push.apply(s,jn(i)):n.push(i)})||n},jn=function(e,t,n){return wt&&!t&&wt.selector?wt.selector(e):jt(e)&&!n&&(hc||!Is())?mc.call((t||Cu).querySelectorAll(e),0):ln(e)?bm(e,n):ud(e)?mc.call(e,0):e?[e]:[]},_c=function(e){return e=jn(e)[0]||Mo("Invalid scope")||{},function(t){var n=e.current||e.nativeElement||e;return jn(t,n.querySelectorAll?n:n===e?Mo("Invalid scope")||Cu.createElement("div"):e)}},hd=function(e){return e.sort(function(){return .5-Math.random()})},fd=function(e){if(Pt(e))return e;var t=Mi(e)?e:{each:e},n=Ur(t.ease),i=t.from||0,s=parseFloat(t.base)||0,o={},a=i>0&&i<1,l=isNaN(i)||a,c=t.axis,u=i,f=i;return jt(i)?u=f={center:.5,edges:.5,end:1}[i]||0:!a&&l&&(u=i[0],f=i[1]),function(h,d,_){var g=(_||t).length,p=o[g],m,y,x,M,R,w,E,D,O;if(!p){if(O=t.grid==="auto"?0:(t.grid||[1,Zn])[1],!O){for(E=-Zn;E<(E=_[O++].getBoundingClientRect().left)&&O<g;);O<g&&O--}for(p=o[g]=[],m=l?Math.min(O,g)*u-.5:i%O,y=O===Zn?0:l?g*f/O-.5:i/O|0,E=0,D=Zn,w=0;w<g;w++)x=w%O-m,M=y-(w/O|0),p[w]=R=c?Math.abs(c==="y"?M:x):$f(x*x+M*M),R>E&&(E=R),R<D&&(D=R);i==="random"&&hd(p),p.max=E-D,p.min=D,p.v=g=(parseFloat(t.amount)||parseFloat(t.each)*(O>g?g-1:c?c==="y"?g/O:O:Math.max(O,g/O))||0)*(i==="edges"?-1:1),p.b=g<0?s-g:s,p.u=on(t.amount||t.each)||0,n=n&&g<0?Bm(n):n}return g=(p[h]-p.min)/p.max||0,At(p.b+(n?n(g):g)*p.v)+p.u}},gc=function(e){var t=Math.pow(10,((e+"").split(".")[1]||"").length);return function(n){var i=At(Math.round(parseFloat(n)/e)*e*t);return(i-i%1)/t+(Oi(n)?0:on(n))}},dd=function(e,t){var n=ln(e),i,s;return!n&&Mi(e)&&(i=n=e.radius||Zn,e.values?(e=jn(e.values),(s=!Oi(e[0]))&&(i*=i)):e=gc(e.increment)),fr(t,n?Pt(e)?function(o){return s=e(o),Math.abs(s-o)<=i?s:o}:function(o){for(var a=parseFloat(s?o.x:o),l=parseFloat(s?o.y:0),c=Zn,u=0,f=e.length,h,d;f--;)s?(h=e[f].x-a,d=e[f].y-l,h=h*h+d*d):h=Math.abs(e[f]-a),h<c&&(c=h,u=f);return u=!i||c<=i?e[u]:o,s||u===o||Oi(o)?u:u+on(o)}:gc(e))},pd=function(e,t,n,i){return fr(ln(e)?!t:n===!0?!!(n=0):!i,function(){return ln(e)?e[~~(Math.random()*e.length)]:(n=n||1e-5)&&(i=n<1?Math.pow(10,(n+"").length-2):1)&&Math.floor(Math.round((e-n/2+Math.random()*(t-e+n*.99))/n)*n*i)/i})},wm=function(){for(var e=arguments.length,t=new Array(e),n=0;n<e;n++)t[n]=arguments[n];return function(i){return t.reduce(function(s,o){return o(s)},i)}},Am=function(e,t){return function(n){return e(parseFloat(n))+(t||on(n))}},Rm=function(e,t,n){return _d(e,t,0,1,n)},md=function(e,t,n){return fr(n,function(i){return e[~~t(i)]})},Cm=function r(e,t,n){var i=t-e;return ln(e)?md(e,r(0,e.length),t):fr(n,function(s){return(i+(s-e)%i)%i+e})},Pm=function r(e,t,n){var i=t-e,s=i*2;return ln(e)?md(e,r(0,e.length-1),t):fr(n,function(o){return o=(s+(o-e)%s)%s||0,e+(o>i?s-o:o)})},Eo=function(e){return e.replace(cm,function(t){var n=t.indexOf("[")+1,i=t.substring(n||7,n?t.indexOf("]"):t.length-1).split(um);return pd(n?i:+i[0],n?0:+i[1],+i[2]||1e-5)})},_d=function(e,t,n,i,s){var o=t-e,a=i-n;return fr(s,function(l){return n+((l-e)/o*a||0)})},Dm=function r(e,t,n,i){var s=isNaN(e+t)?0:function(d){return(1-d)*e+d*t};if(!s){var o=jt(e),a={},l,c,u,f,h;if(n===!0&&(i=1)&&(n=null),o)e={p:e},t={p:t};else if(ln(e)&&!ln(t)){for(u=[],f=e.length,h=f-2,c=1;c<f;c++)u.push(r(e[c-1],e[c]));f--,s=function(_){_*=f;var g=Math.min(h,~~_);return u[g](_-g)},n=t}else i||(e=Ps(ln(e)?[]:{},e));if(!u){for(l in t)Nu.call(a,e,l,"get",t[l]);s=function(_){return zu(_,a)||(o?e.p:e)}}}return fr(n,s)},ph=function(e,t,n){var i=e.labels,s=Zn,o,a,l;for(o in i)a=i[o]-t,a<0==!!n&&a&&s>(a=Math.abs(a))&&(l=o,s=a);return l},zn=function(e,t,n){var i=e.vars,s=i[t],o=wt,a=e._ctx,l,c,u;if(s)return l=i[t+"Params"],c=i.callbackScope||e,n&&nr.length&&Ha(),a&&(wt=a),u=l?s.apply(c,l):s.call(c),wt=o,u},Qs=function(e){return ar(e),e.scrollTrigger&&e.scrollTrigger.kill(!!en),e.progress()<1&&zn(e,"onInterrupt"),e},gs,gd=[],vd=function(e){if(e)if(e=!e.name&&e.default||e,Ru()||e.headless){var t=e.name,n=Pt(e),i=t&&!n&&e.init?function(){this._props=[]}:e,s={init:yo,render:zu,add:Nu,kill:$m,modifier:qm,rawVars:0},o={targetTest:0,get:0,getSetter:Bu,aliases:{},register:0};if(Is(),e!==i){if(Nn[t])return;Vn(i,Vn(Ga(e,s),o)),Ps(i.prototype,Ps(s,Ga(e,o))),Nn[i.prop=t]=i,e.targetTest&&(Ta.push(i),Du[t]=1),t=(t==="css"?"CSS":t.charAt(0).toUpperCase()+t.substr(1))+"Plugin"}ed(t,i),e.register&&e.register(Rn,i,bn)}else gd.push(e)},vt=255,eo={aqua:[0,vt,vt],lime:[0,vt,0],silver:[192,192,192],black:[0,0,0],maroon:[128,0,0],teal:[0,128,128],blue:[0,0,vt],navy:[0,0,128],white:[vt,vt,vt],olive:[128,128,0],yellow:[vt,vt,0],orange:[vt,165,0],gray:[128,128,128],purple:[128,0,128],green:[0,128,0],red:[vt,0,0],pink:[vt,192,203],cyan:[0,vt,vt],transparent:[vt,vt,vt,0]},_l=function(e,t,n){return e+=e<0?1:e>1?-1:0,(e*6<1?t+(n-t)*e*6:e<.5?n:e*3<2?t+(n-t)*(2/3-e)*6:t)*vt+.5|0},xd=function(e,t,n){var i=e?Oi(e)?[e>>16,e>>8&vt,e&vt]:0:eo.black,s,o,a,l,c,u,f,h,d,_;if(!i){if(e.substr(-1)===","&&(e=e.substr(0,e.length-1)),eo[e])i=eo[e];else if(e.charAt(0)==="#"){if(e.length<6&&(s=e.charAt(1),o=e.charAt(2),a=e.charAt(3),e="#"+s+s+o+o+a+a+(e.length===5?e.charAt(4)+e.charAt(4):"")),e.length===9)return i=parseInt(e.substr(1,6),16),[i>>16,i>>8&vt,i&vt,parseInt(e.substr(7),16)/255];e=parseInt(e.substr(1),16),i=[e>>16,e>>8&vt,e&vt]}else if(e.substr(0,3)==="hsl"){if(i=_=e.match(ch),!t)l=+i[0]%360/360,c=+i[1]/100,u=+i[2]/100,o=u<=.5?u*(c+1):u+c-u*c,s=u*2-o,i.length>3&&(i[3]*=1),i[0]=_l(l+1/3,s,o),i[1]=_l(l,s,o),i[2]=_l(l-1/3,s,o);else if(~e.indexOf("="))return i=e.match(Zf),n&&i.length<4&&(i[3]=1),i}else i=e.match(ch)||eo.transparent;i=i.map(Number)}return t&&!_&&(s=i[0]/vt,o=i[1]/vt,a=i[2]/vt,f=Math.max(s,o,a),h=Math.min(s,o,a),u=(f+h)/2,f===h?l=c=0:(d=f-h,c=u>.5?d/(2-f-h):d/(f+h),l=f===s?(o-a)/d+(o<a?6:0):f===o?(a-s)/d+2:(s-o)/d+4,l*=60),i[0]=~~(l+.5),i[1]=~~(c*100+.5),i[2]=~~(u*100+.5)),n&&i.length<4&&(i[3]=1),i},Sd=function(e){var t=[],n=[],i=-1;return e.split(ir).forEach(function(s){var o=s.match(_s)||[];t.push.apply(t,o),n.push(i+=o.length+1)}),t.c=n,t},mh=function(e,t,n){var i="",s=(e+i).match(ir),o=t?"hsla(":"rgba(",a=0,l,c,u,f;if(!s)return e;if(s=s.map(function(h){return(h=xd(h,t,1))&&o+(t?h[0]+","+h[1]+"%,"+h[2]+"%,"+h[3]:h.join(","))+")"}),n&&(u=Sd(e),l=n.c,l.join(i)!==u.c.join(i)))for(c=e.replace(ir,"1").split(_s),f=c.length-1;a<f;a++)i+=c[a]+(~l.indexOf(a)?s.shift()||o+"0,0,0,0)":(u.length?u:s.length?s:n).shift());if(!c)for(c=e.split(ir),f=c.length-1;a<f;a++)i+=c[a]+s[a];return i+c[f]},ir=function(){var r="(?:\\b(?:(?:rgb|rgba|hsl|hsla)\\(.+?\\))|\\B#(?:[0-9a-f]{3,4}){1,2}\\b",e;for(e in eo)r+="|"+e+"\\b";return new RegExp(r+")","gi")}(),Lm=/hsl[a]?\(/,Md=function(e){var t=e.join(" "),n;if(ir.lastIndex=0,ir.test(t))return n=Lm.test(t),e[1]=mh(e[1],n),e[0]=mh(e[0],n,Sd(e[1])),!0},To,On=function(){var r=Date.now,e=500,t=33,n=r(),i=n,s=1e3/240,o=s,a=[],l,c,u,f,h,d,_=function g(p){var m=r()-i,y=p===!0,x,M,R,w;if((m>e||m<0)&&(n+=m-t),i+=m,R=i-n,x=R-o,(x>0||y)&&(w=++f.frame,h=R-f.time*1e3,f.time=R=R/1e3,o+=x+(x>=s?4:s-x),M=1),y||(l=c(g)),M)for(d=0;d<a.length;d++)a[d](R,h,w,p)};return f={time:0,frame:0,tick:function(){_(!0)},deltaRatio:function(p){return h/(1e3/(p||60))},wake:function(){Jf&&(!hc&&Ru()&&(di=hc=window,Cu=di.document||{},Gn.gsap=Rn,(di.gsapVersions||(di.gsapVersions=[])).push(Rn.version),Qf(ka||di.GreenSockGlobals||!di.gsap&&di||{}),gd.forEach(vd)),u=typeof requestAnimationFrame<"u"&&requestAnimationFrame,l&&f.sleep(),c=u||function(p){return setTimeout(p,o-f.time*1e3+1|0)},To=1,_(2))},sleep:function(){(u?cancelAnimationFrame:clearTimeout)(l),To=0,c=yo},lagSmoothing:function(p,m){e=p||1/0,t=Math.min(m||33,e)},fps:function(p){s=1e3/(p||240),o=f.time*1e3+s},add:function(p,m,y){var x=m?function(M,R,w,E){p(M,R,w,E),f.remove(x)}:p;return f.remove(p),a[y?"unshift":"push"](x),Is(),x},remove:function(p,m){~(m=a.indexOf(p))&&a.splice(m,1)&&d>=m&&d--},_listeners:a},f}(),Is=function(){return!To&&On.wake()},lt={},Im=/^[\d.\-M][\d.\-,\s]/,Um=/["']/g,Nm=function(e){for(var t={},n=e.substr(1,e.length-3).split(":"),i=n[0],s=1,o=n.length,a,l,c;s<o;s++)l=n[s],a=s!==o-1?l.lastIndexOf(","):l.length,c=l.substr(0,a),t[i]=isNaN(c)?c.replace(Um,"").trim():+c,i=l.substr(a+1).trim();return t},Fm=function(e){var t=e.indexOf("(")+1,n=e.indexOf(")"),i=e.indexOf("(",t);return e.substring(t,~i&&i<n?e.indexOf(")",n+1):n)},Om=function(e){var t=(e+"").split("("),n=lt[t[0]];return n&&t.length>1&&n.config?n.config.apply(null,~e.indexOf("{")?[Nm(t[1])]:Fm(e).split(",").map(rd)):lt._CE&&Im.test(e)?lt._CE("",e):n},Bm=function(e){return function(t){return 1-e(1-t)}},Ur=function(e,t){return e&&(Pt(e)?e:lt[e]||Om(e))||t},Yr=function(e,t,n,i){n===void 0&&(n=function(l){return 1-t(1-l)}),i===void 0&&(i=function(l){return l<.5?t(l*2)/2:1-t((1-l)*2)/2});var s={easeIn:t,easeOut:n,easeInOut:i},o;return Tn(e,function(a){lt[a]=Gn[a]=s,lt[o=a.toLowerCase()]=n;for(var l in s)lt[o+(l==="easeIn"?".in":l==="easeOut"?".out":".inOut")]=lt[a+"."+l]=s[l]}),s},yd=function(e){return function(t){return t<.5?(1-e(1-t*2))/2:.5+e((t-.5)*2)/2}},gl=function r(e,t,n){var i=t>=1?t:1,s=(n||(e?.3:.45))/(t<1?t:1),o=s/uc*(Math.asin(1/i)||0),a=function(u){return u===1?1:i*Math.pow(2,-10*u)*lm((u-o)*s)+1},l=e==="out"?a:e==="in"?function(c){return 1-a(1-c)}:yd(a);return s=uc/s,l.config=function(c,u){return r(e,c,u)},l},vl=function r(e,t){t===void 0&&(t=1.70158);var n=function(o){return o?--o*o*((t+1)*o+t)+1:0},i=e==="out"?n:e==="in"?function(s){return 1-n(1-s)}:yd(n);return i.config=function(s){return r(e,s)},i};Tn("Linear,Quad,Cubic,Quart,Quint,Strong",function(r,e){var t=e<5?e+1:e;Yr(r+",Power"+(t-1),e?function(n){return Math.pow(n,t)}:function(n){return n},function(n){return 1-Math.pow(1-n,t)},function(n){return n<.5?Math.pow(n*2,t)/2:1-Math.pow((1-n)*2,t)/2})});lt.Linear.easeNone=lt.none=lt.Linear.easeIn;Yr("Elastic",gl("in"),gl("out"),gl());(function(r,e){var t=1/e,n=2*t,i=2.5*t,s=function(a){return a<t?r*a*a:a<n?r*Math.pow(a-1.5/e,2)+.75:a<i?r*(a-=2.25/e)*a+.9375:r*Math.pow(a-2.625/e,2)+.984375};Yr("Bounce",function(o){return 1-s(1-o)},s)})(7.5625,2.75);Yr("Expo",function(r){return Math.pow(2,10*(r-1))*r+r*r*r*r*r*r*(1-r)});Yr("Circ",function(r){return-($f(1-r*r)-1)});Yr("Sine",function(r){return r===1?1:-am(r*sm)+1});Yr("Back",vl("in"),vl("out"),vl());lt.SteppedEase=lt.steps=Gn.SteppedEase={config:function(e,t){e===void 0&&(e=1);var n=1/e,i=e+(t?0:1),s=t?1:0,o=1-xt;return function(a){return((i*Do(0,o,a)|0)+s)*n}}};So.ease=lt["quad.out"];Tn("onComplete,onUpdate,onStart,onRepeat,onReverseComplete,onInterrupt",function(r){return Lu+=r+","+r+"Params,"});var Ed=function(e,t){this.id=om++,e._gsap=this,this.target=e,this.harness=t,this.get=t?t.get:nd,this.set=t?t.getSetter:Bu},bo=function(){function r(t){this.vars=t,this._delay=+t.delay||0,(this._repeat=t.repeat===1/0?-2:t.repeat||0)&&(this._rDelay=t.repeatDelay||0,this._yoyo=!!t.yoyo||!!t.yoyoEase),this._ts=1,Ls(this,+t.duration,1,1),this.data=t.data,wt&&(this._ctx=wt,wt.data.push(this)),To||On.wake()}var e=r.prototype;return e.delay=function(n){return n||n===0?(this.parent&&this.parent.smoothChildTiming&&this.startTime(this._start+n-this._delay),this._delay=n,this):this._delay},e.duration=function(n){return arguments.length?this.totalDuration(this._repeat>0?n+(n+this._rDelay)*this._repeat:n):this.totalDuration()&&this._dur},e.totalDuration=function(n){return arguments.length?(this._dirty=0,Ls(this,this._repeat<0?n:(n-this._repeat*this._rDelay)/(this._repeat+1))):this._tDur},e.totalTime=function(n,i){if(Is(),!arguments.length)return this._tTime;var s=this._dp;if(s&&s.smoothChildTiming&&this._ts){for(sl(this,n),!s._dp||s.parent||ad(s,this);s&&s.parent;)s.parent._time!==s._start+(s._ts>=0?s._tTime/s._ts:(s.totalDuration()-s._tTime)/-s._ts)&&s.totalTime(s._tTime,!0),s=s.parent;!this.parent&&this._dp.autoRemoveChildren&&(this._ts>0&&n<this._tDur||this._ts<0&&n>0||!this._tDur&&!n)&&_i(this._dp,this,this._start-this._delay)}return(this._tTime!==n||!this._dur&&!i||this._initted&&Math.abs(this._zTime)===xt||!this._initted&&this._dur&&n||!n&&!this._initted&&(this.add||this._ptLookup))&&(this._ts||(this._pTime=n),id(this,n,i)),this},e.time=function(n,i){return arguments.length?this.totalTime(Math.min(this.totalDuration(),n+fh(this))%(this._dur+this._rDelay)||(n?this._dur:0),i):this._time},e.totalProgress=function(n,i){return arguments.length?this.totalTime(this.totalDuration()*n,i):this.totalDuration()?Math.min(1,this._tTime/this._tDur):this.rawTime()>=0&&this._initted?1:0},e.progress=function(n,i){return arguments.length?this.totalTime(this.duration()*(this._yoyo&&!(this.iteration()&1)?1-n:n)+fh(this),i):this.duration()?Math.min(1,this._time/this._dur):this.rawTime()>0?1:0},e.iteration=function(n,i){var s=this.duration()+this._rDelay;return arguments.length?this.totalTime(this._time+(n-1)*s,i):this._repeat?Ds(this._tTime,s)+1:1},e.timeScale=function(n,i){if(!arguments.length)return this._rts===-xt?0:this._rts;if(this._rts===n)return this;var s=this.parent&&this._ts?Va(this.parent._time,this):this._tTime;return this._rts=+n||0,this._ts=this._ps||n===-xt?0:this._rts,this.totalTime(Do(-Math.abs(this._delay),this.totalDuration(),s),i!==!1),rl(this),vm(this)},e.paused=function(n){return arguments.length?(this._ps!==n&&(this._ps=n,n?(this._pTime=this._tTime||Math.max(-this._delay,this.rawTime()),this._ts=this._act=0):(Is(),this._ts=this._rts,this.totalTime(this.parent&&!this.parent.smoothChildTiming?this.rawTime():this._tTime||this._pTime,this.progress()===1&&Math.abs(this._zTime)!==xt&&(this._tTime-=xt)))),this):this._ps},e.startTime=function(n){if(arguments.length){this._start=At(n);var i=this.parent||this._dp;return i&&(i._sort||!this.parent)&&_i(i,this,this._start-this._delay),this}return this._start},e.endTime=function(n){return this._start+(En(n)?this.totalDuration():this.duration())/Math.abs(this._ts||1)},e.rawTime=function(n){var i=this.parent||this._dp;return i?n&&(!this._ts||this._repeat&&this._time&&this.totalProgress()<1)?this._tTime%(this._dur+this._rDelay):this._ts?Va(i.rawTime(n),this):this._tTime:this._tTime},e.revert=function(n){n===void 0&&(n=pm);var i=en;return en=n,Uu(this)&&(this.timeline&&this.timeline.revert(n),this.totalTime(-.01,n.suppressEvents)),this.data!=="nested"&&n.kill!==!1&&this.kill(),en=i,this},e.globalTime=function(n){for(var i=this,s=arguments.length?n:i.rawTime();i;)s=i._start+s/(Math.abs(i._ts)||1),i=i._dp;return!this.parent&&this._sat?this._sat.globalTime(n):s},e.repeat=function(n){return arguments.length?(this._repeat=n===1/0?-2:n,dh(this)):this._repeat===-2?1/0:this._repeat},e.repeatDelay=function(n){if(arguments.length){var i=this._time;return this._rDelay=n,dh(this),i?this.time(i):this}return this._rDelay},e.yoyo=function(n){return arguments.length?(this._yoyo=n,this):this._yoyo},e.seek=function(n,i){return this.totalTime(Yn(this,n),En(i))},e.restart=function(n,i){return this.play().totalTime(n?-this._delay:0,En(i)),this._dur||(this._zTime=-xt),this},e.play=function(n,i){return n!=null&&this.seek(n,i),this.reversed(!1).paused(!1)},e.reverse=function(n,i){return n!=null&&this.seek(n||this.totalDuration(),i),this.reversed(!0).paused(!1)},e.pause=function(n,i){return n!=null&&this.seek(n,i),this.paused(!0)},e.resume=function(){return this.paused(!1)},e.reversed=function(n){return arguments.length?(!!n!==this.reversed()&&this.timeScale(-this._rts||(n?-xt:0)),this):this._rts<0},e.invalidate=function(){return this._initted=this._act=0,this._zTime=-xt,this},e.isActive=function(){var n=this.parent||this._dp,i=this._start,s;return!!(!n||this._ts&&this._initted&&n.isActive()&&(s=n.rawTime(!0))>=i&&s<this.endTime(!0)-xt)},e.eventCallback=function(n,i,s){var o=this.vars;return arguments.length>1?(i?(o[n]=i,s&&(o[n+"Params"]=s),n==="onUpdate"&&(this._onUpdate=i)):delete o[n],this):o[n]},e.then=function(n){var i=this,s=i._prom;return new Promise(function(o){var a=Pt(n)?n:sd,l=function(){var u=i.then;i.then=null,s&&s(),Pt(a)&&(a=a(i))&&(a.then||a===i)&&(i.then=u),o(a),i.then=u};i._initted&&i.totalProgress()===1&&i._ts>=0||!i._tTime&&i._ts<0?l():i._prom=l})},e.kill=function(){Qs(this)},r}();Vn(bo.prototype,{_time:0,_start:0,_end:0,_tTime:0,_tDur:0,_dirty:0,_repeat:0,_yoyo:!1,parent:null,_initted:!1,_rDelay:0,_ts:1,_dp:0,ratio:0,_zTime:-xt,_prom:0,_ps:!1,_rts:1});var yn=function(r){qf(e,r);function e(n,i){var s;return n===void 0&&(n={}),s=r.call(this,n)||this,s.labels={},s.smoothChildTiming=!!n.smoothChildTiming,s.autoRemoveChildren=!!n.autoRemoveChildren,s._sort=En(n.sortChildren),Rt&&_i(n.parent||Rt,Ri(s),i),n.reversed&&s.reverse(),n.paused&&s.paused(!0),n.scrollTrigger&&ld(Ri(s),n.scrollTrigger),s}var t=e.prototype;return t.to=function(i,s,o){return lo(0,arguments,this),this},t.from=function(i,s,o){return lo(1,arguments,this),this},t.fromTo=function(i,s,o,a){return lo(2,arguments,this),this},t.set=function(i,s,o){return s.duration=0,s.parent=this,ao(s).repeatDelay||(s.repeat=0),s.immediateRender=!!s.immediateRender,new kt(i,s,Yn(this,o),1),this},t.call=function(i,s,o){return _i(this,kt.delayedCall(0,i,s),o)},t.staggerTo=function(i,s,o,a,l,c,u){return o.duration=s,o.stagger=o.stagger||a,o.onComplete=c,o.onCompleteParams=u,o.parent=this,new kt(i,o,Yn(this,l)),this},t.staggerFrom=function(i,s,o,a,l,c,u){return o.runBackwards=1,ao(o).immediateRender=En(o.immediateRender),this.staggerTo(i,s,o,a,l,c,u)},t.staggerFromTo=function(i,s,o,a,l,c,u,f){return a.startAt=o,ao(a).immediateRender=En(a.immediateRender),this.staggerTo(i,s,a,l,c,u,f)},t.render=function(i,s,o){var a=this._time,l=this._dirty?this.totalDuration():this._tDur,c=this._dur,u=i<=0?0:At(i),f=this._zTime<0!=i<0&&(this._initted||!c),h,d,_,g,p,m,y,x,M,R,w,E;if(this!==Rt&&u>l&&i>=0&&(u=l),u!==this._tTime||o||f){if(a!==this._time&&c&&(u+=this._time-a,i+=this._time-a),h=u,M=this._start,x=this._ts,m=!x,f&&(c||(a=this._zTime),(i||!s)&&(this._zTime=i)),this._repeat){if(w=this._yoyo,p=c+this._rDelay,this._repeat<-1&&i<0)return this.totalTime(p*100+i,s,o);if(h=At(u%p),u===l?(g=this._repeat,h=c):(R=At(u/p),g=~~R,g&&g===R&&(h=c,g--),h>c&&(h=c)),R=Ds(this._tTime,p),!a&&this._tTime&&R!==g&&this._tTime-R*p-this._dur<=0&&(R=g),w&&g&1&&(h=c-h,E=1),g!==R&&!this._lock){var D=w&&R&1,O=D===(w&&g&1);if(g<R&&(D=!D),a=D?0:u%c?c:u,this._lock=1,this.render(a||(E?0:At(g*p)),s,!c)._lock=0,this._tTime=u,!s&&this.parent&&zn(this,"onRepeat"),this.vars.repeatRefresh&&!E&&(this.invalidate()._lock=1,R=g),a&&a!==this._time||m!==!this._ts||this.vars.onRepeat&&!this.parent&&!this._act)return this;if(c=this._dur,l=this._tDur,O&&(this._lock=2,a=D?c:-1e-4,this.render(a,!0),this.vars.repeatRefresh&&!E&&this.invalidate()),this._lock=0,!this._ts&&!m)return this}}if(this._hasPause&&!this._forcing&&this._lock<2&&(y=ym(this,At(a),At(h)),y&&(u-=h-(h=y._start))),this._tTime=u,this._time=h,this._act=!!x,this._initted||(this._onUpdate=this.vars.onUpdate,this._initted=1,this._zTime=i,a=0),!a&&u&&c&&!s&&!R&&(zn(this,"onStart"),this._tTime!==u))return this;if(h>=a&&i>=0)for(d=this._first;d;){if(_=d._next,(d._act||h>=d._start)&&d._ts&&y!==d){if(d.parent!==this)return this.render(i,s,o);if(d.render(d._ts>0?(h-d._start)*d._ts:(d._dirty?d.totalDuration():d._tDur)+(h-d._start)*d._ts,s,o),h!==this._time||!this._ts&&!m){y=0,_&&(u+=this._zTime=-xt);break}}d=_}else{d=this._last;for(var v=i<0?i:h;d;){if(_=d._prev,(d._act||v<=d._end)&&d._ts&&y!==d){if(d.parent!==this)return this.render(i,s,o);if(d.render(d._ts>0?(v-d._start)*d._ts:(d._dirty?d.totalDuration():d._tDur)+(v-d._start)*d._ts,s,o||en&&Uu(d)),h!==this._time||!this._ts&&!m){y=0,_&&(u+=this._zTime=v?-xt:xt);break}}d=_}}if(y&&!s&&(this.pause(),y.render(h>=a?0:-xt)._zTime=h>=a?1:-1,this._ts))return this._start=M,rl(this),this.render(i,s,o);this._onUpdate&&!s&&zn(this,"onUpdate",!0),(u===l&&this._tTime>=this.totalDuration()||!u&&a)&&(M===this._start||Math.abs(x)!==Math.abs(this._ts))&&(this._lock||((i||!c)&&(u===l&&this._ts>0||!u&&this._ts<0)&&ar(this,1),!s&&!(i<0&&!a)&&(u||a||!l)&&(zn(this,u===l&&i>=0?"onComplete":"onReverseComplete",!0),this._prom&&!(u<l&&this.timeScale()>0)&&this._prom())))}return this},t.add=function(i,s){var o=this;if(Oi(s)||(s=Yn(this,s,i)),!(i instanceof bo)){if(ln(i))return i.forEach(function(a){return o.add(a,s)}),this;if(jt(i))return this.addLabel(i,s);if(Pt(i))i=kt.delayedCall(0,i);else return this}return this!==i?_i(this,i,s):this},t.getChildren=function(i,s,o,a){i===void 0&&(i=!0),s===void 0&&(s=!0),o===void 0&&(o=!0),a===void 0&&(a=-Zn);for(var l=[],c=this._first;c;)c._start>=a&&(c instanceof kt?s&&l.push(c):(o&&l.push(c),i&&l.push.apply(l,c.getChildren(!0,s,o)))),c=c._next;return l},t.getById=function(i){for(var s=this.getChildren(1,1,1),o=s.length;o--;)if(s[o].vars.id===i)return s[o]},t.remove=function(i){return jt(i)?this.removeLabel(i):Pt(i)?this.killTweensOf(i):(i.parent===this&&il(this,i),i===this._recent&&(this._recent=this._last),Ir(this))},t.totalTime=function(i,s){return arguments.length?(this._forcing=1,!this._dp&&this._ts&&(this._start=At(On.time-(this._ts>0?i/this._ts:(this.totalDuration()-i)/-this._ts))),r.prototype.totalTime.call(this,i,s),this._forcing=0,this):this._tTime},t.addLabel=function(i,s){return this.labels[i]=Yn(this,s),this},t.removeLabel=function(i){return delete this.labels[i],this},t.addPause=function(i,s,o){var a=kt.delayedCall(0,s||yo,o);return a.data="isPause",this._hasPause=1,_i(this,a,Yn(this,i))},t.removePause=function(i){var s=this._first;for(i=Yn(this,i);s;)s._start===i&&s.data==="isPause"&&ar(s),s=s._next},t.killTweensOf=function(i,s,o){for(var a=this.getTweensOf(i,o),l=a.length;l--;)ji!==a[l]&&a[l].kill(i,s);return this},t.getTweensOf=function(i,s){for(var o=[],a=jn(i),l=this._first,c=Oi(s),u;l;)l instanceof kt?mm(l._targets,a)&&(c?(!ji||l._initted&&l._ts)&&l.globalTime(0)<=s&&l.globalTime(l.totalDuration())>s:!s||l.isActive())&&o.push(l):(u=l.getTweensOf(a,s)).length&&o.push.apply(o,u),l=l._next;return o},t.tweenTo=function(i,s){s=s||{};var o=this,a=Yn(o,i),l=s,c=l.startAt,u=l.onStart,f=l.onStartParams,h=l.immediateRender,d,_=kt.to(o,Vn({ease:s.ease||"none",lazy:!1,immediateRender:!1,time:a,overwrite:"auto",duration:s.duration||Math.abs((a-(c&&"time"in c?c.time:o._time))/o.timeScale())||xt,onStart:function(){if(o.pause(),!d){var p=s.duration||Math.abs((a-(c&&"time"in c?c.time:o._time))/o.timeScale());_._dur!==p&&Ls(_,p,0,1).render(_._time,!0,!0),d=1}u&&u.apply(_,f||[])}},s));return h?_.render(0):_},t.tweenFromTo=function(i,s,o){return this.tweenTo(s,Vn({startAt:{time:Yn(this,i)}},o))},t.recent=function(){return this._recent},t.nextLabel=function(i){return i===void 0&&(i=this._time),ph(this,Yn(this,i))},t.previousLabel=function(i){return i===void 0&&(i=this._time),ph(this,Yn(this,i),1)},t.currentLabel=function(i){return arguments.length?this.seek(i,!0):this.previousLabel(this._time+xt)},t.shiftChildren=function(i,s,o){o===void 0&&(o=0);var a=this._first,l=this.labels,c;for(i=At(i);a;)a._start>=o&&(a._start+=i,a._end+=i),a=a._next;if(s)for(c in l)l[c]>=o&&(l[c]+=i);return Ir(this)},t.invalidate=function(i){var s=this._first;for(this._lock=0;s;)s.invalidate(i),s=s._next;return r.prototype.invalidate.call(this,i)},t.clear=function(i){i===void 0&&(i=!0);for(var s=this._first,o;s;)o=s._next,this.remove(s),s=o;return this._dp&&(this._time=this._tTime=this._pTime=0),i&&(this.labels={}),Ir(this)},t.totalDuration=function(i){var s=0,o=this,a=o._last,l=Zn,c,u,f;if(arguments.length)return o.timeScale((o._repeat<0?o.duration():o.totalDuration())/(o.reversed()?-i:i));if(o._dirty){for(f=o.parent;a;)c=a._prev,a._dirty&&a.totalDuration(),u=a._start,u>l&&o._sort&&a._ts&&!o._lock?(o._lock=1,_i(o,a,u-a._delay,1)._lock=0):l=u,u<0&&a._ts&&(s-=u,(!f&&!o._dp||f&&f.smoothChildTiming)&&(o._start+=At(u/o._ts),o._time-=u,o._tTime-=u),o.shiftChildren(-u,!1,-1/0),l=0),a._end>s&&a._ts&&(s=a._end),a=c;Ls(o,o===Rt&&o._time>s?o._time:s,1,1),o._dirty=0}return o._tDur},e.updateRoot=function(i){if(Rt._ts&&(id(Rt,Va(i,Rt)),td=On.frame),On.frame>=uh){uh+=Hn.autoSleep||120;var s=Rt._first;if((!s||!s._ts)&&Hn.autoSleep&&On._listeners.length<2){for(;s&&!s._ts;)s=s._next;s||On.sleep()}}},e}(bo);Vn(yn.prototype,{_lock:0,_hasPause:0,_forcing:0});var zm=function(e,t,n,i,s,o,a){var l=new bn(this._pt,e,t,0,1,Cd,null,s),c=0,u=0,f,h,d,_,g,p,m,y;for(l.b=n,l.e=i,n+="",i+="",(m=~i.indexOf("random("))&&(i=Eo(i)),o&&(y=[n,i],o(y,e,t),n=y[0],i=y[1]),h=n.match(pl)||[];f=pl.exec(i);)_=f[0],g=i.substring(c,f.index),d?d=(d+1)%5:g.substr(-5)==="rgba("&&(d=1),_!==h[u++]&&(p=parseFloat(h[u-1])||0,l._pt={_next:l._pt,p:g||u===1?g:",",s:p,c:_.charAt(1)==="="?Ss(p,_)-p:parseFloat(_)-p,m:d&&d<4?Math.round:0},c=pl.lastIndex);return l.c=c<i.length?i.substring(c,i.length):"",l.fp=a,(jf.test(i)||m)&&(l.e=0),this._pt=l,l},Nu=function(e,t,n,i,s,o,a,l,c,u){Pt(i)&&(i=i(s||0,e,o));var f=e[t],h=n!=="get"?n:Pt(f)?c?e[t.indexOf("set")||!Pt(e["get"+t.substr(3)])?t:"get"+t.substr(3)](c):e[t]():f,d=Pt(f)?c?Wm:Ad:Ou,_;if(jt(i)&&(~i.indexOf("random(")&&(i=Eo(i)),i.charAt(1)==="="&&(_=Ss(h,i)+(on(h)||0),(_||_===0)&&(i=_))),!u||h!==i||vc)return!isNaN(h*i)&&i!==""?(_=new bn(this._pt,e,t,+h||0,i-(h||0),typeof f=="boolean"?Ym:Rd,0,d),c&&(_.fp=c),a&&_.modifier(a,this,e),this._pt=_):(!f&&!(t in e)&&Pu(t,i),zm.call(this,e,t,h,i,d,l||Hn.stringFilter,c))},km=function(e,t,n,i,s){if(Pt(e)&&(e=co(e,s,t,n,i)),!Mi(e)||e.style&&e.nodeType||ln(e)||Kf(e))return jt(e)?co(e,s,t,n,i):e;var o={},a;for(a in e)o[a]=co(e[a],s,t,n,i);return o},Td=function(e,t,n,i,s,o){var a,l,c,u;if(Nn[e]&&(a=new Nn[e]).init(s,a.rawVars?t[e]:km(t[e],i,s,o,n),n,i,o)!==!1&&(n._pt=l=new bn(n._pt,s,e,0,1,a.render,a,0,a.priority),n!==gs))for(c=n._ptLookup[n._targets.indexOf(s)],u=a._props.length;u--;)c[a._props[u]]=l;return a},ji,vc,Fu=function r(e,t,n){var i=e.vars,s=i.ease,o=i.startAt,a=i.immediateRender,l=i.lazy,c=i.onUpdate,u=i.runBackwards,f=i.yoyoEase,h=i.keyframes,d=i.autoRevert,_=e._dur,g=e._startAt,p=e._targets,m=e.parent,y=m&&m.data==="nested"?m.vars.targets:p,x=e._overwrite==="auto"&&!wu,M=e.timeline,R=i.easeReverse||f,w,E,D,O,v,T,N,z,W,K,G,X,V;if(M&&(!h||!s)&&(s="none"),e._ease=Ur(s,So.ease),e._rEase=R&&(Ur(R)||e._ease),e._from=!M&&!!i.runBackwards,e._from&&(e.ratio=1),!M||h&&!i.stagger){if(z=p[0]?Lr(p[0]).harness:0,X=z&&i[z.prop],w=Ga(i,Du),g&&(g._zTime<0&&g.progress(1),t<0&&u&&a&&!d?g.render(-1,!0):g.revert(u&&_?Ea:dm),g._lazy=0),o){if(ar(e._startAt=kt.set(p,Vn({data:"isStart",overwrite:!1,parent:m,immediateRender:!0,lazy:!g&&En(l),startAt:null,delay:0,onUpdate:c&&function(){return zn(e,"onUpdate")},stagger:0},o))),e._startAt._dp=0,e._startAt._sat=e,t<0&&(en||!a&&!d)&&e._startAt.revert(Ea),a&&_&&t<=0&&n<=0){t&&(e._zTime=t);return}}else if(u&&_&&!g){if(t&&(a=!1),D=Vn({overwrite:!1,data:"isFromStart",lazy:a&&!g&&En(l),immediateRender:a,stagger:0,parent:m},w),X&&(D[z.prop]=X),ar(e._startAt=kt.set(p,D)),e._startAt._dp=0,e._startAt._sat=e,t<0&&(en?e._startAt.revert(Ea):e._startAt.render(-1,!0)),e._zTime=t,!a)r(e._startAt,xt,xt);else if(!t)return}for(e._pt=e._ptCache=0,l=_&&En(l)||l&&!_,E=0;E<p.length;E++){if(v=p[E],N=v._gsap||Iu(p)[E]._gsap,e._ptLookup[E]=K={},fc[N.id]&&nr.length&&Ha(),G=y===p?E:y.indexOf(v),z&&(W=new z).init(v,X||w,e,G,y)!==!1&&(e._pt=O=new bn(e._pt,v,W.name,0,1,W.render,W,0,W.priority),W._props.forEach(function(re){K[re]=O}),W.priority&&(T=1)),!z||X)for(D in w)Nn[D]&&(W=Td(D,w,e,G,v,y))?W.priority&&(T=1):K[D]=O=Nu.call(e,v,D,"get",w[D],G,y,0,i.stringFilter);e._op&&e._op[E]&&e.kill(v,e._op[E]),x&&e._pt&&(ji=e,Rt.killTweensOf(v,K,e.globalTime(t)),V=!e.parent,ji=0),e._pt&&l&&(fc[N.id]=1)}T&&Pd(e),e._onInit&&e._onInit(e)}e._onUpdate=c,e._initted=(!e._op||e._pt)&&!V,h&&t<=0&&M.render(Zn,!0,!0)},Hm=function(e,t,n,i,s,o,a,l){var c=(e._pt&&e._ptCache||(e._ptCache={}))[t],u,f,h,d;if(!c)for(c=e._ptCache[t]=[],h=e._ptLookup,d=e._targets.length;d--;){if(u=h[d][t],u&&u.d&&u.d._pt)for(u=u.d._pt;u&&u.p!==t&&u.fp!==t;)u=u._next;if(!u)return vc=1,e.vars[t]="+=0",Fu(e,a),vc=0,l?Mo(t+" not eligible for reset. Try splitting into individual properties"):1;c.push(u)}for(d=c.length;d--;)f=c[d],u=f._pt||f,u.s=(i||i===0)&&!s?i:u.s+(i||0)+o*u.c,u.c=n-u.s,f.e&&(f.e=Ut(n)+on(f.e)),f.b&&(f.b=u.s+on(f.b))},Gm=function(e,t){var n=e[0]?Lr(e[0]).harness:0,i=n&&n.aliases,s,o,a,l;if(!i)return t;s=Ps({},t);for(o in i)if(o in s)for(l=i[o].split(","),a=l.length;a--;)s[l[a]]=s[o];return s},Vm=function(e,t,n,i){var s=t.ease||i||"power1.inOut",o,a;if(ln(t))a=n[e]||(n[e]=[]),t.forEach(function(l,c){return a.push({t:c/(t.length-1)*100,v:l,e:s})});else for(o in t)a=n[o]||(n[o]=[]),o==="ease"||a.push({t:parseFloat(e),v:t[o],e:s})},co=function(e,t,n,i,s){return Pt(e)?e.call(t,n,i,s):jt(e)&&~e.indexOf("random(")?Eo(e):e},bd=Lu+"repeat,repeatDelay,yoyo,repeatRefresh,yoyoEase,easeReverse,autoRevert",wd={};Tn(bd+",id,stagger,delay,duration,paused,scrollTrigger",function(r){return wd[r]=1});var kt=function(r){qf(e,r);function e(n,i,s,o){var a;typeof i=="number"&&(s.duration=i,i=s,s=null),a=r.call(this,o?i:ao(i))||this;var l=a.vars,c=l.duration,u=l.delay,f=l.immediateRender,h=l.stagger,d=l.overwrite,_=l.keyframes,g=l.defaults,p=l.scrollTrigger,m=i.parent||Rt,y=(ln(n)||Kf(n)?Oi(n[0]):"length"in i)?[n]:jn(n),x,M,R,w,E,D,O,v;if(a._targets=y.length?Iu(y):Mo("GSAP target "+n+" not found. https://gsap.com",!Hn.nullTargetWarn)||[],a._ptLookup=[],a._overwrite=d,_||h||ko(c)||ko(u)){i=a.vars;var T=i.easeReverse||i.yoyoEase;if(x=a.timeline=new yn({data:"nested",defaults:g||{},targets:m&&m.data==="nested"?m.vars.targets:y}),x.kill(),x.parent=x._dp=Ri(a),x._start=0,h||ko(c)||ko(u)){if(w=y.length,O=h&&fd(h),Mi(h))for(E in h)~bd.indexOf(E)&&(v||(v={}),v[E]=h[E]);for(M=0;M<w;M++)R=Ga(i,wd),R.stagger=0,T&&(R.easeReverse=T),v&&Ps(R,v),D=y[M],R.duration=+co(c,Ri(a),M,D,y),R.delay=(+co(u,Ri(a),M,D,y)||0)-a._delay,!h&&w===1&&R.delay&&(a._delay=u=R.delay,a._start+=u,R.delay=0),x.to(D,R,O?O(M,D,y):0),x._ease=lt.none;x.duration()?c=u=0:a.timeline=0}else if(_){ao(Vn(x.vars.defaults,{ease:"none"})),x._ease=Ur(_.ease||i.ease||"none");var N=0,z,W,K;if(ln(_))_.forEach(function(G){return x.to(y,G,">")}),x.duration();else{R={};for(E in _)E==="ease"||E==="easeEach"||Vm(E,_[E],R,_.easeEach);for(E in R)for(z=R[E].sort(function(G,X){return G.t-X.t}),N=0,M=0;M<z.length;M++)W=z[M],K={ease:W.e,duration:(W.t-(M?z[M-1].t:0))/100*c},K[E]=W.v,x.to(y,K,N),N+=K.duration;x.duration()<c&&x.to({},{duration:c-x.duration()})}}c||a.duration(c=x.duration())}else a.timeline=0;return d===!0&&!wu&&(ji=Ri(a),Rt.killTweensOf(y),ji=0),_i(m,Ri(a),s),i.reversed&&a.reverse(),i.paused&&a.paused(!0),(f||!c&&!_&&a._start===At(m._time)&&En(f)&&xm(Ri(a))&&m.data!=="nested")&&(a._tTime=-xt,a.render(Math.max(0,-u)||0)),p&&ld(Ri(a),p),a}var t=e.prototype;return t.render=function(i,s,o){var a=this._time,l=this._tDur,c=this._dur,u=i<0,f=i>l-xt&&!u?l:i<xt?0:i,h,d,_,g,p,m,y,x;if(!c)Mm(this,i,s,o);else if(f!==this._tTime||!i||o||!this._initted&&this._tTime||this._startAt&&this._zTime<0!==u||this._lazy){if(h=f,x=this.timeline,this._repeat){if(g=c+this._rDelay,this._repeat<-1&&u)return this.totalTime(g*100+i,s,o);if(h=At(f%g),f===l?(_=this._repeat,h=c):(p=At(f/g),_=~~p,_&&_===p?(h=c,_--):h>c&&(h=c)),m=this._yoyo&&_&1,m&&(h=c-h),p=Ds(this._tTime,g),h===a&&!o&&this._initted&&_===p)return this._tTime=f,this;_!==p&&this.vars.repeatRefresh&&!m&&!this._lock&&h!==g&&this._initted&&(this._lock=o=1,this.render(At(g*_),!0).invalidate()._lock=0)}if(!this._initted){if(cd(this,u?i:h,o,s,f))return this._tTime=0,this;if(a!==this._time&&!(o&&this.vars.repeatRefresh&&_!==p))return this;if(c!==this._dur)return this.render(i,s,o)}if(this._rEase){var M=h<a;if(M!==this._inv){var R=M?a:c-a;this._inv=M,this._from&&(this.ratio=1-this.ratio),this._invRatio=this.ratio,this._invTime=a,this._invRecip=R?(M?-1:1)/R:0,this._invScale=M?-this.ratio:1-this.ratio,this._invEase=M?this._rEase:this._ease}this.ratio=y=this._invRatio+this._invScale*this._invEase((h-this._invTime)*this._invRecip)}else this.ratio=y=this._ease(h/c);if(this._from&&(this.ratio=y=1-y),this._tTime=f,this._time=h,!this._act&&this._ts&&(this._act=1,this._lazy=0),!a&&f&&!s&&!p&&(zn(this,"onStart"),this._tTime!==f))return this;for(d=this._pt;d;)d.r(y,d.d),d=d._next;x&&x.render(i<0?i:x._dur*x._ease(h/this._dur),s,o)||this._startAt&&(this._zTime=i),this._onUpdate&&!s&&(u&&dc(this,i,s,o),zn(this,"onUpdate")),this._repeat&&_!==p&&this.vars.onRepeat&&!s&&this.parent&&zn(this,"onRepeat"),(f===this._tDur||!f)&&this._tTime===f&&(u&&!this._onUpdate&&dc(this,i,!0,!0),(i||!c)&&(f===this._tDur&&this._ts>0||!f&&this._ts<0)&&ar(this,1),!s&&!(u&&!a)&&(f||a||m)&&(zn(this,f===l?"onComplete":"onReverseComplete",!0),this._prom&&!(f<l&&this.timeScale()>0)&&this._prom()))}return this},t.targets=function(){return this._targets},t.invalidate=function(i){return(!i||!this.vars.runBackwards)&&(this._startAt=0),this._pt=this._op=this._onUpdate=this._lazy=this.ratio=0,this._ptLookup=[],this.timeline&&this.timeline.invalidate(i),r.prototype.invalidate.call(this,i)},t.resetTo=function(i,s,o,a,l){To||On.wake(),this._ts||this.play();var c=Math.min(this._dur,(this._dp._time-this._start)*this._ts),u;return this._initted||Fu(this,c),u=this._ease(c/this._dur),Hm(this,i,s,o,a,u,c,l)?this.resetTo(i,s,o,a,1):(sl(this,0),this.parent||od(this._dp,this,"_first","_last",this._dp._sort?"_start":0),this.render(0))},t.kill=function(i,s){if(s===void 0&&(s="all"),!i&&(!s||s==="all"))return this._lazy=this._pt=0,this.parent?Qs(this):this.scrollTrigger&&this.scrollTrigger.kill(!!en),this;if(this.timeline){var o=this.timeline.totalDuration();return this.timeline.killTweensOf(i,s,ji&&ji.vars.overwrite!==!0)._first||Qs(this),this.parent&&o!==this.timeline.totalDuration()&&Ls(this,this._dur*this.timeline._tDur/o,0,1),this}var a=this._targets,l=i?jn(i):a,c=this._ptLookup,u=this._pt,f,h,d,_,g,p,m;if((!s||s==="all")&&gm(a,l))return s==="all"&&(this._pt=0),Qs(this);for(f=this._op=this._op||[],s!=="all"&&(jt(s)&&(g={},Tn(s,function(y){return g[y]=1}),s=g),s=Gm(a,s)),m=a.length;m--;)if(~l.indexOf(a[m])){h=c[m],s==="all"?(f[m]=s,_=h,d={}):(d=f[m]=f[m]||{},_=s);for(g in _)p=h&&h[g],p&&((!("kill"in p.d)||p.d.kill(g)===!0)&&il(this,p,"_pt"),delete h[g]),d!=="all"&&(d[g]=1)}return this._initted&&!this._pt&&u&&Qs(this),this},e.to=function(i,s){return new e(i,s,arguments[2])},e.from=function(i,s){return lo(1,arguments)},e.delayedCall=function(i,s,o,a){return new e(s,0,{immediateRender:!1,lazy:!1,overwrite:!1,delay:i,onComplete:s,onReverseComplete:s,onCompleteParams:o,onReverseCompleteParams:o,callbackScope:a})},e.fromTo=function(i,s,o){return lo(2,arguments)},e.set=function(i,s){return s.duration=0,s.repeatDelay||(s.repeat=0),new e(i,s)},e.killTweensOf=function(i,s,o){return Rt.killTweensOf(i,s,o)},e}(bo);Vn(kt.prototype,{_targets:[],_lazy:0,_startAt:0,_op:0,_onInit:0});Tn("staggerTo,staggerFrom,staggerFromTo",function(r){kt[r]=function(){var e=new yn,t=mc.call(arguments,0);return t.splice(r==="staggerFromTo"?5:4,0,0),e[r].apply(e,t)}});var Ou=function(e,t,n){return e[t]=n},Ad=function(e,t,n){return e[t](n)},Wm=function(e,t,n,i){return e[t](i.fp,n)},Xm=function(e,t,n){return e.setAttribute(t,n)},Bu=function(e,t){return Pt(e[t])?Ad:Au(e[t])&&e.setAttribute?Xm:Ou},Rd=function(e,t){return t.set(t.t,t.p,Math.round((t.s+t.c*e)*1e6)/1e6,t)},Ym=function(e,t){return t.set(t.t,t.p,!!(t.s+t.c*e),t)},Cd=function(e,t){var n=t._pt,i="";if(!e&&t.b)i=t.b;else if(e===1&&t.e)i=t.e;else{for(;n;)i=n.p+(n.m?n.m(n.s+n.c*e):Math.round((n.s+n.c*e)*1e4)/1e4)+i,n=n._next;i+=t.c}t.set(t.t,t.p,i,t)},zu=function(e,t){for(var n=t._pt;n;)n.r(e,n.d),n=n._next},qm=function(e,t,n,i){for(var s=this._pt,o;s;)o=s._next,s.p===i&&s.modifier(e,t,n),s=o},$m=function(e){for(var t=this._pt,n,i;t;)i=t._next,t.p===e&&!t.op||t.op===e?il(this,t,"_pt"):t.dep||(n=1),t=i;return!n},Km=function(e,t,n,i){i.mSet(e,t,i.m.call(i.tween,n,i.mt),i)},Pd=function(e){for(var t=e._pt,n,i,s,o;t;){for(n=t._next,i=s;i&&i.pr>t.pr;)i=i._next;(t._prev=i?i._prev:o)?t._prev._next=t:s=t,(t._next=i)?i._prev=t:o=t,t=n}e._pt=s},bn=function(){function r(t,n,i,s,o,a,l,c,u){this.t=n,this.s=s,this.c=o,this.p=i,this.r=a||Rd,this.d=l||this,this.set=c||Ou,this.pr=u||0,this._next=t,t&&(t._prev=this)}var e=r.prototype;return e.modifier=function(n,i,s){this.mSet=this.mSet||this.set,this.set=Km,this.m=n,this.mt=s,this.tween=i},r}();Tn(Lu+"parent,duration,ease,delay,overwrite,runBackwards,startAt,yoyo,immediateRender,repeat,repeatDelay,data,paused,reversed,lazy,callbackScope,stringFilter,id,yoyoEase,stagger,inherit,repeatRefresh,keyframes,autoRevert,scrollTrigger,easeReverse",function(r){return Du[r]=1});Gn.TweenMax=Gn.TweenLite=kt;Gn.TimelineLite=Gn.TimelineMax=yn;Rt=new yn({sortChildren:!1,defaults:So,autoRemoveChildren:!0,id:"root",smoothChildTiming:!0});Hn.stringFilter=Md;var Nr=[],ba={},Zm=[],_h=0,jm=0,xl=function(e){return(ba[e]||Zm).map(function(t){return t()})},xc=function(){var e=Date.now(),t=[];e-_h>2&&(xl("matchMediaInit"),Nr.forEach(function(n){var i=n.queries,s=n.conditions,o,a,l,c;for(a in i)o=di.matchMedia(i[a]).matches,o&&(l=1),o!==s[a]&&(s[a]=o,c=1);c&&(n.revert(),l&&t.push(n))}),xl("matchMediaRevert"),t.forEach(function(n){return n.onMatch(n,function(i){return n.add(null,i)})}),_h=e,xl("matchMedia"))},Dd=function(){function r(t,n){this.selector=n&&_c(n),this.data=[],this._r=[],this.isReverted=!1,this.id=jm++,t&&this.add(t)}var e=r.prototype;return e.add=function(n,i,s){Pt(n)&&(s=i,i=n,n=Pt);var o=this,a=function(){var c=wt,u=o.selector,f;return c&&c!==o&&c.data.push(o),s&&(o.selector=_c(s)),wt=o,f=i.apply(o,arguments),Pt(f)&&o._r.push(f),wt=c,o.selector=u,o.isReverted=!1,f};return o.last=a,n===Pt?a(o,function(l){return o.add(null,l)}):n?o[n]=a:a},e.ignore=function(n){var i=wt;wt=null,n(this),wt=i},e.getTweens=function(){var n=[];return this.data.forEach(function(i){return i instanceof r?n.push.apply(n,i.getTweens()):i instanceof kt&&!(i.parent&&i.parent.data==="nested")&&n.push(i)}),n},e.clear=function(){this._r.length=this.data.length=0},e.kill=function(n,i){var s=this;if(n?function(){for(var a=s.getTweens(),l=s.data.length,c;l--;)c=s.data[l],c.data==="isFlip"&&(c.revert(),c.getChildren(!0,!0,!1).forEach(function(u){return a.splice(a.indexOf(u),1)}));for(a.map(function(u){return{g:u._dur||u._delay||u._sat&&!u._sat.vars.immediateRender?u.globalTime(0):-1/0,t:u}}).sort(function(u,f){return f.g-u.g||-1/0}).forEach(function(u){return u.t.revert(n)}),l=s.data.length;l--;)c=s.data[l],c instanceof yn?c.data!=="nested"&&(c.scrollTrigger&&c.scrollTrigger.revert(),c.kill()):!(c instanceof kt)&&c.revert&&c.revert(n);s._r.forEach(function(u){return u(n,s)}),s.isReverted=!0}():this.data.forEach(function(a){return a.kill&&a.kill()}),this.clear(),i)for(var o=Nr.length;o--;)Nr[o].id===this.id&&Nr.splice(o,1)},e.revert=function(n){this.kill(n||{})},r}(),Jm=function(){function r(t){this.contexts=[],this.scope=t,wt&&wt.data.push(this)}var e=r.prototype;return e.add=function(n,i,s){Mi(n)||(n={matches:n});var o=new Dd(0,s||this.scope),a=o.conditions={},l,c,u;wt&&!o.selector&&(o.selector=wt.selector),this.contexts.push(o),i=o.add("onMatch",i),o.queries=n;for(c in n)c==="all"?u=1:(l=di.matchMedia(n[c]),l&&(Nr.indexOf(o)<0&&Nr.push(o),(a[c]=l.matches)&&(u=1),l.addListener?l.addListener(xc):l.addEventListener("change",xc)));return u&&i(o,function(f){return o.add(null,f)}),this},e.revert=function(n){this.kill(n||{})},e.kill=function(n){this.contexts.forEach(function(i){return i.kill(n,!0)})},r}(),Wa={registerPlugin:function(){for(var e=arguments.length,t=new Array(e),n=0;n<e;n++)t[n]=arguments[n];t.forEach(function(i){return vd(i)})},timeline:function(e){return new yn(e)},getTweensOf:function(e,t){return Rt.getTweensOf(e,t)},getProperty:function(e,t,n,i){jt(e)&&(e=jn(e)[0]);var s=Lr(e||{}).get,o=n?sd:rd;return n==="native"&&(n=""),e&&(t?o((Nn[t]&&Nn[t].get||s)(e,t,n,i)):function(a,l,c){return o((Nn[a]&&Nn[a].get||s)(e,a,l,c))})},quickSetter:function(e,t,n){if(e=jn(e),e.length>1){var i=e.map(function(u){return Rn.quickSetter(u,t,n)}),s=i.length;return function(u){for(var f=s;f--;)i[f](u)}}e=e[0]||{};var o=Nn[t],a=Lr(e),l=a.harness&&(a.harness.aliases||{})[t]||t,c=o?function(u){var f=new o;gs._pt=0,f.init(e,n?u+n:u,gs,0,[e]),f.render(1,f),gs._pt&&zu(1,gs)}:a.set(e,l);return o?c:function(u){return c(e,l,n?u+n:u,a,1)}},quickTo:function(e,t,n){var i,s=Rn.to(e,Vn((i={},i[t]="+=0.1",i.paused=!0,i.stagger=0,i),n||{})),o=function(l,c,u){return s.resetTo(t,l,c,u)};return o.tween=s,o},isTweening:function(e){return Rt.getTweensOf(e,!0).length>0},defaults:function(e){return e&&e.ease&&(e.ease=Ur(e.ease,So.ease)),hh(So,e||{})},config:function(e){return hh(Hn,e||{})},registerEffect:function(e){var t=e.name,n=e.effect,i=e.plugins,s=e.defaults,o=e.extendTimeline;(i||"").split(",").forEach(function(a){return a&&!Nn[a]&&!Gn[a]&&Mo(t+" effect requires "+a+" plugin.")}),ml[t]=function(a,l,c){return n(jn(a),Vn(l||{},s),c)},o&&(yn.prototype[t]=function(a,l,c){return this.add(ml[t](a,Mi(l)?l:(c=l)&&{},this),c)})},registerEase:function(e,t){lt[e]=Ur(t)},parseEase:function(e,t){return arguments.length?Ur(e,t):lt},getById:function(e){return Rt.getById(e)},exportRoot:function(e,t){e===void 0&&(e={});var n=new yn(e),i,s;for(n.smoothChildTiming=En(e.smoothChildTiming),Rt.remove(n),n._dp=0,n._time=n._tTime=Rt._time,i=Rt._first;i;)s=i._next,(t||!(!i._dur&&i instanceof kt&&i.vars.onComplete===i._targets[0]))&&_i(n,i,i._start-i._delay),i=s;return _i(Rt,n,0),n},context:function(e,t){return e?new Dd(e,t):wt},matchMedia:function(e){return new Jm(e)},matchMediaRefresh:function(){return Nr.forEach(function(e){var t=e.conditions,n,i;for(i in t)t[i]&&(t[i]=!1,n=1);n&&e.revert()})||xc()},addEventListener:function(e,t){var n=ba[e]||(ba[e]=[]);~n.indexOf(t)||n.push(t)},removeEventListener:function(e,t){var n=ba[e],i=n&&n.indexOf(t);i>=0&&n.splice(i,1)},utils:{wrap:Cm,wrapYoyo:Pm,distribute:fd,random:pd,snap:dd,normalize:Rm,getUnit:on,clamp:Tm,splitColor:xd,toArray:jn,selector:_c,mapRange:_d,pipe:wm,unitize:Am,interpolate:Dm,shuffle:hd},install:Qf,effects:ml,ticker:On,updateRoot:yn.updateRoot,plugins:Nn,globalTimeline:Rt,core:{PropTween:bn,globals:ed,Tween:kt,Timeline:yn,Animation:bo,getCache:Lr,_removeLinkedListItem:il,reverting:function(){return en},context:function(e){return e&&wt&&(wt.data.push(e),e._ctx=wt),wt},suppressOverwrites:function(e){return wu=e}}};Tn("to,from,fromTo,delayedCall,set,killTweensOf",function(r){return Wa[r]=kt[r]});On.add(yn.updateRoot);gs=Wa.to({},{duration:0});var Qm=function(e,t){for(var n=e._pt;n&&n.p!==t&&n.op!==t&&n.fp!==t;)n=n._next;return n},e_=function(e,t){var n=e._targets,i,s,o;for(i in t)for(s=n.length;s--;)o=e._ptLookup[s][i],o&&(o=o.d)&&(o._pt&&(o=Qm(o,i)),o&&o.modifier&&o.modifier(t[i],e,n[s],i))},Sl=function(e,t){return{name:e,headless:1,rawVars:1,init:function(i,s,o){o._onInit=function(a){var l,c;if(jt(s)&&(l={},Tn(s,function(u){return l[u]=1}),s=l),t){l={};for(c in s)l[c]=t(s[c]);s=l}e_(a,s)}}}},Rn=Wa.registerPlugin({name:"attr",init:function(e,t,n,i,s){var o,a,l;this.tween=n;for(o in t)l=e.getAttribute(o)||"",a=this.add(e,"setAttribute",(l||0)+"",t[o],i,s,0,0,o),a.op=o,a.b=l,this._props.push(o)},render:function(e,t){for(var n=t._pt;n;)en?n.set(n.t,n.p,n.b,n):n.r(e,n.d),n=n._next}},{name:"endArray",headless:1,init:function(e,t){for(var n=t.length;n--;)this.add(e,n,e[n]||0,t[n],0,0,0,0,0,1)}},Sl("roundProps",gc),Sl("modifiers"),Sl("snap",dd))||Wa;kt.version=yn.version=Rn.version="3.15.0";Jf=1;Ru()&&Is();lt.Power0;lt.Power1;lt.Power2;lt.Power3;lt.Power4;lt.Linear;lt.Quad;lt.Cubic;lt.Quart;lt.Quint;lt.Strong;lt.Elastic;lt.Back;lt.SteppedEase;lt.Bounce;lt.Sine;lt.Expo;lt.Circ;/*!
 * CSSPlugin 3.15.0
 * https://gsap.com
 *
 * Copyright 2008-2026, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/var gh,Ji,Ms,ku,Cr,vh,Hu,t_=function(){return typeof window<"u"},Bi={},yr=180/Math.PI,ys=Math.PI/180,$r=Math.atan2,xh=1e8,Gu=/([A-Z])/g,n_=/(left|right|width|margin|padding|x)/i,i_=/[\s,\(]\S/,gi={autoAlpha:"opacity,visibility",scale:"scaleX,scaleY",alpha:"opacity"},Sc=function(e,t){return t.set(t.t,t.p,Math.round((t.s+t.c*e)*1e4)/1e4+t.u,t)},r_=function(e,t){return t.set(t.t,t.p,e===1?t.e:Math.round((t.s+t.c*e)*1e4)/1e4+t.u,t)},s_=function(e,t){return t.set(t.t,t.p,e?Math.round((t.s+t.c*e)*1e4)/1e4+t.u:t.b,t)},o_=function(e,t){return t.set(t.t,t.p,e===1?t.e:e?Math.round((t.s+t.c*e)*1e4)/1e4+t.u:t.b,t)},a_=function(e,t){var n=t.s+t.c*e;t.set(t.t,t.p,~~(n+(n<0?-.5:.5))+t.u,t)},Ld=function(e,t){return t.set(t.t,t.p,e?t.e:t.b,t)},Id=function(e,t){return t.set(t.t,t.p,e!==1?t.b:t.e,t)},l_=function(e,t,n){return e.style[t]=n},c_=function(e,t,n){return e.style.setProperty(t,n)},u_=function(e,t,n){return e._gsap[t]=n},h_=function(e,t,n){return e._gsap.scaleX=e._gsap.scaleY=n},f_=function(e,t,n,i,s){var o=e._gsap;o.scaleX=o.scaleY=n,o.renderTransform(s,o)},d_=function(e,t,n,i,s){var o=e._gsap;o[t]=n,o.renderTransform(s,o)},Ct="transform",wn=Ct+"Origin",p_=function r(e,t){var n=this,i=this.target,s=i.style,o=i._gsap;if(e in Bi&&s){if(this.tfm=this.tfm||{},e!=="transform")e=gi[e]||e,~e.indexOf(",")?e.split(",").forEach(function(a){return n.tfm[a]=Ci(i,a)}):this.tfm[e]=o.x?o[e]:Ci(i,e),e===wn&&(this.tfm.zOrigin=o.zOrigin);else return gi.transform.split(",").forEach(function(a){return r.call(n,a,t)});if(this.props.indexOf(Ct)>=0)return;o.svg&&(this.svgo=i.getAttribute("data-svg-origin"),this.props.push(wn,t,"")),e=Ct}(s||t)&&this.props.push(e,t,s[e])},Ud=function(e){e.translate&&(e.removeProperty("translate"),e.removeProperty("scale"),e.removeProperty("rotate"))},m_=function(){var e=this.props,t=this.target,n=t.style,i=t._gsap,s,o;for(s=0;s<e.length;s+=3)e[s+1]?e[s+1]===2?t[e[s]](e[s+2]):t[e[s]]=e[s+2]:e[s+2]?n[e[s]]=e[s+2]:n.removeProperty(e[s].substr(0,2)==="--"?e[s]:e[s].replace(Gu,"-$1").toLowerCase());if(this.tfm){for(o in this.tfm)i[o]=this.tfm[o];i.svg&&(i.renderTransform(),t.setAttribute("data-svg-origin",this.svgo||"")),s=Hu(),(!s||!s.isStart)&&!n[Ct]&&(Ud(n),i.zOrigin&&n[wn]&&(n[wn]+=" "+i.zOrigin+"px",i.zOrigin=0,i.renderTransform()),i.uncache=1)}},Nd=function(e,t){var n={target:e,props:[],revert:m_,save:p_};return e._gsap||Rn.core.getCache(e),t&&e.style&&e.nodeType&&t.split(",").forEach(function(i){return n.save(i)}),n},Fd,Mc=function(e,t){var n=Ji.createElementNS?Ji.createElementNS((t||"http://www.w3.org/1999/xhtml").replace(/^https/,"http"),e):Ji.createElement(e);return n&&n.style?n:Ji.createElement(e)},kn=function r(e,t,n){var i=getComputedStyle(e);return i[t]||i.getPropertyValue(t.replace(Gu,"-$1").toLowerCase())||i.getPropertyValue(t)||!n&&r(e,Us(t)||t,1)||""},Sh="O,Moz,ms,Ms,Webkit".split(","),Us=function(e,t,n){var i=t||Cr,s=i.style,o=5;if(e in s&&!n)return e;for(e=e.charAt(0).toUpperCase()+e.substr(1);o--&&!(Sh[o]+e in s););return o<0?null:(o===3?"ms":o>=0?Sh[o]:"")+e},yc=function(){t_()&&window.document&&(gh=window,Ji=gh.document,Ms=Ji.documentElement,Cr=Mc("div")||{style:{}},Mc("div"),Ct=Us(Ct),wn=Ct+"Origin",Cr.style.cssText="border-width:0;line-height:0;position:absolute;padding:0",Fd=!!Us("perspective"),Hu=Rn.core.reverting,ku=1)},Mh=function(e){var t=e.ownerSVGElement,n=Mc("svg",t&&t.getAttribute("xmlns")||"http://www.w3.org/2000/svg"),i=e.cloneNode(!0),s;i.style.display="block",n.appendChild(i),Ms.appendChild(n);try{s=i.getBBox()}catch{}return n.removeChild(i),Ms.removeChild(n),s},yh=function(e,t){for(var n=t.length;n--;)if(e.hasAttribute(t[n]))return e.getAttribute(t[n])},Od=function(e){var t,n;try{t=e.getBBox()}catch{t=Mh(e),n=1}return t&&(t.width||t.height)||n||(t=Mh(e)),t&&!t.width&&!t.x&&!t.y?{x:+yh(e,["x","cx","x1"])||0,y:+yh(e,["y","cy","y1"])||0,width:0,height:0}:t},Bd=function(e){return!!(e.getCTM&&(!e.parentNode||e.ownerSVGElement)&&Od(e))},lr=function(e,t){if(t){var n=e.style,i;t in Bi&&t!==wn&&(t=Ct),n.removeProperty?(i=t.substr(0,2),(i==="ms"||t.substr(0,6)==="webkit")&&(t="-"+t),n.removeProperty(i==="--"?t:t.replace(Gu,"-$1").toLowerCase())):n.removeAttribute(t)}},Qi=function(e,t,n,i,s,o){var a=new bn(e._pt,t,n,0,1,o?Id:Ld);return e._pt=a,a.b=i,a.e=s,e._props.push(n),a},Eh={deg:1,rad:1,turn:1},__={grid:1,flex:1},cr=function r(e,t,n,i){var s=parseFloat(n)||0,o=(n+"").trim().substr((s+"").length)||"px",a=Cr.style,l=n_.test(t),c=e.tagName.toLowerCase()==="svg",u=(c?"client":"offset")+(l?"Width":"Height"),f=100,h=i==="px",d=i==="%",_,g,p,m;if(i===o||!s||Eh[i]||Eh[o])return s;if(o!=="px"&&!h&&(s=r(e,t,n,"px")),m=e.getCTM&&Bd(e),(d||o==="%")&&(Bi[t]||~t.indexOf("adius")))return _=m?e.getBBox()[l?"width":"height"]:e[u],Ut(d?s/_*f:s/100*_);if(a[l?"width":"height"]=f+(h?o:i),g=i!=="rem"&&~t.indexOf("adius")||i==="em"&&e.appendChild&&!c?e:e.parentNode,m&&(g=(e.ownerSVGElement||{}).parentNode),(!g||g===Ji||!g.appendChild)&&(g=Ji.body),p=g._gsap,p&&d&&p.width&&l&&p.time===On.time&&!p.uncache)return Ut(s/p.width*f);if(d&&(t==="height"||t==="width")){var y=e.style[t];e.style[t]=f+i,_=e[u],y?e.style[t]=y:lr(e,t)}else(d||o==="%")&&!__[kn(g,"display")]&&(a.position=kn(e,"position")),g===e&&(a.position="static"),g.appendChild(Cr),_=Cr[u],g.removeChild(Cr),a.position="absolute";return l&&d&&(p=Lr(g),p.time=On.time,p.width=g[u]),Ut(h?_*s/f:_&&s?f/_*s:0)},Ci=function(e,t,n,i){var s;return ku||yc(),t in gi&&t!=="transform"&&(t=gi[t],~t.indexOf(",")&&(t=t.split(",")[0])),Bi[t]&&t!=="transform"?(s=Ao(e,i),s=t!=="transformOrigin"?s[t]:s.svg?s.origin:Ya(kn(e,wn))+" "+s.zOrigin+"px"):(s=e.style[t],(!s||s==="auto"||i||~(s+"").indexOf("calc("))&&(s=Xa[t]&&Xa[t](e,t,n)||kn(e,t)||nd(e,t)||(t==="opacity"?1:0))),n&&!~(s+"").trim().indexOf(" ")?cr(e,t,s,n)+n:s},g_=function(e,t,n,i){if(!n||n==="none"){var s=Us(t,e,1),o=s&&kn(e,s,1);o&&o!==n?(t=s,n=o):t==="borderColor"&&(n=kn(e,"borderTopColor"))}var a=new bn(this._pt,e.style,t,0,1,Cd),l=0,c=0,u,f,h,d,_,g,p,m,y,x,M,R;if(a.b=n,a.e=i,n+="",i+="",i.substring(0,6)==="var(--"&&(i=kn(e,i.substring(4,i.indexOf(")")))),i==="auto"&&(g=e.style[t],e.style[t]=i,i=kn(e,t)||i,g?e.style[t]=g:lr(e,t)),u=[n,i],Md(u),n=u[0],i=u[1],h=n.match(_s)||[],R=i.match(_s)||[],R.length){for(;f=_s.exec(i);)p=f[0],y=i.substring(l,f.index),_?_=(_+1)%5:(y.substr(-5)==="rgba("||y.substr(-5)==="hsla(")&&(_=1),p!==(g=h[c++]||"")&&(d=parseFloat(g)||0,M=g.substr((d+"").length),p.charAt(1)==="="&&(p=Ss(d,p)+M),m=parseFloat(p),x=p.substr((m+"").length),l=_s.lastIndex-x.length,x||(x=x||Hn.units[t]||M,l===i.length&&(i+=x,a.e+=x)),M!==x&&(d=cr(e,t,g,x)||0),a._pt={_next:a._pt,p:y||c===1?y:",",s:d,c:m-d,m:_&&_<4||t==="zIndex"?Math.round:0});a.c=l<i.length?i.substring(l,i.length):""}else a.r=t==="display"&&i==="none"?Id:Ld;return jf.test(i)&&(a.e=0),this._pt=a,a},Th={top:"0%",bottom:"100%",left:"0%",right:"100%",center:"50%"},v_=function(e){var t=e.split(" "),n=t[0],i=t[1]||"50%";return(n==="top"||n==="bottom"||i==="left"||i==="right")&&(e=n,n=i,i=e),t[0]=Th[n]||n,t[1]=Th[i]||i,t.join(" ")},x_=function(e,t){if(t.tween&&t.tween._time===t.tween._dur){var n=t.t,i=n.style,s=t.u,o=n._gsap,a,l,c;if(s==="all"||s===!0)i.cssText="",l=1;else for(s=s.split(","),c=s.length;--c>-1;)a=s[c],Bi[a]&&(l=1,a=a==="transformOrigin"?wn:Ct),lr(n,a);l&&(lr(n,Ct),o&&(o.svg&&n.removeAttribute("transform"),i.scale=i.rotate=i.translate="none",Ao(n,1),o.uncache=1,Ud(i)))}},Xa={clearProps:function(e,t,n,i,s){if(s.data!=="isFromStart"){var o=e._pt=new bn(e._pt,t,n,0,0,x_);return o.u=i,o.pr=-10,o.tween=s,e._props.push(n),1}}},wo=[1,0,0,1,0,0],zd={},kd=function(e){return e==="matrix(1, 0, 0, 1, 0, 0)"||e==="none"||!e},bh=function(e){var t=kn(e,Ct);return kd(t)?wo:t.substr(7).match(Zf).map(Ut)},Vu=function(e,t){var n=e._gsap||Lr(e),i=e.style,s=bh(e),o,a,l,c;return n.svg&&e.getAttribute("transform")?(l=e.transform.baseVal.consolidate().matrix,s=[l.a,l.b,l.c,l.d,l.e,l.f],s.join(",")==="1,0,0,1,0,0"?wo:s):(s===wo&&!e.offsetParent&&e!==Ms&&!n.svg&&(l=i.display,i.display="block",o=e.parentNode,(!o||!e.offsetParent&&!e.getBoundingClientRect().width)&&(c=1,a=e.nextElementSibling,Ms.appendChild(e)),s=bh(e),l?i.display=l:lr(e,"display"),c&&(a?o.insertBefore(e,a):o?o.appendChild(e):Ms.removeChild(e))),t&&s.length>6?[s[0],s[1],s[4],s[5],s[12],s[13]]:s)},Ec=function(e,t,n,i,s,o){var a=e._gsap,l=s||Vu(e,!0),c=a.xOrigin||0,u=a.yOrigin||0,f=a.xOffset||0,h=a.yOffset||0,d=l[0],_=l[1],g=l[2],p=l[3],m=l[4],y=l[5],x=t.split(" "),M=parseFloat(x[0])||0,R=parseFloat(x[1])||0,w,E,D,O;n?l!==wo&&(E=d*p-_*g)&&(D=M*(p/E)+R*(-g/E)+(g*y-p*m)/E,O=M*(-_/E)+R*(d/E)-(d*y-_*m)/E,M=D,R=O):(w=Od(e),M=w.x+(~x[0].indexOf("%")?M/100*w.width:M),R=w.y+(~(x[1]||x[0]).indexOf("%")?R/100*w.height:R)),i||i!==!1&&a.smooth?(m=M-c,y=R-u,a.xOffset=f+(m*d+y*g)-m,a.yOffset=h+(m*_+y*p)-y):a.xOffset=a.yOffset=0,a.xOrigin=M,a.yOrigin=R,a.smooth=!!i,a.origin=t,a.originIsAbsolute=!!n,e.style[wn]="0px 0px",o&&(Qi(o,a,"xOrigin",c,M),Qi(o,a,"yOrigin",u,R),Qi(o,a,"xOffset",f,a.xOffset),Qi(o,a,"yOffset",h,a.yOffset)),e.setAttribute("data-svg-origin",M+" "+R)},Ao=function(e,t){var n=e._gsap||new Ed(e);if("x"in n&&!t&&!n.uncache)return n;var i=e.style,s=n.scaleX<0,o="px",a="deg",l=getComputedStyle(e),c=kn(e,wn)||"0",u,f,h,d,_,g,p,m,y,x,M,R,w,E,D,O,v,T,N,z,W,K,G,X,V,re,C,ae,Be,We,q,Q;return u=f=h=g=p=m=y=x=M=0,d=_=1,n.svg=!!(e.getCTM&&Bd(e)),l.translate&&((l.translate!=="none"||l.scale!=="none"||l.rotate!=="none")&&(i[Ct]=(l.translate!=="none"?"translate3d("+(l.translate+" 0 0").split(" ").slice(0,3).join(", ")+") ":"")+(l.rotate!=="none"?"rotate("+l.rotate+") ":"")+(l.scale!=="none"?"scale("+l.scale.split(" ").join(",")+") ":"")+(l[Ct]!=="none"?l[Ct]:"")),i.scale=i.rotate=i.translate="none"),E=Vu(e,n.svg),n.svg&&(n.uncache?(V=e.getBBox(),c=n.xOrigin-V.x+"px "+(n.yOrigin-V.y)+"px",X=""):X=!t&&e.getAttribute("data-svg-origin"),Ec(e,X||c,!!X||n.originIsAbsolute,n.smooth!==!1,E)),R=n.xOrigin||0,w=n.yOrigin||0,E!==wo&&(T=E[0],N=E[1],z=E[2],W=E[3],u=K=E[4],f=G=E[5],E.length===6?(d=Math.sqrt(T*T+N*N),_=Math.sqrt(W*W+z*z),g=T||N?$r(N,T)*yr:0,y=z||W?$r(z,W)*yr+g:0,y&&(_*=Math.abs(Math.cos(y*ys))),n.svg&&(u-=R-(R*T+w*z),f-=w-(R*N+w*W))):(Q=E[6],We=E[7],C=E[8],ae=E[9],Be=E[10],q=E[11],u=E[12],f=E[13],h=E[14],D=$r(Q,Be),p=D*yr,D&&(O=Math.cos(-D),v=Math.sin(-D),X=K*O+C*v,V=G*O+ae*v,re=Q*O+Be*v,C=K*-v+C*O,ae=G*-v+ae*O,Be=Q*-v+Be*O,q=We*-v+q*O,K=X,G=V,Q=re),D=$r(-z,Be),m=D*yr,D&&(O=Math.cos(-D),v=Math.sin(-D),X=T*O-C*v,V=N*O-ae*v,re=z*O-Be*v,q=W*v+q*O,T=X,N=V,z=re),D=$r(N,T),g=D*yr,D&&(O=Math.cos(D),v=Math.sin(D),X=T*O+N*v,V=K*O+G*v,N=N*O-T*v,G=G*O-K*v,T=X,K=V),p&&Math.abs(p)+Math.abs(g)>359.9&&(p=g=0,m=180-m),d=Ut(Math.sqrt(T*T+N*N+z*z)),_=Ut(Math.sqrt(G*G+Q*Q)),D=$r(K,G),y=Math.abs(D)>2e-4?D*yr:0,M=q?1/(q<0?-q:q):0),n.svg&&(X=e.getAttribute("transform"),n.forceCSS=e.setAttribute("transform","")||!kd(kn(e,Ct)),X&&e.setAttribute("transform",X))),Math.abs(y)>90&&Math.abs(y)<270&&(s?(d*=-1,y+=g<=0?180:-180,g+=g<=0?180:-180):(_*=-1,y+=y<=0?180:-180)),t=t||n.uncache,n.x=u-((n.xPercent=u&&(!t&&n.xPercent||(Math.round(e.offsetWidth/2)===Math.round(-u)?-50:0)))?e.offsetWidth*n.xPercent/100:0)+o,n.y=f-((n.yPercent=f&&(!t&&n.yPercent||(Math.round(e.offsetHeight/2)===Math.round(-f)?-50:0)))?e.offsetHeight*n.yPercent/100:0)+o,n.z=h+o,n.scaleX=Ut(d),n.scaleY=Ut(_),n.rotation=Ut(g)+a,n.rotationX=Ut(p)+a,n.rotationY=Ut(m)+a,n.skewX=y+a,n.skewY=x+a,n.transformPerspective=M+o,(n.zOrigin=parseFloat(c.split(" ")[2])||!t&&n.zOrigin||0)&&(i[wn]=Ya(c)),n.xOffset=n.yOffset=0,n.force3D=Hn.force3D,n.renderTransform=n.svg?M_:Fd?Hd:S_,n.uncache=0,n},Ya=function(e){return(e=e.split(" "))[0]+" "+e[1]},Ml=function(e,t,n){var i=on(t);return Ut(parseFloat(t)+parseFloat(cr(e,"x",n+"px",i)))+i},S_=function(e,t){t.z="0px",t.rotationY=t.rotationX="0deg",t.force3D=0,Hd(e,t)},pr="0deg",Ws="0px",mr=") ",Hd=function(e,t){var n=t||this,i=n.xPercent,s=n.yPercent,o=n.x,a=n.y,l=n.z,c=n.rotation,u=n.rotationY,f=n.rotationX,h=n.skewX,d=n.skewY,_=n.scaleX,g=n.scaleY,p=n.transformPerspective,m=n.force3D,y=n.target,x=n.zOrigin,M="",R=m==="auto"&&e&&e!==1||m===!0;if(x&&(f!==pr||u!==pr)){var w=parseFloat(u)*ys,E=Math.sin(w),D=Math.cos(w),O;w=parseFloat(f)*ys,O=Math.cos(w),o=Ml(y,o,E*O*-x),a=Ml(y,a,-Math.sin(w)*-x),l=Ml(y,l,D*O*-x+x)}p!==Ws&&(M+="perspective("+p+mr),(i||s)&&(M+="translate("+i+"%, "+s+"%) "),(R||o!==Ws||a!==Ws||l!==Ws)&&(M+=l!==Ws||R?"translate3d("+o+", "+a+", "+l+") ":"translate("+o+", "+a+mr),c!==pr&&(M+="rotate("+c+mr),u!==pr&&(M+="rotateY("+u+mr),f!==pr&&(M+="rotateX("+f+mr),(h!==pr||d!==pr)&&(M+="skew("+h+", "+d+mr),(_!==1||g!==1)&&(M+="scale("+_+", "+g+mr),y.style[Ct]=M||"translate(0, 0)"},M_=function(e,t){var n=t||this,i=n.xPercent,s=n.yPercent,o=n.x,a=n.y,l=n.rotation,c=n.skewX,u=n.skewY,f=n.scaleX,h=n.scaleY,d=n.target,_=n.xOrigin,g=n.yOrigin,p=n.xOffset,m=n.yOffset,y=n.forceCSS,x=parseFloat(o),M=parseFloat(a),R,w,E,D,O;l=parseFloat(l),c=parseFloat(c),u=parseFloat(u),u&&(u=parseFloat(u),c+=u,l+=u),l||c?(l*=ys,c*=ys,R=Math.cos(l)*f,w=Math.sin(l)*f,E=Math.sin(l-c)*-h,D=Math.cos(l-c)*h,c&&(u*=ys,O=Math.tan(c-u),O=Math.sqrt(1+O*O),E*=O,D*=O,u&&(O=Math.tan(u),O=Math.sqrt(1+O*O),R*=O,w*=O)),R=Ut(R),w=Ut(w),E=Ut(E),D=Ut(D)):(R=f,D=h,w=E=0),(x&&!~(o+"").indexOf("px")||M&&!~(a+"").indexOf("px"))&&(x=cr(d,"x",o,"px"),M=cr(d,"y",a,"px")),(_||g||p||m)&&(x=Ut(x+_-(_*R+g*E)+p),M=Ut(M+g-(_*w+g*D)+m)),(i||s)&&(O=d.getBBox(),x=Ut(x+i/100*O.width),M=Ut(M+s/100*O.height)),O="matrix("+R+","+w+","+E+","+D+","+x+","+M+")",d.setAttribute("transform",O),y&&(d.style[Ct]=O)},y_=function(e,t,n,i,s){var o=360,a=jt(s),l=parseFloat(s)*(a&&~s.indexOf("rad")?yr:1),c=l-i,u=i+c+"deg",f,h;return a&&(f=s.split("_")[1],f==="short"&&(c%=o,c!==c%(o/2)&&(c+=c<0?o:-o)),f==="cw"&&c<0?c=(c+o*xh)%o-~~(c/o)*o:f==="ccw"&&c>0&&(c=(c-o*xh)%o-~~(c/o)*o)),e._pt=h=new bn(e._pt,t,n,i,c,r_),h.e=u,h.u="deg",e._props.push(n),h},wh=function(e,t){for(var n in t)e[n]=t[n];return e},E_=function(e,t,n){var i=wh({},n._gsap),s="perspective,force3D,transformOrigin,svgOrigin",o=n.style,a,l,c,u,f,h,d,_;i.svg?(c=n.getAttribute("transform"),n.setAttribute("transform",""),o[Ct]=t,a=Ao(n,1),lr(n,Ct),n.setAttribute("transform",c)):(c=getComputedStyle(n)[Ct],o[Ct]=t,a=Ao(n,1),o[Ct]=c);for(l in Bi)c=i[l],u=a[l],c!==u&&s.indexOf(l)<0&&(d=on(c),_=on(u),f=d!==_?cr(n,l,c,_):parseFloat(c),h=parseFloat(u),e._pt=new bn(e._pt,a,l,f,h-f,Sc),e._pt.u=_||0,e._props.push(l));wh(a,i)};Tn("padding,margin,Width,Radius",function(r,e){var t="Top",n="Right",i="Bottom",s="Left",o=(e<3?[t,n,i,s]:[t+s,t+n,i+n,i+s]).map(function(a){return e<2?r+a:"border"+a+r});Xa[e>1?"border"+r:r]=function(a,l,c,u,f){var h,d;if(arguments.length<4)return h=o.map(function(_){return Ci(a,_,c)}),d=h.join(" "),d.split(h[0]).length===5?h[0]:d;h=(u+"").split(" "),d={},o.forEach(function(_,g){return d[_]=h[g]=h[g]||h[(g-1)/2|0]}),a.init(l,d,f)}});var Gd={name:"css",register:yc,targetTest:function(e){return e.style&&e.nodeType},init:function(e,t,n,i,s){var o=this._props,a=e.style,l=n.vars.startAt,c,u,f,h,d,_,g,p,m,y,x,M,R,w,E,D,O;ku||yc(),this.styles=this.styles||Nd(e),D=this.styles.props,this.tween=n;for(g in t)if(g!=="autoRound"&&(u=t[g],!(Nn[g]&&Td(g,t,n,i,e,s)))){if(d=typeof u,_=Xa[g],d==="function"&&(u=u.call(n,i,e,s),d=typeof u),d==="string"&&~u.indexOf("random(")&&(u=Eo(u)),_)_(this,e,g,u,n)&&(E=1);else if(g.substr(0,2)==="--")c=(getComputedStyle(e).getPropertyValue(g)+"").trim(),u+="",ir.lastIndex=0,ir.test(c)||(p=on(c),m=on(u),m?p!==m&&(c=cr(e,g,c,m)+m):p&&(u+=p)),this.add(a,"setProperty",c,u,i,s,0,0,g),o.push(g),D.push(g,0,a[g]);else if(d!=="undefined"){if(l&&g in l?(c=typeof l[g]=="function"?l[g].call(n,i,e,s):l[g],jt(c)&&~c.indexOf("random(")&&(c=Eo(c)),on(c+"")||c==="auto"||(c+=Hn.units[g]||on(Ci(e,g))||""),(c+"").charAt(1)==="="&&(c=Ci(e,g))):c=Ci(e,g),h=parseFloat(c),y=d==="string"&&u.charAt(1)==="="&&u.substr(0,2),y&&(u=u.substr(2)),f=parseFloat(u),g in gi&&(g==="autoAlpha"&&(h===1&&Ci(e,"visibility")==="hidden"&&f&&(h=0),D.push("visibility",0,a.visibility),Qi(this,a,"visibility",h?"inherit":"hidden",f?"inherit":"hidden",!f)),g!=="scale"&&g!=="transform"&&(g=gi[g],~g.indexOf(",")&&(g=g.split(",")[0]))),x=g in Bi,x){if(this.styles.save(g),O=u,d==="string"&&u.substring(0,6)==="var(--"){if(u=kn(e,u.substring(4,u.indexOf(")"))),u.substring(0,5)==="calc("){var v=e.style.perspective;e.style.perspective=u,u=kn(e,"perspective"),v?e.style.perspective=v:lr(e,"perspective")}f=parseFloat(u)}if(M||(R=e._gsap,R.renderTransform&&!t.parseTransform||Ao(e,t.parseTransform),w=t.smoothOrigin!==!1&&R.smooth,M=this._pt=new bn(this._pt,a,Ct,0,1,R.renderTransform,R,0,-1),M.dep=1),g==="scale")this._pt=new bn(this._pt,R,"scaleY",R.scaleY,(y?Ss(R.scaleY,y+f):f)-R.scaleY||0,Sc),this._pt.u=0,o.push("scaleY",g),g+="X";else if(g==="transformOrigin"){D.push(wn,0,a[wn]),u=v_(u),R.svg?Ec(e,u,0,w,0,this):(m=parseFloat(u.split(" ")[2])||0,m!==R.zOrigin&&Qi(this,R,"zOrigin",R.zOrigin,m),Qi(this,a,g,Ya(c),Ya(u)));continue}else if(g==="svgOrigin"){Ec(e,u,1,w,0,this);continue}else if(g in zd){y_(this,R,g,h,y?Ss(h,y+u):u);continue}else if(g==="smoothOrigin"){Qi(this,R,"smooth",R.smooth,u);continue}else if(g==="force3D"){R[g]=u;continue}else if(g==="transform"){E_(this,u,e);continue}}else g in a||(g=Us(g)||g);if(x||(f||f===0)&&(h||h===0)&&!i_.test(u)&&g in a)p=(c+"").substr((h+"").length),f||(f=0),m=on(u)||(g in Hn.units?Hn.units[g]:p),p!==m&&(h=cr(e,g,c,m)),this._pt=new bn(this._pt,x?R:a,g,h,(y?Ss(h,y+f):f)-h,!x&&(m==="px"||g==="zIndex")&&t.autoRound!==!1?a_:Sc),this._pt.u=m||0,x&&O!==u?(this._pt.b=c,this._pt.e=O,this._pt.r=o_):p!==m&&m!=="%"&&(this._pt.b=c,this._pt.r=s_);else if(g in a)g_.call(this,e,g,c,y?y+u:u);else if(g in e)this.add(e,g,c||e[g],y?y+u:u,i,s);else if(g!=="parseTransform"){Pu(g,u);continue}x||(g in a?D.push(g,0,a[g]):typeof e[g]=="function"?D.push(g,2,e[g]()):D.push(g,1,c||e[g])),o.push(g)}}E&&Pd(this)},render:function(e,t){if(t.tween._time||!Hu())for(var n=t._pt;n;)n.r(e,n.d),n=n._next;else t.styles.revert()},get:Ci,aliases:gi,getSetter:function(e,t,n){var i=gi[t];return i&&i.indexOf(",")<0&&(t=i),t in Bi&&t!==wn&&(e._gsap.x||Ci(e,"x"))?n&&vh===n?t==="scale"?h_:u_:(vh=n||{})&&(t==="scale"?f_:d_):e.style&&!Au(e.style[t])?l_:~t.indexOf("-")?c_:Bu(e,t)},core:{_removeProperty:lr,_getMatrix:Vu}};Rn.utils.checkPrefix=Us;Rn.core.getStyleSaver=Nd;(function(r,e,t,n){var i=Tn(r+","+e+","+t,function(s){Bi[s]=1});Tn(e,function(s){Hn.units[s]="deg",zd[s]=1}),gi[i[13]]=r+","+e,Tn(n,function(s){var o=s.split(":");gi[o[1]]=i[o[0]]})})("x,y,z,scale,scaleX,scaleY,xPercent,yPercent","rotation,rotationX,rotationY,skewX,skewY","transform,transformOrigin,svgOrigin,force3D,smoothOrigin,transformPerspective","0:translateX,1:translateY,2:translateZ,8:rotate,8:rotationZ,8:rotateZ,9:rotateX,10:rotateY");Tn("x,y,z,top,right,bottom,left,width,height,fontSize,padding,margin,perspective",function(r){Hn.units[r]="px"});Rn.registerPlugin(Gd);var kr=Rn.registerPlugin(Gd)||Rn;kr.core.Tween;function T_(r,e){for(var t=0;t<e.length;t++){var n=e[t];n.enumerable=n.enumerable||!1,n.configurable=!0,"value"in n&&(n.writable=!0),Object.defineProperty(r,n.key,n)}}function b_(r,e,t){return e&&T_(r.prototype,e),r}/*!
 * Observer 3.15.0
 * https://gsap.com
 *
 * @license Copyright 2008-2026, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/var Qt,wa,Bn,er,tr,Es,Vd,Er,Ts,Wd,Li,oi,Xd,Yd=function(){return Qt||typeof window<"u"&&(Qt=window.gsap)&&Qt.registerPlugin&&Qt},qd=1,vs=[],tt=[],xi=[],uo=Date.now,Tc=function(e,t){return t},w_=function(){var e=Ts.core,t=e.bridge||{},n=e._scrollers,i=e._proxies;n.push.apply(n,tt),i.push.apply(i,xi),tt=n,xi=i,Tc=function(o,a){return t[o](a)}},rr=function(e,t){return~xi.indexOf(e)&&xi[xi.indexOf(e)+1][t]},ho=function(e){return!!~Wd.indexOf(e)},un=function(e,t,n,i,s){return e.addEventListener(t,n,{passive:i!==!1,capture:!!s})},cn=function(e,t,n,i){return e.removeEventListener(t,n,!!i)},Ho="scrollLeft",Go="scrollTop",bc=function(){return Li&&Li.isPressed||tt.cache++},qa=function(e,t){var n=function i(s){if(s||s===0){qd&&(Bn.history.scrollRestoration="manual");var o=Li&&Li.isPressed;s=i.v=Math.round(s)||(Li&&Li.iOS?1:0),e(s),i.cacheID=tt.cache,o&&Tc("ss",s)}else(t||tt.cache!==i.cacheID||Tc("ref"))&&(i.cacheID=tt.cache,i.v=e());return i.v+i.offset};return n.offset=0,e&&n},mn={s:Ho,p:"left",p2:"Left",os:"right",os2:"Right",d:"width",d2:"Width",a:"x",sc:qa(function(r){return arguments.length?Bn.scrollTo(r,Gt.sc()):Bn.pageXOffset||er[Ho]||tr[Ho]||Es[Ho]||0})},Gt={s:Go,p:"top",p2:"Top",os:"bottom",os2:"Bottom",d:"height",d2:"Height",a:"y",op:mn,sc:qa(function(r){return arguments.length?Bn.scrollTo(mn.sc(),r):Bn.pageYOffset||er[Go]||tr[Go]||Es[Go]||0})},Sn=function(e,t){return(t&&t._ctx&&t._ctx.selector||Qt.utils.toArray)(e)[0]||(typeof e=="string"&&Qt.config().nullTargetWarn!==!1?console.warn("Element not found:",e):null)},A_=function(e,t){for(var n=t.length;n--;)if(t[n]===e||t[n].contains(e))return!0;return!1},ur=function(e,t){var n=t.s,i=t.sc;ho(e)&&(e=er.scrollingElement||tr);var s=tt.indexOf(e),o=i===Gt.sc?1:2;!~s&&(s=tt.push(e)-1),tt[s+o]||un(e,"scroll",bc);var a=tt[s+o],l=a||(tt[s+o]=qa(rr(e,n),!0)||(ho(e)?i:qa(function(c){return arguments.length?e[n]=c:e[n]})));return l.target=e,a||(l.smooth=Qt.getProperty(e,"scrollBehavior")==="smooth"),l},wc=function(e,t,n){var i=e,s=e,o=uo(),a=o,l=t||50,c=Math.max(500,l*3),u=function(_,g){var p=uo();g||p-o>l?(s=i,i=_,a=o,o=p):n?i+=_:i=s+(_-s)/(p-a)*(o-a)},f=function(){s=i=n?0:i,a=o=0},h=function(_){var g=a,p=s,m=uo();return(_||_===0)&&_!==i&&u(_),o===a||m-a>c?0:(i+(n?p:-p))/((n?m:o)-g)*1e3};return{update:u,reset:f,getVelocity:h}},Xs=function(e,t){return t&&!e._gsapAllow&&e.cancelable!==!1&&e.preventDefault(),e.changedTouches?e.changedTouches[0]:e},Ah=function(e){var t=Math.max.apply(Math,e),n=Math.min.apply(Math,e);return Math.abs(t)>=Math.abs(n)?t:n},$d=function(){Ts=Qt.core.globals().ScrollTrigger,Ts&&Ts.core&&w_()},Kd=function(e){return Qt=e||Yd(),!wa&&Qt&&typeof document<"u"&&document.body&&(Bn=window,er=document,tr=er.documentElement,Es=er.body,Wd=[Bn,er,tr,Es],Qt.utils.clamp,Xd=Qt.core.context||function(){},Er="onpointerenter"in Es?"pointer":"mouse",Vd=Ft.isTouch=Bn.matchMedia&&Bn.matchMedia("(hover: none), (pointer: coarse)").matches?1:"ontouchstart"in Bn||navigator.maxTouchPoints>0||navigator.msMaxTouchPoints>0?2:0,oi=Ft.eventTypes=("ontouchstart"in tr?"touchstart,touchmove,touchcancel,touchend":"onpointerdown"in tr?"pointerdown,pointermove,pointercancel,pointerup":"mousedown,mousemove,mouseup,mouseup").split(","),setTimeout(function(){return qd=0},500),wa=1),Ts||$d(),wa};mn.op=Gt;tt.cache=0;var Ft=function(){function r(t){this.init(t)}var e=r.prototype;return e.init=function(n){wa||Kd(Qt)||console.warn("Please gsap.registerPlugin(Observer)"),Ts||$d();var i=n.tolerance,s=n.dragMinimum,o=n.type,a=n.target,l=n.lineHeight,c=n.debounce,u=n.preventDefault,f=n.onStop,h=n.onStopDelay,d=n.ignore,_=n.wheelSpeed,g=n.event,p=n.onDragStart,m=n.onDragEnd,y=n.onDrag,x=n.onPress,M=n.onRelease,R=n.onRight,w=n.onLeft,E=n.onUp,D=n.onDown,O=n.onChangeX,v=n.onChangeY,T=n.onChange,N=n.onToggleX,z=n.onToggleY,W=n.onHover,K=n.onHoverEnd,G=n.onMove,X=n.ignoreCheck,V=n.isNormalizer,re=n.onGestureStart,C=n.onGestureEnd,ae=n.onWheel,Be=n.onEnable,We=n.onDisable,q=n.onClick,Q=n.scrollSpeed,fe=n.capture,oe=n.allowClicks,we=n.lockAxis,ye=n.onLockAxis;this.target=a=Sn(a)||tr,this.vars=n,d&&(d=Qt.utils.toArray(d)),i=i||1e-9,s=s||0,_=_||1,Q=Q||1,o=o||"wheel,touch,pointer",c=c!==!1,l||(l=parseFloat(Bn.getComputedStyle(Es).lineHeight)||22);var Ve,Ge,Ne,P,rt,Fe,ze,F=this,je=0,De=0,A=n.passive||!u&&n.passive!==!1,S=ur(a,mn),H=ur(a,Gt),j=S(),te=H(),Z=~o.indexOf("touch")&&!~o.indexOf("pointer")&&oi[0]==="pointerdown",Se=ho(a),ie=a.ownerDocument||er,de=[0,0,0],He=[0,0,0],ne=0,ve=function(){return ne=uo()},xe=function(Te,ct){return(F.event=Te)&&d&&A_(Te.target,d)||ct&&Z&&Te.pointerType!=="touch"||X&&X(Te,ct)},Ie=function(){F._vx.reset(),F._vy.reset(),Ge.pause(),f&&f(F)},ge=function(){var Te=F.deltaX=Ah(de),ct=F.deltaY=Ah(He),pe=Math.abs(Te)>=i,Le=Math.abs(ct)>=i;T&&(pe||Le)&&T(F,Te,ct,de,He),pe&&(R&&F.deltaX>0&&R(F),w&&F.deltaX<0&&w(F),O&&O(F),N&&F.deltaX<0!=je<0&&N(F),je=F.deltaX,de[0]=de[1]=de[2]=0),Le&&(D&&F.deltaY>0&&D(F),E&&F.deltaY<0&&E(F),v&&v(F),z&&F.deltaY<0!=De<0&&z(F),De=F.deltaY,He[0]=He[1]=He[2]=0),(P||Ne)&&(G&&G(F),Ne&&(p&&Ne===1&&p(F),y&&y(F),Ne=0),P=!1),Fe&&!(Fe=!1)&&ye&&ye(F),rt&&(ae(F),rt=!1),Ve=0},Xe=function(Te,ct,pe){de[pe]+=Te,He[pe]+=ct,F._vx.update(Te),F._vy.update(ct),c?Ve||(Ve=requestAnimationFrame(ge)):ge()},Oe=function(Te,ct){we&&!ze&&(F.axis=ze=Math.abs(Te)>Math.abs(ct)?"x":"y",Fe=!0),ze!=="y"&&(de[2]+=Te,F._vx.update(Te,!0)),ze!=="x"&&(He[2]+=ct,F._vy.update(ct,!0)),c?Ve||(Ve=requestAnimationFrame(ge)):ge()},st=function(Te){if(!xe(Te,1)){Te=Xs(Te,u);var ct=Te.clientX,pe=Te.clientY,Le=ct-F.x,Ce=pe-F.y,ke=F.isDragging;F.x=ct,F.y=pe,(ke||(Le||Ce)&&(Math.abs(F.startX-ct)>=s||Math.abs(F.startY-pe)>=s))&&(Ne||(Ne=ke?2:1),ke||(F.isDragging=!0),Oe(Le,Ce))}},L=F.onPress=function(Re){xe(Re,1)||Re&&Re.button||(F.axis=ze=null,Ge.pause(),F.isPressed=!0,Re=Xs(Re),je=De=0,F.startX=F.x=Re.clientX,F.startY=F.y=Re.clientY,F._vx.reset(),F._vy.reset(),un(V?a:ie,oi[1],st,A,!0),F.deltaX=F.deltaY=0,x&&x(F))},ee=F.onRelease=function(Re){if(!xe(Re,1)){cn(V?a:ie,oi[1],st,!0);var Te=!isNaN(F.y-F.startY),ct=F.isDragging,pe=ct&&(Math.abs(F.x-F.startX)>3||Math.abs(F.y-F.startY)>3),Le=Xs(Re);!pe&&Te&&(F._vx.reset(),F._vy.reset(),u&&oe&&Qt.delayedCall(.08,function(){if(uo()-ne>300&&!Re.defaultPrevented){if(Re.target.click)Re.target.click();else if(ie.createEvent){var Ce=ie.createEvent("MouseEvents");Ce.initMouseEvent("click",!0,!0,Bn,1,Le.screenX,Le.screenY,Le.clientX,Le.clientY,!1,!1,!1,!1,0,null),Re.target.dispatchEvent(Ce)}}})),F.isDragging=F.isGesturing=F.isPressed=!1,f&&ct&&!V&&Ge.restart(!0),Ne&&ge(),m&&ct&&m(F),M&&M(F,pe)}},$=function(Te){return Te.touches&&Te.touches.length>1&&(F.isGesturing=!0)&&re(Te,F.isDragging)},J=function(){return(F.isGesturing=!1)||C(F)},le=function(Te){if(!xe(Te)){var ct=S(),pe=H();Xe((ct-j)*Q,(pe-te)*Q,1),j=ct,te=pe,f&&Ge.restart(!0)}},ce=function(Te){if(!xe(Te)){Te=Xs(Te,u),ae&&(rt=!0);var ct=(Te.deltaMode===1?l:Te.deltaMode===2?Bn.innerHeight:1)*_;Xe(Te.deltaX*ct,Te.deltaY*ct,0),f&&!V&&Ge.restart(!0)}},Ye=function(Te){if(!xe(Te)){var ct=Te.clientX,pe=Te.clientY,Le=ct-F.x,Ce=pe-F.y;F.x=ct,F.y=pe,P=!0,f&&Ge.restart(!0),(Le||Ce)&&Oe(Le,Ce)}},_t=function(Te){F.event=Te,W(F)},Tt=function(Te){F.event=Te,K(F)},nt=function(Te){return xe(Te)||Xs(Te,u)&&q(F)};Ge=F._dc=Qt.delayedCall(h||.25,Ie).pause(),F.deltaX=F.deltaY=0,F._vx=wc(0,50,!0),F._vy=wc(0,50,!0),F.scrollX=S,F.scrollY=H,F.isDragging=F.isGesturing=F.isPressed=!1,Xd(this),F.enable=function(Re){return F.isEnabled||(un(Se?ie:a,"scroll",bc),o.indexOf("scroll")>=0&&un(Se?ie:a,"scroll",le,A,fe),o.indexOf("wheel")>=0&&un(a,"wheel",ce,A,fe),(o.indexOf("touch")>=0&&Vd||o.indexOf("pointer")>=0)&&(un(a,oi[0],L,A,fe),un(ie,oi[2],ee),un(ie,oi[3],ee),oe&&un(a,"click",ve,!0,!0),q&&un(a,"click",nt),re&&un(ie,"gesturestart",$),C&&un(ie,"gestureend",J),W&&un(a,Er+"enter",_t),K&&un(a,Er+"leave",Tt),G&&un(a,Er+"move",Ye)),F.isEnabled=!0,F.isDragging=F.isGesturing=F.isPressed=P=Ne=!1,F._vx.reset(),F._vy.reset(),j=S(),te=H(),Re&&Re.type&&L(Re),Be&&Be(F)),F},F.disable=function(){F.isEnabled&&(vs.filter(function(Re){return Re!==F&&ho(Re.target)}).length||cn(Se?ie:a,"scroll",bc),F.isPressed&&(F._vx.reset(),F._vy.reset(),cn(V?a:ie,oi[1],st,!0)),cn(Se?ie:a,"scroll",le,fe),cn(a,"wheel",ce,fe),cn(a,oi[0],L,fe),cn(ie,oi[2],ee),cn(ie,oi[3],ee),cn(a,"click",ve,!0),cn(a,"click",nt),cn(ie,"gesturestart",$),cn(ie,"gestureend",J),cn(a,Er+"enter",_t),cn(a,Er+"leave",Tt),cn(a,Er+"move",Ye),F.isEnabled=F.isPressed=F.isDragging=!1,We&&We(F))},F.kill=F.revert=function(){F.disable();var Re=vs.indexOf(F);Re>=0&&vs.splice(Re,1),Li===F&&(Li=0)},vs.push(F),V&&ho(a)&&(Li=F),F.enable(g)},b_(r,[{key:"velocityX",get:function(){return this._vx.getVelocity()}},{key:"velocityY",get:function(){return this._vy.getVelocity()}}]),r}();Ft.version="3.15.0";Ft.create=function(r){return new Ft(r)};Ft.register=Kd;Ft.getAll=function(){return vs.slice()};Ft.getById=function(r){return vs.filter(function(e){return e.vars.id===r})[0]};Yd()&&Qt.registerPlugin(Ft);/*!
 * ScrollTrigger 3.15.0
 * https://gsap.com
 *
 * @license Copyright 2008-2026, GreenSock. All rights reserved.
 * Subject to the terms at https://gsap.com/standard-license
 * @author: Jack Doyle, jack@greensock.com
*/var Me,ds,et,pt,Fn,ht,Wu,$a,Ro,fo,to,Vo,rn,ol,Ac,dn,Rh,Ch,ps,Zd,yl,jd,fn,Rc,Jd,Qd,Ki,Cc,Xu,bs,Yu,po,Pc,El,Wo=1,sn=Date.now,Tl=sn(),Qn=0,no=0,Ph=function(e,t,n){var i=Un(e)&&(e.substr(0,6)==="clamp("||e.indexOf("max")>-1);return n["_"+t+"Clamp"]=i,i?e.substr(6,e.length-7):e},Dh=function(e,t){return t&&(!Un(e)||e.substr(0,6)!=="clamp(")?"clamp("+e+")":e},R_=function r(){return no&&requestAnimationFrame(r)},Lh=function(){return ol=1},Ih=function(){return ol=0},pi=function(e){return e},io=function(e){return Math.round(e*1e5)/1e5||0},ep=function(){return typeof window<"u"},tp=function(){return Me||ep()&&(Me=window.gsap)&&Me.registerPlugin&&Me},Hr=function(e){return!!~Wu.indexOf(e)},np=function(e){return(e==="Height"?Yu:et["inner"+e])||Fn["client"+e]||ht["client"+e]},ip=function(e){return rr(e,"getBoundingClientRect")||(Hr(e)?function(){return Da.width=et.innerWidth,Da.height=Yu,Da}:function(){return Pi(e)})},C_=function(e,t,n){var i=n.d,s=n.d2,o=n.a;return(o=rr(e,"getBoundingClientRect"))?function(){return o()[i]}:function(){return(t?np(s):e["client"+s])||0}},P_=function(e,t){return!t||~xi.indexOf(e)?ip(e):function(){return Da}},vi=function(e,t){var n=t.s,i=t.d2,s=t.d,o=t.a;return Math.max(0,(n="scroll"+i)&&(o=rr(e,n))?o()-ip(e)()[s]:Hr(e)?(Fn[n]||ht[n])-np(i):e[n]-e["offset"+i])},Xo=function(e,t){for(var n=0;n<ps.length;n+=3)(!t||~t.indexOf(ps[n+1]))&&e(ps[n],ps[n+1],ps[n+2])},Un=function(e){return typeof e=="string"},an=function(e){return typeof e=="function"},ro=function(e){return typeof e=="number"},Tr=function(e){return typeof e=="object"},Ys=function(e,t,n){return e&&e.progress(t?0:1)&&n&&e.pause()},Kr=function(e,t,n){if(e.enabled){var i=e._ctx?e._ctx.add(function(){return t(e,n)}):t(e,n);i&&i.totalTime&&(e.callbackAnimation=i)}},Zr=Math.abs,rp="left",sp="top",qu="right",$u="bottom",Fr="width",Or="height",mo="Right",_o="Left",go="Top",vo="Bottom",zt="padding",qn="margin",Ns="Width",Ku="Height",Ht="px",$n=function(e){return et.getComputedStyle(e.nodeType===Node.DOCUMENT_NODE?e.scrollingElement:e)},D_=function(e){var t=$n(e).position;e.style.position=t==="absolute"||t==="fixed"?t:"relative"},Uh=function(e,t){for(var n in t)n in e||(e[n]=t[n]);return e},Pi=function(e,t){var n=t&&$n(e)[Ac]!=="matrix(1, 0, 0, 1, 0, 0)"&&Me.to(e,{x:0,y:0,xPercent:0,yPercent:0,rotation:0,rotationX:0,rotationY:0,scale:1,skewX:0,skewY:0}).progress(1),i=e.getBoundingClientRect?e.getBoundingClientRect():e.scrollingElement.getBoundingClientRect();return n&&n.progress(0).kill(),i},Ka=function(e,t){var n=t.d2;return e["offset"+n]||e["client"+n]||0},op=function(e){var t=[],n=e.labels,i=e.duration(),s;for(s in n)t.push(n[s]/i);return t},L_=function(e){return function(t){return Me.utils.snap(op(e),t)}},Zu=function(e){var t=Me.utils.snap(e),n=Array.isArray(e)&&e.slice(0).sort(function(i,s){return i-s});return n?function(i,s,o){o===void 0&&(o=.001);var a;if(!s)return t(i);if(s>0){for(i-=o,a=0;a<n.length;a++)if(n[a]>=i)return n[a];return n[a-1]}else for(a=n.length,i+=o;a--;)if(n[a]<=i)return n[a];return n[0]}:function(i,s,o){o===void 0&&(o=.001);var a=t(i);return!s||Math.abs(a-i)<o||a-i<0==s<0?a:t(s<0?i-e:i+e)}},I_=function(e){return function(t,n){return Zu(op(e))(t,n.direction)}},Yo=function(e,t,n,i){return n.split(",").forEach(function(s){return e(t,s,i)})},$t=function(e,t,n,i,s){return e.addEventListener(t,n,{passive:!i,capture:!!s})},qt=function(e,t,n,i){return e.removeEventListener(t,n,!!i)},qo=function(e,t,n){n=n&&n.wheelHandler,n&&(e(t,"wheel",n),e(t,"touchmove",n))},Nh={startColor:"green",endColor:"red",indent:0,fontSize:"16px",fontWeight:"normal"},$o={toggleActions:"play",anticipatePin:0},Za={top:0,left:0,center:.5,bottom:1,right:1},Aa=function(e,t){if(Un(e)){var n=e.indexOf("="),i=~n?+(e.charAt(n-1)+1)*parseFloat(e.substr(n+1)):0;~n&&(e.indexOf("%")>n&&(i*=t/100),e=e.substr(0,n-1)),e=i+(e in Za?Za[e]*t:~e.indexOf("%")?parseFloat(e)*t/100:parseFloat(e)||0)}return e},Ko=function(e,t,n,i,s,o,a,l){var c=s.startColor,u=s.endColor,f=s.fontSize,h=s.indent,d=s.fontWeight,_=pt.createElement("div"),g=Hr(n)||rr(n,"pinType")==="fixed",p=e.indexOf("scroller")!==-1,m=g?ht:n.tagName==="IFRAME"?n.contentDocument.body:n,y=e.indexOf("start")!==-1,x=y?c:u,M="border-color:"+x+";font-size:"+f+";color:"+x+";font-weight:"+d+";pointer-events:none;white-space:nowrap;font-family:sans-serif,Arial;z-index:1000;padding:4px 8px;border-width:0;border-style:solid;";return M+="position:"+((p||l)&&g?"fixed;":"absolute;"),(p||l||!g)&&(M+=(i===Gt?qu:$u)+":"+(o+parseFloat(h))+"px;"),a&&(M+="box-sizing:border-box;text-align:left;width:"+a.offsetWidth+"px;"),_._isStart=y,_.setAttribute("class","gsap-marker-"+e+(t?" marker-"+t:"")),_.style.cssText=M,_.innerText=t||t===0?e+"-"+t:e,m.children[0]?m.insertBefore(_,m.children[0]):m.appendChild(_),_._offset=_["offset"+i.op.d2],Ra(_,0,i,y),_},Ra=function(e,t,n,i){var s={display:"block"},o=n[i?"os2":"p2"],a=n[i?"p2":"os2"];e._isFlipped=i,s[n.a+"Percent"]=i?-100:0,s[n.a]=i?"1px":0,s["border"+o+Ns]=1,s["border"+a+Ns]=0,s[n.p]=t+"px",Me.set(e,s)},Qe=[],Dc={},Co,Fh=function(){return sn()-Qn>34&&(Co||(Co=requestAnimationFrame(Fi)))},jr=function(){(!fn||!fn.isPressed||fn.startX>ht.clientWidth)&&(tt.cache++,fn?Co||(Co=requestAnimationFrame(Fi)):Fi(),Qn||Vr("scrollStart"),Qn=sn())},bl=function(){Qd=et.innerWidth,Jd=et.innerHeight},so=function(e){tt.cache++,(e===!0||!rn&&!jd&&!pt.fullscreenElement&&!pt.webkitFullscreenElement&&(!Rc||Qd!==et.innerWidth||Math.abs(et.innerHeight-Jd)>et.innerHeight*.25))&&$a.restart(!0)},Gr={},U_=[],ap=function r(){return qt(Ze,"scrollEnd",r)||Pr(!0)},Vr=function(e){return Gr[e]&&Gr[e].map(function(t){return t()})||U_},In=[],lp=function(e){for(var t=0;t<In.length;t+=5)(!e||In[t+4]&&In[t+4].query===e)&&(In[t].style.cssText=In[t+1],In[t].getBBox&&In[t].setAttribute("transform",In[t+2]||""),In[t+3].uncache=1)},cp=function(){return tt.forEach(function(e){return an(e)&&++e.cacheID&&(e.rec=e())})},ju=function(e,t){var n;for(dn=0;dn<Qe.length;dn++)n=Qe[dn],n&&(!t||n._ctx===t)&&(e?n.kill(1):n.revert(!0,!0));po=!0,t&&lp(t),t||Vr("revert")},up=function(e,t){tt.cache++,(t||!pn)&&tt.forEach(function(n){return an(n)&&n.cacheID++&&(n.rec=0)}),Un(e)&&(et.history.scrollRestoration=Xu=e)},pn,Br=0,Oh,N_=function(){if(Oh!==Br){var e=Oh=Br;requestAnimationFrame(function(){return e===Br&&Pr(!0)})}},hp=function(){ht.appendChild(bs),Yu=!fn&&bs.offsetHeight||et.innerHeight,ht.removeChild(bs)},Bh=function(e){return Ro(".gsap-marker-start, .gsap-marker-end, .gsap-marker-scroller-start, .gsap-marker-scroller-end").forEach(function(t){return t.style.display=e?"none":"block"})},Pr=function(e,t){if(Fn=pt.documentElement,ht=pt.body,Wu=[et,pt,Fn,ht],Qn&&!e&&!po){$t(Ze,"scrollEnd",ap);return}hp(),pn=Ze.isRefreshing=!0,po||cp();var n=Vr("refreshInit");Zd&&Ze.sort(),t||ju(),tt.forEach(function(i){an(i)&&(i.smooth&&(i.target.style.scrollBehavior="auto"),i(0))}),Qe.slice(0).forEach(function(i){return i.refresh()}),po=!1,Qe.forEach(function(i){if(i._subPinOffset&&i.pin){var s=i.vars.horizontal?"offsetWidth":"offsetHeight",o=i.pin[s];i.revert(!0,1),i.adjustPinSpacing(i.pin[s]-o),i.refresh()}}),Pc=1,Bh(!0),Qe.forEach(function(i){var s=vi(i.scroller,i._dir),o=i.vars.end==="max"||i._endClamp&&i.end>s,a=i._startClamp&&i.start>=s;(o||a)&&i.setPositions(a?s-1:i.start,o?Math.max(a?s:i.start+1,s):i.end,!0)}),Bh(!1),Pc=0,n.forEach(function(i){return i&&i.render&&i.render(-1)}),tt.forEach(function(i){an(i)&&(i.smooth&&requestAnimationFrame(function(){return i.target.style.scrollBehavior="smooth"}),i.rec&&i(i.rec))}),up(Xu,1),$a.pause(),Br++,pn=2,Fi(2),Qe.forEach(function(i){return an(i.vars.onRefresh)&&i.vars.onRefresh(i)}),pn=Ze.isRefreshing=!1,Vr("refresh")},Lc=0,Ca=1,xo,Fi=function(e){if(e===2||!pn&&!po){Ze.isUpdating=!0,xo&&xo.update(0);var t=Qe.length,n=sn(),i=n-Tl>=50,s=t&&Qe[0].scroll();if(Ca=Lc>s?-1:1,pn||(Lc=s),i&&(Qn&&!ol&&n-Qn>200&&(Qn=0,Vr("scrollEnd")),to=Tl,Tl=n),Ca<0){for(dn=t;dn-- >0;)Qe[dn]&&Qe[dn].update(0,i);Ca=1}else for(dn=0;dn<t;dn++)Qe[dn]&&Qe[dn].update(0,i);Ze.isUpdating=!1}Co=0},Ic=[rp,sp,$u,qu,qn+vo,qn+mo,qn+go,qn+_o,"display","flexShrink","float","zIndex","gridColumnStart","gridColumnEnd","gridRowStart","gridRowEnd","gridArea","justifySelf","alignSelf","placeSelf","order"],Pa=Ic.concat([Fr,Or,"boxSizing","max"+Ns,"max"+Ku,"position",qn,zt,zt+go,zt+mo,zt+vo,zt+_o]),F_=function(e,t,n){ws(n);var i=e._gsap;if(i.spacerIsNative)ws(i.spacerState);else if(e._gsap.swappedIn){var s=t.parentNode;s&&(s.insertBefore(e,t),s.removeChild(t))}e._gsap.swappedIn=!1},wl=function(e,t,n,i){if(!e._gsap.swappedIn){for(var s=Ic.length,o=t.style,a=e.style,l;s--;)l=Ic[s],o[l]=n[l];o.position=n.position==="absolute"?"absolute":"relative",n.display==="inline"&&(o.display="inline-block"),a[$u]=a[qu]="auto",o.flexBasis=n.flexBasis||"auto",o.overflow="visible",o.boxSizing="border-box",o[Fr]=Ka(e,mn)+Ht,o[Or]=Ka(e,Gt)+Ht,o[zt]=a[qn]=a[sp]=a[rp]="0",ws(i),a[Fr]=a["max"+Ns]=n[Fr],a[Or]=a["max"+Ku]=n[Or],a[zt]=n[zt],e.parentNode!==t&&(e.parentNode.insertBefore(t,e),t.appendChild(e)),e._gsap.swappedIn=!0}},O_=/([A-Z])/g,ws=function(e){if(e){var t=e.t.style,n=e.length,i=0,s,o;for((e.t._gsap||Me.core.getCache(e.t)).uncache=1;i<n;i+=2)o=e[i+1],s=e[i],o?t[s]=o:t[s]&&t.removeProperty(s.replace(O_,"-$1").toLowerCase())}},Zo=function(e){for(var t=Pa.length,n=e.style,i=[],s=0;s<t;s++)i.push(Pa[s],n[Pa[s]]);return i.t=e,i},B_=function(e,t,n){for(var i=[],s=e.length,o=n?8:0,a;o<s;o+=2)a=e[o],i.push(a,a in t?t[a]:e[o+1]);return i.t=e.t,i},Da={left:0,top:0},zh=function(e,t,n,i,s,o,a,l,c,u,f,h,d,_){an(e)&&(e=e(l)),Un(e)&&e.substr(0,3)==="max"&&(e=h+(e.charAt(4)==="="?Aa("0"+e.substr(3),n):0));var g=d?d.time():0,p,m,y;if(d&&d.seek(0),isNaN(e)||(e=+e),ro(e))d&&(e=Me.utils.mapRange(d.scrollTrigger.start,d.scrollTrigger.end,0,h,e)),a&&Ra(a,n,i,!0);else{an(t)&&(t=t(l));var x=(e||"0").split(" "),M,R,w,E;y=Sn(t,l)||ht,M=Pi(y)||{},(!M||!M.left&&!M.top)&&$n(y).display==="none"&&(E=y.style.display,y.style.display="block",M=Pi(y),E?y.style.display=E:y.style.removeProperty("display")),R=Aa(x[0],M[i.d]),w=Aa(x[1]||"0",n),e=M[i.p]-c[i.p]-u+R+s-w,a&&Ra(a,w,i,n-w<20||a._isStart&&w>20),n-=n-w}if(_&&(l[_]=e||-.001,e<0&&(e=0)),o){var D=e+n,O=o._isStart;p="scroll"+i.d2,Ra(o,D,i,O&&D>20||!O&&(f?Math.max(ht[p],Fn[p]):o.parentNode[p])<=D+1),f&&(c=Pi(a),f&&(o.style[i.op.p]=c[i.op.p]-i.op.m-o._offset+Ht))}return d&&y&&(p=Pi(y),d.seek(h),m=Pi(y),d._caScrollDist=p[i.p]-m[i.p],e=e/d._caScrollDist*h),d&&d.seek(g),d?e:Math.round(e)},z_=/(webkit|moz|length|cssText|inset)/i,kh=function(e,t,n,i){if(e.parentNode!==t){var s=e.style,o,a;if(t===ht){e._stOrig=s.cssText,a=$n(e);for(o in a)!+o&&!z_.test(o)&&a[o]&&typeof s[o]=="string"&&o!=="0"&&(s[o]=a[o]);s.top=n,s.left=i}else s.cssText=e._stOrig;Me.core.getCache(e).uncache=1,t.appendChild(e)}},fp=function(e,t,n){var i=t,s=i;return function(o){var a=Math.round(e());return a!==i&&a!==s&&Math.abs(a-i)>3&&Math.abs(a-s)>3&&(o=a,n&&n()),s=i,i=Math.round(o),i}},jo=function(e,t,n){var i={};i[t.p]="+="+n,Me.set(e,i)},Hh=function(e,t){var n=ur(e,t),i="_scroll"+t.p2,s=function o(a,l,c,u,f){var h=o.tween,d=l.onComplete,_={};c=c||n();var g=fp(n,c,function(){h.kill(),o.tween=0});return f=u&&f||0,u=u||a-c,h&&h.kill(),l[i]=a,l.inherit=!1,l.modifiers=_,_[i]=function(){return g(c+u*h.ratio+f*h.ratio*h.ratio)},l.onUpdate=function(){tt.cache++,o.tween&&Fi()},l.onComplete=function(){o.tween=0,d&&d.call(h)},h=o.tween=Me.to(e,l),h};return e[i]=n,n.wheelHandler=function(){return s.tween&&s.tween.kill()&&(s.tween=0)},$t(e,"wheel",n.wheelHandler),Ze.isTouch&&$t(e,"touchmove",n.wheelHandler),s},Ze=function(){function r(t,n){ds||r.register(Me)||console.warn("Please gsap.registerPlugin(ScrollTrigger)"),Cc(this),this.init(t,n)}var e=r.prototype;return e.init=function(n,i){if(this.progress=this.start=0,this.vars&&this.kill(!0,!0),!no){this.update=this.refresh=this.kill=pi;return}n=Uh(Un(n)||ro(n)||n.nodeType?{trigger:n}:n,$o);var s=n,o=s.onUpdate,a=s.toggleClass,l=s.id,c=s.onToggle,u=s.onRefresh,f=s.scrub,h=s.trigger,d=s.pin,_=s.pinSpacing,g=s.invalidateOnRefresh,p=s.anticipatePin,m=s.onScrubComplete,y=s.onSnapComplete,x=s.once,M=s.snap,R=s.pinReparent,w=s.pinSpacer,E=s.containerAnimation,D=s.fastScrollEnd,O=s.preventOverlaps,v=n.horizontal||n.containerAnimation&&n.horizontal!==!1?mn:Gt,T=!f&&f!==0,N=Sn(n.scroller||et),z=Me.core.getCache(N),W=Hr(N),K=("pinType"in n?n.pinType:rr(N,"pinType")||W&&"fixed")==="fixed",G=[n.onEnter,n.onLeave,n.onEnterBack,n.onLeaveBack],X=T&&n.toggleActions.split(" "),V="markers"in n?n.markers:$o.markers,re=W?0:parseFloat($n(N)["border"+v.p2+Ns])||0,C=this,ae=n.onRefreshInit&&function(){return n.onRefreshInit(C)},Be=C_(N,W,v),We=P_(N,W),q=0,Q=0,fe=0,oe=ur(N,v),we,ye,Ve,Ge,Ne,P,rt,Fe,ze,F,je,De,A,S,H,j,te,Z,Se,ie,de,He,ne,ve,xe,Ie,ge,Xe,Oe,st,L,ee,$,J,le,ce,Ye,_t,Tt;if(C._startClamp=C._endClamp=!1,C._dir=v,p*=45,C.scroller=N,C.scroll=E?E.time.bind(E):oe,Ge=oe(),C.vars=n,i=i||n.animation,"refreshPriority"in n&&(Zd=1,n.refreshPriority===-9999&&(xo=C)),z.tweenScroll=z.tweenScroll||{top:Hh(N,Gt),left:Hh(N,mn)},C.tweenTo=we=z.tweenScroll[v.p],C.scrubDuration=function(pe){$=ro(pe)&&pe,$?ee?ee.duration(pe):ee=Me.to(i,{ease:"expo",totalProgress:"+=0",inherit:!1,duration:$,paused:!0,onComplete:function(){return m&&m(C)}}):(ee&&ee.progress(1).kill(),ee=0)},i&&(i.vars.lazy=!1,i._initted&&!C.isReverted||i.vars.immediateRender!==!1&&n.immediateRender!==!1&&i.duration()&&i.render(0,!0,!0),C.animation=i.pause(),i.scrollTrigger=C,C.scrubDuration(f),st=0,l||(l=i.vars.id)),M&&((!Tr(M)||M.push)&&(M={snapTo:M}),"scrollBehavior"in ht.style&&Me.set(W?[ht,Fn]:N,{scrollBehavior:"auto"}),tt.forEach(function(pe){return an(pe)&&pe.target===(W?pt.scrollingElement||Fn:N)&&(pe.smooth=!1)}),Ve=an(M.snapTo)?M.snapTo:M.snapTo==="labels"?L_(i):M.snapTo==="labelsDirectional"?I_(i):M.directional!==!1?function(pe,Le){return Zu(M.snapTo)(pe,sn()-Q<500?0:Le.direction)}:Me.utils.snap(M.snapTo),J=M.duration||{min:.1,max:2},J=Tr(J)?fo(J.min,J.max):fo(J,J),le=Me.delayedCall(M.delay||$/2||.1,function(){var pe=oe(),Le=sn()-Q<500,Ce=we.tween;if((Le||Math.abs(C.getVelocity())<10)&&!Ce&&!ol&&q!==pe){var ke=(pe-P)/S,Dt=i&&!T?i.totalProgress():ke,qe=Le?0:(Dt-L)/(sn()-to)*1e3||0,bt=Me.utils.clamp(-ke,1-ke,Zr(qe/2)*qe/.185),Lt=ke+(M.inertia===!1?0:bt),Mt,gt,dt=M,Cn=dt.onStart,yt=dt.onInterrupt,b=dt.onComplete;if(Mt=Ve(Lt,C),ro(Mt)||(Mt=Lt),gt=Math.max(0,Math.round(P+Mt*S)),pe<=rt&&pe>=P&&gt!==pe){if(Ce&&!Ce._initted&&Ce.data<=Zr(gt-pe))return;M.inertia===!1&&(bt=Mt-ke),we(gt,{duration:J(Zr(Math.max(Zr(Lt-Dt),Zr(Mt-Dt))*.185/qe/.05||0)),ease:M.ease||"power3",data:Zr(gt-pe),onInterrupt:function(){return le.restart(!0)&&yt&&Kr(C,yt)},onComplete:function(){C.update(),q=oe(),i&&!T&&(ee?ee.resetTo("totalProgress",Mt,i._tTime/i._tDur):i.progress(Mt)),st=L=i&&!T?i.totalProgress():C.progress,y&&y(C),b&&Kr(C,b)}},pe,bt*S,gt-pe-bt*S),Cn&&Kr(C,Cn,we.tween)}}else C.isActive&&q!==pe&&le.restart(!0)}).pause()),l&&(Dc[l]=C),h=C.trigger=Sn(h||d!==!0&&d),Tt=h&&h._gsap&&h._gsap.stRevert,Tt&&(Tt=Tt(C)),d=d===!0?h:Sn(d),Un(a)&&(a={targets:h,className:a}),d&&(_===!1||_===qn||(_=!_&&d.parentNode&&d.parentNode.style&&$n(d.parentNode).display==="flex"?!1:zt),C.pin=d,ye=Me.core.getCache(d),ye.spacer?H=ye.pinState:(w&&(w=Sn(w),w&&!w.nodeType&&(w=w.current||w.nativeElement),ye.spacerIsNative=!!w,w&&(ye.spacerState=Zo(w))),ye.spacer=Z=w||pt.createElement("div"),Z.classList.add("pin-spacer"),l&&Z.classList.add("pin-spacer-"+l),ye.pinState=H=Zo(d)),n.force3D!==!1&&Me.set(d,{force3D:!0}),C.spacer=Z=ye.spacer,Oe=$n(d),ve=Oe[_+v.os2],ie=Me.getProperty(d),de=Me.quickSetter(d,v.a,Ht),wl(d,Z,Oe),te=Zo(d)),V){De=Tr(V)?Uh(V,Nh):Nh,F=Ko("scroller-start",l,N,v,De,0),je=Ko("scroller-end",l,N,v,De,0,F),Se=F["offset"+v.op.d2];var nt=Sn(rr(N,"content")||N);Fe=this.markerStart=Ko("start",l,nt,v,De,Se,0,E),ze=this.markerEnd=Ko("end",l,nt,v,De,Se,0,E),E&&(_t=Me.quickSetter([Fe,ze],v.a,Ht)),!K&&!(xi.length&&rr(N,"fixedMarkers")===!0)&&(D_(W?ht:N),Me.set([F,je],{force3D:!0}),Ie=Me.quickSetter(F,v.a,Ht),Xe=Me.quickSetter(je,v.a,Ht))}if(E){var Re=E.vars.onUpdate,Te=E.vars.onUpdateParams;E.eventCallback("onUpdate",function(){C.update(0,0,1),Re&&Re.apply(E,Te||[])})}if(C.previous=function(){return Qe[Qe.indexOf(C)-1]},C.next=function(){return Qe[Qe.indexOf(C)+1]},C.revert=function(pe,Le){if(!Le)return C.kill(!0);var Ce=pe!==!1||!C.enabled,ke=rn;Ce!==C.isReverted&&(Ce&&(ce=Math.max(oe(),C.scroll.rec||0),fe=C.progress,Ye=i&&i.progress()),Fe&&[Fe,ze,F,je].forEach(function(Dt){return Dt.style.display=Ce?"none":"block"}),Ce&&(rn=C,C.update(Ce)),d&&(!R||!C.isActive)&&(Ce?F_(d,Z,H):wl(d,Z,$n(d),xe)),Ce||C.update(Ce),rn=ke,C.isReverted=Ce)},C.refresh=function(pe,Le,Ce,ke){if(!((rn||!C.enabled)&&!Le)){if(d&&pe&&Qn){$t(r,"scrollEnd",ap);return}!pn&&ae&&ae(C),rn=C,we.tween&&!Ce&&(we.tween.kill(),we.tween=0),ee&&ee.pause(),g&&i&&(i.revert({kill:!1}).invalidate(),i.getChildren?i.getChildren(!0,!0,!1).forEach(function(Je){return Je.vars.immediateRender&&Je.render(0,!0,!0)}):i.vars.immediateRender&&i.render(0,!0,!0)),C.isReverted||C.revert(!0,!0),C._subPinOffset=!1;var Dt=Be(),qe=We(),bt=E?E.duration():vi(N,v),Lt=S<=.01||!S,Mt=0,gt=ke||0,dt=Tr(Ce)?Ce.end:n.end,Cn=n.endTrigger||h,yt=Tr(Ce)?Ce.start:n.start||(n.start===0||!h?0:d?"0 0":"0 100%"),b=C.pinnedContainer=n.pinnedContainer&&Sn(n.pinnedContainer,C),U=h&&Math.max(0,Qe.indexOf(C))||0,B=U,k,I,se,_e,he,ue,Ae,Ue,be,ot,it,mt,Xt;for(V&&Tr(Ce)&&(mt=Me.getProperty(F,v.p),Xt=Me.getProperty(je,v.p));B-- >0;)ue=Qe[B],ue.end||ue.refresh(0,1)||(rn=C),Ae=ue.pin,Ae&&(Ae===h||Ae===d||Ae===b)&&!ue.isReverted&&(ot||(ot=[]),ot.unshift(ue),ue.revert(!0,!0)),ue!==Qe[B]&&(U--,B--);for(an(yt)&&(yt=yt(C)),yt=Ph(yt,"start",C),P=zh(yt,h,Dt,v,oe(),Fe,F,C,qe,re,K,bt,E,C._startClamp&&"_startClamp")||(d?-.001:0),an(dt)&&(dt=dt(C)),Un(dt)&&!dt.indexOf("+=")&&(~dt.indexOf(" ")?dt=(Un(yt)?yt.split(" ")[0]:"")+dt:(Mt=Aa(dt.substr(2),Dt),dt=Un(yt)?yt:(E?Me.utils.mapRange(0,E.duration(),E.scrollTrigger.start,E.scrollTrigger.end,P):P)+Mt,Cn=h)),dt=Ph(dt,"end",C),rt=Math.max(P,zh(dt||(Cn?"100% 0":bt),Cn,Dt,v,oe()+Mt,ze,je,C,qe,re,K,bt,E,C._endClamp&&"_endClamp"))||-.001,Mt=0,B=U;B--;)ue=Qe[B]||{},Ae=ue.pin,Ae&&ue.start-ue._pinPush<=P&&!E&&ue.end>0&&(k=ue.end-(C._startClamp?Math.max(0,ue.start):ue.start),(Ae===h&&ue.start-ue._pinPush<P||Ae===b)&&isNaN(yt)&&(Mt+=k*(1-ue.progress)),Ae===d&&(gt+=k));if(P+=Mt,rt+=Mt,C._startClamp&&(C._startClamp+=Mt),C._endClamp&&!pn&&(C._endClamp=rt||-.001,rt=Math.min(rt,vi(N,v))),S=rt-P||(P-=.01)&&.001,Lt&&(fe=Me.utils.clamp(0,1,Me.utils.normalize(P,rt,ce))),C._pinPush=gt,Fe&&Mt&&(k={},k[v.a]="+="+Mt,b&&(k[v.p]="-="+oe()),Me.set([Fe,ze],k)),d&&!(Pc&&C.end>=vi(N,v)))k=$n(d),_e=v===Gt,se=oe(),He=parseFloat(ie(v.a))+gt,!bt&&rt>1&&(it=(W?pt.scrollingElement||Fn:N).style,it={style:it,value:it["overflow"+v.a.toUpperCase()]},W&&$n(ht)["overflow"+v.a.toUpperCase()]!=="scroll"&&(it.style["overflow"+v.a.toUpperCase()]="scroll")),wl(d,Z,k),te=Zo(d),I=Pi(d,!0),Ue=K&&ur(N,_e?mn:Gt)(),_?(xe=[_+v.os2,S+gt+Ht],xe.t=Z,B=_===zt?Ka(d,v)+S+gt:0,B&&(xe.push(v.d,B+Ht),Z.style.flexBasis!=="auto"&&(Z.style.flexBasis=B+Ht)),ws(xe),b&&Qe.forEach(function(Je){Je.pin===b&&Je.vars.pinSpacing!==!1&&(Je._subPinOffset=!0)}),K&&oe(ce)):(B=Ka(d,v),B&&Z.style.flexBasis!=="auto"&&(Z.style.flexBasis=B+Ht)),K&&(he={top:I.top+(_e?se-P:Ue)+Ht,left:I.left+(_e?Ue:se-P)+Ht,boxSizing:"border-box",position:"fixed"},he[Fr]=he["max"+Ns]=Math.ceil(I.width)+Ht,he[Or]=he["max"+Ku]=Math.ceil(I.height)+Ht,he[qn]=he[qn+go]=he[qn+mo]=he[qn+vo]=he[qn+_o]="0",he[zt]=k[zt],he[zt+go]=k[zt+go],he[zt+mo]=k[zt+mo],he[zt+vo]=k[zt+vo],he[zt+_o]=k[zt+_o],j=B_(H,he,R),pn&&oe(0)),i?(be=i._initted,yl(1),i.render(i.duration(),!0,!0),ne=ie(v.a)-He+S+gt,ge=Math.abs(S-ne)>1,K&&ge&&j.splice(j.length-2,2),i.render(0,!0,!0),be||i.invalidate(!0),i.parent||i.totalTime(i.totalTime()),yl(0)):ne=S,it&&(it.value?it.style["overflow"+v.a.toUpperCase()]=it.value:it.style.removeProperty("overflow-"+v.a));else if(h&&oe()&&!E)for(I=h.parentNode;I&&I!==ht;)I._pinOffset&&(P-=I._pinOffset,rt-=I._pinOffset),I=I.parentNode;ot&&ot.forEach(function(Je){return Je.revert(!1,!0)}),C.start=P,C.end=rt,Ge=Ne=pn?ce:oe(),!E&&!pn&&(Ge<ce&&oe(ce),C.scroll.rec=0),C.revert(!1,!0),Q=sn(),le&&(q=-1,le.restart(!0)),rn=0,i&&T&&(i._initted||Ye)&&i.progress()!==Ye&&i.progress(Ye||0,!0).render(i.time(),!0,!0),(Lt||fe!==C.progress||E||g||i&&!i._initted)&&(i&&!T&&(i._initted||fe||i.vars.immediateRender!==!1)&&i.totalProgress(E&&P<-.001&&!fe?Me.utils.normalize(P,rt,0):fe,!0),C.progress=Lt||(Ge-P)/S===fe?0:fe),d&&_&&(Z._pinOffset=Math.round(C.progress*ne)),ee&&ee.invalidate(),isNaN(mt)||(mt-=Me.getProperty(F,v.p),Xt-=Me.getProperty(je,v.p),jo(F,v,mt),jo(Fe,v,mt-(ke||0)),jo(je,v,Xt),jo(ze,v,Xt-(ke||0))),Lt&&!pn&&C.update(),u&&!pn&&!A&&(A=!0,u(C),A=!1)}},C.getVelocity=function(){return(oe()-Ne)/(sn()-to)*1e3||0},C.endAnimation=function(){Ys(C.callbackAnimation),i&&(ee?ee.progress(1):i.paused()?T||Ys(i,C.direction<0,1):Ys(i,i.reversed()))},C.labelToScroll=function(pe){return i&&i.labels&&(P||C.refresh()||P)+i.labels[pe]/i.duration()*S||0},C.getTrailing=function(pe){var Le=Qe.indexOf(C),Ce=C.direction>0?Qe.slice(0,Le).reverse():Qe.slice(Le+1);return(Un(pe)?Ce.filter(function(ke){return ke.vars.preventOverlaps===pe}):Ce).filter(function(ke){return C.direction>0?ke.end<=P:ke.start>=rt})},C.update=function(pe,Le,Ce){if(!(E&&!Ce&&!pe)){var ke=pn===!0?ce:C.scroll(),Dt=pe?0:(ke-P)/S,qe=Dt<0?0:Dt>1?1:Dt||0,bt=C.progress,Lt,Mt,gt,dt,Cn,yt,b,U;if(Le&&(Ne=Ge,Ge=E?oe():ke,M&&(L=st,st=i&&!T?i.totalProgress():qe)),p&&d&&!rn&&!Wo&&Qn&&(!qe&&P<ke+(ke-Ne)/(sn()-to)*p?qe=1e-4:qe===1&&rt>ke+(ke-Ne)/(sn()-to)*p&&(qe=.9999)),qe!==bt&&C.enabled){if(Lt=C.isActive=!!qe&&qe<1,Mt=!!bt&&bt<1,yt=Lt!==Mt,Cn=yt||!!qe!=!!bt,C.direction=qe>bt?1:-1,C.progress=qe,Cn&&!rn&&(gt=qe&&!bt?0:qe===1?1:bt===1?2:3,T&&(dt=!yt&&X[gt+1]!=="none"&&X[gt+1]||X[gt],U=i&&(dt==="complete"||dt==="reset"||dt in i))),O&&(yt||U)&&(U||f||!i)&&(an(O)?O(C):C.getTrailing(O).forEach(function(se){return se.endAnimation()})),T||(ee&&!rn&&!Wo?(ee._dp._time-ee._start!==ee._time&&ee.render(ee._dp._time-ee._start),ee.resetTo?ee.resetTo("totalProgress",qe,i._tTime/i._tDur):(ee.vars.totalProgress=qe,ee.invalidate().restart())):i&&i.totalProgress(qe,!!(rn&&(Q||pe)))),d){if(pe&&_&&(Z.style[_+v.os2]=ve),!K)de(io(He+ne*qe));else if(Cn){if(b=!pe&&qe>bt&&rt+1>ke&&ke+1>=vi(N,v),R)if(!pe&&(Lt||b)){var B=Pi(d,!0),k=ke-P;kh(d,ht,B.top+(v===Gt?k:0)+Ht,B.left+(v===Gt?0:k)+Ht)}else kh(d,Z);ws(Lt||b?j:te),ge&&qe<1&&Lt||de(He+(qe===1&&!b?ne:0))}}M&&!we.tween&&!rn&&!Wo&&le.restart(!0),a&&(yt||x&&qe&&(qe<1||!El))&&Ro(a.targets).forEach(function(se){return se.classList[Lt||x?"add":"remove"](a.className)}),o&&!T&&!pe&&o(C),Cn&&!rn?(T&&(U&&(dt==="complete"?i.pause().totalProgress(1):dt==="reset"?i.restart(!0).pause():dt==="restart"?i.restart(!0):i[dt]()),o&&o(C)),(yt||!El)&&(c&&yt&&Kr(C,c),G[gt]&&Kr(C,G[gt]),x&&(qe===1?C.kill(!1,1):G[gt]=0),yt||(gt=qe===1?1:3,G[gt]&&Kr(C,G[gt]))),D&&!Lt&&Math.abs(C.getVelocity())>(ro(D)?D:2500)&&(Ys(C.callbackAnimation),ee?ee.progress(1):Ys(i,dt==="reverse"?1:!qe,1))):T&&o&&!rn&&o(C)}if(Xe){var I=E?ke/E.duration()*(E._caScrollDist||0):ke;Ie(I+(F._isFlipped?1:0)),Xe(I)}_t&&_t(-ke/E.duration()*(E._caScrollDist||0))}},C.enable=function(pe,Le){C.enabled||(C.enabled=!0,$t(N,"resize",so),W||$t(N,"scroll",jr),ae&&$t(r,"refreshInit",ae),pe!==!1&&(C.progress=fe=0,Ge=Ne=q=oe()),Le!==!1&&C.refresh())},C.getTween=function(pe){return pe&&we?we.tween:ee},C.setPositions=function(pe,Le,Ce,ke){if(E){var Dt=E.scrollTrigger,qe=E.duration(),bt=Dt.end-Dt.start;pe=Dt.start+bt*pe/qe,Le=Dt.start+bt*Le/qe}C.refresh(!1,!1,{start:Dh(pe,Ce&&!!C._startClamp),end:Dh(Le,Ce&&!!C._endClamp)},ke),C.update()},C.adjustPinSpacing=function(pe){if(xe&&pe){var Le=xe.indexOf(v.d)+1;xe[Le]=parseFloat(xe[Le])+pe+Ht,xe[1]=parseFloat(xe[1])+pe+Ht,ws(xe)}},C.disable=function(pe,Le){if(pe!==!1&&C.revert(!0,!0),C.enabled&&(C.enabled=C.isActive=!1,Le||ee&&ee.pause(),ce=0,ye&&(ye.uncache=1),ae&&qt(r,"refreshInit",ae),le&&(le.pause(),we.tween&&we.tween.kill()&&(we.tween=0)),!W)){for(var Ce=Qe.length;Ce--;)if(Qe[Ce].scroller===N&&Qe[Ce]!==C)return;qt(N,"resize",so),W||qt(N,"scroll",jr)}},C.kill=function(pe,Le){C.disable(pe,Le),ee&&!Le&&ee.kill(),l&&delete Dc[l];var Ce=Qe.indexOf(C);Ce>=0&&Qe.splice(Ce,1),Ce===dn&&Ca>0&&dn--,Ce=0,Qe.forEach(function(ke){return ke.scroller===C.scroller&&(Ce=1)}),Ce||pn||(C.scroll.rec=0),i&&(i.scrollTrigger=null,pe&&i.revert({kill:!1}),Le||i.kill()),Fe&&[Fe,ze,F,je].forEach(function(ke){return ke.parentNode&&ke.parentNode.removeChild(ke)}),xo===C&&(xo=0),d&&(ye&&(ye.uncache=1),Ce=0,Qe.forEach(function(ke){return ke.pin===d&&Ce++}),Ce||(ye.spacer=0)),n.onKill&&n.onKill(C)},Qe.push(C),C.enable(!1,!1),Tt&&Tt(C),i&&i.add&&!S){var ct=C.update;C.update=function(){C.update=ct,tt.cache++,P||rt||C.refresh()},Me.delayedCall(.01,C.update),S=.01,P=rt=0}else C.refresh();d&&N_()},r.register=function(n){return ds||(Me=n||tp(),ep()&&window.document&&r.enable(),ds=no),ds},r.defaults=function(n){if(n)for(var i in n)$o[i]=n[i];return $o},r.disable=function(n,i){no=0,Qe.forEach(function(o){return o[i?"kill":"disable"](n)}),qt(et,"wheel",jr),qt(pt,"scroll",jr),clearInterval(Vo),qt(pt,"touchcancel",pi),qt(ht,"touchstart",pi),Yo(qt,pt,"pointerdown,touchstart,mousedown",Lh),Yo(qt,pt,"pointerup,touchend,mouseup",Ih),$a.kill(),Xo(qt);for(var s=0;s<tt.length;s+=3)qo(qt,tt[s],tt[s+1]),qo(qt,tt[s],tt[s+2])},r.enable=function(){if(et=window,pt=document,Fn=pt.documentElement,ht=pt.body,Me){if(Ro=Me.utils.toArray,fo=Me.utils.clamp,Cc=Me.core.context||pi,yl=Me.core.suppressOverwrites||pi,Xu=et.history.scrollRestoration||"auto",Lc=et.pageYOffset||0,Me.core.globals("ScrollTrigger",r),ht){no=1,bs=document.createElement("div"),bs.style.height="100vh",bs.style.position="absolute",hp(),R_(),Ft.register(Me),r.isTouch=Ft.isTouch,Ki=Ft.isTouch&&/(iPad|iPhone|iPod|Mac)/g.test(navigator.userAgent),Rc=Ft.isTouch===1,$t(et,"wheel",jr),Wu=[et,pt,Fn,ht],Me.matchMedia?(r.matchMedia=function(u){var f=Me.matchMedia(),h;for(h in u)f.add(h,u[h]);return f},Me.addEventListener("matchMediaInit",function(){cp(),ju()}),Me.addEventListener("matchMediaRevert",function(){return lp()}),Me.addEventListener("matchMedia",function(){Pr(0,1),Vr("matchMedia")}),Me.matchMedia().add("(orientation: portrait)",function(){return bl(),bl})):console.warn("Requires GSAP 3.11.0 or later"),bl(),$t(pt,"scroll",jr);var n=ht.hasAttribute("style"),i=ht.style,s=i.borderTopStyle,o=Me.core.Animation.prototype,a,l;for(o.revert||Object.defineProperty(o,"revert",{value:function(){return this.time(-.01,!0)}}),i.borderTopStyle="solid",a=Pi(ht),Gt.m=Math.round(a.top+Gt.sc())||0,mn.m=Math.round(a.left+mn.sc())||0,s?i.borderTopStyle=s:i.removeProperty("border-top-style"),n||(ht.setAttribute("style",""),ht.removeAttribute("style")),Vo=setInterval(Fh,250),Me.delayedCall(.5,function(){return Wo=0}),$t(pt,"touchcancel",pi),$t(ht,"touchstart",pi),Yo($t,pt,"pointerdown,touchstart,mousedown",Lh),Yo($t,pt,"pointerup,touchend,mouseup",Ih),Ac=Me.utils.checkPrefix("transform"),Pa.push(Ac),ds=sn(),$a=Me.delayedCall(.2,Pr).pause(),ps=[pt,"visibilitychange",function(){var u=et.innerWidth,f=et.innerHeight;pt.hidden?(Rh=u,Ch=f):(Rh!==u||Ch!==f)&&so()},pt,"DOMContentLoaded",Pr,et,"load",Pr,et,"resize",so],Xo($t),Qe.forEach(function(u){return u.enable(0,1)}),l=0;l<tt.length;l+=3)qo(qt,tt[l],tt[l+1]),qo(qt,tt[l],tt[l+2])}else if(pt){var c=function u(){r.enable(),pt.removeEventListener("DOMContentLoaded",u)};pt.addEventListener("DOMContentLoaded",c)}}},r.config=function(n){"limitCallbacks"in n&&(El=!!n.limitCallbacks);var i=n.syncInterval;i&&clearInterval(Vo)||(Vo=i)&&setInterval(Fh,i),"ignoreMobileResize"in n&&(Rc=r.isTouch===1&&n.ignoreMobileResize),"autoRefreshEvents"in n&&(Xo(qt)||Xo($t,n.autoRefreshEvents||"none"),jd=(n.autoRefreshEvents+"").indexOf("resize")===-1)},r.scrollerProxy=function(n,i){var s=Sn(n),o=tt.indexOf(s),a=Hr(s);~o&&tt.splice(o,a?6:2),i&&(a?xi.unshift(et,i,ht,i,Fn,i):xi.unshift(s,i))},r.clearMatchMedia=function(n){Qe.forEach(function(i){return i._ctx&&i._ctx.query===n&&i._ctx.kill(!0,!0)})},r.isInViewport=function(n,i,s){var o=(Un(n)?Sn(n):n).getBoundingClientRect(),a=o[s?Fr:Or]*i||0;return s?o.right-a>0&&o.left+a<et.innerWidth:o.bottom-a>0&&o.top+a<et.innerHeight},r.positionInViewport=function(n,i,s){Un(n)&&(n=Sn(n));var o=n.getBoundingClientRect(),a=o[s?Fr:Or],l=i==null?a/2:i in Za?Za[i]*a:~i.indexOf("%")?parseFloat(i)*a/100:parseFloat(i)||0;return s?(o.left+l)/et.innerWidth:(o.top+l)/et.innerHeight},r.killAll=function(n){if(Qe.slice(0).forEach(function(s){return s.vars.id!=="ScrollSmoother"&&s.kill()}),n!==!0){var i=Gr.killAll||[];Gr={},i.forEach(function(s){return s()})}},r}();Ze.version="3.15.0";Ze.saveStyles=function(r){return r?Ro(r).forEach(function(e){if(e&&e.style){var t=In.indexOf(e);t>=0&&In.splice(t,5),In.push(e,e.style.cssText,e.getBBox&&e.getAttribute("transform"),Me.core.getCache(e),Cc())}}):In};Ze.revert=function(r,e){return ju(!r,e)};Ze.create=function(r,e){return new Ze(r,e)};Ze.refresh=function(r){return r?so(!0):(ds||Ze.register())&&Pr(!0)};Ze.update=function(r){return++tt.cache&&Fi(r===!0?2:0)};Ze.clearScrollMemory=up;Ze.maxScroll=function(r,e){return vi(r,e?mn:Gt)};Ze.getScrollFunc=function(r,e){return ur(Sn(r),e?mn:Gt)};Ze.getById=function(r){return Dc[r]};Ze.getAll=function(){return Qe.filter(function(r){return r.vars.id!=="ScrollSmoother"})};Ze.isScrolling=function(){return!!Qn};Ze.snapDirectional=Zu;Ze.addEventListener=function(r,e){var t=Gr[r]||(Gr[r]=[]);~t.indexOf(e)||t.push(e)};Ze.removeEventListener=function(r,e){var t=Gr[r],n=t&&t.indexOf(e);n>=0&&t.splice(n,1)};Ze.batch=function(r,e){var t=[],n={},i=e.interval||.016,s=e.batchMax||1e9,o=function(c,u){var f=[],h=[],d=Me.delayedCall(i,function(){u(f,h),f=[],h=[]}).pause();return function(_){f.length||d.restart(!0),f.push(_.trigger),h.push(_),s<=f.length&&d.progress(1)}},a;for(a in e)n[a]=a.substr(0,2)==="on"&&an(e[a])&&a!=="onRefreshInit"?o(a,e[a]):e[a];return an(s)&&(s=s(),$t(Ze,"refresh",function(){return s=e.batchMax()})),Ro(r).forEach(function(l){var c={};for(a in n)c[a]=n[a];c.trigger=l,t.push(Ze.create(c))}),t};var Gh=function(e,t,n,i){return t>i?e(i):t<0&&e(0),n>i?(i-t)/(n-t):n<0?t/(t-n):1},Al=function r(e,t){t===!0?e.style.removeProperty("touch-action"):e.style.touchAction=t===!0?"auto":t?"pan-"+t+(Ft.isTouch?" pinch-zoom":""):"none",e===Fn&&r(ht,t)},Jo={auto:1,scroll:1},k_=function(e){var t=e.event,n=e.target,i=e.axis,s=(t.changedTouches?t.changedTouches[0]:t).target,o=s._gsap||Me.core.getCache(s),a=sn(),l;if(!o._isScrollT||a-o._isScrollT>2e3){for(;s&&s!==ht&&(s.scrollHeight<=s.clientHeight&&s.scrollWidth<=s.clientWidth||!(Jo[(l=$n(s)).overflowY]||Jo[l.overflowX]));)s=s.parentNode;o._isScroll=s&&s!==n&&!Hr(s)&&(Jo[(l=$n(s)).overflowY]||Jo[l.overflowX]),o._isScrollT=a}(o._isScroll||i==="x")&&(t.stopPropagation(),t._gsapAllow=!0)},dp=function(e,t,n,i){return Ft.create({target:e,capture:!0,debounce:!1,lockAxis:!0,type:t,onWheel:i=i&&k_,onPress:i,onDrag:i,onScroll:i,onEnable:function(){return n&&$t(pt,Ft.eventTypes[0],Wh,!1,!0)},onDisable:function(){return qt(pt,Ft.eventTypes[0],Wh,!0)}})},H_=/(input|label|select|textarea)/i,Vh,Wh=function(e){var t=H_.test(e.target.tagName);(t||Vh)&&(e._gsapAllow=!0,Vh=t)},G_=function(e){Tr(e)||(e={}),e.preventDefault=e.isNormalizer=e.allowClicks=!0,e.type||(e.type="wheel,touch"),e.debounce=!!e.debounce,e.id=e.id||"normalizer";var t=e,n=t.normalizeScrollX,i=t.momentum,s=t.allowNestedScroll,o=t.onRelease,a,l,c=Sn(e.target)||Fn,u=Me.core.globals().ScrollSmoother,f=u&&u.get(),h=Ki&&(e.content&&Sn(e.content)||f&&e.content!==!1&&!f.smooth()&&f.content()),d=ur(c,Gt),_=ur(c,mn),g=1,p=(Ft.isTouch&&et.visualViewport?et.visualViewport.scale*et.visualViewport.width:et.outerWidth)/et.innerWidth,m=0,y=an(i)?function(){return i(a)}:function(){return i||2.8},x,M,R=dp(c,e.type,!0,s),w=function(){return M=!1},E=pi,D=pi,O=function(){l=vi(c,Gt),D=fo(Ki?1:0,l),n&&(E=fo(0,vi(c,mn))),x=Br},v=function(){h._gsap.y=io(parseFloat(h._gsap.y)+d.offset)+"px",h.style.transform="matrix3d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, "+parseFloat(h._gsap.y)+", 0, 1)",d.offset=d.cacheID=0},T=function(){if(M){requestAnimationFrame(w);var V=io(a.deltaY/2),re=D(d.v-V);if(h&&re!==d.v+d.offset){d.offset=re-d.v;var C=io((parseFloat(h&&h._gsap.y)||0)-d.offset);h.style.transform="matrix3d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, "+C+", 0, 1)",h._gsap.y=C+"px",d.cacheID=tt.cache,Fi()}return!0}d.offset&&v(),M=!0},N,z,W,K,G=function(){O(),N.isActive()&&N.vars.scrollY>l&&(d()>l?N.progress(1)&&d(l):N.resetTo("scrollY",l))};return h&&Me.set(h,{y:"+=0"}),e.ignoreCheck=function(X){return Ki&&X.type==="touchmove"&&T()||g>1.05&&X.type!=="touchstart"||a.isGesturing||X.touches&&X.touches.length>1},e.onPress=function(){M=!1;var X=g;g=io((et.visualViewport&&et.visualViewport.scale||1)/p),N.pause(),X!==g&&Al(c,g>1.01?!0:n?!1:"x"),z=_(),W=d(),O(),x=Br},e.onRelease=e.onGestureStart=function(X,V){if(d.offset&&v(),!V)K.restart(!0);else{tt.cache++;var re=y(),C,ae;n&&(C=_(),ae=C+re*.05*-X.velocityX/.227,re*=Gh(_,C,ae,vi(c,mn)),N.vars.scrollX=E(ae)),C=d(),ae=C+re*.05*-X.velocityY/.227,re*=Gh(d,C,ae,vi(c,Gt)),N.vars.scrollY=D(ae),N.invalidate().duration(re).play(.01),(Ki&&N.vars.scrollY>=l||C>=l-1)&&Me.to({},{onUpdate:G,duration:re})}o&&o(X)},e.onWheel=function(){N._ts&&N.pause(),sn()-m>1e3&&(x=0,m=sn())},e.onChange=function(X,V,re,C,ae){if(Br!==x&&O(),V&&n&&_(E(C[2]===V?z+(X.startX-X.x):_()+V-C[1])),re){d.offset&&v();var Be=ae[2]===re,We=Be?W+X.startY-X.y:d()+re-ae[1],q=D(We);Be&&We!==q&&(W+=q-We),d(q)}(re||V)&&Fi()},e.onEnable=function(){Al(c,n?!1:"x"),Ze.addEventListener("refresh",G),$t(et,"resize",G),d.smooth&&(d.target.style.scrollBehavior="auto",d.smooth=_.smooth=!1),R.enable()},e.onDisable=function(){Al(c,!0),qt(et,"resize",G),Ze.removeEventListener("refresh",G),R.kill()},e.lockAxis=e.lockAxis!==!1,a=new Ft(e),a.iOS=Ki,Ki&&!d()&&d(1),Ki&&Me.ticker.add(pi),K=a._dc,N=Me.to(a,{ease:"power4",paused:!0,inherit:!1,scrollX:n?"+=0.1":"+=0",scrollY:"+=0.1",modifiers:{scrollY:fp(d,d(),function(){return N.pause()})},onUpdate:Fi,onComplete:K.vars.onComplete}),a};Ze.sort=function(r){if(an(r))return Qe.sort(r);var e=et.pageYOffset||0;return Ze.getAll().forEach(function(t){return t._sortY=t.trigger?e+t.trigger.getBoundingClientRect().top:t.start+et.innerHeight}),Qe.sort(r||function(t,n){return(t.vars.refreshPriority||0)*-1e6+(t.vars.containerAnimation?1e6:t._sortY)-((n.vars.containerAnimation?1e6:n._sortY)+(n.vars.refreshPriority||0)*-1e6)})};Ze.observe=function(r){return new Ft(r)};Ze.normalizeScroll=function(r){if(typeof r>"u")return fn;if(r===!0&&fn)return fn.enable();if(r===!1){fn&&fn.kill(),fn=r;return}var e=r instanceof Ft?r:G_(r);return fn&&fn.target===e.target&&fn.kill(),Hr(e.target)&&(fn=e),e};Ze.core={_getVelocityProp:wc,_inputObserver:dp,_scrollers:tt,_proxies:xi,bridge:{ss:function(){Qn||Vr("scrollStart"),Qn=sn()},ref:function(){return rn}}};tp()&&Me.registerPlugin(Ze);var Xh="1.3.26";function pp(r,e,t){return Math.max(r,Math.min(e,t))}function V_(r,e,t){return(1-t)*r+t*e}function W_(r,e,t,n){return V_(r,e,1-Math.exp(-t*n))}function X_(r,e){return(r%e+e)%e}var Y_=class{constructor(){Ee(this,"isRunning",!1);Ee(this,"value",0);Ee(this,"from",0);Ee(this,"to",0);Ee(this,"currentTime",0);Ee(this,"lerp");Ee(this,"duration");Ee(this,"easing");Ee(this,"onUpdate")}advance(r){if(!this.isRunning)return;let e=!1;if(this.duration&&this.easing){this.currentTime+=r;const t=pp(0,this.currentTime/this.duration,1);e=t>=1;const n=e?1:this.easing(t);this.value=this.from+(this.to-this.from)*n}else this.lerp?(this.value=W_(this.value,this.to,this.lerp*60,r),Math.round(this.value)===Math.round(this.to)&&(this.value=this.to,e=!0)):(this.value=this.to,e=!0);e&&this.stop(),this.onUpdate?.(this.value,e)}stop(){this.isRunning=!1}fromTo(r,e,{lerp:t,duration:n,easing:i,onStart:s,onUpdate:o}){this.from=this.value=r,this.to=e,this.lerp=t,this.duration=n,this.easing=i,this.currentTime=0,this.isRunning=!0,s?.(),this.onUpdate=o}};function q_(r,e){let t;return function(...n){clearTimeout(t),t=setTimeout(()=>{t=void 0,r.apply(this,n)},e)}}var $_=class{constructor(r,e,{autoResize:t=!0,debounce:n=250}={}){Ee(this,"width",0);Ee(this,"height",0);Ee(this,"scrollHeight",0);Ee(this,"scrollWidth",0);Ee(this,"debouncedResize");Ee(this,"wrapperResizeObserver");Ee(this,"contentResizeObserver");Ee(this,"resize",()=>{this.onWrapperResize(),this.onContentResize()});Ee(this,"onWrapperResize",()=>{this.wrapper instanceof Window?(this.width=window.innerWidth,this.height=window.innerHeight):(this.width=this.wrapper.clientWidth,this.height=this.wrapper.clientHeight)});Ee(this,"onContentResize",()=>{this.wrapper instanceof Window?(this.scrollHeight=this.content.scrollHeight,this.scrollWidth=this.content.scrollWidth):(this.scrollHeight=this.wrapper.scrollHeight,this.scrollWidth=this.wrapper.scrollWidth)});this.wrapper=r,this.content=e,t&&(this.debouncedResize=q_(this.resize,n),this.wrapper instanceof Window?window.addEventListener("resize",this.debouncedResize):(this.wrapperResizeObserver=new ResizeObserver(this.debouncedResize),this.wrapperResizeObserver.observe(this.wrapper)),this.contentResizeObserver=new ResizeObserver(this.debouncedResize),this.contentResizeObserver.observe(this.content)),this.resize()}destroy(){this.wrapperResizeObserver?.disconnect(),this.contentResizeObserver?.disconnect(),this.wrapper===window&&this.debouncedResize&&window.removeEventListener("resize",this.debouncedResize)}get limit(){return{x:this.scrollWidth-this.width,y:this.scrollHeight-this.height}}},mp=class{constructor(){Ee(this,"events",{})}emit(r,...e){const t=this.events[r]||[];for(let n=0,i=t.length;n<i;n++)t[n]?.(...e)}on(r,e){return this.events[r]?this.events[r].push(e):this.events[r]=[e],()=>{this.events[r]=this.events[r]?.filter(t=>e!==t)}}off(r,e){this.events[r]=this.events[r]?.filter(t=>e!==t)}destroy(){this.events={}}};const K_=100/6,Gi={passive:!1};function Yh(r,e){return r===1?K_:r===2?e:1}var Z_=class{constructor(r,e={wheelMultiplier:1,touchMultiplier:1}){Ee(this,"touchStart",{x:0,y:0});Ee(this,"lastDelta",{x:0,y:0});Ee(this,"window",{width:0,height:0});Ee(this,"emitter",new mp);Ee(this,"onTouchStart",r=>{const{clientX:e,clientY:t}=r.targetTouches?r.targetTouches[0]:r;this.touchStart.x=e,this.touchStart.y=t,this.lastDelta={x:0,y:0},this.emitter.emit("scroll",{deltaX:0,deltaY:0,event:r})});Ee(this,"onTouchMove",r=>{const{clientX:e,clientY:t}=r.targetTouches?r.targetTouches[0]:r,n=-(e-this.touchStart.x)*this.options.touchMultiplier,i=-(t-this.touchStart.y)*this.options.touchMultiplier;this.touchStart.x=e,this.touchStart.y=t,this.lastDelta={x:n,y:i},this.emitter.emit("scroll",{deltaX:n,deltaY:i,event:r})});Ee(this,"onTouchEnd",r=>{this.emitter.emit("scroll",{deltaX:this.lastDelta.x,deltaY:this.lastDelta.y,event:r})});Ee(this,"onWheel",r=>{let{deltaX:e,deltaY:t,deltaMode:n}=r;const i=Yh(n,this.window.width),s=Yh(n,this.window.height);e*=i,t*=s,e*=this.options.wheelMultiplier,t*=this.options.wheelMultiplier,this.emitter.emit("scroll",{deltaX:e,deltaY:t,event:r})});Ee(this,"onWindowResize",()=>{this.window={width:window.innerWidth,height:window.innerHeight}});this.element=r,this.options=e,window.addEventListener("resize",this.onWindowResize),this.onWindowResize(),this.element.addEventListener("wheel",this.onWheel,Gi),this.element.addEventListener("touchstart",this.onTouchStart,Gi),this.element.addEventListener("touchmove",this.onTouchMove,Gi),this.element.addEventListener("touchend",this.onTouchEnd,Gi)}on(r,e){return this.emitter.on(r,e)}destroy(){this.emitter.destroy(),window.removeEventListener("resize",this.onWindowResize),this.element.removeEventListener("wheel",this.onWheel,Gi),this.element.removeEventListener("touchstart",this.onTouchStart,Gi),this.element.removeEventListener("touchmove",this.onTouchMove,Gi),this.element.removeEventListener("touchend",this.onTouchEnd,Gi)}};const qh=r=>Math.min(1,1.001-2**(-10*r));var j_=class{constructor({wrapper:r=window,content:e=document.documentElement,eventsTarget:t=r,smoothWheel:n=!0,syncTouch:i=!1,syncTouchLerp:s=.075,touchInertiaExponent:o=1.7,duration:a,easing:l,lerp:c=.1,infinite:u=!1,orientation:f="vertical",gestureOrientation:h=f==="horizontal"?"both":"vertical",touchMultiplier:d=1,wheelMultiplier:_=1,autoResize:g=!0,prevent:p,virtualScroll:m,overscroll:y=!0,autoRaf:x=!1,anchors:M=!1,autoToggle:R=!1,allowNestedScroll:w=!1,__experimental__naiveDimensions:E=!1,naiveDimensions:D=E,stopInertiaOnNavigate:O=!1,respectReducedMotion:v=!0}={}){Ee(this,"_isScrolling",!1);Ee(this,"_isStopped",!1);Ee(this,"_isLocked",!1);Ee(this,"_preventNextNativeScrollEvent",!1);Ee(this,"_resetVelocityTimeout",null);Ee(this,"_rafId",null);Ee(this,"_isDraggingSelection",!1);Ee(this,"reducedMotionMediaQuery",window.matchMedia("(prefers-reduced-motion: reduce)"));Ee(this,"isTouching");Ee(this,"isIos");Ee(this,"time",0);Ee(this,"userData",{});Ee(this,"lastVelocity",0);Ee(this,"velocity",0);Ee(this,"direction",0);Ee(this,"options");Ee(this,"targetScroll");Ee(this,"animatedScroll");Ee(this,"animate",new Y_);Ee(this,"emitter",new mp);Ee(this,"dimensions");Ee(this,"virtualScroll");Ee(this,"onScrollEnd",r=>{r instanceof CustomEvent||(this.isScrolling==="smooth"||this.isScrolling===!1)&&r.stopPropagation()});Ee(this,"dispatchScrollendEvent",()=>{this.options.wrapper.dispatchEvent(new CustomEvent("scrollend",{bubbles:this.options.wrapper===window,detail:{lenisScrollEnd:!0}}))});Ee(this,"onTransitionEnd",r=>{r.propertyName?.includes("overflow")&&r.target===this.rootElement&&this.checkOverflow()});Ee(this,"onClick",r=>{const e=r.composedPath().filter(n=>n instanceof HTMLAnchorElement&&n.href).map(n=>new URL(n.href)),t=new URL(window.location.href);if(this.options.anchors){const n=e.find(i=>t.host===i.host&&t.pathname===i.pathname&&i.hash);if(n){const i=typeof this.options.anchors=="object"&&this.options.anchors?this.options.anchors:void 0,s=decodeURIComponent(n.hash);this.scrollTo(s,i);return}}if(this.options.stopInertiaOnNavigate&&e.some(n=>t.host===n.host&&t.pathname!==n.pathname)){this.reset();return}});Ee(this,"onPointerDown",r=>{r.button===1&&this.reset()});Ee(this,"onVirtualScroll",r=>{if(typeof this.options.virtualScroll=="function"&&this.options.virtualScroll(r)===!1)return;const{deltaX:e,deltaY:t,event:n}=r;if(this.emitter.emit("virtual-scroll",{deltaX:e,deltaY:t,event:n}),n.ctrlKey||n.lenisStopPropagation)return;const i=n.type.includes("touch"),s=n.type.includes("wheel");if(i&&this.isIos&&(n.type==="touchstart"&&(this._isDraggingSelection=this.isTouchOnSelectionHandle(n)),this._isDraggingSelection)){n.type==="touchend"&&(this._isDraggingSelection=!1);return}this.isTouching=n.type==="touchstart"||n.type==="touchmove";const o=e===0&&t===0;if(this.options.syncTouch&&i&&n.type==="touchstart"&&o&&!this.isStopped&&!this.isLocked){this.reset();return}const a=this.options.gestureOrientation==="vertical"&&t===0||this.options.gestureOrientation==="horizontal"&&e===0;if(o||a)return;let l=n.composedPath();l=l.slice(0,l.indexOf(this.rootElement));const c=this.options.prevent,u=Math.abs(e)>=Math.abs(t)?"horizontal":"vertical";if(l.find(_=>_ instanceof HTMLElement&&(typeof c=="function"&&c?.(_)||_.hasAttribute?.("data-lenis-prevent")||u==="vertical"&&_.hasAttribute?.("data-lenis-prevent-vertical")||u==="horizontal"&&_.hasAttribute?.("data-lenis-prevent-horizontal")||i&&_.hasAttribute?.("data-lenis-prevent-touch")||s&&_.hasAttribute?.("data-lenis-prevent-wheel")||this.options.allowNestedScroll&&this.hasNestedScroll(_,{deltaX:e,deltaY:t}))))return;if(this.isStopped||this.isLocked){n.cancelable&&n.preventDefault();return}if(!(this.options.syncTouch&&i||this.options.smoothWheel&&s)){this.isScrolling="native",this.animate.stop(),n.lenisStopPropagation=!0;return}let f=t;this.options.gestureOrientation==="both"?f=Math.abs(t)>Math.abs(e)?t:e:this.options.gestureOrientation==="horizontal"&&(f=e),(!this.options.overscroll||this.options.infinite||this.options.wrapper!==window&&this.limit>0&&(this.animatedScroll>0&&this.animatedScroll<this.limit||this.animatedScroll===0&&t>0||this.animatedScroll===this.limit&&t<0))&&(n.lenisStopPropagation=!0),n.cancelable&&n.preventDefault();const h=i&&this.options.syncTouch,d=i&&n.type==="touchend";d&&(f=Math.sign(f)*Math.abs(this.velocity)**this.options.touchInertiaExponent),this.scrollTo(this.targetScroll+f,{programmatic:!1,...h?{lerp:d?this.options.syncTouchLerp:1}:{lerp:this.options.lerp,duration:this.options.duration,easing:this.options.easing}})});Ee(this,"onNativeScroll",()=>{if(this._resetVelocityTimeout!==null&&(clearTimeout(this._resetVelocityTimeout),this._resetVelocityTimeout=null),this._preventNextNativeScrollEvent){this._preventNextNativeScrollEvent=!1;return}if(this.isScrolling===!1||this.isScrolling==="native"){const r=this.animatedScroll;this.animatedScroll=this.targetScroll=this.actualScroll,this.lastVelocity=this.velocity,this.velocity=this.animatedScroll-r,this.direction=Math.sign(this.animatedScroll-r),this.isStopped||(this.isScrolling="native"),this.emit(),this.velocity!==0&&(this._resetVelocityTimeout=setTimeout(()=>{this.lastVelocity=this.velocity,this.velocity=0,this.isScrolling=!1,this.emit()},400))}});Ee(this,"raf",r=>{const e=r-(this.time||r);this.time=r,this.animate.advance(e*.001),this.options.autoRaf&&(this._rafId=requestAnimationFrame(this.raf))});window.lenisVersion=Xh,window.lenis||(window.lenis={}),window.lenis.version=Xh,f==="horizontal"&&(window.lenis.horizontal=!0),i===!0&&(window.lenis.touch=!0),this.isIos=/(iPad|iPhone|iPod)/g.test(navigator.userAgent),(!r||r===document.documentElement)&&(r=window),typeof a=="number"&&typeof l!="function"?l=qh:typeof l=="function"&&typeof a!="number"&&(a=1),this.options={wrapper:r,content:e,eventsTarget:t,smoothWheel:n,syncTouch:i,syncTouchLerp:s,touchInertiaExponent:o,duration:a,easing:l,lerp:c,infinite:u,gestureOrientation:h,orientation:f,touchMultiplier:d,wheelMultiplier:_,autoResize:g,prevent:p,virtualScroll:m,overscroll:y,autoRaf:x,anchors:M,autoToggle:R,allowNestedScroll:w,naiveDimensions:D,stopInertiaOnNavigate:O,respectReducedMotion:v},this.dimensions=new $_(r,e,{autoResize:g}),this.updateClassName(),this.targetScroll=this.animatedScroll=this.actualScroll,this.options.wrapper.addEventListener("scroll",this.onNativeScroll),this.options.wrapper.addEventListener("scrollend",this.onScrollEnd,{capture:!0}),(this.options.anchors||this.options.stopInertiaOnNavigate)&&this.options.wrapper.addEventListener("click",this.onClick),this.options.wrapper.addEventListener("pointerdown",this.onPointerDown),this.virtualScroll=new Z_(t,{touchMultiplier:d,wheelMultiplier:_}),this.virtualScroll.on("scroll",this.onVirtualScroll),this.options.autoToggle&&(this.checkOverflow(),this.rootElement.addEventListener("transitionend",this.onTransitionEnd)),this.options.autoRaf&&(this._rafId=requestAnimationFrame(this.raf))}destroy(){this.emitter.destroy(),this.options.wrapper.removeEventListener("scroll",this.onNativeScroll),this.options.wrapper.removeEventListener("scrollend",this.onScrollEnd,{capture:!0}),this.options.wrapper.removeEventListener("pointerdown",this.onPointerDown),(this.options.anchors||this.options.stopInertiaOnNavigate)&&this.options.wrapper.removeEventListener("click",this.onClick),this.virtualScroll.destroy(),this.dimensions.destroy(),this.cleanUpClassName(),this._rafId&&cancelAnimationFrame(this._rafId)}on(r,e){return this.emitter.on(r,e)}off(r,e){return this.emitter.off(r,e)}get overflow(){const r=this.isHorizontal?"overflow-x":"overflow-y";return getComputedStyle(this.rootElement)[r]}checkOverflow(){["hidden","clip"].includes(this.overflow)?this.internalStop():this.internalStart()}setScroll(r){this.isHorizontal?this.options.wrapper.scrollTo({left:r,behavior:"instant"}):this.options.wrapper.scrollTo({top:r,behavior:"instant"})}isTouchOnSelectionHandle(r){const e=window.getSelection();if(!e||e.isCollapsed||e.rangeCount===0)return!1;const t=r.targetTouches[0]??r.changedTouches[0];if(!t)return!1;const n=e.getRangeAt(0).getClientRects();if(n.length===0)return!1;const i=n[0],s=n[n.length-1],o=40,a=Math.hypot(t.clientX-i.left,t.clientY-i.top)<=o,l=Math.hypot(t.clientX-s.right,t.clientY-s.bottom)<=o;return a||l}resize(){this.dimensions.resize(),this.animatedScroll=this.targetScroll=this.actualScroll,this.emit()}emit(){this.emitter.emit("scroll",this)}reset(){this.isLocked=!1,this.isScrolling=!1,this.animatedScroll=this.targetScroll=this.actualScroll,this.lastVelocity=this.velocity=0,this.animate.stop()}start(){if(this.isStopped){if(this.options.autoToggle){this.rootElement.style.removeProperty("overflow");return}this.internalStart()}}internalStart(){this.isStopped&&(this.reset(),this.isStopped=!1,this.emit())}stop(){if(!this.isStopped){if(this.options.autoToggle){this.rootElement.style.setProperty("overflow","clip");return}this.internalStop()}}internalStop(){this.isStopped||(this.reset(),this.isStopped=!0,this.emit())}scrollTo(r,{offset:e=0,immediate:t=!1,lock:n=!1,programmatic:i=!0,lerp:s=i?this.options.lerp:void 0,duration:o=i?this.options.duration:void 0,easing:a=i?this.options.easing:void 0,onStart:l,onComplete:c,force:u=!1,userData:f}={}){if(this.prefersReducedMotion&&(i?t=!0:(s=1,o=void 0,a=void 0)),(this.isStopped||this.isLocked)&&!u)return;let h=r,d=e;if(typeof h=="string"&&["top","left","start","#"].includes(h))h=0;else if(typeof h=="string"&&["bottom","right","end"].includes(h))h=this.limit;else{let _=null;if(typeof h=="string"?(_=h.startsWith("#")?document.getElementById(h.slice(1)):document.querySelector(h),_||(h==="#top"?h=0:console.warn("Lenis: Target not found",h))):h instanceof HTMLElement&&h?.nodeType&&(_=h),_){if(this.options.wrapper!==window){const M=this.rootElement.getBoundingClientRect();d-=this.isHorizontal?M.left:M.top}const g=_.getBoundingClientRect(),p=getComputedStyle(_),m=this.isHorizontal?Number.parseFloat(p.scrollMarginLeft):Number.parseFloat(p.scrollMarginTop),y=getComputedStyle(this.rootElement),x=this.isHorizontal?Number.parseFloat(y.scrollPaddingLeft):Number.parseFloat(y.scrollPaddingTop);h=(this.isHorizontal?g.left:g.top)+this.animatedScroll-(Number.isNaN(m)?0:m)-(Number.isNaN(x)?0:x)}}if(typeof h=="number"){if(h+=d,this.options.infinite){if(i){this.targetScroll=this.animatedScroll=this.scroll;const _=h-this.animatedScroll;_>this.limit/2?h-=this.limit:_<-this.limit/2&&(h+=this.limit)}}else h=pp(0,h,this.limit);if(h===this.targetScroll){l?.(this),c?.(this);return}if(this.userData=f??{},t){this.animatedScroll=this.targetScroll=h,this.setScroll(this.scroll),this.reset(),this.preventNextNativeScrollEvent(),this.emit(),c?.(this),this.userData={},requestAnimationFrame(()=>{this.dispatchScrollendEvent()});return}i||(this.targetScroll=h),typeof o=="number"&&typeof a!="function"?a=qh:typeof a=="function"&&typeof o!="number"&&(o=1),this.animate.fromTo(this.animatedScroll,h,{duration:o,easing:a,lerp:s,onStart:()=>{n&&(this.isLocked=!0),this.isScrolling="smooth",l?.(this)},onUpdate:(_,g)=>{this.isScrolling="smooth",this.lastVelocity=this.velocity,this.velocity=_-this.animatedScroll,this.direction=Math.sign(this.velocity),this.animatedScroll=_,this.setScroll(this.scroll),i&&(this.targetScroll=_),g||this.emit(),g&&(this.reset(),this.emit(),c?.(this),this.userData={},requestAnimationFrame(()=>{this.dispatchScrollendEvent()}),this.preventNextNativeScrollEvent())}})}}preventNextNativeScrollEvent(){this._preventNextNativeScrollEvent=!0,requestAnimationFrame(()=>{this._preventNextNativeScrollEvent=!1})}hasNestedScroll(r,{deltaX:e,deltaY:t}){const n=Date.now();r._lenis||(r._lenis={});const i=r._lenis;let s,o,a,l,c,u,f,h,d,_;if(n-(i.time??0)>2e3){i.time=Date.now();const w=window.getComputedStyle(r);if(i.computedStyle=w,s=["auto","overlay","scroll"].includes(w.overflowX),o=["auto","overlay","scroll"].includes(w.overflowY),c=["auto"].includes(w.overscrollBehaviorX),u=["auto"].includes(w.overscrollBehaviorY),i.hasOverflowX=s,i.hasOverflowY=o,!(s||o))return!1;f=r.scrollWidth,h=r.scrollHeight,d=r.clientWidth,_=r.clientHeight,a=f>d,l=h>_,i.isScrollableX=a,i.isScrollableY=l,i.scrollWidth=f,i.scrollHeight=h,i.clientWidth=d,i.clientHeight=_,i.hasOverscrollBehaviorX=c,i.hasOverscrollBehaviorY=u}else a=i.isScrollableX,l=i.isScrollableY,s=i.hasOverflowX,o=i.hasOverflowY,f=i.scrollWidth,h=i.scrollHeight,d=i.clientWidth,_=i.clientHeight,c=i.hasOverscrollBehaviorX,u=i.hasOverscrollBehaviorY;if(!(s&&a||o&&l))return!1;const g=Math.abs(e)>=Math.abs(t)?"horizontal":"vertical";let p,m,y,x,M,R;if(g==="horizontal")p=Math.round(r.scrollLeft),m=f-d,y=e,x=s,M=a,R=c;else if(g==="vertical")p=Math.round(r.scrollTop),m=h-_,y=t,x=o,M=l,R=u;else return!1;return!R&&(p>=m||p<=0)?!0:(y>0?p<m:p>0)&&x&&M}get rootElement(){return this.options.wrapper===window?document.documentElement:this.options.wrapper}get limit(){return this.options.naiveDimensions?this.isHorizontal?this.rootElement.scrollWidth-this.rootElement.clientWidth:this.rootElement.scrollHeight-this.rootElement.clientHeight:this.dimensions.limit[this.isHorizontal?"x":"y"]}get isHorizontal(){return this.options.orientation==="horizontal"}get actualScroll(){const r=this.options.wrapper;return this.isHorizontal?r.scrollX??r.scrollLeft:r.scrollY??r.scrollTop}get scroll(){return this.options.infinite?X_(this.animatedScroll,this.limit):this.animatedScroll}get progress(){return this.limit===0?1:this.scroll/this.limit}get isScrolling(){return this._isScrolling}set isScrolling(r){this._isScrolling!==r&&(this._isScrolling=r,this.updateClassName())}get isStopped(){return this._isStopped}set isStopped(r){this._isStopped!==r&&(this._isStopped=r,this.updateClassName())}get isLocked(){return this._isLocked}set isLocked(r){this._isLocked!==r&&(this._isLocked=r,this.updateClassName())}get isSmooth(){return this.isScrolling==="smooth"}get prefersReducedMotion(){return this.options.respectReducedMotion&&this.reducedMotionMediaQuery.matches}get className(){let r="lenis";return this.options.autoToggle&&(r+=" lenis-autoToggle"),this.isStopped&&(r+=" lenis-stopped"),this.isLocked&&(r+=" lenis-locked"),this.isScrolling&&(r+=" lenis-scrolling"),this.isScrolling==="smooth"&&(r+=" lenis-smooth"),r}updateClassName(){this.cleanUpClassName(),this.className.split(" ").forEach(r=>{this.rootElement.classList.add(r)})}cleanUpClassName(){for(const r of Array.from(this.rootElement.classList))(r==="lenis"||r.startsWith("lenis-"))&&this.rootElement.classList.remove(r)}};/**
 * @license
 * Copyright 2010-2024 Three.js Authors
 * SPDX-License-Identifier: MIT
 */const Ju="169",J_=0,$h=1,Q_=2,_p=1,eg=2,Ai=3,hr=0,_n=1,Di=2,sr=0,zr=1,Uc=2,Kh=3,Zh=4,tg=5,Ar=100,ng=101,ig=102,rg=103,sg=104,og=200,ag=201,lg=202,cg=203,Nc=204,Fc=205,ug=206,hg=207,fg=208,dg=209,pg=210,mg=211,_g=212,gg=213,vg=214,Oc=0,Bc=1,zc=2,Fs=3,kc=4,Hc=5,Gc=6,Vc=7,gp=0,xg=1,Sg=2,or=0,Mg=1,yg=2,Eg=3,Tg=4,bg=5,wg=6,Ag=7,vp=300,Os=301,Bs=302,Wc=303,Xc=304,al=306,Yc=1e3,Ii=1001,qc=1002,Jn=1003,Rg=1004,Qo=1005,li=1006,Rl=1007,Dr=1008,zi=1009,xp=1010,Sp=1011,Po=1012,Qu=1013,Wr=1014,Ui=1015,Lo=1016,eh=1017,th=1018,zs=1020,Mp=35902,yp=1021,Ep=1022,ui=1023,Tp=1024,bp=1025,As=1026,ks=1027,wp=1028,nh=1029,Ap=1030,ih=1031,rh=1033,La=33776,Ia=33777,Ua=33778,Na=33779,$c=35840,Kc=35841,Zc=35842,jc=35843,Jc=36196,Qc=37492,eu=37496,tu=37808,nu=37809,iu=37810,ru=37811,su=37812,ou=37813,au=37814,lu=37815,cu=37816,uu=37817,hu=37818,fu=37819,du=37820,pu=37821,Fa=36492,mu=36494,_u=36495,Rp=36283,gu=36284,vu=36285,xu=36286,Cg=3200,Pg=3201,Dg=0,Lg=1,Zi="",ai="srgb",dr="srgb-linear",sh="display-p3",ll="display-p3-linear",ja="linear",Et="srgb",Ja="rec709",Qa="p3",Jr=7680,jh=519,Ig=512,Ug=513,Ng=514,Cp=515,Fg=516,Og=517,Bg=518,zg=519,Jh=35044,Qh="300 es",Ni=2e3,el=2001;class Gs{addEventListener(e,t){this._listeners===void 0&&(this._listeners={});const n=this._listeners;n[e]===void 0&&(n[e]=[]),n[e].indexOf(t)===-1&&n[e].push(t)}hasEventListener(e,t){if(this._listeners===void 0)return!1;const n=this._listeners;return n[e]!==void 0&&n[e].indexOf(t)!==-1}removeEventListener(e,t){if(this._listeners===void 0)return;const i=this._listeners[e];if(i!==void 0){const s=i.indexOf(t);s!==-1&&i.splice(s,1)}}dispatchEvent(e){if(this._listeners===void 0)return;const n=this._listeners[e.type];if(n!==void 0){e.target=this;const i=n.slice(0);for(let s=0,o=i.length;s<o;s++)i[s].call(this,e);e.target=null}}}const tn=["00","01","02","03","04","05","06","07","08","09","0a","0b","0c","0d","0e","0f","10","11","12","13","14","15","16","17","18","19","1a","1b","1c","1d","1e","1f","20","21","22","23","24","25","26","27","28","29","2a","2b","2c","2d","2e","2f","30","31","32","33","34","35","36","37","38","39","3a","3b","3c","3d","3e","3f","40","41","42","43","44","45","46","47","48","49","4a","4b","4c","4d","4e","4f","50","51","52","53","54","55","56","57","58","59","5a","5b","5c","5d","5e","5f","60","61","62","63","64","65","66","67","68","69","6a","6b","6c","6d","6e","6f","70","71","72","73","74","75","76","77","78","79","7a","7b","7c","7d","7e","7f","80","81","82","83","84","85","86","87","88","89","8a","8b","8c","8d","8e","8f","90","91","92","93","94","95","96","97","98","99","9a","9b","9c","9d","9e","9f","a0","a1","a2","a3","a4","a5","a6","a7","a8","a9","aa","ab","ac","ad","ae","af","b0","b1","b2","b3","b4","b5","b6","b7","b8","b9","ba","bb","bc","bd","be","bf","c0","c1","c2","c3","c4","c5","c6","c7","c8","c9","ca","cb","cc","cd","ce","cf","d0","d1","d2","d3","d4","d5","d6","d7","d8","d9","da","db","dc","dd","de","df","e0","e1","e2","e3","e4","e5","e6","e7","e8","e9","ea","eb","ec","ed","ee","ef","f0","f1","f2","f3","f4","f5","f6","f7","f8","f9","fa","fb","fc","fd","fe","ff"],Cl=Math.PI/180,Su=180/Math.PI;function Io(){const r=Math.random()*4294967295|0,e=Math.random()*4294967295|0,t=Math.random()*4294967295|0,n=Math.random()*4294967295|0;return(tn[r&255]+tn[r>>8&255]+tn[r>>16&255]+tn[r>>24&255]+"-"+tn[e&255]+tn[e>>8&255]+"-"+tn[e>>16&15|64]+tn[e>>24&255]+"-"+tn[t&63|128]+tn[t>>8&255]+"-"+tn[t>>16&255]+tn[t>>24&255]+tn[n&255]+tn[n>>8&255]+tn[n>>16&255]+tn[n>>24&255]).toLowerCase()}function Mn(r,e,t){return Math.max(e,Math.min(t,r))}function kg(r,e){return(r%e+e)%e}function Pl(r,e,t){return(1-t)*r+t*e}function qs(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return r/4294967295;case Uint16Array:return r/65535;case Uint8Array:return r/255;case Int32Array:return Math.max(r/2147483647,-1);case Int16Array:return Math.max(r/32767,-1);case Int8Array:return Math.max(r/127,-1);default:throw new Error("Invalid component type.")}}function xn(r,e){switch(e.constructor){case Float32Array:return r;case Uint32Array:return Math.round(r*4294967295);case Uint16Array:return Math.round(r*65535);case Uint8Array:return Math.round(r*255);case Int32Array:return Math.round(r*2147483647);case Int16Array:return Math.round(r*32767);case Int8Array:return Math.round(r*127);default:throw new Error("Invalid component type.")}}class St{constructor(e=0,t=0){St.prototype.isVector2=!0,this.x=e,this.y=t}get width(){return this.x}set width(e){this.x=e}get height(){return this.y}set height(e){this.y=e}set(e,t){return this.x=e,this.y=t,this}setScalar(e){return this.x=e,this.y=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y)}copy(e){return this.x=e.x,this.y=e.y,this}add(e){return this.x+=e.x,this.y+=e.y,this}addScalar(e){return this.x+=e,this.y+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this}subScalar(e){return this.x-=e,this.y-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this}multiply(e){return this.x*=e.x,this.y*=e.y,this}multiplyScalar(e){return this.x*=e,this.y*=e,this}divide(e){return this.x/=e.x,this.y/=e.y,this}divideScalar(e){return this.multiplyScalar(1/e)}applyMatrix3(e){const t=this.x,n=this.y,i=e.elements;return this.x=i[0]*t+i[3]*n+i[6],this.y=i[1]*t+i[4]*n+i[7],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this}negate(){return this.x=-this.x,this.y=-this.y,this}dot(e){return this.x*e.x+this.y*e.y}cross(e){return this.x*e.y-this.y*e.x}lengthSq(){return this.x*this.x+this.y*this.y}length(){return Math.sqrt(this.x*this.x+this.y*this.y)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)}normalize(){return this.divideScalar(this.length()||1)}angle(){return Math.atan2(-this.y,-this.x)+Math.PI}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Mn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y;return t*t+n*n}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this}equals(e){return e.x===this.x&&e.y===this.y}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this}rotateAround(e,t){const n=Math.cos(t),i=Math.sin(t),s=this.x-e.x,o=this.y-e.y;return this.x=s*n-o*i+e.x,this.y=s*i+o*n+e.y,this}random(){return this.x=Math.random(),this.y=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y}}class Ke{constructor(e,t,n,i,s,o,a,l,c){Ke.prototype.isMatrix3=!0,this.elements=[1,0,0,0,1,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,o,a,l,c)}set(e,t,n,i,s,o,a,l,c){const u=this.elements;return u[0]=e,u[1]=i,u[2]=a,u[3]=t,u[4]=s,u[5]=l,u[6]=n,u[7]=o,u[8]=c,this}identity(){return this.set(1,0,0,0,1,0,0,0,1),this}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],this}extractBasis(e,t,n){return e.setFromMatrix3Column(this,0),t.setFromMatrix3Column(this,1),n.setFromMatrix3Column(this,2),this}setFromMatrix4(e){const t=e.elements;return this.set(t[0],t[4],t[8],t[1],t[5],t[9],t[2],t[6],t[10]),this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,o=n[0],a=n[3],l=n[6],c=n[1],u=n[4],f=n[7],h=n[2],d=n[5],_=n[8],g=i[0],p=i[3],m=i[6],y=i[1],x=i[4],M=i[7],R=i[2],w=i[5],E=i[8];return s[0]=o*g+a*y+l*R,s[3]=o*p+a*x+l*w,s[6]=o*m+a*M+l*E,s[1]=c*g+u*y+f*R,s[4]=c*p+u*x+f*w,s[7]=c*m+u*M+f*E,s[2]=h*g+d*y+_*R,s[5]=h*p+d*x+_*w,s[8]=h*m+d*M+_*E,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[3]*=e,t[6]*=e,t[1]*=e,t[4]*=e,t[7]*=e,t[2]*=e,t[5]*=e,t[8]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8];return t*o*u-t*a*c-n*s*u+n*a*l+i*s*c-i*o*l}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8],f=u*o-a*c,h=a*l-u*s,d=c*s-o*l,_=t*f+n*h+i*d;if(_===0)return this.set(0,0,0,0,0,0,0,0,0);const g=1/_;return e[0]=f*g,e[1]=(i*c-u*n)*g,e[2]=(a*n-i*o)*g,e[3]=h*g,e[4]=(u*t-i*l)*g,e[5]=(i*s-a*t)*g,e[6]=d*g,e[7]=(n*l-c*t)*g,e[8]=(o*t-n*s)*g,this}transpose(){let e;const t=this.elements;return e=t[1],t[1]=t[3],t[3]=e,e=t[2],t[2]=t[6],t[6]=e,e=t[5],t[5]=t[7],t[7]=e,this}getNormalMatrix(e){return this.setFromMatrix4(e).invert().transpose()}transposeIntoArray(e){const t=this.elements;return e[0]=t[0],e[1]=t[3],e[2]=t[6],e[3]=t[1],e[4]=t[4],e[5]=t[7],e[6]=t[2],e[7]=t[5],e[8]=t[8],this}setUvTransform(e,t,n,i,s,o,a){const l=Math.cos(s),c=Math.sin(s);return this.set(n*l,n*c,-n*(l*o+c*a)+o+e,-i*c,i*l,-i*(-c*o+l*a)+a+t,0,0,1),this}scale(e,t){return this.premultiply(Dl.makeScale(e,t)),this}rotate(e){return this.premultiply(Dl.makeRotation(-e)),this}translate(e,t){return this.premultiply(Dl.makeTranslation(e,t)),this}makeTranslation(e,t){return e.isVector2?this.set(1,0,e.x,0,1,e.y,0,0,1):this.set(1,0,e,0,1,t,0,0,1),this}makeRotation(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,n,t,0,0,0,1),this}makeScale(e,t){return this.set(e,0,0,0,t,0,0,0,1),this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<9;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<9;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e}clone(){return new this.constructor().fromArray(this.elements)}}const Dl=new Ke;function Pp(r){for(let e=r.length-1;e>=0;--e)if(r[e]>=65535)return!0;return!1}function tl(r){return document.createElementNS("http://www.w3.org/1999/xhtml",r)}function Hg(){const r=tl("canvas");return r.style.display="block",r}const ef={};function Oa(r){r in ef||(ef[r]=!0,console.warn(r))}function Gg(r,e,t){return new Promise(function(n,i){function s(){switch(r.clientWaitSync(e,r.SYNC_FLUSH_COMMANDS_BIT,0)){case r.WAIT_FAILED:i();break;case r.TIMEOUT_EXPIRED:setTimeout(s,t);break;default:n()}}setTimeout(s,t)})}function Vg(r){const e=r.elements;e[2]=.5*e[2]+.5*e[3],e[6]=.5*e[6]+.5*e[7],e[10]=.5*e[10]+.5*e[11],e[14]=.5*e[14]+.5*e[15]}function Wg(r){const e=r.elements;e[11]===-1?(e[10]=-e[10]-1,e[14]=-e[14]):(e[10]=-e[10],e[14]=-e[14]+1)}const tf=new Ke().set(.8224621,.177538,0,.0331941,.9668058,0,.0170827,.0723974,.9105199),nf=new Ke().set(1.2249401,-.2249404,0,-.0420569,1.0420571,0,-.0196376,-.0786361,1.0982735),$s={[dr]:{transfer:ja,primaries:Ja,luminanceCoefficients:[.2126,.7152,.0722],toReference:r=>r,fromReference:r=>r},[ai]:{transfer:Et,primaries:Ja,luminanceCoefficients:[.2126,.7152,.0722],toReference:r=>r.convertSRGBToLinear(),fromReference:r=>r.convertLinearToSRGB()},[ll]:{transfer:ja,primaries:Qa,luminanceCoefficients:[.2289,.6917,.0793],toReference:r=>r.applyMatrix3(nf),fromReference:r=>r.applyMatrix3(tf)},[sh]:{transfer:Et,primaries:Qa,luminanceCoefficients:[.2289,.6917,.0793],toReference:r=>r.convertSRGBToLinear().applyMatrix3(nf),fromReference:r=>r.applyMatrix3(tf).convertLinearToSRGB()}},Xg=new Set([dr,ll]),ft={enabled:!0,_workingColorSpace:dr,get workingColorSpace(){return this._workingColorSpace},set workingColorSpace(r){if(!Xg.has(r))throw new Error(`Unsupported working color space, "${r}".`);this._workingColorSpace=r},convert:function(r,e,t){if(this.enabled===!1||e===t||!e||!t)return r;const n=$s[e].toReference,i=$s[t].fromReference;return i(n(r))},fromWorkingColorSpace:function(r,e){return this.convert(r,this._workingColorSpace,e)},toWorkingColorSpace:function(r,e){return this.convert(r,e,this._workingColorSpace)},getPrimaries:function(r){return $s[r].primaries},getTransfer:function(r){return r===Zi?ja:$s[r].transfer},getLuminanceCoefficients:function(r,e=this._workingColorSpace){return r.fromArray($s[e].luminanceCoefficients)}};function Rs(r){return r<.04045?r*.0773993808:Math.pow(r*.9478672986+.0521327014,2.4)}function Ll(r){return r<.0031308?r*12.92:1.055*Math.pow(r,.41666)-.055}let Qr;class Yg{static getDataURL(e){if(/^data:/i.test(e.src)||typeof HTMLCanvasElement>"u")return e.src;let t;if(e instanceof HTMLCanvasElement)t=e;else{Qr===void 0&&(Qr=tl("canvas")),Qr.width=e.width,Qr.height=e.height;const n=Qr.getContext("2d");e instanceof ImageData?n.putImageData(e,0,0):n.drawImage(e,0,0,e.width,e.height),t=Qr}return t.width>2048||t.height>2048?(console.warn("THREE.ImageUtils.getDataURL: Image converted to jpg for performance reasons",e),t.toDataURL("image/jpeg",.6)):t.toDataURL("image/png")}static sRGBToLinear(e){if(typeof HTMLImageElement<"u"&&e instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&e instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&e instanceof ImageBitmap){const t=tl("canvas");t.width=e.width,t.height=e.height;const n=t.getContext("2d");n.drawImage(e,0,0,e.width,e.height);const i=n.getImageData(0,0,e.width,e.height),s=i.data;for(let o=0;o<s.length;o++)s[o]=Rs(s[o]/255)*255;return n.putImageData(i,0,0),t}else if(e.data){const t=e.data.slice(0);for(let n=0;n<t.length;n++)t instanceof Uint8Array||t instanceof Uint8ClampedArray?t[n]=Math.floor(Rs(t[n]/255)*255):t[n]=Rs(t[n]);return{data:t,width:e.width,height:e.height}}else return console.warn("THREE.ImageUtils.sRGBToLinear(): Unsupported image type. No color space conversion applied."),e}}let qg=0;class Dp{constructor(e=null){this.isSource=!0,Object.defineProperty(this,"id",{value:qg++}),this.uuid=Io(),this.data=e,this.dataReady=!0,this.version=0}set needsUpdate(e){e===!0&&this.version++}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.images[this.uuid]!==void 0)return e.images[this.uuid];const n={uuid:this.uuid,url:""},i=this.data;if(i!==null){let s;if(Array.isArray(i)){s=[];for(let o=0,a=i.length;o<a;o++)i[o].isDataTexture?s.push(Il(i[o].image)):s.push(Il(i[o]))}else s=Il(i);n.url=s}return t||(e.images[this.uuid]=n),n}}function Il(r){return typeof HTMLImageElement<"u"&&r instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&r instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&r instanceof ImageBitmap?Yg.getDataURL(r):r.data?{data:Array.from(r.data),width:r.width,height:r.height,type:r.data.constructor.name}:(console.warn("THREE.Texture: Unable to serialize Texture."),{})}let $g=0;class gn extends Gs{constructor(e=gn.DEFAULT_IMAGE,t=gn.DEFAULT_MAPPING,n=Ii,i=Ii,s=li,o=Dr,a=ui,l=zi,c=gn.DEFAULT_ANISOTROPY,u=Zi){super(),this.isTexture=!0,Object.defineProperty(this,"id",{value:$g++}),this.uuid=Io(),this.name="",this.source=new Dp(e),this.mipmaps=[],this.mapping=t,this.channel=0,this.wrapS=n,this.wrapT=i,this.magFilter=s,this.minFilter=o,this.anisotropy=c,this.format=a,this.internalFormat=null,this.type=l,this.offset=new St(0,0),this.repeat=new St(1,1),this.center=new St(0,0),this.rotation=0,this.matrixAutoUpdate=!0,this.matrix=new Ke,this.generateMipmaps=!0,this.premultiplyAlpha=!1,this.flipY=!0,this.unpackAlignment=4,this.colorSpace=u,this.userData={},this.version=0,this.onUpdate=null,this.isRenderTargetTexture=!1,this.pmremVersion=0}get image(){return this.source.data}set image(e=null){this.source.data=e}updateMatrix(){this.matrix.setUvTransform(this.offset.x,this.offset.y,this.repeat.x,this.repeat.y,this.rotation,this.center.x,this.center.y)}clone(){return new this.constructor().copy(this)}copy(e){return this.name=e.name,this.source=e.source,this.mipmaps=e.mipmaps.slice(0),this.mapping=e.mapping,this.channel=e.channel,this.wrapS=e.wrapS,this.wrapT=e.wrapT,this.magFilter=e.magFilter,this.minFilter=e.minFilter,this.anisotropy=e.anisotropy,this.format=e.format,this.internalFormat=e.internalFormat,this.type=e.type,this.offset.copy(e.offset),this.repeat.copy(e.repeat),this.center.copy(e.center),this.rotation=e.rotation,this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrix.copy(e.matrix),this.generateMipmaps=e.generateMipmaps,this.premultiplyAlpha=e.premultiplyAlpha,this.flipY=e.flipY,this.unpackAlignment=e.unpackAlignment,this.colorSpace=e.colorSpace,this.userData=JSON.parse(JSON.stringify(e.userData)),this.needsUpdate=!0,this}toJSON(e){const t=e===void 0||typeof e=="string";if(!t&&e.textures[this.uuid]!==void 0)return e.textures[this.uuid];const n={metadata:{version:4.6,type:"Texture",generator:"Texture.toJSON"},uuid:this.uuid,name:this.name,image:this.source.toJSON(e).uuid,mapping:this.mapping,channel:this.channel,repeat:[this.repeat.x,this.repeat.y],offset:[this.offset.x,this.offset.y],center:[this.center.x,this.center.y],rotation:this.rotation,wrap:[this.wrapS,this.wrapT],format:this.format,internalFormat:this.internalFormat,type:this.type,colorSpace:this.colorSpace,minFilter:this.minFilter,magFilter:this.magFilter,anisotropy:this.anisotropy,flipY:this.flipY,generateMipmaps:this.generateMipmaps,premultiplyAlpha:this.premultiplyAlpha,unpackAlignment:this.unpackAlignment};return Object.keys(this.userData).length>0&&(n.userData=this.userData),t||(e.textures[this.uuid]=n),n}dispose(){this.dispatchEvent({type:"dispose"})}transformUv(e){if(this.mapping!==vp)return e;if(e.applyMatrix3(this.matrix),e.x<0||e.x>1)switch(this.wrapS){case Yc:e.x=e.x-Math.floor(e.x);break;case Ii:e.x=e.x<0?0:1;break;case qc:Math.abs(Math.floor(e.x)%2)===1?e.x=Math.ceil(e.x)-e.x:e.x=e.x-Math.floor(e.x);break}if(e.y<0||e.y>1)switch(this.wrapT){case Yc:e.y=e.y-Math.floor(e.y);break;case Ii:e.y=e.y<0?0:1;break;case qc:Math.abs(Math.floor(e.y)%2)===1?e.y=Math.ceil(e.y)-e.y:e.y=e.y-Math.floor(e.y);break}return this.flipY&&(e.y=1-e.y),e}set needsUpdate(e){e===!0&&(this.version++,this.source.needsUpdate=!0)}set needsPMREMUpdate(e){e===!0&&this.pmremVersion++}}gn.DEFAULT_IMAGE=null;gn.DEFAULT_MAPPING=vp;gn.DEFAULT_ANISOTROPY=1;class Nt{constructor(e=0,t=0,n=0,i=1){Nt.prototype.isVector4=!0,this.x=e,this.y=t,this.z=n,this.w=i}get width(){return this.z}set width(e){this.z=e}get height(){return this.w}set height(e){this.w=e}set(e,t,n,i){return this.x=e,this.y=t,this.z=n,this.w=i,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this.w=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setW(e){return this.w=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;case 3:this.w=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;case 3:return this.w;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z,this.w)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this.w=e.w!==void 0?e.w:1,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this.w+=e.w,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this.w+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this.w=e.w+t.w,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this.w+=e.w*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this.w-=e.w,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this.w-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this.w=e.w-t.w,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this.w*=e.w,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this.w*=e,this}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=this.w,o=e.elements;return this.x=o[0]*t+o[4]*n+o[8]*i+o[12]*s,this.y=o[1]*t+o[5]*n+o[9]*i+o[13]*s,this.z=o[2]*t+o[6]*n+o[10]*i+o[14]*s,this.w=o[3]*t+o[7]*n+o[11]*i+o[15]*s,this}divideScalar(e){return this.multiplyScalar(1/e)}setAxisAngleFromQuaternion(e){this.w=2*Math.acos(e.w);const t=Math.sqrt(1-e.w*e.w);return t<1e-4?(this.x=1,this.y=0,this.z=0):(this.x=e.x/t,this.y=e.y/t,this.z=e.z/t),this}setAxisAngleFromRotationMatrix(e){let t,n,i,s;const l=e.elements,c=l[0],u=l[4],f=l[8],h=l[1],d=l[5],_=l[9],g=l[2],p=l[6],m=l[10];if(Math.abs(u-h)<.01&&Math.abs(f-g)<.01&&Math.abs(_-p)<.01){if(Math.abs(u+h)<.1&&Math.abs(f+g)<.1&&Math.abs(_+p)<.1&&Math.abs(c+d+m-3)<.1)return this.set(1,0,0,0),this;t=Math.PI;const x=(c+1)/2,M=(d+1)/2,R=(m+1)/2,w=(u+h)/4,E=(f+g)/4,D=(_+p)/4;return x>M&&x>R?x<.01?(n=0,i=.707106781,s=.707106781):(n=Math.sqrt(x),i=w/n,s=E/n):M>R?M<.01?(n=.707106781,i=0,s=.707106781):(i=Math.sqrt(M),n=w/i,s=D/i):R<.01?(n=.707106781,i=.707106781,s=0):(s=Math.sqrt(R),n=E/s,i=D/s),this.set(n,i,s,t),this}let y=Math.sqrt((p-_)*(p-_)+(f-g)*(f-g)+(h-u)*(h-u));return Math.abs(y)<.001&&(y=1),this.x=(p-_)/y,this.y=(f-g)/y,this.z=(h-u)/y,this.w=Math.acos((c+d+m-1)/2),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this.w=t[15],this}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this.w=Math.min(this.w,e.w),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this.w=Math.max(this.w,e.w),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this.w=Math.max(e.w,Math.min(t.w,this.w)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this.w=Math.max(e,Math.min(t,this.w)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this.w=Math.floor(this.w),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this.w=Math.ceil(this.w),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this.w=Math.round(this.w),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this.w=Math.trunc(this.w),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this.w=-this.w,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z+this.w*e.w}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z+this.w*this.w)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)+Math.abs(this.w)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this.w+=(e.w-this.w)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this.w=e.w+(t.w-e.w)*n,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z&&e.w===this.w}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this.w=e[t+3],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e[t+3]=this.w,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this.w=e.getW(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this.w=Math.random(),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z,yield this.w}}class Kg extends Gs{constructor(e=1,t=1,n={}){super(),this.isRenderTarget=!0,this.width=e,this.height=t,this.depth=1,this.scissor=new Nt(0,0,e,t),this.scissorTest=!1,this.viewport=new Nt(0,0,e,t);const i={width:e,height:t,depth:1};n=Object.assign({generateMipmaps:!1,internalFormat:null,minFilter:li,depthBuffer:!0,stencilBuffer:!1,resolveDepthBuffer:!0,resolveStencilBuffer:!0,depthTexture:null,samples:0,count:1},n);const s=new gn(i,n.mapping,n.wrapS,n.wrapT,n.magFilter,n.minFilter,n.format,n.type,n.anisotropy,n.colorSpace);s.flipY=!1,s.generateMipmaps=n.generateMipmaps,s.internalFormat=n.internalFormat,this.textures=[];const o=n.count;for(let a=0;a<o;a++)this.textures[a]=s.clone(),this.textures[a].isRenderTargetTexture=!0;this.depthBuffer=n.depthBuffer,this.stencilBuffer=n.stencilBuffer,this.resolveDepthBuffer=n.resolveDepthBuffer,this.resolveStencilBuffer=n.resolveStencilBuffer,this.depthTexture=n.depthTexture,this.samples=n.samples}get texture(){return this.textures[0]}set texture(e){this.textures[0]=e}setSize(e,t,n=1){if(this.width!==e||this.height!==t||this.depth!==n){this.width=e,this.height=t,this.depth=n;for(let i=0,s=this.textures.length;i<s;i++)this.textures[i].image.width=e,this.textures[i].image.height=t,this.textures[i].image.depth=n;this.dispose()}this.viewport.set(0,0,e,t),this.scissor.set(0,0,e,t)}clone(){return new this.constructor().copy(this)}copy(e){this.width=e.width,this.height=e.height,this.depth=e.depth,this.scissor.copy(e.scissor),this.scissorTest=e.scissorTest,this.viewport.copy(e.viewport),this.textures.length=0;for(let n=0,i=e.textures.length;n<i;n++)this.textures[n]=e.textures[n].clone(),this.textures[n].isRenderTargetTexture=!0;const t=Object.assign({},e.texture.image);return this.texture.source=new Dp(t),this.depthBuffer=e.depthBuffer,this.stencilBuffer=e.stencilBuffer,this.resolveDepthBuffer=e.resolveDepthBuffer,this.resolveStencilBuffer=e.resolveStencilBuffer,e.depthTexture!==null&&(this.depthTexture=e.depthTexture.clone()),this.samples=e.samples,this}dispose(){this.dispatchEvent({type:"dispose"})}}class Xr extends Kg{constructor(e=1,t=1,n={}){super(e,t,n),this.isWebGLRenderTarget=!0}}class Lp extends gn{constructor(e=null,t=1,n=1,i=1){super(null),this.isDataArrayTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Jn,this.minFilter=Jn,this.wrapR=Ii,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1,this.layerUpdates=new Set}addLayerUpdate(e){this.layerUpdates.add(e)}clearLayerUpdates(){this.layerUpdates.clear()}}class Zg extends gn{constructor(e=null,t=1,n=1,i=1){super(null),this.isData3DTexture=!0,this.image={data:e,width:t,height:n,depth:i},this.magFilter=Jn,this.minFilter=Jn,this.wrapR=Ii,this.generateMipmaps=!1,this.flipY=!1,this.unpackAlignment=1}}class Uo{constructor(e=0,t=0,n=0,i=1){this.isQuaternion=!0,this._x=e,this._y=t,this._z=n,this._w=i}static slerpFlat(e,t,n,i,s,o,a){let l=n[i+0],c=n[i+1],u=n[i+2],f=n[i+3];const h=s[o+0],d=s[o+1],_=s[o+2],g=s[o+3];if(a===0){e[t+0]=l,e[t+1]=c,e[t+2]=u,e[t+3]=f;return}if(a===1){e[t+0]=h,e[t+1]=d,e[t+2]=_,e[t+3]=g;return}if(f!==g||l!==h||c!==d||u!==_){let p=1-a;const m=l*h+c*d+u*_+f*g,y=m>=0?1:-1,x=1-m*m;if(x>Number.EPSILON){const R=Math.sqrt(x),w=Math.atan2(R,m*y);p=Math.sin(p*w)/R,a=Math.sin(a*w)/R}const M=a*y;if(l=l*p+h*M,c=c*p+d*M,u=u*p+_*M,f=f*p+g*M,p===1-a){const R=1/Math.sqrt(l*l+c*c+u*u+f*f);l*=R,c*=R,u*=R,f*=R}}e[t]=l,e[t+1]=c,e[t+2]=u,e[t+3]=f}static multiplyQuaternionsFlat(e,t,n,i,s,o){const a=n[i],l=n[i+1],c=n[i+2],u=n[i+3],f=s[o],h=s[o+1],d=s[o+2],_=s[o+3];return e[t]=a*_+u*f+l*d-c*h,e[t+1]=l*_+u*h+c*f-a*d,e[t+2]=c*_+u*d+a*h-l*f,e[t+3]=u*_-a*f-l*h-c*d,e}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get w(){return this._w}set w(e){this._w=e,this._onChangeCallback()}set(e,t,n,i){return this._x=e,this._y=t,this._z=n,this._w=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._w)}copy(e){return this._x=e.x,this._y=e.y,this._z=e.z,this._w=e.w,this._onChangeCallback(),this}setFromEuler(e,t=!0){const n=e._x,i=e._y,s=e._z,o=e._order,a=Math.cos,l=Math.sin,c=a(n/2),u=a(i/2),f=a(s/2),h=l(n/2),d=l(i/2),_=l(s/2);switch(o){case"XYZ":this._x=h*u*f+c*d*_,this._y=c*d*f-h*u*_,this._z=c*u*_+h*d*f,this._w=c*u*f-h*d*_;break;case"YXZ":this._x=h*u*f+c*d*_,this._y=c*d*f-h*u*_,this._z=c*u*_-h*d*f,this._w=c*u*f+h*d*_;break;case"ZXY":this._x=h*u*f-c*d*_,this._y=c*d*f+h*u*_,this._z=c*u*_+h*d*f,this._w=c*u*f-h*d*_;break;case"ZYX":this._x=h*u*f-c*d*_,this._y=c*d*f+h*u*_,this._z=c*u*_-h*d*f,this._w=c*u*f+h*d*_;break;case"YZX":this._x=h*u*f+c*d*_,this._y=c*d*f+h*u*_,this._z=c*u*_-h*d*f,this._w=c*u*f-h*d*_;break;case"XZY":this._x=h*u*f-c*d*_,this._y=c*d*f-h*u*_,this._z=c*u*_+h*d*f,this._w=c*u*f+h*d*_;break;default:console.warn("THREE.Quaternion: .setFromEuler() encountered an unknown order: "+o)}return t===!0&&this._onChangeCallback(),this}setFromAxisAngle(e,t){const n=t/2,i=Math.sin(n);return this._x=e.x*i,this._y=e.y*i,this._z=e.z*i,this._w=Math.cos(n),this._onChangeCallback(),this}setFromRotationMatrix(e){const t=e.elements,n=t[0],i=t[4],s=t[8],o=t[1],a=t[5],l=t[9],c=t[2],u=t[6],f=t[10],h=n+a+f;if(h>0){const d=.5/Math.sqrt(h+1);this._w=.25/d,this._x=(u-l)*d,this._y=(s-c)*d,this._z=(o-i)*d}else if(n>a&&n>f){const d=2*Math.sqrt(1+n-a-f);this._w=(u-l)/d,this._x=.25*d,this._y=(i+o)/d,this._z=(s+c)/d}else if(a>f){const d=2*Math.sqrt(1+a-n-f);this._w=(s-c)/d,this._x=(i+o)/d,this._y=.25*d,this._z=(l+u)/d}else{const d=2*Math.sqrt(1+f-n-a);this._w=(o-i)/d,this._x=(s+c)/d,this._y=(l+u)/d,this._z=.25*d}return this._onChangeCallback(),this}setFromUnitVectors(e,t){let n=e.dot(t)+1;return n<Number.EPSILON?(n=0,Math.abs(e.x)>Math.abs(e.z)?(this._x=-e.y,this._y=e.x,this._z=0,this._w=n):(this._x=0,this._y=-e.z,this._z=e.y,this._w=n)):(this._x=e.y*t.z-e.z*t.y,this._y=e.z*t.x-e.x*t.z,this._z=e.x*t.y-e.y*t.x,this._w=n),this.normalize()}angleTo(e){return 2*Math.acos(Math.abs(Mn(this.dot(e),-1,1)))}rotateTowards(e,t){const n=this.angleTo(e);if(n===0)return this;const i=Math.min(1,t/n);return this.slerp(e,i),this}identity(){return this.set(0,0,0,1)}invert(){return this.conjugate()}conjugate(){return this._x*=-1,this._y*=-1,this._z*=-1,this._onChangeCallback(),this}dot(e){return this._x*e._x+this._y*e._y+this._z*e._z+this._w*e._w}lengthSq(){return this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w}length(){return Math.sqrt(this._x*this._x+this._y*this._y+this._z*this._z+this._w*this._w)}normalize(){let e=this.length();return e===0?(this._x=0,this._y=0,this._z=0,this._w=1):(e=1/e,this._x=this._x*e,this._y=this._y*e,this._z=this._z*e,this._w=this._w*e),this._onChangeCallback(),this}multiply(e){return this.multiplyQuaternions(this,e)}premultiply(e){return this.multiplyQuaternions(e,this)}multiplyQuaternions(e,t){const n=e._x,i=e._y,s=e._z,o=e._w,a=t._x,l=t._y,c=t._z,u=t._w;return this._x=n*u+o*a+i*c-s*l,this._y=i*u+o*l+s*a-n*c,this._z=s*u+o*c+n*l-i*a,this._w=o*u-n*a-i*l-s*c,this._onChangeCallback(),this}slerp(e,t){if(t===0)return this;if(t===1)return this.copy(e);const n=this._x,i=this._y,s=this._z,o=this._w;let a=o*e._w+n*e._x+i*e._y+s*e._z;if(a<0?(this._w=-e._w,this._x=-e._x,this._y=-e._y,this._z=-e._z,a=-a):this.copy(e),a>=1)return this._w=o,this._x=n,this._y=i,this._z=s,this;const l=1-a*a;if(l<=Number.EPSILON){const d=1-t;return this._w=d*o+t*this._w,this._x=d*n+t*this._x,this._y=d*i+t*this._y,this._z=d*s+t*this._z,this.normalize(),this}const c=Math.sqrt(l),u=Math.atan2(c,a),f=Math.sin((1-t)*u)/c,h=Math.sin(t*u)/c;return this._w=o*f+this._w*h,this._x=n*f+this._x*h,this._y=i*f+this._y*h,this._z=s*f+this._z*h,this._onChangeCallback(),this}slerpQuaternions(e,t,n){return this.copy(e).slerp(t,n)}random(){const e=2*Math.PI*Math.random(),t=2*Math.PI*Math.random(),n=Math.random(),i=Math.sqrt(1-n),s=Math.sqrt(n);return this.set(i*Math.sin(e),i*Math.cos(e),s*Math.sin(t),s*Math.cos(t))}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._w===this._w}fromArray(e,t=0){return this._x=e[t],this._y=e[t+1],this._z=e[t+2],this._w=e[t+3],this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._w,e}fromBufferAttribute(e,t){return this._x=e.getX(t),this._y=e.getY(t),this._z=e.getZ(t),this._w=e.getW(t),this._onChangeCallback(),this}toJSON(){return this.toArray()}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._w}}class Y{constructor(e=0,t=0,n=0){Y.prototype.isVector3=!0,this.x=e,this.y=t,this.z=n}set(e,t,n){return n===void 0&&(n=this.z),this.x=e,this.y=t,this.z=n,this}setScalar(e){return this.x=e,this.y=e,this.z=e,this}setX(e){return this.x=e,this}setY(e){return this.y=e,this}setZ(e){return this.z=e,this}setComponent(e,t){switch(e){case 0:this.x=t;break;case 1:this.y=t;break;case 2:this.z=t;break;default:throw new Error("index is out of range: "+e)}return this}getComponent(e){switch(e){case 0:return this.x;case 1:return this.y;case 2:return this.z;default:throw new Error("index is out of range: "+e)}}clone(){return new this.constructor(this.x,this.y,this.z)}copy(e){return this.x=e.x,this.y=e.y,this.z=e.z,this}add(e){return this.x+=e.x,this.y+=e.y,this.z+=e.z,this}addScalar(e){return this.x+=e,this.y+=e,this.z+=e,this}addVectors(e,t){return this.x=e.x+t.x,this.y=e.y+t.y,this.z=e.z+t.z,this}addScaledVector(e,t){return this.x+=e.x*t,this.y+=e.y*t,this.z+=e.z*t,this}sub(e){return this.x-=e.x,this.y-=e.y,this.z-=e.z,this}subScalar(e){return this.x-=e,this.y-=e,this.z-=e,this}subVectors(e,t){return this.x=e.x-t.x,this.y=e.y-t.y,this.z=e.z-t.z,this}multiply(e){return this.x*=e.x,this.y*=e.y,this.z*=e.z,this}multiplyScalar(e){return this.x*=e,this.y*=e,this.z*=e,this}multiplyVectors(e,t){return this.x=e.x*t.x,this.y=e.y*t.y,this.z=e.z*t.z,this}applyEuler(e){return this.applyQuaternion(rf.setFromEuler(e))}applyAxisAngle(e,t){return this.applyQuaternion(rf.setFromAxisAngle(e,t))}applyMatrix3(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[3]*n+s[6]*i,this.y=s[1]*t+s[4]*n+s[7]*i,this.z=s[2]*t+s[5]*n+s[8]*i,this}applyNormalMatrix(e){return this.applyMatrix3(e).normalize()}applyMatrix4(e){const t=this.x,n=this.y,i=this.z,s=e.elements,o=1/(s[3]*t+s[7]*n+s[11]*i+s[15]);return this.x=(s[0]*t+s[4]*n+s[8]*i+s[12])*o,this.y=(s[1]*t+s[5]*n+s[9]*i+s[13])*o,this.z=(s[2]*t+s[6]*n+s[10]*i+s[14])*o,this}applyQuaternion(e){const t=this.x,n=this.y,i=this.z,s=e.x,o=e.y,a=e.z,l=e.w,c=2*(o*i-a*n),u=2*(a*t-s*i),f=2*(s*n-o*t);return this.x=t+l*c+o*f-a*u,this.y=n+l*u+a*c-s*f,this.z=i+l*f+s*u-o*c,this}project(e){return this.applyMatrix4(e.matrixWorldInverse).applyMatrix4(e.projectionMatrix)}unproject(e){return this.applyMatrix4(e.projectionMatrixInverse).applyMatrix4(e.matrixWorld)}transformDirection(e){const t=this.x,n=this.y,i=this.z,s=e.elements;return this.x=s[0]*t+s[4]*n+s[8]*i,this.y=s[1]*t+s[5]*n+s[9]*i,this.z=s[2]*t+s[6]*n+s[10]*i,this.normalize()}divide(e){return this.x/=e.x,this.y/=e.y,this.z/=e.z,this}divideScalar(e){return this.multiplyScalar(1/e)}min(e){return this.x=Math.min(this.x,e.x),this.y=Math.min(this.y,e.y),this.z=Math.min(this.z,e.z),this}max(e){return this.x=Math.max(this.x,e.x),this.y=Math.max(this.y,e.y),this.z=Math.max(this.z,e.z),this}clamp(e,t){return this.x=Math.max(e.x,Math.min(t.x,this.x)),this.y=Math.max(e.y,Math.min(t.y,this.y)),this.z=Math.max(e.z,Math.min(t.z,this.z)),this}clampScalar(e,t){return this.x=Math.max(e,Math.min(t,this.x)),this.y=Math.max(e,Math.min(t,this.y)),this.z=Math.max(e,Math.min(t,this.z)),this}clampLength(e,t){const n=this.length();return this.divideScalar(n||1).multiplyScalar(Math.max(e,Math.min(t,n)))}floor(){return this.x=Math.floor(this.x),this.y=Math.floor(this.y),this.z=Math.floor(this.z),this}ceil(){return this.x=Math.ceil(this.x),this.y=Math.ceil(this.y),this.z=Math.ceil(this.z),this}round(){return this.x=Math.round(this.x),this.y=Math.round(this.y),this.z=Math.round(this.z),this}roundToZero(){return this.x=Math.trunc(this.x),this.y=Math.trunc(this.y),this.z=Math.trunc(this.z),this}negate(){return this.x=-this.x,this.y=-this.y,this.z=-this.z,this}dot(e){return this.x*e.x+this.y*e.y+this.z*e.z}lengthSq(){return this.x*this.x+this.y*this.y+this.z*this.z}length(){return Math.sqrt(this.x*this.x+this.y*this.y+this.z*this.z)}manhattanLength(){return Math.abs(this.x)+Math.abs(this.y)+Math.abs(this.z)}normalize(){return this.divideScalar(this.length()||1)}setLength(e){return this.normalize().multiplyScalar(e)}lerp(e,t){return this.x+=(e.x-this.x)*t,this.y+=(e.y-this.y)*t,this.z+=(e.z-this.z)*t,this}lerpVectors(e,t,n){return this.x=e.x+(t.x-e.x)*n,this.y=e.y+(t.y-e.y)*n,this.z=e.z+(t.z-e.z)*n,this}cross(e){return this.crossVectors(this,e)}crossVectors(e,t){const n=e.x,i=e.y,s=e.z,o=t.x,a=t.y,l=t.z;return this.x=i*l-s*a,this.y=s*o-n*l,this.z=n*a-i*o,this}projectOnVector(e){const t=e.lengthSq();if(t===0)return this.set(0,0,0);const n=e.dot(this)/t;return this.copy(e).multiplyScalar(n)}projectOnPlane(e){return Ul.copy(this).projectOnVector(e),this.sub(Ul)}reflect(e){return this.sub(Ul.copy(e).multiplyScalar(2*this.dot(e)))}angleTo(e){const t=Math.sqrt(this.lengthSq()*e.lengthSq());if(t===0)return Math.PI/2;const n=this.dot(e)/t;return Math.acos(Mn(n,-1,1))}distanceTo(e){return Math.sqrt(this.distanceToSquared(e))}distanceToSquared(e){const t=this.x-e.x,n=this.y-e.y,i=this.z-e.z;return t*t+n*n+i*i}manhattanDistanceTo(e){return Math.abs(this.x-e.x)+Math.abs(this.y-e.y)+Math.abs(this.z-e.z)}setFromSpherical(e){return this.setFromSphericalCoords(e.radius,e.phi,e.theta)}setFromSphericalCoords(e,t,n){const i=Math.sin(t)*e;return this.x=i*Math.sin(n),this.y=Math.cos(t)*e,this.z=i*Math.cos(n),this}setFromCylindrical(e){return this.setFromCylindricalCoords(e.radius,e.theta,e.y)}setFromCylindricalCoords(e,t,n){return this.x=e*Math.sin(t),this.y=n,this.z=e*Math.cos(t),this}setFromMatrixPosition(e){const t=e.elements;return this.x=t[12],this.y=t[13],this.z=t[14],this}setFromMatrixScale(e){const t=this.setFromMatrixColumn(e,0).length(),n=this.setFromMatrixColumn(e,1).length(),i=this.setFromMatrixColumn(e,2).length();return this.x=t,this.y=n,this.z=i,this}setFromMatrixColumn(e,t){return this.fromArray(e.elements,t*4)}setFromMatrix3Column(e,t){return this.fromArray(e.elements,t*3)}setFromEuler(e){return this.x=e._x,this.y=e._y,this.z=e._z,this}setFromColor(e){return this.x=e.r,this.y=e.g,this.z=e.b,this}equals(e){return e.x===this.x&&e.y===this.y&&e.z===this.z}fromArray(e,t=0){return this.x=e[t],this.y=e[t+1],this.z=e[t+2],this}toArray(e=[],t=0){return e[t]=this.x,e[t+1]=this.y,e[t+2]=this.z,e}fromBufferAttribute(e,t){return this.x=e.getX(t),this.y=e.getY(t),this.z=e.getZ(t),this}random(){return this.x=Math.random(),this.y=Math.random(),this.z=Math.random(),this}randomDirection(){const e=Math.random()*Math.PI*2,t=Math.random()*2-1,n=Math.sqrt(1-t*t);return this.x=n*Math.cos(e),this.y=t,this.z=n*Math.sin(e),this}*[Symbol.iterator](){yield this.x,yield this.y,yield this.z}}const Ul=new Y,rf=new Uo;class No{constructor(e=new Y(1/0,1/0,1/0),t=new Y(-1/0,-1/0,-1/0)){this.isBox3=!0,this.min=e,this.max=t}set(e,t){return this.min.copy(e),this.max.copy(t),this}setFromArray(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t+=3)this.expandByPoint(ni.fromArray(e,t));return this}setFromBufferAttribute(e){this.makeEmpty();for(let t=0,n=e.count;t<n;t++)this.expandByPoint(ni.fromBufferAttribute(e,t));return this}setFromPoints(e){this.makeEmpty();for(let t=0,n=e.length;t<n;t++)this.expandByPoint(e[t]);return this}setFromCenterAndSize(e,t){const n=ni.copy(t).multiplyScalar(.5);return this.min.copy(e).sub(n),this.max.copy(e).add(n),this}setFromObject(e,t=!1){return this.makeEmpty(),this.expandByObject(e,t)}clone(){return new this.constructor().copy(this)}copy(e){return this.min.copy(e.min),this.max.copy(e.max),this}makeEmpty(){return this.min.x=this.min.y=this.min.z=1/0,this.max.x=this.max.y=this.max.z=-1/0,this}isEmpty(){return this.max.x<this.min.x||this.max.y<this.min.y||this.max.z<this.min.z}getCenter(e){return this.isEmpty()?e.set(0,0,0):e.addVectors(this.min,this.max).multiplyScalar(.5)}getSize(e){return this.isEmpty()?e.set(0,0,0):e.subVectors(this.max,this.min)}expandByPoint(e){return this.min.min(e),this.max.max(e),this}expandByVector(e){return this.min.sub(e),this.max.add(e),this}expandByScalar(e){return this.min.addScalar(-e),this.max.addScalar(e),this}expandByObject(e,t=!1){e.updateWorldMatrix(!1,!1);const n=e.geometry;if(n!==void 0){const s=n.getAttribute("position");if(t===!0&&s!==void 0&&e.isInstancedMesh!==!0)for(let o=0,a=s.count;o<a;o++)e.isMesh===!0?e.getVertexPosition(o,ni):ni.fromBufferAttribute(s,o),ni.applyMatrix4(e.matrixWorld),this.expandByPoint(ni);else e.boundingBox!==void 0?(e.boundingBox===null&&e.computeBoundingBox(),ea.copy(e.boundingBox)):(n.boundingBox===null&&n.computeBoundingBox(),ea.copy(n.boundingBox)),ea.applyMatrix4(e.matrixWorld),this.union(ea)}const i=e.children;for(let s=0,o=i.length;s<o;s++)this.expandByObject(i[s],t);return this}containsPoint(e){return e.x>=this.min.x&&e.x<=this.max.x&&e.y>=this.min.y&&e.y<=this.max.y&&e.z>=this.min.z&&e.z<=this.max.z}containsBox(e){return this.min.x<=e.min.x&&e.max.x<=this.max.x&&this.min.y<=e.min.y&&e.max.y<=this.max.y&&this.min.z<=e.min.z&&e.max.z<=this.max.z}getParameter(e,t){return t.set((e.x-this.min.x)/(this.max.x-this.min.x),(e.y-this.min.y)/(this.max.y-this.min.y),(e.z-this.min.z)/(this.max.z-this.min.z))}intersectsBox(e){return e.max.x>=this.min.x&&e.min.x<=this.max.x&&e.max.y>=this.min.y&&e.min.y<=this.max.y&&e.max.z>=this.min.z&&e.min.z<=this.max.z}intersectsSphere(e){return this.clampPoint(e.center,ni),ni.distanceToSquared(e.center)<=e.radius*e.radius}intersectsPlane(e){let t,n;return e.normal.x>0?(t=e.normal.x*this.min.x,n=e.normal.x*this.max.x):(t=e.normal.x*this.max.x,n=e.normal.x*this.min.x),e.normal.y>0?(t+=e.normal.y*this.min.y,n+=e.normal.y*this.max.y):(t+=e.normal.y*this.max.y,n+=e.normal.y*this.min.y),e.normal.z>0?(t+=e.normal.z*this.min.z,n+=e.normal.z*this.max.z):(t+=e.normal.z*this.max.z,n+=e.normal.z*this.min.z),t<=-e.constant&&n>=-e.constant}intersectsTriangle(e){if(this.isEmpty())return!1;this.getCenter(Ks),ta.subVectors(this.max,Ks),es.subVectors(e.a,Ks),ts.subVectors(e.b,Ks),ns.subVectors(e.c,Ks),Vi.subVectors(ts,es),Wi.subVectors(ns,ts),_r.subVectors(es,ns);let t=[0,-Vi.z,Vi.y,0,-Wi.z,Wi.y,0,-_r.z,_r.y,Vi.z,0,-Vi.x,Wi.z,0,-Wi.x,_r.z,0,-_r.x,-Vi.y,Vi.x,0,-Wi.y,Wi.x,0,-_r.y,_r.x,0];return!Nl(t,es,ts,ns,ta)||(t=[1,0,0,0,1,0,0,0,1],!Nl(t,es,ts,ns,ta))?!1:(na.crossVectors(Vi,Wi),t=[na.x,na.y,na.z],Nl(t,es,ts,ns,ta))}clampPoint(e,t){return t.copy(e).clamp(this.min,this.max)}distanceToPoint(e){return this.clampPoint(e,ni).distanceTo(e)}getBoundingSphere(e){return this.isEmpty()?e.makeEmpty():(this.getCenter(e.center),e.radius=this.getSize(ni).length()*.5),e}intersect(e){return this.min.max(e.min),this.max.min(e.max),this.isEmpty()&&this.makeEmpty(),this}union(e){return this.min.min(e.min),this.max.max(e.max),this}applyMatrix4(e){return this.isEmpty()?this:(yi[0].set(this.min.x,this.min.y,this.min.z).applyMatrix4(e),yi[1].set(this.min.x,this.min.y,this.max.z).applyMatrix4(e),yi[2].set(this.min.x,this.max.y,this.min.z).applyMatrix4(e),yi[3].set(this.min.x,this.max.y,this.max.z).applyMatrix4(e),yi[4].set(this.max.x,this.min.y,this.min.z).applyMatrix4(e),yi[5].set(this.max.x,this.min.y,this.max.z).applyMatrix4(e),yi[6].set(this.max.x,this.max.y,this.min.z).applyMatrix4(e),yi[7].set(this.max.x,this.max.y,this.max.z).applyMatrix4(e),this.setFromPoints(yi),this)}translate(e){return this.min.add(e),this.max.add(e),this}equals(e){return e.min.equals(this.min)&&e.max.equals(this.max)}}const yi=[new Y,new Y,new Y,new Y,new Y,new Y,new Y,new Y],ni=new Y,ea=new No,es=new Y,ts=new Y,ns=new Y,Vi=new Y,Wi=new Y,_r=new Y,Ks=new Y,ta=new Y,na=new Y,gr=new Y;function Nl(r,e,t,n,i){for(let s=0,o=r.length-3;s<=o;s+=3){gr.fromArray(r,s);const a=i.x*Math.abs(gr.x)+i.y*Math.abs(gr.y)+i.z*Math.abs(gr.z),l=e.dot(gr),c=t.dot(gr),u=n.dot(gr);if(Math.max(-Math.max(l,c,u),Math.min(l,c,u))>a)return!1}return!0}const jg=new No,Zs=new Y,Fl=new Y;class cl{constructor(e=new Y,t=-1){this.isSphere=!0,this.center=e,this.radius=t}set(e,t){return this.center.copy(e),this.radius=t,this}setFromPoints(e,t){const n=this.center;t!==void 0?n.copy(t):jg.setFromPoints(e).getCenter(n);let i=0;for(let s=0,o=e.length;s<o;s++)i=Math.max(i,n.distanceToSquared(e[s]));return this.radius=Math.sqrt(i),this}copy(e){return this.center.copy(e.center),this.radius=e.radius,this}isEmpty(){return this.radius<0}makeEmpty(){return this.center.set(0,0,0),this.radius=-1,this}containsPoint(e){return e.distanceToSquared(this.center)<=this.radius*this.radius}distanceToPoint(e){return e.distanceTo(this.center)-this.radius}intersectsSphere(e){const t=this.radius+e.radius;return e.center.distanceToSquared(this.center)<=t*t}intersectsBox(e){return e.intersectsSphere(this)}intersectsPlane(e){return Math.abs(e.distanceToPoint(this.center))<=this.radius}clampPoint(e,t){const n=this.center.distanceToSquared(e);return t.copy(e),n>this.radius*this.radius&&(t.sub(this.center).normalize(),t.multiplyScalar(this.radius).add(this.center)),t}getBoundingBox(e){return this.isEmpty()?(e.makeEmpty(),e):(e.set(this.center,this.center),e.expandByScalar(this.radius),e)}applyMatrix4(e){return this.center.applyMatrix4(e),this.radius=this.radius*e.getMaxScaleOnAxis(),this}translate(e){return this.center.add(e),this}expandByPoint(e){if(this.isEmpty())return this.center.copy(e),this.radius=0,this;Zs.subVectors(e,this.center);const t=Zs.lengthSq();if(t>this.radius*this.radius){const n=Math.sqrt(t),i=(n-this.radius)*.5;this.center.addScaledVector(Zs,i/n),this.radius+=i}return this}union(e){return e.isEmpty()?this:this.isEmpty()?(this.copy(e),this):(this.center.equals(e.center)===!0?this.radius=Math.max(this.radius,e.radius):(Fl.subVectors(e.center,this.center).setLength(e.radius),this.expandByPoint(Zs.copy(e.center).add(Fl)),this.expandByPoint(Zs.copy(e.center).sub(Fl))),this)}equals(e){return e.center.equals(this.center)&&e.radius===this.radius}clone(){return new this.constructor().copy(this)}}const Ei=new Y,Ol=new Y,ia=new Y,Xi=new Y,Bl=new Y,ra=new Y,zl=new Y;class Ip{constructor(e=new Y,t=new Y(0,0,-1)){this.origin=e,this.direction=t}set(e,t){return this.origin.copy(e),this.direction.copy(t),this}copy(e){return this.origin.copy(e.origin),this.direction.copy(e.direction),this}at(e,t){return t.copy(this.origin).addScaledVector(this.direction,e)}lookAt(e){return this.direction.copy(e).sub(this.origin).normalize(),this}recast(e){return this.origin.copy(this.at(e,Ei)),this}closestPointToPoint(e,t){t.subVectors(e,this.origin);const n=t.dot(this.direction);return n<0?t.copy(this.origin):t.copy(this.origin).addScaledVector(this.direction,n)}distanceToPoint(e){return Math.sqrt(this.distanceSqToPoint(e))}distanceSqToPoint(e){const t=Ei.subVectors(e,this.origin).dot(this.direction);return t<0?this.origin.distanceToSquared(e):(Ei.copy(this.origin).addScaledVector(this.direction,t),Ei.distanceToSquared(e))}distanceSqToSegment(e,t,n,i){Ol.copy(e).add(t).multiplyScalar(.5),ia.copy(t).sub(e).normalize(),Xi.copy(this.origin).sub(Ol);const s=e.distanceTo(t)*.5,o=-this.direction.dot(ia),a=Xi.dot(this.direction),l=-Xi.dot(ia),c=Xi.lengthSq(),u=Math.abs(1-o*o);let f,h,d,_;if(u>0)if(f=o*l-a,h=o*a-l,_=s*u,f>=0)if(h>=-_)if(h<=_){const g=1/u;f*=g,h*=g,d=f*(f+o*h+2*a)+h*(o*f+h+2*l)+c}else h=s,f=Math.max(0,-(o*h+a)),d=-f*f+h*(h+2*l)+c;else h=-s,f=Math.max(0,-(o*h+a)),d=-f*f+h*(h+2*l)+c;else h<=-_?(f=Math.max(0,-(-o*s+a)),h=f>0?-s:Math.min(Math.max(-s,-l),s),d=-f*f+h*(h+2*l)+c):h<=_?(f=0,h=Math.min(Math.max(-s,-l),s),d=h*(h+2*l)+c):(f=Math.max(0,-(o*s+a)),h=f>0?s:Math.min(Math.max(-s,-l),s),d=-f*f+h*(h+2*l)+c);else h=o>0?-s:s,f=Math.max(0,-(o*h+a)),d=-f*f+h*(h+2*l)+c;return n&&n.copy(this.origin).addScaledVector(this.direction,f),i&&i.copy(Ol).addScaledVector(ia,h),d}intersectSphere(e,t){Ei.subVectors(e.center,this.origin);const n=Ei.dot(this.direction),i=Ei.dot(Ei)-n*n,s=e.radius*e.radius;if(i>s)return null;const o=Math.sqrt(s-i),a=n-o,l=n+o;return l<0?null:a<0?this.at(l,t):this.at(a,t)}intersectsSphere(e){return this.distanceSqToPoint(e.center)<=e.radius*e.radius}distanceToPlane(e){const t=e.normal.dot(this.direction);if(t===0)return e.distanceToPoint(this.origin)===0?0:null;const n=-(this.origin.dot(e.normal)+e.constant)/t;return n>=0?n:null}intersectPlane(e,t){const n=this.distanceToPlane(e);return n===null?null:this.at(n,t)}intersectsPlane(e){const t=e.distanceToPoint(this.origin);return t===0||e.normal.dot(this.direction)*t<0}intersectBox(e,t){let n,i,s,o,a,l;const c=1/this.direction.x,u=1/this.direction.y,f=1/this.direction.z,h=this.origin;return c>=0?(n=(e.min.x-h.x)*c,i=(e.max.x-h.x)*c):(n=(e.max.x-h.x)*c,i=(e.min.x-h.x)*c),u>=0?(s=(e.min.y-h.y)*u,o=(e.max.y-h.y)*u):(s=(e.max.y-h.y)*u,o=(e.min.y-h.y)*u),n>o||s>i||((s>n||isNaN(n))&&(n=s),(o<i||isNaN(i))&&(i=o),f>=0?(a=(e.min.z-h.z)*f,l=(e.max.z-h.z)*f):(a=(e.max.z-h.z)*f,l=(e.min.z-h.z)*f),n>l||a>i)||((a>n||n!==n)&&(n=a),(l<i||i!==i)&&(i=l),i<0)?null:this.at(n>=0?n:i,t)}intersectsBox(e){return this.intersectBox(e,Ei)!==null}intersectTriangle(e,t,n,i,s){Bl.subVectors(t,e),ra.subVectors(n,e),zl.crossVectors(Bl,ra);let o=this.direction.dot(zl),a;if(o>0){if(i)return null;a=1}else if(o<0)a=-1,o=-o;else return null;Xi.subVectors(this.origin,e);const l=a*this.direction.dot(ra.crossVectors(Xi,ra));if(l<0)return null;const c=a*this.direction.dot(Bl.cross(Xi));if(c<0||l+c>o)return null;const u=-a*Xi.dot(zl);return u<0?null:this.at(u/o,s)}applyMatrix4(e){return this.origin.applyMatrix4(e),this.direction.transformDirection(e),this}equals(e){return e.origin.equals(this.origin)&&e.direction.equals(this.direction)}clone(){return new this.constructor().copy(this)}}class Ot{constructor(e,t,n,i,s,o,a,l,c,u,f,h,d,_,g,p){Ot.prototype.isMatrix4=!0,this.elements=[1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1],e!==void 0&&this.set(e,t,n,i,s,o,a,l,c,u,f,h,d,_,g,p)}set(e,t,n,i,s,o,a,l,c,u,f,h,d,_,g,p){const m=this.elements;return m[0]=e,m[4]=t,m[8]=n,m[12]=i,m[1]=s,m[5]=o,m[9]=a,m[13]=l,m[2]=c,m[6]=u,m[10]=f,m[14]=h,m[3]=d,m[7]=_,m[11]=g,m[15]=p,this}identity(){return this.set(1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1),this}clone(){return new Ot().fromArray(this.elements)}copy(e){const t=this.elements,n=e.elements;return t[0]=n[0],t[1]=n[1],t[2]=n[2],t[3]=n[3],t[4]=n[4],t[5]=n[5],t[6]=n[6],t[7]=n[7],t[8]=n[8],t[9]=n[9],t[10]=n[10],t[11]=n[11],t[12]=n[12],t[13]=n[13],t[14]=n[14],t[15]=n[15],this}copyPosition(e){const t=this.elements,n=e.elements;return t[12]=n[12],t[13]=n[13],t[14]=n[14],this}setFromMatrix3(e){const t=e.elements;return this.set(t[0],t[3],t[6],0,t[1],t[4],t[7],0,t[2],t[5],t[8],0,0,0,0,1),this}extractBasis(e,t,n){return e.setFromMatrixColumn(this,0),t.setFromMatrixColumn(this,1),n.setFromMatrixColumn(this,2),this}makeBasis(e,t,n){return this.set(e.x,t.x,n.x,0,e.y,t.y,n.y,0,e.z,t.z,n.z,0,0,0,0,1),this}extractRotation(e){const t=this.elements,n=e.elements,i=1/is.setFromMatrixColumn(e,0).length(),s=1/is.setFromMatrixColumn(e,1).length(),o=1/is.setFromMatrixColumn(e,2).length();return t[0]=n[0]*i,t[1]=n[1]*i,t[2]=n[2]*i,t[3]=0,t[4]=n[4]*s,t[5]=n[5]*s,t[6]=n[6]*s,t[7]=0,t[8]=n[8]*o,t[9]=n[9]*o,t[10]=n[10]*o,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromEuler(e){const t=this.elements,n=e.x,i=e.y,s=e.z,o=Math.cos(n),a=Math.sin(n),l=Math.cos(i),c=Math.sin(i),u=Math.cos(s),f=Math.sin(s);if(e.order==="XYZ"){const h=o*u,d=o*f,_=a*u,g=a*f;t[0]=l*u,t[4]=-l*f,t[8]=c,t[1]=d+_*c,t[5]=h-g*c,t[9]=-a*l,t[2]=g-h*c,t[6]=_+d*c,t[10]=o*l}else if(e.order==="YXZ"){const h=l*u,d=l*f,_=c*u,g=c*f;t[0]=h+g*a,t[4]=_*a-d,t[8]=o*c,t[1]=o*f,t[5]=o*u,t[9]=-a,t[2]=d*a-_,t[6]=g+h*a,t[10]=o*l}else if(e.order==="ZXY"){const h=l*u,d=l*f,_=c*u,g=c*f;t[0]=h-g*a,t[4]=-o*f,t[8]=_+d*a,t[1]=d+_*a,t[5]=o*u,t[9]=g-h*a,t[2]=-o*c,t[6]=a,t[10]=o*l}else if(e.order==="ZYX"){const h=o*u,d=o*f,_=a*u,g=a*f;t[0]=l*u,t[4]=_*c-d,t[8]=h*c+g,t[1]=l*f,t[5]=g*c+h,t[9]=d*c-_,t[2]=-c,t[6]=a*l,t[10]=o*l}else if(e.order==="YZX"){const h=o*l,d=o*c,_=a*l,g=a*c;t[0]=l*u,t[4]=g-h*f,t[8]=_*f+d,t[1]=f,t[5]=o*u,t[9]=-a*u,t[2]=-c*u,t[6]=d*f+_,t[10]=h-g*f}else if(e.order==="XZY"){const h=o*l,d=o*c,_=a*l,g=a*c;t[0]=l*u,t[4]=-f,t[8]=c*u,t[1]=h*f+g,t[5]=o*u,t[9]=d*f-_,t[2]=_*f-d,t[6]=a*u,t[10]=g*f+h}return t[3]=0,t[7]=0,t[11]=0,t[12]=0,t[13]=0,t[14]=0,t[15]=1,this}makeRotationFromQuaternion(e){return this.compose(Jg,e,Qg)}lookAt(e,t,n){const i=this.elements;return Dn.subVectors(e,t),Dn.lengthSq()===0&&(Dn.z=1),Dn.normalize(),Yi.crossVectors(n,Dn),Yi.lengthSq()===0&&(Math.abs(n.z)===1?Dn.x+=1e-4:Dn.z+=1e-4,Dn.normalize(),Yi.crossVectors(n,Dn)),Yi.normalize(),sa.crossVectors(Dn,Yi),i[0]=Yi.x,i[4]=sa.x,i[8]=Dn.x,i[1]=Yi.y,i[5]=sa.y,i[9]=Dn.y,i[2]=Yi.z,i[6]=sa.z,i[10]=Dn.z,this}multiply(e){return this.multiplyMatrices(this,e)}premultiply(e){return this.multiplyMatrices(e,this)}multiplyMatrices(e,t){const n=e.elements,i=t.elements,s=this.elements,o=n[0],a=n[4],l=n[8],c=n[12],u=n[1],f=n[5],h=n[9],d=n[13],_=n[2],g=n[6],p=n[10],m=n[14],y=n[3],x=n[7],M=n[11],R=n[15],w=i[0],E=i[4],D=i[8],O=i[12],v=i[1],T=i[5],N=i[9],z=i[13],W=i[2],K=i[6],G=i[10],X=i[14],V=i[3],re=i[7],C=i[11],ae=i[15];return s[0]=o*w+a*v+l*W+c*V,s[4]=o*E+a*T+l*K+c*re,s[8]=o*D+a*N+l*G+c*C,s[12]=o*O+a*z+l*X+c*ae,s[1]=u*w+f*v+h*W+d*V,s[5]=u*E+f*T+h*K+d*re,s[9]=u*D+f*N+h*G+d*C,s[13]=u*O+f*z+h*X+d*ae,s[2]=_*w+g*v+p*W+m*V,s[6]=_*E+g*T+p*K+m*re,s[10]=_*D+g*N+p*G+m*C,s[14]=_*O+g*z+p*X+m*ae,s[3]=y*w+x*v+M*W+R*V,s[7]=y*E+x*T+M*K+R*re,s[11]=y*D+x*N+M*G+R*C,s[15]=y*O+x*z+M*X+R*ae,this}multiplyScalar(e){const t=this.elements;return t[0]*=e,t[4]*=e,t[8]*=e,t[12]*=e,t[1]*=e,t[5]*=e,t[9]*=e,t[13]*=e,t[2]*=e,t[6]*=e,t[10]*=e,t[14]*=e,t[3]*=e,t[7]*=e,t[11]*=e,t[15]*=e,this}determinant(){const e=this.elements,t=e[0],n=e[4],i=e[8],s=e[12],o=e[1],a=e[5],l=e[9],c=e[13],u=e[2],f=e[6],h=e[10],d=e[14],_=e[3],g=e[7],p=e[11],m=e[15];return _*(+s*l*f-i*c*f-s*a*h+n*c*h+i*a*d-n*l*d)+g*(+t*l*d-t*c*h+s*o*h-i*o*d+i*c*u-s*l*u)+p*(+t*c*f-t*a*d-s*o*f+n*o*d+s*a*u-n*c*u)+m*(-i*a*u-t*l*f+t*a*h+i*o*f-n*o*h+n*l*u)}transpose(){const e=this.elements;let t;return t=e[1],e[1]=e[4],e[4]=t,t=e[2],e[2]=e[8],e[8]=t,t=e[6],e[6]=e[9],e[9]=t,t=e[3],e[3]=e[12],e[12]=t,t=e[7],e[7]=e[13],e[13]=t,t=e[11],e[11]=e[14],e[14]=t,this}setPosition(e,t,n){const i=this.elements;return e.isVector3?(i[12]=e.x,i[13]=e.y,i[14]=e.z):(i[12]=e,i[13]=t,i[14]=n),this}invert(){const e=this.elements,t=e[0],n=e[1],i=e[2],s=e[3],o=e[4],a=e[5],l=e[6],c=e[7],u=e[8],f=e[9],h=e[10],d=e[11],_=e[12],g=e[13],p=e[14],m=e[15],y=f*p*c-g*h*c+g*l*d-a*p*d-f*l*m+a*h*m,x=_*h*c-u*p*c-_*l*d+o*p*d+u*l*m-o*h*m,M=u*g*c-_*f*c+_*a*d-o*g*d-u*a*m+o*f*m,R=_*f*l-u*g*l-_*a*h+o*g*h+u*a*p-o*f*p,w=t*y+n*x+i*M+s*R;if(w===0)return this.set(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0);const E=1/w;return e[0]=y*E,e[1]=(g*h*s-f*p*s-g*i*d+n*p*d+f*i*m-n*h*m)*E,e[2]=(a*p*s-g*l*s+g*i*c-n*p*c-a*i*m+n*l*m)*E,e[3]=(f*l*s-a*h*s-f*i*c+n*h*c+a*i*d-n*l*d)*E,e[4]=x*E,e[5]=(u*p*s-_*h*s+_*i*d-t*p*d-u*i*m+t*h*m)*E,e[6]=(_*l*s-o*p*s-_*i*c+t*p*c+o*i*m-t*l*m)*E,e[7]=(o*h*s-u*l*s+u*i*c-t*h*c-o*i*d+t*l*d)*E,e[8]=M*E,e[9]=(_*f*s-u*g*s-_*n*d+t*g*d+u*n*m-t*f*m)*E,e[10]=(o*g*s-_*a*s+_*n*c-t*g*c-o*n*m+t*a*m)*E,e[11]=(u*a*s-o*f*s-u*n*c+t*f*c+o*n*d-t*a*d)*E,e[12]=R*E,e[13]=(u*g*i-_*f*i+_*n*h-t*g*h-u*n*p+t*f*p)*E,e[14]=(_*a*i-o*g*i-_*n*l+t*g*l+o*n*p-t*a*p)*E,e[15]=(o*f*i-u*a*i+u*n*l-t*f*l-o*n*h+t*a*h)*E,this}scale(e){const t=this.elements,n=e.x,i=e.y,s=e.z;return t[0]*=n,t[4]*=i,t[8]*=s,t[1]*=n,t[5]*=i,t[9]*=s,t[2]*=n,t[6]*=i,t[10]*=s,t[3]*=n,t[7]*=i,t[11]*=s,this}getMaxScaleOnAxis(){const e=this.elements,t=e[0]*e[0]+e[1]*e[1]+e[2]*e[2],n=e[4]*e[4]+e[5]*e[5]+e[6]*e[6],i=e[8]*e[8]+e[9]*e[9]+e[10]*e[10];return Math.sqrt(Math.max(t,n,i))}makeTranslation(e,t,n){return e.isVector3?this.set(1,0,0,e.x,0,1,0,e.y,0,0,1,e.z,0,0,0,1):this.set(1,0,0,e,0,1,0,t,0,0,1,n,0,0,0,1),this}makeRotationX(e){const t=Math.cos(e),n=Math.sin(e);return this.set(1,0,0,0,0,t,-n,0,0,n,t,0,0,0,0,1),this}makeRotationY(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,0,n,0,0,1,0,0,-n,0,t,0,0,0,0,1),this}makeRotationZ(e){const t=Math.cos(e),n=Math.sin(e);return this.set(t,-n,0,0,n,t,0,0,0,0,1,0,0,0,0,1),this}makeRotationAxis(e,t){const n=Math.cos(t),i=Math.sin(t),s=1-n,o=e.x,a=e.y,l=e.z,c=s*o,u=s*a;return this.set(c*o+n,c*a-i*l,c*l+i*a,0,c*a+i*l,u*a+n,u*l-i*o,0,c*l-i*a,u*l+i*o,s*l*l+n,0,0,0,0,1),this}makeScale(e,t,n){return this.set(e,0,0,0,0,t,0,0,0,0,n,0,0,0,0,1),this}makeShear(e,t,n,i,s,o){return this.set(1,n,s,0,e,1,o,0,t,i,1,0,0,0,0,1),this}compose(e,t,n){const i=this.elements,s=t._x,o=t._y,a=t._z,l=t._w,c=s+s,u=o+o,f=a+a,h=s*c,d=s*u,_=s*f,g=o*u,p=o*f,m=a*f,y=l*c,x=l*u,M=l*f,R=n.x,w=n.y,E=n.z;return i[0]=(1-(g+m))*R,i[1]=(d+M)*R,i[2]=(_-x)*R,i[3]=0,i[4]=(d-M)*w,i[5]=(1-(h+m))*w,i[6]=(p+y)*w,i[7]=0,i[8]=(_+x)*E,i[9]=(p-y)*E,i[10]=(1-(h+g))*E,i[11]=0,i[12]=e.x,i[13]=e.y,i[14]=e.z,i[15]=1,this}decompose(e,t,n){const i=this.elements;let s=is.set(i[0],i[1],i[2]).length();const o=is.set(i[4],i[5],i[6]).length(),a=is.set(i[8],i[9],i[10]).length();this.determinant()<0&&(s=-s),e.x=i[12],e.y=i[13],e.z=i[14],ii.copy(this);const c=1/s,u=1/o,f=1/a;return ii.elements[0]*=c,ii.elements[1]*=c,ii.elements[2]*=c,ii.elements[4]*=u,ii.elements[5]*=u,ii.elements[6]*=u,ii.elements[8]*=f,ii.elements[9]*=f,ii.elements[10]*=f,t.setFromRotationMatrix(ii),n.x=s,n.y=o,n.z=a,this}makePerspective(e,t,n,i,s,o,a=Ni){const l=this.elements,c=2*s/(t-e),u=2*s/(n-i),f=(t+e)/(t-e),h=(n+i)/(n-i);let d,_;if(a===Ni)d=-(o+s)/(o-s),_=-2*o*s/(o-s);else if(a===el)d=-o/(o-s),_=-o*s/(o-s);else throw new Error("THREE.Matrix4.makePerspective(): Invalid coordinate system: "+a);return l[0]=c,l[4]=0,l[8]=f,l[12]=0,l[1]=0,l[5]=u,l[9]=h,l[13]=0,l[2]=0,l[6]=0,l[10]=d,l[14]=_,l[3]=0,l[7]=0,l[11]=-1,l[15]=0,this}makeOrthographic(e,t,n,i,s,o,a=Ni){const l=this.elements,c=1/(t-e),u=1/(n-i),f=1/(o-s),h=(t+e)*c,d=(n+i)*u;let _,g;if(a===Ni)_=(o+s)*f,g=-2*f;else if(a===el)_=s*f,g=-1*f;else throw new Error("THREE.Matrix4.makeOrthographic(): Invalid coordinate system: "+a);return l[0]=2*c,l[4]=0,l[8]=0,l[12]=-h,l[1]=0,l[5]=2*u,l[9]=0,l[13]=-d,l[2]=0,l[6]=0,l[10]=g,l[14]=-_,l[3]=0,l[7]=0,l[11]=0,l[15]=1,this}equals(e){const t=this.elements,n=e.elements;for(let i=0;i<16;i++)if(t[i]!==n[i])return!1;return!0}fromArray(e,t=0){for(let n=0;n<16;n++)this.elements[n]=e[n+t];return this}toArray(e=[],t=0){const n=this.elements;return e[t]=n[0],e[t+1]=n[1],e[t+2]=n[2],e[t+3]=n[3],e[t+4]=n[4],e[t+5]=n[5],e[t+6]=n[6],e[t+7]=n[7],e[t+8]=n[8],e[t+9]=n[9],e[t+10]=n[10],e[t+11]=n[11],e[t+12]=n[12],e[t+13]=n[13],e[t+14]=n[14],e[t+15]=n[15],e}}const is=new Y,ii=new Ot,Jg=new Y(0,0,0),Qg=new Y(1,1,1),Yi=new Y,sa=new Y,Dn=new Y,sf=new Ot,of=new Uo;class ki{constructor(e=0,t=0,n=0,i=ki.DEFAULT_ORDER){this.isEuler=!0,this._x=e,this._y=t,this._z=n,this._order=i}get x(){return this._x}set x(e){this._x=e,this._onChangeCallback()}get y(){return this._y}set y(e){this._y=e,this._onChangeCallback()}get z(){return this._z}set z(e){this._z=e,this._onChangeCallback()}get order(){return this._order}set order(e){this._order=e,this._onChangeCallback()}set(e,t,n,i=this._order){return this._x=e,this._y=t,this._z=n,this._order=i,this._onChangeCallback(),this}clone(){return new this.constructor(this._x,this._y,this._z,this._order)}copy(e){return this._x=e._x,this._y=e._y,this._z=e._z,this._order=e._order,this._onChangeCallback(),this}setFromRotationMatrix(e,t=this._order,n=!0){const i=e.elements,s=i[0],o=i[4],a=i[8],l=i[1],c=i[5],u=i[9],f=i[2],h=i[6],d=i[10];switch(t){case"XYZ":this._y=Math.asin(Mn(a,-1,1)),Math.abs(a)<.9999999?(this._x=Math.atan2(-u,d),this._z=Math.atan2(-o,s)):(this._x=Math.atan2(h,c),this._z=0);break;case"YXZ":this._x=Math.asin(-Mn(u,-1,1)),Math.abs(u)<.9999999?(this._y=Math.atan2(a,d),this._z=Math.atan2(l,c)):(this._y=Math.atan2(-f,s),this._z=0);break;case"ZXY":this._x=Math.asin(Mn(h,-1,1)),Math.abs(h)<.9999999?(this._y=Math.atan2(-f,d),this._z=Math.atan2(-o,c)):(this._y=0,this._z=Math.atan2(l,s));break;case"ZYX":this._y=Math.asin(-Mn(f,-1,1)),Math.abs(f)<.9999999?(this._x=Math.atan2(h,d),this._z=Math.atan2(l,s)):(this._x=0,this._z=Math.atan2(-o,c));break;case"YZX":this._z=Math.asin(Mn(l,-1,1)),Math.abs(l)<.9999999?(this._x=Math.atan2(-u,c),this._y=Math.atan2(-f,s)):(this._x=0,this._y=Math.atan2(a,d));break;case"XZY":this._z=Math.asin(-Mn(o,-1,1)),Math.abs(o)<.9999999?(this._x=Math.atan2(h,c),this._y=Math.atan2(a,s)):(this._x=Math.atan2(-u,d),this._y=0);break;default:console.warn("THREE.Euler: .setFromRotationMatrix() encountered an unknown order: "+t)}return this._order=t,n===!0&&this._onChangeCallback(),this}setFromQuaternion(e,t,n){return sf.makeRotationFromQuaternion(e),this.setFromRotationMatrix(sf,t,n)}setFromVector3(e,t=this._order){return this.set(e.x,e.y,e.z,t)}reorder(e){return of.setFromEuler(this),this.setFromQuaternion(of,e)}equals(e){return e._x===this._x&&e._y===this._y&&e._z===this._z&&e._order===this._order}fromArray(e){return this._x=e[0],this._y=e[1],this._z=e[2],e[3]!==void 0&&(this._order=e[3]),this._onChangeCallback(),this}toArray(e=[],t=0){return e[t]=this._x,e[t+1]=this._y,e[t+2]=this._z,e[t+3]=this._order,e}_onChange(e){return this._onChangeCallback=e,this}_onChangeCallback(){}*[Symbol.iterator](){yield this._x,yield this._y,yield this._z,yield this._order}}ki.DEFAULT_ORDER="XYZ";class Up{constructor(){this.mask=1}set(e){this.mask=(1<<e|0)>>>0}enable(e){this.mask|=1<<e|0}enableAll(){this.mask=-1}toggle(e){this.mask^=1<<e|0}disable(e){this.mask&=~(1<<e|0)}disableAll(){this.mask=0}test(e){return(this.mask&e.mask)!==0}isEnabled(e){return(this.mask&(1<<e|0))!==0}}let e0=0;const af=new Y,rs=new Uo,Ti=new Ot,oa=new Y,js=new Y,t0=new Y,n0=new Uo,lf=new Y(1,0,0),cf=new Y(0,1,0),uf=new Y(0,0,1),hf={type:"added"},i0={type:"removed"},ss={type:"childadded",child:null},kl={type:"childremoved",child:null};class An extends Gs{constructor(){super(),this.isObject3D=!0,Object.defineProperty(this,"id",{value:e0++}),this.uuid=Io(),this.name="",this.type="Object3D",this.parent=null,this.children=[],this.up=An.DEFAULT_UP.clone();const e=new Y,t=new ki,n=new Uo,i=new Y(1,1,1);function s(){n.setFromEuler(t,!1)}function o(){t.setFromQuaternion(n,void 0,!1)}t._onChange(s),n._onChange(o),Object.defineProperties(this,{position:{configurable:!0,enumerable:!0,value:e},rotation:{configurable:!0,enumerable:!0,value:t},quaternion:{configurable:!0,enumerable:!0,value:n},scale:{configurable:!0,enumerable:!0,value:i},modelViewMatrix:{value:new Ot},normalMatrix:{value:new Ke}}),this.matrix=new Ot,this.matrixWorld=new Ot,this.matrixAutoUpdate=An.DEFAULT_MATRIX_AUTO_UPDATE,this.matrixWorldAutoUpdate=An.DEFAULT_MATRIX_WORLD_AUTO_UPDATE,this.matrixWorldNeedsUpdate=!1,this.layers=new Up,this.visible=!0,this.castShadow=!1,this.receiveShadow=!1,this.frustumCulled=!0,this.renderOrder=0,this.animations=[],this.userData={}}onBeforeShadow(){}onAfterShadow(){}onBeforeRender(){}onAfterRender(){}applyMatrix4(e){this.matrixAutoUpdate&&this.updateMatrix(),this.matrix.premultiply(e),this.matrix.decompose(this.position,this.quaternion,this.scale)}applyQuaternion(e){return this.quaternion.premultiply(e),this}setRotationFromAxisAngle(e,t){this.quaternion.setFromAxisAngle(e,t)}setRotationFromEuler(e){this.quaternion.setFromEuler(e,!0)}setRotationFromMatrix(e){this.quaternion.setFromRotationMatrix(e)}setRotationFromQuaternion(e){this.quaternion.copy(e)}rotateOnAxis(e,t){return rs.setFromAxisAngle(e,t),this.quaternion.multiply(rs),this}rotateOnWorldAxis(e,t){return rs.setFromAxisAngle(e,t),this.quaternion.premultiply(rs),this}rotateX(e){return this.rotateOnAxis(lf,e)}rotateY(e){return this.rotateOnAxis(cf,e)}rotateZ(e){return this.rotateOnAxis(uf,e)}translateOnAxis(e,t){return af.copy(e).applyQuaternion(this.quaternion),this.position.add(af.multiplyScalar(t)),this}translateX(e){return this.translateOnAxis(lf,e)}translateY(e){return this.translateOnAxis(cf,e)}translateZ(e){return this.translateOnAxis(uf,e)}localToWorld(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(this.matrixWorld)}worldToLocal(e){return this.updateWorldMatrix(!0,!1),e.applyMatrix4(Ti.copy(this.matrixWorld).invert())}lookAt(e,t,n){e.isVector3?oa.copy(e):oa.set(e,t,n);const i=this.parent;this.updateWorldMatrix(!0,!1),js.setFromMatrixPosition(this.matrixWorld),this.isCamera||this.isLight?Ti.lookAt(js,oa,this.up):Ti.lookAt(oa,js,this.up),this.quaternion.setFromRotationMatrix(Ti),i&&(Ti.extractRotation(i.matrixWorld),rs.setFromRotationMatrix(Ti),this.quaternion.premultiply(rs.invert()))}add(e){if(arguments.length>1){for(let t=0;t<arguments.length;t++)this.add(arguments[t]);return this}return e===this?(console.error("THREE.Object3D.add: object can't be added as a child of itself.",e),this):(e&&e.isObject3D?(e.removeFromParent(),e.parent=this,this.children.push(e),e.dispatchEvent(hf),ss.child=e,this.dispatchEvent(ss),ss.child=null):console.error("THREE.Object3D.add: object not an instance of THREE.Object3D.",e),this)}remove(e){if(arguments.length>1){for(let n=0;n<arguments.length;n++)this.remove(arguments[n]);return this}const t=this.children.indexOf(e);return t!==-1&&(e.parent=null,this.children.splice(t,1),e.dispatchEvent(i0),kl.child=e,this.dispatchEvent(kl),kl.child=null),this}removeFromParent(){const e=this.parent;return e!==null&&e.remove(this),this}clear(){return this.remove(...this.children)}attach(e){return this.updateWorldMatrix(!0,!1),Ti.copy(this.matrixWorld).invert(),e.parent!==null&&(e.parent.updateWorldMatrix(!0,!1),Ti.multiply(e.parent.matrixWorld)),e.applyMatrix4(Ti),e.removeFromParent(),e.parent=this,this.children.push(e),e.updateWorldMatrix(!1,!0),e.dispatchEvent(hf),ss.child=e,this.dispatchEvent(ss),ss.child=null,this}getObjectById(e){return this.getObjectByProperty("id",e)}getObjectByName(e){return this.getObjectByProperty("name",e)}getObjectByProperty(e,t){if(this[e]===t)return this;for(let n=0,i=this.children.length;n<i;n++){const o=this.children[n].getObjectByProperty(e,t);if(o!==void 0)return o}}getObjectsByProperty(e,t,n=[]){this[e]===t&&n.push(this);const i=this.children;for(let s=0,o=i.length;s<o;s++)i[s].getObjectsByProperty(e,t,n);return n}getWorldPosition(e){return this.updateWorldMatrix(!0,!1),e.setFromMatrixPosition(this.matrixWorld)}getWorldQuaternion(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(js,e,t0),e}getWorldScale(e){return this.updateWorldMatrix(!0,!1),this.matrixWorld.decompose(js,n0,e),e}getWorldDirection(e){this.updateWorldMatrix(!0,!1);const t=this.matrixWorld.elements;return e.set(t[8],t[9],t[10]).normalize()}raycast(){}traverse(e){e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverse(e)}traverseVisible(e){if(this.visible===!1)return;e(this);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].traverseVisible(e)}traverseAncestors(e){const t=this.parent;t!==null&&(e(t),t.traverseAncestors(e))}updateMatrix(){this.matrix.compose(this.position,this.quaternion,this.scale),this.matrixWorldNeedsUpdate=!0}updateMatrixWorld(e){this.matrixAutoUpdate&&this.updateMatrix(),(this.matrixWorldNeedsUpdate||e)&&(this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),this.matrixWorldNeedsUpdate=!1,e=!0);const t=this.children;for(let n=0,i=t.length;n<i;n++)t[n].updateMatrixWorld(e)}updateWorldMatrix(e,t){const n=this.parent;if(e===!0&&n!==null&&n.updateWorldMatrix(!0,!1),this.matrixAutoUpdate&&this.updateMatrix(),this.matrixWorldAutoUpdate===!0&&(this.parent===null?this.matrixWorld.copy(this.matrix):this.matrixWorld.multiplyMatrices(this.parent.matrixWorld,this.matrix)),t===!0){const i=this.children;for(let s=0,o=i.length;s<o;s++)i[s].updateWorldMatrix(!1,!0)}}toJSON(e){const t=e===void 0||typeof e=="string",n={};t&&(e={geometries:{},materials:{},textures:{},images:{},shapes:{},skeletons:{},animations:{},nodes:{}},n.metadata={version:4.6,type:"Object",generator:"Object3D.toJSON"});const i={};i.uuid=this.uuid,i.type=this.type,this.name!==""&&(i.name=this.name),this.castShadow===!0&&(i.castShadow=!0),this.receiveShadow===!0&&(i.receiveShadow=!0),this.visible===!1&&(i.visible=!1),this.frustumCulled===!1&&(i.frustumCulled=!1),this.renderOrder!==0&&(i.renderOrder=this.renderOrder),Object.keys(this.userData).length>0&&(i.userData=this.userData),i.layers=this.layers.mask,i.matrix=this.matrix.toArray(),i.up=this.up.toArray(),this.matrixAutoUpdate===!1&&(i.matrixAutoUpdate=!1),this.isInstancedMesh&&(i.type="InstancedMesh",i.count=this.count,i.instanceMatrix=this.instanceMatrix.toJSON(),this.instanceColor!==null&&(i.instanceColor=this.instanceColor.toJSON())),this.isBatchedMesh&&(i.type="BatchedMesh",i.perObjectFrustumCulled=this.perObjectFrustumCulled,i.sortObjects=this.sortObjects,i.drawRanges=this._drawRanges,i.reservedRanges=this._reservedRanges,i.visibility=this._visibility,i.active=this._active,i.bounds=this._bounds.map(a=>({boxInitialized:a.boxInitialized,boxMin:a.box.min.toArray(),boxMax:a.box.max.toArray(),sphereInitialized:a.sphereInitialized,sphereRadius:a.sphere.radius,sphereCenter:a.sphere.center.toArray()})),i.maxInstanceCount=this._maxInstanceCount,i.maxVertexCount=this._maxVertexCount,i.maxIndexCount=this._maxIndexCount,i.geometryInitialized=this._geometryInitialized,i.geometryCount=this._geometryCount,i.matricesTexture=this._matricesTexture.toJSON(e),this._colorsTexture!==null&&(i.colorsTexture=this._colorsTexture.toJSON(e)),this.boundingSphere!==null&&(i.boundingSphere={center:i.boundingSphere.center.toArray(),radius:i.boundingSphere.radius}),this.boundingBox!==null&&(i.boundingBox={min:i.boundingBox.min.toArray(),max:i.boundingBox.max.toArray()}));function s(a,l){return a[l.uuid]===void 0&&(a[l.uuid]=l.toJSON(e)),l.uuid}if(this.isScene)this.background&&(this.background.isColor?i.background=this.background.toJSON():this.background.isTexture&&(i.background=this.background.toJSON(e).uuid)),this.environment&&this.environment.isTexture&&this.environment.isRenderTargetTexture!==!0&&(i.environment=this.environment.toJSON(e).uuid);else if(this.isMesh||this.isLine||this.isPoints){i.geometry=s(e.geometries,this.geometry);const a=this.geometry.parameters;if(a!==void 0&&a.shapes!==void 0){const l=a.shapes;if(Array.isArray(l))for(let c=0,u=l.length;c<u;c++){const f=l[c];s(e.shapes,f)}else s(e.shapes,l)}}if(this.isSkinnedMesh&&(i.bindMode=this.bindMode,i.bindMatrix=this.bindMatrix.toArray(),this.skeleton!==void 0&&(s(e.skeletons,this.skeleton),i.skeleton=this.skeleton.uuid)),this.material!==void 0)if(Array.isArray(this.material)){const a=[];for(let l=0,c=this.material.length;l<c;l++)a.push(s(e.materials,this.material[l]));i.material=a}else i.material=s(e.materials,this.material);if(this.children.length>0){i.children=[];for(let a=0;a<this.children.length;a++)i.children.push(this.children[a].toJSON(e).object)}if(this.animations.length>0){i.animations=[];for(let a=0;a<this.animations.length;a++){const l=this.animations[a];i.animations.push(s(e.animations,l))}}if(t){const a=o(e.geometries),l=o(e.materials),c=o(e.textures),u=o(e.images),f=o(e.shapes),h=o(e.skeletons),d=o(e.animations),_=o(e.nodes);a.length>0&&(n.geometries=a),l.length>0&&(n.materials=l),c.length>0&&(n.textures=c),u.length>0&&(n.images=u),f.length>0&&(n.shapes=f),h.length>0&&(n.skeletons=h),d.length>0&&(n.animations=d),_.length>0&&(n.nodes=_)}return n.object=i,n;function o(a){const l=[];for(const c in a){const u=a[c];delete u.metadata,l.push(u)}return l}}clone(e){return new this.constructor().copy(this,e)}copy(e,t=!0){if(this.name=e.name,this.up.copy(e.up),this.position.copy(e.position),this.rotation.order=e.rotation.order,this.quaternion.copy(e.quaternion),this.scale.copy(e.scale),this.matrix.copy(e.matrix),this.matrixWorld.copy(e.matrixWorld),this.matrixAutoUpdate=e.matrixAutoUpdate,this.matrixWorldAutoUpdate=e.matrixWorldAutoUpdate,this.matrixWorldNeedsUpdate=e.matrixWorldNeedsUpdate,this.layers.mask=e.layers.mask,this.visible=e.visible,this.castShadow=e.castShadow,this.receiveShadow=e.receiveShadow,this.frustumCulled=e.frustumCulled,this.renderOrder=e.renderOrder,this.animations=e.animations.slice(),this.userData=JSON.parse(JSON.stringify(e.userData)),t===!0)for(let n=0;n<e.children.length;n++){const i=e.children[n];this.add(i.clone())}return this}}An.DEFAULT_UP=new Y(0,1,0);An.DEFAULT_MATRIX_AUTO_UPDATE=!0;An.DEFAULT_MATRIX_WORLD_AUTO_UPDATE=!0;const ri=new Y,bi=new Y,Hl=new Y,wi=new Y,os=new Y,as=new Y,ff=new Y,Gl=new Y,Vl=new Y,Wl=new Y,Xl=new Nt,Yl=new Nt,ql=new Nt;class ci{constructor(e=new Y,t=new Y,n=new Y){this.a=e,this.b=t,this.c=n}static getNormal(e,t,n,i){i.subVectors(n,t),ri.subVectors(e,t),i.cross(ri);const s=i.lengthSq();return s>0?i.multiplyScalar(1/Math.sqrt(s)):i.set(0,0,0)}static getBarycoord(e,t,n,i,s){ri.subVectors(i,t),bi.subVectors(n,t),Hl.subVectors(e,t);const o=ri.dot(ri),a=ri.dot(bi),l=ri.dot(Hl),c=bi.dot(bi),u=bi.dot(Hl),f=o*c-a*a;if(f===0)return s.set(0,0,0),null;const h=1/f,d=(c*l-a*u)*h,_=(o*u-a*l)*h;return s.set(1-d-_,_,d)}static containsPoint(e,t,n,i){return this.getBarycoord(e,t,n,i,wi)===null?!1:wi.x>=0&&wi.y>=0&&wi.x+wi.y<=1}static getInterpolation(e,t,n,i,s,o,a,l){return this.getBarycoord(e,t,n,i,wi)===null?(l.x=0,l.y=0,"z"in l&&(l.z=0),"w"in l&&(l.w=0),null):(l.setScalar(0),l.addScaledVector(s,wi.x),l.addScaledVector(o,wi.y),l.addScaledVector(a,wi.z),l)}static getInterpolatedAttribute(e,t,n,i,s,o){return Xl.setScalar(0),Yl.setScalar(0),ql.setScalar(0),Xl.fromBufferAttribute(e,t),Yl.fromBufferAttribute(e,n),ql.fromBufferAttribute(e,i),o.setScalar(0),o.addScaledVector(Xl,s.x),o.addScaledVector(Yl,s.y),o.addScaledVector(ql,s.z),o}static isFrontFacing(e,t,n,i){return ri.subVectors(n,t),bi.subVectors(e,t),ri.cross(bi).dot(i)<0}set(e,t,n){return this.a.copy(e),this.b.copy(t),this.c.copy(n),this}setFromPointsAndIndices(e,t,n,i){return this.a.copy(e[t]),this.b.copy(e[n]),this.c.copy(e[i]),this}setFromAttributeAndIndices(e,t,n,i){return this.a.fromBufferAttribute(e,t),this.b.fromBufferAttribute(e,n),this.c.fromBufferAttribute(e,i),this}clone(){return new this.constructor().copy(this)}copy(e){return this.a.copy(e.a),this.b.copy(e.b),this.c.copy(e.c),this}getArea(){return ri.subVectors(this.c,this.b),bi.subVectors(this.a,this.b),ri.cross(bi).length()*.5}getMidpoint(e){return e.addVectors(this.a,this.b).add(this.c).multiplyScalar(1/3)}getNormal(e){return ci.getNormal(this.a,this.b,this.c,e)}getPlane(e){return e.setFromCoplanarPoints(this.a,this.b,this.c)}getBarycoord(e,t){return ci.getBarycoord(e,this.a,this.b,this.c,t)}getInterpolation(e,t,n,i,s){return ci.getInterpolation(e,this.a,this.b,this.c,t,n,i,s)}containsPoint(e){return ci.containsPoint(e,this.a,this.b,this.c)}isFrontFacing(e){return ci.isFrontFacing(this.a,this.b,this.c,e)}intersectsBox(e){return e.intersectsTriangle(this)}closestPointToPoint(e,t){const n=this.a,i=this.b,s=this.c;let o,a;os.subVectors(i,n),as.subVectors(s,n),Gl.subVectors(e,n);const l=os.dot(Gl),c=as.dot(Gl);if(l<=0&&c<=0)return t.copy(n);Vl.subVectors(e,i);const u=os.dot(Vl),f=as.dot(Vl);if(u>=0&&f<=u)return t.copy(i);const h=l*f-u*c;if(h<=0&&l>=0&&u<=0)return o=l/(l-u),t.copy(n).addScaledVector(os,o);Wl.subVectors(e,s);const d=os.dot(Wl),_=as.dot(Wl);if(_>=0&&d<=_)return t.copy(s);const g=d*c-l*_;if(g<=0&&c>=0&&_<=0)return a=c/(c-_),t.copy(n).addScaledVector(as,a);const p=u*_-d*f;if(p<=0&&f-u>=0&&d-_>=0)return ff.subVectors(s,i),a=(f-u)/(f-u+(d-_)),t.copy(i).addScaledVector(ff,a);const m=1/(p+g+h);return o=g*m,a=h*m,t.copy(n).addScaledVector(os,o).addScaledVector(as,a)}equals(e){return e.a.equals(this.a)&&e.b.equals(this.b)&&e.c.equals(this.c)}}const Np={aliceblue:15792383,antiquewhite:16444375,aqua:65535,aquamarine:8388564,azure:15794175,beige:16119260,bisque:16770244,black:0,blanchedalmond:16772045,blue:255,blueviolet:9055202,brown:10824234,burlywood:14596231,cadetblue:6266528,chartreuse:8388352,chocolate:13789470,coral:16744272,cornflowerblue:6591981,cornsilk:16775388,crimson:14423100,cyan:65535,darkblue:139,darkcyan:35723,darkgoldenrod:12092939,darkgray:11119017,darkgreen:25600,darkgrey:11119017,darkkhaki:12433259,darkmagenta:9109643,darkolivegreen:5597999,darkorange:16747520,darkorchid:10040012,darkred:9109504,darksalmon:15308410,darkseagreen:9419919,darkslateblue:4734347,darkslategray:3100495,darkslategrey:3100495,darkturquoise:52945,darkviolet:9699539,deeppink:16716947,deepskyblue:49151,dimgray:6908265,dimgrey:6908265,dodgerblue:2003199,firebrick:11674146,floralwhite:16775920,forestgreen:2263842,fuchsia:16711935,gainsboro:14474460,ghostwhite:16316671,gold:16766720,goldenrod:14329120,gray:8421504,green:32768,greenyellow:11403055,grey:8421504,honeydew:15794160,hotpink:16738740,indianred:13458524,indigo:4915330,ivory:16777200,khaki:15787660,lavender:15132410,lavenderblush:16773365,lawngreen:8190976,lemonchiffon:16775885,lightblue:11393254,lightcoral:15761536,lightcyan:14745599,lightgoldenrodyellow:16448210,lightgray:13882323,lightgreen:9498256,lightgrey:13882323,lightpink:16758465,lightsalmon:16752762,lightseagreen:2142890,lightskyblue:8900346,lightslategray:7833753,lightslategrey:7833753,lightsteelblue:11584734,lightyellow:16777184,lime:65280,limegreen:3329330,linen:16445670,magenta:16711935,maroon:8388608,mediumaquamarine:6737322,mediumblue:205,mediumorchid:12211667,mediumpurple:9662683,mediumseagreen:3978097,mediumslateblue:8087790,mediumspringgreen:64154,mediumturquoise:4772300,mediumvioletred:13047173,midnightblue:1644912,mintcream:16121850,mistyrose:16770273,moccasin:16770229,navajowhite:16768685,navy:128,oldlace:16643558,olive:8421376,olivedrab:7048739,orange:16753920,orangered:16729344,orchid:14315734,palegoldenrod:15657130,palegreen:10025880,paleturquoise:11529966,palevioletred:14381203,papayawhip:16773077,peachpuff:16767673,peru:13468991,pink:16761035,plum:14524637,powderblue:11591910,purple:8388736,rebeccapurple:6697881,red:16711680,rosybrown:12357519,royalblue:4286945,saddlebrown:9127187,salmon:16416882,sandybrown:16032864,seagreen:3050327,seashell:16774638,sienna:10506797,silver:12632256,skyblue:8900331,slateblue:6970061,slategray:7372944,slategrey:7372944,snow:16775930,springgreen:65407,steelblue:4620980,tan:13808780,teal:32896,thistle:14204888,tomato:16737095,turquoise:4251856,violet:15631086,wheat:16113331,white:16777215,whitesmoke:16119285,yellow:16776960,yellowgreen:10145074},qi={h:0,s:0,l:0},aa={h:0,s:0,l:0};function $l(r,e,t){return t<0&&(t+=1),t>1&&(t-=1),t<1/6?r+(e-r)*6*t:t<1/2?e:t<2/3?r+(e-r)*6*(2/3-t):r}class at{constructor(e,t,n){return this.isColor=!0,this.r=1,this.g=1,this.b=1,this.set(e,t,n)}set(e,t,n){if(t===void 0&&n===void 0){const i=e;i&&i.isColor?this.copy(i):typeof i=="number"?this.setHex(i):typeof i=="string"&&this.setStyle(i)}else this.setRGB(e,t,n);return this}setScalar(e){return this.r=e,this.g=e,this.b=e,this}setHex(e,t=ai){return e=Math.floor(e),this.r=(e>>16&255)/255,this.g=(e>>8&255)/255,this.b=(e&255)/255,ft.toWorkingColorSpace(this,t),this}setRGB(e,t,n,i=ft.workingColorSpace){return this.r=e,this.g=t,this.b=n,ft.toWorkingColorSpace(this,i),this}setHSL(e,t,n,i=ft.workingColorSpace){if(e=kg(e,1),t=Mn(t,0,1),n=Mn(n,0,1),t===0)this.r=this.g=this.b=n;else{const s=n<=.5?n*(1+t):n+t-n*t,o=2*n-s;this.r=$l(o,s,e+1/3),this.g=$l(o,s,e),this.b=$l(o,s,e-1/3)}return ft.toWorkingColorSpace(this,i),this}setStyle(e,t=ai){function n(s){s!==void 0&&parseFloat(s)<1&&console.warn("THREE.Color: Alpha component of "+e+" will be ignored.")}let i;if(i=/^(\w+)\(([^\)]*)\)/.exec(e)){let s;const o=i[1],a=i[2];switch(o){case"rgb":case"rgba":if(s=/^\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(s[4]),this.setRGB(Math.min(255,parseInt(s[1],10))/255,Math.min(255,parseInt(s[2],10))/255,Math.min(255,parseInt(s[3],10))/255,t);if(s=/^\s*(\d+)\%\s*,\s*(\d+)\%\s*,\s*(\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(s[4]),this.setRGB(Math.min(100,parseInt(s[1],10))/100,Math.min(100,parseInt(s[2],10))/100,Math.min(100,parseInt(s[3],10))/100,t);break;case"hsl":case"hsla":if(s=/^\s*(\d*\.?\d+)\s*,\s*(\d*\.?\d+)\%\s*,\s*(\d*\.?\d+)\%\s*(?:,\s*(\d*\.?\d+)\s*)?$/.exec(a))return n(s[4]),this.setHSL(parseFloat(s[1])/360,parseFloat(s[2])/100,parseFloat(s[3])/100,t);break;default:console.warn("THREE.Color: Unknown color model "+e)}}else if(i=/^\#([A-Fa-f\d]+)$/.exec(e)){const s=i[1],o=s.length;if(o===3)return this.setRGB(parseInt(s.charAt(0),16)/15,parseInt(s.charAt(1),16)/15,parseInt(s.charAt(2),16)/15,t);if(o===6)return this.setHex(parseInt(s,16),t);console.warn("THREE.Color: Invalid hex color "+e)}else if(e&&e.length>0)return this.setColorName(e,t);return this}setColorName(e,t=ai){const n=Np[e.toLowerCase()];return n!==void 0?this.setHex(n,t):console.warn("THREE.Color: Unknown color "+e),this}clone(){return new this.constructor(this.r,this.g,this.b)}copy(e){return this.r=e.r,this.g=e.g,this.b=e.b,this}copySRGBToLinear(e){return this.r=Rs(e.r),this.g=Rs(e.g),this.b=Rs(e.b),this}copyLinearToSRGB(e){return this.r=Ll(e.r),this.g=Ll(e.g),this.b=Ll(e.b),this}convertSRGBToLinear(){return this.copySRGBToLinear(this),this}convertLinearToSRGB(){return this.copyLinearToSRGB(this),this}getHex(e=ai){return ft.fromWorkingColorSpace(nn.copy(this),e),Math.round(Mn(nn.r*255,0,255))*65536+Math.round(Mn(nn.g*255,0,255))*256+Math.round(Mn(nn.b*255,0,255))}getHexString(e=ai){return("000000"+this.getHex(e).toString(16)).slice(-6)}getHSL(e,t=ft.workingColorSpace){ft.fromWorkingColorSpace(nn.copy(this),t);const n=nn.r,i=nn.g,s=nn.b,o=Math.max(n,i,s),a=Math.min(n,i,s);let l,c;const u=(a+o)/2;if(a===o)l=0,c=0;else{const f=o-a;switch(c=u<=.5?f/(o+a):f/(2-o-a),o){case n:l=(i-s)/f+(i<s?6:0);break;case i:l=(s-n)/f+2;break;case s:l=(n-i)/f+4;break}l/=6}return e.h=l,e.s=c,e.l=u,e}getRGB(e,t=ft.workingColorSpace){return ft.fromWorkingColorSpace(nn.copy(this),t),e.r=nn.r,e.g=nn.g,e.b=nn.b,e}getStyle(e=ai){ft.fromWorkingColorSpace(nn.copy(this),e);const t=nn.r,n=nn.g,i=nn.b;return e!==ai?`color(${e} ${t.toFixed(3)} ${n.toFixed(3)} ${i.toFixed(3)})`:`rgb(${Math.round(t*255)},${Math.round(n*255)},${Math.round(i*255)})`}offsetHSL(e,t,n){return this.getHSL(qi),this.setHSL(qi.h+e,qi.s+t,qi.l+n)}add(e){return this.r+=e.r,this.g+=e.g,this.b+=e.b,this}addColors(e,t){return this.r=e.r+t.r,this.g=e.g+t.g,this.b=e.b+t.b,this}addScalar(e){return this.r+=e,this.g+=e,this.b+=e,this}sub(e){return this.r=Math.max(0,this.r-e.r),this.g=Math.max(0,this.g-e.g),this.b=Math.max(0,this.b-e.b),this}multiply(e){return this.r*=e.r,this.g*=e.g,this.b*=e.b,this}multiplyScalar(e){return this.r*=e,this.g*=e,this.b*=e,this}lerp(e,t){return this.r+=(e.r-this.r)*t,this.g+=(e.g-this.g)*t,this.b+=(e.b-this.b)*t,this}lerpColors(e,t,n){return this.r=e.r+(t.r-e.r)*n,this.g=e.g+(t.g-e.g)*n,this.b=e.b+(t.b-e.b)*n,this}lerpHSL(e,t){this.getHSL(qi),e.getHSL(aa);const n=Pl(qi.h,aa.h,t),i=Pl(qi.s,aa.s,t),s=Pl(qi.l,aa.l,t);return this.setHSL(n,i,s),this}setFromVector3(e){return this.r=e.x,this.g=e.y,this.b=e.z,this}applyMatrix3(e){const t=this.r,n=this.g,i=this.b,s=e.elements;return this.r=s[0]*t+s[3]*n+s[6]*i,this.g=s[1]*t+s[4]*n+s[7]*i,this.b=s[2]*t+s[5]*n+s[8]*i,this}equals(e){return e.r===this.r&&e.g===this.g&&e.b===this.b}fromArray(e,t=0){return this.r=e[t],this.g=e[t+1],this.b=e[t+2],this}toArray(e=[],t=0){return e[t]=this.r,e[t+1]=this.g,e[t+2]=this.b,e}fromBufferAttribute(e,t){return this.r=e.getX(t),this.g=e.getY(t),this.b=e.getZ(t),this}toJSON(){return this.getHex()}*[Symbol.iterator](){yield this.r,yield this.g,yield this.b}}const nn=new at;at.NAMES=Np;let r0=0;class Fo extends Gs{constructor(){super(),this.isMaterial=!0,Object.defineProperty(this,"id",{value:r0++}),this.uuid=Io(),this.name="",this.type="Material",this.blending=zr,this.side=hr,this.vertexColors=!1,this.opacity=1,this.transparent=!1,this.alphaHash=!1,this.blendSrc=Nc,this.blendDst=Fc,this.blendEquation=Ar,this.blendSrcAlpha=null,this.blendDstAlpha=null,this.blendEquationAlpha=null,this.blendColor=new at(0,0,0),this.blendAlpha=0,this.depthFunc=Fs,this.depthTest=!0,this.depthWrite=!0,this.stencilWriteMask=255,this.stencilFunc=jh,this.stencilRef=0,this.stencilFuncMask=255,this.stencilFail=Jr,this.stencilZFail=Jr,this.stencilZPass=Jr,this.stencilWrite=!1,this.clippingPlanes=null,this.clipIntersection=!1,this.clipShadows=!1,this.shadowSide=null,this.colorWrite=!0,this.precision=null,this.polygonOffset=!1,this.polygonOffsetFactor=0,this.polygonOffsetUnits=0,this.dithering=!1,this.alphaToCoverage=!1,this.premultipliedAlpha=!1,this.forceSinglePass=!1,this.visible=!0,this.toneMapped=!0,this.userData={},this.version=0,this._alphaTest=0}get alphaTest(){return this._alphaTest}set alphaTest(e){this._alphaTest>0!=e>0&&this.version++,this._alphaTest=e}onBeforeRender(){}onBeforeCompile(){}customProgramCacheKey(){return this.onBeforeCompile.toString()}setValues(e){if(e!==void 0)for(const t in e){const n=e[t];if(n===void 0){console.warn(`THREE.Material: parameter '${t}' has value of undefined.`);continue}const i=this[t];if(i===void 0){console.warn(`THREE.Material: '${t}' is not a property of THREE.${this.type}.`);continue}i&&i.isColor?i.set(n):i&&i.isVector3&&n&&n.isVector3?i.copy(n):this[t]=n}}toJSON(e){const t=e===void 0||typeof e=="string";t&&(e={textures:{},images:{}});const n={metadata:{version:4.6,type:"Material",generator:"Material.toJSON"}};n.uuid=this.uuid,n.type=this.type,this.name!==""&&(n.name=this.name),this.color&&this.color.isColor&&(n.color=this.color.getHex()),this.roughness!==void 0&&(n.roughness=this.roughness),this.metalness!==void 0&&(n.metalness=this.metalness),this.sheen!==void 0&&(n.sheen=this.sheen),this.sheenColor&&this.sheenColor.isColor&&(n.sheenColor=this.sheenColor.getHex()),this.sheenRoughness!==void 0&&(n.sheenRoughness=this.sheenRoughness),this.emissive&&this.emissive.isColor&&(n.emissive=this.emissive.getHex()),this.emissiveIntensity!==void 0&&this.emissiveIntensity!==1&&(n.emissiveIntensity=this.emissiveIntensity),this.specular&&this.specular.isColor&&(n.specular=this.specular.getHex()),this.specularIntensity!==void 0&&(n.specularIntensity=this.specularIntensity),this.specularColor&&this.specularColor.isColor&&(n.specularColor=this.specularColor.getHex()),this.shininess!==void 0&&(n.shininess=this.shininess),this.clearcoat!==void 0&&(n.clearcoat=this.clearcoat),this.clearcoatRoughness!==void 0&&(n.clearcoatRoughness=this.clearcoatRoughness),this.clearcoatMap&&this.clearcoatMap.isTexture&&(n.clearcoatMap=this.clearcoatMap.toJSON(e).uuid),this.clearcoatRoughnessMap&&this.clearcoatRoughnessMap.isTexture&&(n.clearcoatRoughnessMap=this.clearcoatRoughnessMap.toJSON(e).uuid),this.clearcoatNormalMap&&this.clearcoatNormalMap.isTexture&&(n.clearcoatNormalMap=this.clearcoatNormalMap.toJSON(e).uuid,n.clearcoatNormalScale=this.clearcoatNormalScale.toArray()),this.dispersion!==void 0&&(n.dispersion=this.dispersion),this.iridescence!==void 0&&(n.iridescence=this.iridescence),this.iridescenceIOR!==void 0&&(n.iridescenceIOR=this.iridescenceIOR),this.iridescenceThicknessRange!==void 0&&(n.iridescenceThicknessRange=this.iridescenceThicknessRange),this.iridescenceMap&&this.iridescenceMap.isTexture&&(n.iridescenceMap=this.iridescenceMap.toJSON(e).uuid),this.iridescenceThicknessMap&&this.iridescenceThicknessMap.isTexture&&(n.iridescenceThicknessMap=this.iridescenceThicknessMap.toJSON(e).uuid),this.anisotropy!==void 0&&(n.anisotropy=this.anisotropy),this.anisotropyRotation!==void 0&&(n.anisotropyRotation=this.anisotropyRotation),this.anisotropyMap&&this.anisotropyMap.isTexture&&(n.anisotropyMap=this.anisotropyMap.toJSON(e).uuid),this.map&&this.map.isTexture&&(n.map=this.map.toJSON(e).uuid),this.matcap&&this.matcap.isTexture&&(n.matcap=this.matcap.toJSON(e).uuid),this.alphaMap&&this.alphaMap.isTexture&&(n.alphaMap=this.alphaMap.toJSON(e).uuid),this.lightMap&&this.lightMap.isTexture&&(n.lightMap=this.lightMap.toJSON(e).uuid,n.lightMapIntensity=this.lightMapIntensity),this.aoMap&&this.aoMap.isTexture&&(n.aoMap=this.aoMap.toJSON(e).uuid,n.aoMapIntensity=this.aoMapIntensity),this.bumpMap&&this.bumpMap.isTexture&&(n.bumpMap=this.bumpMap.toJSON(e).uuid,n.bumpScale=this.bumpScale),this.normalMap&&this.normalMap.isTexture&&(n.normalMap=this.normalMap.toJSON(e).uuid,n.normalMapType=this.normalMapType,n.normalScale=this.normalScale.toArray()),this.displacementMap&&this.displacementMap.isTexture&&(n.displacementMap=this.displacementMap.toJSON(e).uuid,n.displacementScale=this.displacementScale,n.displacementBias=this.displacementBias),this.roughnessMap&&this.roughnessMap.isTexture&&(n.roughnessMap=this.roughnessMap.toJSON(e).uuid),this.metalnessMap&&this.metalnessMap.isTexture&&(n.metalnessMap=this.metalnessMap.toJSON(e).uuid),this.emissiveMap&&this.emissiveMap.isTexture&&(n.emissiveMap=this.emissiveMap.toJSON(e).uuid),this.specularMap&&this.specularMap.isTexture&&(n.specularMap=this.specularMap.toJSON(e).uuid),this.specularIntensityMap&&this.specularIntensityMap.isTexture&&(n.specularIntensityMap=this.specularIntensityMap.toJSON(e).uuid),this.specularColorMap&&this.specularColorMap.isTexture&&(n.specularColorMap=this.specularColorMap.toJSON(e).uuid),this.envMap&&this.envMap.isTexture&&(n.envMap=this.envMap.toJSON(e).uuid,this.combine!==void 0&&(n.combine=this.combine)),this.envMapRotation!==void 0&&(n.envMapRotation=this.envMapRotation.toArray()),this.envMapIntensity!==void 0&&(n.envMapIntensity=this.envMapIntensity),this.reflectivity!==void 0&&(n.reflectivity=this.reflectivity),this.refractionRatio!==void 0&&(n.refractionRatio=this.refractionRatio),this.gradientMap&&this.gradientMap.isTexture&&(n.gradientMap=this.gradientMap.toJSON(e).uuid),this.transmission!==void 0&&(n.transmission=this.transmission),this.transmissionMap&&this.transmissionMap.isTexture&&(n.transmissionMap=this.transmissionMap.toJSON(e).uuid),this.thickness!==void 0&&(n.thickness=this.thickness),this.thicknessMap&&this.thicknessMap.isTexture&&(n.thicknessMap=this.thicknessMap.toJSON(e).uuid),this.attenuationDistance!==void 0&&this.attenuationDistance!==1/0&&(n.attenuationDistance=this.attenuationDistance),this.attenuationColor!==void 0&&(n.attenuationColor=this.attenuationColor.getHex()),this.size!==void 0&&(n.size=this.size),this.shadowSide!==null&&(n.shadowSide=this.shadowSide),this.sizeAttenuation!==void 0&&(n.sizeAttenuation=this.sizeAttenuation),this.blending!==zr&&(n.blending=this.blending),this.side!==hr&&(n.side=this.side),this.vertexColors===!0&&(n.vertexColors=!0),this.opacity<1&&(n.opacity=this.opacity),this.transparent===!0&&(n.transparent=!0),this.blendSrc!==Nc&&(n.blendSrc=this.blendSrc),this.blendDst!==Fc&&(n.blendDst=this.blendDst),this.blendEquation!==Ar&&(n.blendEquation=this.blendEquation),this.blendSrcAlpha!==null&&(n.blendSrcAlpha=this.blendSrcAlpha),this.blendDstAlpha!==null&&(n.blendDstAlpha=this.blendDstAlpha),this.blendEquationAlpha!==null&&(n.blendEquationAlpha=this.blendEquationAlpha),this.blendColor&&this.blendColor.isColor&&(n.blendColor=this.blendColor.getHex()),this.blendAlpha!==0&&(n.blendAlpha=this.blendAlpha),this.depthFunc!==Fs&&(n.depthFunc=this.depthFunc),this.depthTest===!1&&(n.depthTest=this.depthTest),this.depthWrite===!1&&(n.depthWrite=this.depthWrite),this.colorWrite===!1&&(n.colorWrite=this.colorWrite),this.stencilWriteMask!==255&&(n.stencilWriteMask=this.stencilWriteMask),this.stencilFunc!==jh&&(n.stencilFunc=this.stencilFunc),this.stencilRef!==0&&(n.stencilRef=this.stencilRef),this.stencilFuncMask!==255&&(n.stencilFuncMask=this.stencilFuncMask),this.stencilFail!==Jr&&(n.stencilFail=this.stencilFail),this.stencilZFail!==Jr&&(n.stencilZFail=this.stencilZFail),this.stencilZPass!==Jr&&(n.stencilZPass=this.stencilZPass),this.stencilWrite===!0&&(n.stencilWrite=this.stencilWrite),this.rotation!==void 0&&this.rotation!==0&&(n.rotation=this.rotation),this.polygonOffset===!0&&(n.polygonOffset=!0),this.polygonOffsetFactor!==0&&(n.polygonOffsetFactor=this.polygonOffsetFactor),this.polygonOffsetUnits!==0&&(n.polygonOffsetUnits=this.polygonOffsetUnits),this.linewidth!==void 0&&this.linewidth!==1&&(n.linewidth=this.linewidth),this.dashSize!==void 0&&(n.dashSize=this.dashSize),this.gapSize!==void 0&&(n.gapSize=this.gapSize),this.scale!==void 0&&(n.scale=this.scale),this.dithering===!0&&(n.dithering=!0),this.alphaTest>0&&(n.alphaTest=this.alphaTest),this.alphaHash===!0&&(n.alphaHash=!0),this.alphaToCoverage===!0&&(n.alphaToCoverage=!0),this.premultipliedAlpha===!0&&(n.premultipliedAlpha=!0),this.forceSinglePass===!0&&(n.forceSinglePass=!0),this.wireframe===!0&&(n.wireframe=!0),this.wireframeLinewidth>1&&(n.wireframeLinewidth=this.wireframeLinewidth),this.wireframeLinecap!=="round"&&(n.wireframeLinecap=this.wireframeLinecap),this.wireframeLinejoin!=="round"&&(n.wireframeLinejoin=this.wireframeLinejoin),this.flatShading===!0&&(n.flatShading=!0),this.visible===!1&&(n.visible=!1),this.toneMapped===!1&&(n.toneMapped=!1),this.fog===!1&&(n.fog=!1),Object.keys(this.userData).length>0&&(n.userData=this.userData);function i(s){const o=[];for(const a in s){const l=s[a];delete l.metadata,o.push(l)}return o}if(t){const s=i(e.textures),o=i(e.images);s.length>0&&(n.textures=s),o.length>0&&(n.images=o)}return n}clone(){return new this.constructor().copy(this)}copy(e){this.name=e.name,this.blending=e.blending,this.side=e.side,this.vertexColors=e.vertexColors,this.opacity=e.opacity,this.transparent=e.transparent,this.blendSrc=e.blendSrc,this.blendDst=e.blendDst,this.blendEquation=e.blendEquation,this.blendSrcAlpha=e.blendSrcAlpha,this.blendDstAlpha=e.blendDstAlpha,this.blendEquationAlpha=e.blendEquationAlpha,this.blendColor.copy(e.blendColor),this.blendAlpha=e.blendAlpha,this.depthFunc=e.depthFunc,this.depthTest=e.depthTest,this.depthWrite=e.depthWrite,this.stencilWriteMask=e.stencilWriteMask,this.stencilFunc=e.stencilFunc,this.stencilRef=e.stencilRef,this.stencilFuncMask=e.stencilFuncMask,this.stencilFail=e.stencilFail,this.stencilZFail=e.stencilZFail,this.stencilZPass=e.stencilZPass,this.stencilWrite=e.stencilWrite;const t=e.clippingPlanes;let n=null;if(t!==null){const i=t.length;n=new Array(i);for(let s=0;s!==i;++s)n[s]=t[s].clone()}return this.clippingPlanes=n,this.clipIntersection=e.clipIntersection,this.clipShadows=e.clipShadows,this.shadowSide=e.shadowSide,this.colorWrite=e.colorWrite,this.precision=e.precision,this.polygonOffset=e.polygonOffset,this.polygonOffsetFactor=e.polygonOffsetFactor,this.polygonOffsetUnits=e.polygonOffsetUnits,this.dithering=e.dithering,this.alphaTest=e.alphaTest,this.alphaHash=e.alphaHash,this.alphaToCoverage=e.alphaToCoverage,this.premultipliedAlpha=e.premultipliedAlpha,this.forceSinglePass=e.forceSinglePass,this.visible=e.visible,this.toneMapped=e.toneMapped,this.userData=JSON.parse(JSON.stringify(e.userData)),this}dispose(){this.dispatchEvent({type:"dispose"})}set needsUpdate(e){e===!0&&this.version++}onBuild(){console.warn("Material: onBuild() has been removed.")}}class Fp extends Fo{constructor(e){super(),this.isMeshBasicMaterial=!0,this.type="MeshBasicMaterial",this.color=new at(16777215),this.map=null,this.lightMap=null,this.lightMapIntensity=1,this.aoMap=null,this.aoMapIntensity=1,this.specularMap=null,this.alphaMap=null,this.envMap=null,this.envMapRotation=new ki,this.combine=gp,this.reflectivity=1,this.refractionRatio=.98,this.wireframe=!1,this.wireframeLinewidth=1,this.wireframeLinecap="round",this.wireframeLinejoin="round",this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.lightMap=e.lightMap,this.lightMapIntensity=e.lightMapIntensity,this.aoMap=e.aoMap,this.aoMapIntensity=e.aoMapIntensity,this.specularMap=e.specularMap,this.alphaMap=e.alphaMap,this.envMap=e.envMap,this.envMapRotation.copy(e.envMapRotation),this.combine=e.combine,this.reflectivity=e.reflectivity,this.refractionRatio=e.refractionRatio,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.wireframeLinecap=e.wireframeLinecap,this.wireframeLinejoin=e.wireframeLinejoin,this.fog=e.fog,this}}const Bt=new Y,la=new St;class Zt{constructor(e,t,n=!1){if(Array.isArray(e))throw new TypeError("THREE.BufferAttribute: array should be a Typed Array.");this.isBufferAttribute=!0,this.name="",this.array=e,this.itemSize=t,this.count=e!==void 0?e.length/t:0,this.normalized=n,this.usage=Jh,this.updateRanges=[],this.gpuType=Ui,this.version=0}onUploadCallback(){}set needsUpdate(e){e===!0&&this.version++}setUsage(e){return this.usage=e,this}addUpdateRange(e,t){this.updateRanges.push({start:e,count:t})}clearUpdateRanges(){this.updateRanges.length=0}copy(e){return this.name=e.name,this.array=new e.array.constructor(e.array),this.itemSize=e.itemSize,this.count=e.count,this.normalized=e.normalized,this.usage=e.usage,this.gpuType=e.gpuType,this}copyAt(e,t,n){e*=this.itemSize,n*=t.itemSize;for(let i=0,s=this.itemSize;i<s;i++)this.array[e+i]=t.array[n+i];return this}copyArray(e){return this.array.set(e),this}applyMatrix3(e){if(this.itemSize===2)for(let t=0,n=this.count;t<n;t++)la.fromBufferAttribute(this,t),la.applyMatrix3(e),this.setXY(t,la.x,la.y);else if(this.itemSize===3)for(let t=0,n=this.count;t<n;t++)Bt.fromBufferAttribute(this,t),Bt.applyMatrix3(e),this.setXYZ(t,Bt.x,Bt.y,Bt.z);return this}applyMatrix4(e){for(let t=0,n=this.count;t<n;t++)Bt.fromBufferAttribute(this,t),Bt.applyMatrix4(e),this.setXYZ(t,Bt.x,Bt.y,Bt.z);return this}applyNormalMatrix(e){for(let t=0,n=this.count;t<n;t++)Bt.fromBufferAttribute(this,t),Bt.applyNormalMatrix(e),this.setXYZ(t,Bt.x,Bt.y,Bt.z);return this}transformDirection(e){for(let t=0,n=this.count;t<n;t++)Bt.fromBufferAttribute(this,t),Bt.transformDirection(e),this.setXYZ(t,Bt.x,Bt.y,Bt.z);return this}set(e,t=0){return this.array.set(e,t),this}getComponent(e,t){let n=this.array[e*this.itemSize+t];return this.normalized&&(n=qs(n,this.array)),n}setComponent(e,t,n){return this.normalized&&(n=xn(n,this.array)),this.array[e*this.itemSize+t]=n,this}getX(e){let t=this.array[e*this.itemSize];return this.normalized&&(t=qs(t,this.array)),t}setX(e,t){return this.normalized&&(t=xn(t,this.array)),this.array[e*this.itemSize]=t,this}getY(e){let t=this.array[e*this.itemSize+1];return this.normalized&&(t=qs(t,this.array)),t}setY(e,t){return this.normalized&&(t=xn(t,this.array)),this.array[e*this.itemSize+1]=t,this}getZ(e){let t=this.array[e*this.itemSize+2];return this.normalized&&(t=qs(t,this.array)),t}setZ(e,t){return this.normalized&&(t=xn(t,this.array)),this.array[e*this.itemSize+2]=t,this}getW(e){let t=this.array[e*this.itemSize+3];return this.normalized&&(t=qs(t,this.array)),t}setW(e,t){return this.normalized&&(t=xn(t,this.array)),this.array[e*this.itemSize+3]=t,this}setXY(e,t,n){return e*=this.itemSize,this.normalized&&(t=xn(t,this.array),n=xn(n,this.array)),this.array[e+0]=t,this.array[e+1]=n,this}setXYZ(e,t,n,i){return e*=this.itemSize,this.normalized&&(t=xn(t,this.array),n=xn(n,this.array),i=xn(i,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this}setXYZW(e,t,n,i,s){return e*=this.itemSize,this.normalized&&(t=xn(t,this.array),n=xn(n,this.array),i=xn(i,this.array),s=xn(s,this.array)),this.array[e+0]=t,this.array[e+1]=n,this.array[e+2]=i,this.array[e+3]=s,this}onUpload(e){return this.onUploadCallback=e,this}clone(){return new this.constructor(this.array,this.itemSize).copy(this)}toJSON(){const e={itemSize:this.itemSize,type:this.array.constructor.name,array:Array.from(this.array),normalized:this.normalized};return this.name!==""&&(e.name=this.name),this.usage!==Jh&&(e.usage=this.usage),e}}class Op extends Zt{constructor(e,t,n){super(new Uint16Array(e),t,n)}}class Bp extends Zt{constructor(e,t,n){super(new Uint32Array(e),t,n)}}class Si extends Zt{constructor(e,t,n){super(new Float32Array(e),t,n)}}let s0=0;const Xn=new Ot,Kl=new An,ls=new Y,Ln=new No,Js=new No,Yt=new Y;class fi extends Gs{constructor(){super(),this.isBufferGeometry=!0,Object.defineProperty(this,"id",{value:s0++}),this.uuid=Io(),this.name="",this.type="BufferGeometry",this.index=null,this.attributes={},this.morphAttributes={},this.morphTargetsRelative=!1,this.groups=[],this.boundingBox=null,this.boundingSphere=null,this.drawRange={start:0,count:1/0},this.userData={}}getIndex(){return this.index}setIndex(e){return Array.isArray(e)?this.index=new(Pp(e)?Bp:Op)(e,1):this.index=e,this}getAttribute(e){return this.attributes[e]}setAttribute(e,t){return this.attributes[e]=t,this}deleteAttribute(e){return delete this.attributes[e],this}hasAttribute(e){return this.attributes[e]!==void 0}addGroup(e,t,n=0){this.groups.push({start:e,count:t,materialIndex:n})}clearGroups(){this.groups=[]}setDrawRange(e,t){this.drawRange.start=e,this.drawRange.count=t}applyMatrix4(e){const t=this.attributes.position;t!==void 0&&(t.applyMatrix4(e),t.needsUpdate=!0);const n=this.attributes.normal;if(n!==void 0){const s=new Ke().getNormalMatrix(e);n.applyNormalMatrix(s),n.needsUpdate=!0}const i=this.attributes.tangent;return i!==void 0&&(i.transformDirection(e),i.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}applyQuaternion(e){return Xn.makeRotationFromQuaternion(e),this.applyMatrix4(Xn),this}rotateX(e){return Xn.makeRotationX(e),this.applyMatrix4(Xn),this}rotateY(e){return Xn.makeRotationY(e),this.applyMatrix4(Xn),this}rotateZ(e){return Xn.makeRotationZ(e),this.applyMatrix4(Xn),this}translate(e,t,n){return Xn.makeTranslation(e,t,n),this.applyMatrix4(Xn),this}scale(e,t,n){return Xn.makeScale(e,t,n),this.applyMatrix4(Xn),this}lookAt(e){return Kl.lookAt(e),Kl.updateMatrix(),this.applyMatrix4(Kl.matrix),this}center(){return this.computeBoundingBox(),this.boundingBox.getCenter(ls).negate(),this.translate(ls.x,ls.y,ls.z),this}setFromPoints(e){const t=[];for(let n=0,i=e.length;n<i;n++){const s=e[n];t.push(s.x,s.y,s.z||0)}return this.setAttribute("position",new Si(t,3)),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new No);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingBox(): GLBufferAttribute requires a manual bounding box.",this),this.boundingBox.set(new Y(-1/0,-1/0,-1/0),new Y(1/0,1/0,1/0));return}if(e!==void 0){if(this.boundingBox.setFromBufferAttribute(e),t)for(let n=0,i=t.length;n<i;n++){const s=t[n];Ln.setFromBufferAttribute(s),this.morphTargetsRelative?(Yt.addVectors(this.boundingBox.min,Ln.min),this.boundingBox.expandByPoint(Yt),Yt.addVectors(this.boundingBox.max,Ln.max),this.boundingBox.expandByPoint(Yt)):(this.boundingBox.expandByPoint(Ln.min),this.boundingBox.expandByPoint(Ln.max))}}else this.boundingBox.makeEmpty();(isNaN(this.boundingBox.min.x)||isNaN(this.boundingBox.min.y)||isNaN(this.boundingBox.min.z))&&console.error('THREE.BufferGeometry.computeBoundingBox(): Computed min/max have NaN values. The "position" attribute is likely to have NaN values.',this)}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new cl);const e=this.attributes.position,t=this.morphAttributes.position;if(e&&e.isGLBufferAttribute){console.error("THREE.BufferGeometry.computeBoundingSphere(): GLBufferAttribute requires a manual bounding sphere.",this),this.boundingSphere.set(new Y,1/0);return}if(e){const n=this.boundingSphere.center;if(Ln.setFromBufferAttribute(e),t)for(let s=0,o=t.length;s<o;s++){const a=t[s];Js.setFromBufferAttribute(a),this.morphTargetsRelative?(Yt.addVectors(Ln.min,Js.min),Ln.expandByPoint(Yt),Yt.addVectors(Ln.max,Js.max),Ln.expandByPoint(Yt)):(Ln.expandByPoint(Js.min),Ln.expandByPoint(Js.max))}Ln.getCenter(n);let i=0;for(let s=0,o=e.count;s<o;s++)Yt.fromBufferAttribute(e,s),i=Math.max(i,n.distanceToSquared(Yt));if(t)for(let s=0,o=t.length;s<o;s++){const a=t[s],l=this.morphTargetsRelative;for(let c=0,u=a.count;c<u;c++)Yt.fromBufferAttribute(a,c),l&&(ls.fromBufferAttribute(e,c),Yt.add(ls)),i=Math.max(i,n.distanceToSquared(Yt))}this.boundingSphere.radius=Math.sqrt(i),isNaN(this.boundingSphere.radius)&&console.error('THREE.BufferGeometry.computeBoundingSphere(): Computed radius is NaN. The "position" attribute is likely to have NaN values.',this)}}computeTangents(){const e=this.index,t=this.attributes;if(e===null||t.position===void 0||t.normal===void 0||t.uv===void 0){console.error("THREE.BufferGeometry: .computeTangents() failed. Missing required attributes (index, position, normal or uv)");return}const n=t.position,i=t.normal,s=t.uv;this.hasAttribute("tangent")===!1&&this.setAttribute("tangent",new Zt(new Float32Array(4*n.count),4));const o=this.getAttribute("tangent"),a=[],l=[];for(let D=0;D<n.count;D++)a[D]=new Y,l[D]=new Y;const c=new Y,u=new Y,f=new Y,h=new St,d=new St,_=new St,g=new Y,p=new Y;function m(D,O,v){c.fromBufferAttribute(n,D),u.fromBufferAttribute(n,O),f.fromBufferAttribute(n,v),h.fromBufferAttribute(s,D),d.fromBufferAttribute(s,O),_.fromBufferAttribute(s,v),u.sub(c),f.sub(c),d.sub(h),_.sub(h);const T=1/(d.x*_.y-_.x*d.y);isFinite(T)&&(g.copy(u).multiplyScalar(_.y).addScaledVector(f,-d.y).multiplyScalar(T),p.copy(f).multiplyScalar(d.x).addScaledVector(u,-_.x).multiplyScalar(T),a[D].add(g),a[O].add(g),a[v].add(g),l[D].add(p),l[O].add(p),l[v].add(p))}let y=this.groups;y.length===0&&(y=[{start:0,count:e.count}]);for(let D=0,O=y.length;D<O;++D){const v=y[D],T=v.start,N=v.count;for(let z=T,W=T+N;z<W;z+=3)m(e.getX(z+0),e.getX(z+1),e.getX(z+2))}const x=new Y,M=new Y,R=new Y,w=new Y;function E(D){R.fromBufferAttribute(i,D),w.copy(R);const O=a[D];x.copy(O),x.sub(R.multiplyScalar(R.dot(O))).normalize(),M.crossVectors(w,O);const T=M.dot(l[D])<0?-1:1;o.setXYZW(D,x.x,x.y,x.z,T)}for(let D=0,O=y.length;D<O;++D){const v=y[D],T=v.start,N=v.count;for(let z=T,W=T+N;z<W;z+=3)E(e.getX(z+0)),E(e.getX(z+1)),E(e.getX(z+2))}}computeVertexNormals(){const e=this.index,t=this.getAttribute("position");if(t!==void 0){let n=this.getAttribute("normal");if(n===void 0)n=new Zt(new Float32Array(t.count*3),3),this.setAttribute("normal",n);else for(let h=0,d=n.count;h<d;h++)n.setXYZ(h,0,0,0);const i=new Y,s=new Y,o=new Y,a=new Y,l=new Y,c=new Y,u=new Y,f=new Y;if(e)for(let h=0,d=e.count;h<d;h+=3){const _=e.getX(h+0),g=e.getX(h+1),p=e.getX(h+2);i.fromBufferAttribute(t,_),s.fromBufferAttribute(t,g),o.fromBufferAttribute(t,p),u.subVectors(o,s),f.subVectors(i,s),u.cross(f),a.fromBufferAttribute(n,_),l.fromBufferAttribute(n,g),c.fromBufferAttribute(n,p),a.add(u),l.add(u),c.add(u),n.setXYZ(_,a.x,a.y,a.z),n.setXYZ(g,l.x,l.y,l.z),n.setXYZ(p,c.x,c.y,c.z)}else for(let h=0,d=t.count;h<d;h+=3)i.fromBufferAttribute(t,h+0),s.fromBufferAttribute(t,h+1),o.fromBufferAttribute(t,h+2),u.subVectors(o,s),f.subVectors(i,s),u.cross(f),n.setXYZ(h+0,u.x,u.y,u.z),n.setXYZ(h+1,u.x,u.y,u.z),n.setXYZ(h+2,u.x,u.y,u.z);this.normalizeNormals(),n.needsUpdate=!0}}normalizeNormals(){const e=this.attributes.normal;for(let t=0,n=e.count;t<n;t++)Yt.fromBufferAttribute(e,t),Yt.normalize(),e.setXYZ(t,Yt.x,Yt.y,Yt.z)}toNonIndexed(){function e(a,l){const c=a.array,u=a.itemSize,f=a.normalized,h=new c.constructor(l.length*u);let d=0,_=0;for(let g=0,p=l.length;g<p;g++){a.isInterleavedBufferAttribute?d=l[g]*a.data.stride+a.offset:d=l[g]*u;for(let m=0;m<u;m++)h[_++]=c[d++]}return new Zt(h,u,f)}if(this.index===null)return console.warn("THREE.BufferGeometry.toNonIndexed(): BufferGeometry is already non-indexed."),this;const t=new fi,n=this.index.array,i=this.attributes;for(const a in i){const l=i[a],c=e(l,n);t.setAttribute(a,c)}const s=this.morphAttributes;for(const a in s){const l=[],c=s[a];for(let u=0,f=c.length;u<f;u++){const h=c[u],d=e(h,n);l.push(d)}t.morphAttributes[a]=l}t.morphTargetsRelative=this.morphTargetsRelative;const o=this.groups;for(let a=0,l=o.length;a<l;a++){const c=o[a];t.addGroup(c.start,c.count,c.materialIndex)}return t}toJSON(){const e={metadata:{version:4.6,type:"BufferGeometry",generator:"BufferGeometry.toJSON"}};if(e.uuid=this.uuid,e.type=this.type,this.name!==""&&(e.name=this.name),Object.keys(this.userData).length>0&&(e.userData=this.userData),this.parameters!==void 0){const l=this.parameters;for(const c in l)l[c]!==void 0&&(e[c]=l[c]);return e}e.data={attributes:{}};const t=this.index;t!==null&&(e.data.index={type:t.array.constructor.name,array:Array.prototype.slice.call(t.array)});const n=this.attributes;for(const l in n){const c=n[l];e.data.attributes[l]=c.toJSON(e.data)}const i={};let s=!1;for(const l in this.morphAttributes){const c=this.morphAttributes[l],u=[];for(let f=0,h=c.length;f<h;f++){const d=c[f];u.push(d.toJSON(e.data))}u.length>0&&(i[l]=u,s=!0)}s&&(e.data.morphAttributes=i,e.data.morphTargetsRelative=this.morphTargetsRelative);const o=this.groups;o.length>0&&(e.data.groups=JSON.parse(JSON.stringify(o)));const a=this.boundingSphere;return a!==null&&(e.data.boundingSphere={center:a.center.toArray(),radius:a.radius}),e}clone(){return new this.constructor().copy(this)}copy(e){this.index=null,this.attributes={},this.morphAttributes={},this.groups=[],this.boundingBox=null,this.boundingSphere=null;const t={};this.name=e.name;const n=e.index;n!==null&&this.setIndex(n.clone(t));const i=e.attributes;for(const c in i){const u=i[c];this.setAttribute(c,u.clone(t))}const s=e.morphAttributes;for(const c in s){const u=[],f=s[c];for(let h=0,d=f.length;h<d;h++)u.push(f[h].clone(t));this.morphAttributes[c]=u}this.morphTargetsRelative=e.morphTargetsRelative;const o=e.groups;for(let c=0,u=o.length;c<u;c++){const f=o[c];this.addGroup(f.start,f.count,f.materialIndex)}const a=e.boundingBox;a!==null&&(this.boundingBox=a.clone());const l=e.boundingSphere;return l!==null&&(this.boundingSphere=l.clone()),this.drawRange.start=e.drawRange.start,this.drawRange.count=e.drawRange.count,this.userData=e.userData,this}dispose(){this.dispatchEvent({type:"dispose"})}}const df=new Ot,vr=new Ip,ca=new cl,pf=new Y,ua=new Y,ha=new Y,fa=new Y,Zl=new Y,da=new Y,mf=new Y,pa=new Y;class hi extends An{constructor(e=new fi,t=new Fp){super(),this.isMesh=!0,this.type="Mesh",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),e.morphTargetInfluences!==void 0&&(this.morphTargetInfluences=e.morphTargetInfluences.slice()),e.morphTargetDictionary!==void 0&&(this.morphTargetDictionary=Object.assign({},e.morphTargetDictionary)),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,o=i.length;s<o;s++){const a=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}getVertexPosition(e,t){const n=this.geometry,i=n.attributes.position,s=n.morphAttributes.position,o=n.morphTargetsRelative;t.fromBufferAttribute(i,e);const a=this.morphTargetInfluences;if(s&&a){da.set(0,0,0);for(let l=0,c=s.length;l<c;l++){const u=a[l],f=s[l];u!==0&&(Zl.fromBufferAttribute(f,e),o?da.addScaledVector(Zl,u):da.addScaledVector(Zl.sub(t),u))}t.add(da)}return t}raycast(e,t){const n=this.geometry,i=this.material,s=this.matrixWorld;i!==void 0&&(n.boundingSphere===null&&n.computeBoundingSphere(),ca.copy(n.boundingSphere),ca.applyMatrix4(s),vr.copy(e.ray).recast(e.near),!(ca.containsPoint(vr.origin)===!1&&(vr.intersectSphere(ca,pf)===null||vr.origin.distanceToSquared(pf)>(e.far-e.near)**2))&&(df.copy(s).invert(),vr.copy(e.ray).applyMatrix4(df),!(n.boundingBox!==null&&vr.intersectsBox(n.boundingBox)===!1)&&this._computeIntersections(e,t,vr)))}_computeIntersections(e,t,n){let i;const s=this.geometry,o=this.material,a=s.index,l=s.attributes.position,c=s.attributes.uv,u=s.attributes.uv1,f=s.attributes.normal,h=s.groups,d=s.drawRange;if(a!==null)if(Array.isArray(o))for(let _=0,g=h.length;_<g;_++){const p=h[_],m=o[p.materialIndex],y=Math.max(p.start,d.start),x=Math.min(a.count,Math.min(p.start+p.count,d.start+d.count));for(let M=y,R=x;M<R;M+=3){const w=a.getX(M),E=a.getX(M+1),D=a.getX(M+2);i=ma(this,m,e,n,c,u,f,w,E,D),i&&(i.faceIndex=Math.floor(M/3),i.face.materialIndex=p.materialIndex,t.push(i))}}else{const _=Math.max(0,d.start),g=Math.min(a.count,d.start+d.count);for(let p=_,m=g;p<m;p+=3){const y=a.getX(p),x=a.getX(p+1),M=a.getX(p+2);i=ma(this,o,e,n,c,u,f,y,x,M),i&&(i.faceIndex=Math.floor(p/3),t.push(i))}}else if(l!==void 0)if(Array.isArray(o))for(let _=0,g=h.length;_<g;_++){const p=h[_],m=o[p.materialIndex],y=Math.max(p.start,d.start),x=Math.min(l.count,Math.min(p.start+p.count,d.start+d.count));for(let M=y,R=x;M<R;M+=3){const w=M,E=M+1,D=M+2;i=ma(this,m,e,n,c,u,f,w,E,D),i&&(i.faceIndex=Math.floor(M/3),i.face.materialIndex=p.materialIndex,t.push(i))}}else{const _=Math.max(0,d.start),g=Math.min(l.count,d.start+d.count);for(let p=_,m=g;p<m;p+=3){const y=p,x=p+1,M=p+2;i=ma(this,o,e,n,c,u,f,y,x,M),i&&(i.faceIndex=Math.floor(p/3),t.push(i))}}}}function o0(r,e,t,n,i,s,o,a){let l;if(e.side===_n?l=n.intersectTriangle(o,s,i,!0,a):l=n.intersectTriangle(i,s,o,e.side===hr,a),l===null)return null;pa.copy(a),pa.applyMatrix4(r.matrixWorld);const c=t.ray.origin.distanceTo(pa);return c<t.near||c>t.far?null:{distance:c,point:pa.clone(),object:r}}function ma(r,e,t,n,i,s,o,a,l,c){r.getVertexPosition(a,ua),r.getVertexPosition(l,ha),r.getVertexPosition(c,fa);const u=o0(r,e,t,n,ua,ha,fa,mf);if(u){const f=new Y;ci.getBarycoord(mf,ua,ha,fa,f),i&&(u.uv=ci.getInterpolatedAttribute(i,a,l,c,f,new St)),s&&(u.uv1=ci.getInterpolatedAttribute(s,a,l,c,f,new St)),o&&(u.normal=ci.getInterpolatedAttribute(o,a,l,c,f,new Y),u.normal.dot(n.direction)>0&&u.normal.multiplyScalar(-1));const h={a,b:l,c,normal:new Y,materialIndex:0};ci.getNormal(ua,ha,fa,h.normal),u.face=h,u.barycoord=f}return u}class Oo extends fi{constructor(e=1,t=1,n=1,i=1,s=1,o=1){super(),this.type="BoxGeometry",this.parameters={width:e,height:t,depth:n,widthSegments:i,heightSegments:s,depthSegments:o};const a=this;i=Math.floor(i),s=Math.floor(s),o=Math.floor(o);const l=[],c=[],u=[],f=[];let h=0,d=0;_("z","y","x",-1,-1,n,t,e,o,s,0),_("z","y","x",1,-1,n,t,-e,o,s,1),_("x","z","y",1,1,e,n,t,i,o,2),_("x","z","y",1,-1,e,n,-t,i,o,3),_("x","y","z",1,-1,e,t,n,i,s,4),_("x","y","z",-1,-1,e,t,-n,i,s,5),this.setIndex(l),this.setAttribute("position",new Si(c,3)),this.setAttribute("normal",new Si(u,3)),this.setAttribute("uv",new Si(f,2));function _(g,p,m,y,x,M,R,w,E,D,O){const v=M/E,T=R/D,N=M/2,z=R/2,W=w/2,K=E+1,G=D+1;let X=0,V=0;const re=new Y;for(let C=0;C<G;C++){const ae=C*T-z;for(let Be=0;Be<K;Be++){const We=Be*v-N;re[g]=We*y,re[p]=ae*x,re[m]=W,c.push(re.x,re.y,re.z),re[g]=0,re[p]=0,re[m]=w>0?1:-1,u.push(re.x,re.y,re.z),f.push(Be/E),f.push(1-C/D),X+=1}}for(let C=0;C<D;C++)for(let ae=0;ae<E;ae++){const Be=h+ae+K*C,We=h+ae+K*(C+1),q=h+(ae+1)+K*(C+1),Q=h+(ae+1)+K*C;l.push(Be,We,Q),l.push(We,q,Q),V+=6}a.addGroup(d,V,O),d+=V,h+=X}}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Oo(e.width,e.height,e.depth,e.widthSegments,e.heightSegments,e.depthSegments)}}function Hs(r){const e={};for(const t in r){e[t]={};for(const n in r[t]){const i=r[t][n];i&&(i.isColor||i.isMatrix3||i.isMatrix4||i.isVector2||i.isVector3||i.isVector4||i.isTexture||i.isQuaternion)?i.isRenderTargetTexture?(console.warn("UniformsUtils: Textures of render targets cannot be cloned via cloneUniforms() or mergeUniforms()."),e[t][n]=null):e[t][n]=i.clone():Array.isArray(i)?e[t][n]=i.slice():e[t][n]=i}}return e}function hn(r){const e={};for(let t=0;t<r.length;t++){const n=Hs(r[t]);for(const i in n)e[i]=n[i]}return e}function a0(r){const e=[];for(let t=0;t<r.length;t++)e.push(r[t].clone());return e}function zp(r){const e=r.getRenderTarget();return e===null?r.outputColorSpace:e.isXRRenderTarget===!0?e.texture.colorSpace:ft.workingColorSpace}const l0={clone:Hs,merge:hn};var c0=`void main() {
	gl_Position = projectionMatrix * modelViewMatrix * vec4( position, 1.0 );
}`,u0=`void main() {
	gl_FragColor = vec4( 1.0, 0.0, 0.0, 1.0 );
}`;class ei extends Fo{constructor(e){super(),this.isShaderMaterial=!0,this.type="ShaderMaterial",this.defines={},this.uniforms={},this.uniformsGroups=[],this.vertexShader=c0,this.fragmentShader=u0,this.linewidth=1,this.wireframe=!1,this.wireframeLinewidth=1,this.fog=!1,this.lights=!1,this.clipping=!1,this.forceSinglePass=!0,this.extensions={clipCullDistance:!1,multiDraw:!1},this.defaultAttributeValues={color:[1,1,1],uv:[0,0],uv1:[0,0]},this.index0AttributeName=void 0,this.uniformsNeedUpdate=!1,this.glslVersion=null,e!==void 0&&this.setValues(e)}copy(e){return super.copy(e),this.fragmentShader=e.fragmentShader,this.vertexShader=e.vertexShader,this.uniforms=Hs(e.uniforms),this.uniformsGroups=a0(e.uniformsGroups),this.defines=Object.assign({},e.defines),this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this.fog=e.fog,this.lights=e.lights,this.clipping=e.clipping,this.extensions=Object.assign({},e.extensions),this.glslVersion=e.glslVersion,this}toJSON(e){const t=super.toJSON(e);t.glslVersion=this.glslVersion,t.uniforms={};for(const i in this.uniforms){const o=this.uniforms[i].value;o&&o.isTexture?t.uniforms[i]={type:"t",value:o.toJSON(e).uuid}:o&&o.isColor?t.uniforms[i]={type:"c",value:o.getHex()}:o&&o.isVector2?t.uniforms[i]={type:"v2",value:o.toArray()}:o&&o.isVector3?t.uniforms[i]={type:"v3",value:o.toArray()}:o&&o.isVector4?t.uniforms[i]={type:"v4",value:o.toArray()}:o&&o.isMatrix3?t.uniforms[i]={type:"m3",value:o.toArray()}:o&&o.isMatrix4?t.uniforms[i]={type:"m4",value:o.toArray()}:t.uniforms[i]={value:o}}Object.keys(this.defines).length>0&&(t.defines=this.defines),t.vertexShader=this.vertexShader,t.fragmentShader=this.fragmentShader,t.lights=this.lights,t.clipping=this.clipping;const n={};for(const i in this.extensions)this.extensions[i]===!0&&(n[i]=!0);return Object.keys(n).length>0&&(t.extensions=n),t}}class kp extends An{constructor(){super(),this.isCamera=!0,this.type="Camera",this.matrixWorldInverse=new Ot,this.projectionMatrix=new Ot,this.projectionMatrixInverse=new Ot,this.coordinateSystem=Ni}copy(e,t){return super.copy(e,t),this.matrixWorldInverse.copy(e.matrixWorldInverse),this.projectionMatrix.copy(e.projectionMatrix),this.projectionMatrixInverse.copy(e.projectionMatrixInverse),this.coordinateSystem=e.coordinateSystem,this}getWorldDirection(e){return super.getWorldDirection(e).negate()}updateMatrixWorld(e){super.updateMatrixWorld(e),this.matrixWorldInverse.copy(this.matrixWorld).invert()}updateWorldMatrix(e,t){super.updateWorldMatrix(e,t),this.matrixWorldInverse.copy(this.matrixWorld).invert()}clone(){return new this.constructor().copy(this)}}const $i=new Y,_f=new St,gf=new St;class Kn extends kp{constructor(e=50,t=1,n=.1,i=2e3){super(),this.isPerspectiveCamera=!0,this.type="PerspectiveCamera",this.fov=e,this.zoom=1,this.near=n,this.far=i,this.focus=10,this.aspect=t,this.view=null,this.filmGauge=35,this.filmOffset=0,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.fov=e.fov,this.zoom=e.zoom,this.near=e.near,this.far=e.far,this.focus=e.focus,this.aspect=e.aspect,this.view=e.view===null?null:Object.assign({},e.view),this.filmGauge=e.filmGauge,this.filmOffset=e.filmOffset,this}setFocalLength(e){const t=.5*this.getFilmHeight()/e;this.fov=Su*2*Math.atan(t),this.updateProjectionMatrix()}getFocalLength(){const e=Math.tan(Cl*.5*this.fov);return .5*this.getFilmHeight()/e}getEffectiveFOV(){return Su*2*Math.atan(Math.tan(Cl*.5*this.fov)/this.zoom)}getFilmWidth(){return this.filmGauge*Math.min(this.aspect,1)}getFilmHeight(){return this.filmGauge/Math.max(this.aspect,1)}getViewBounds(e,t,n){$i.set(-1,-1,.5).applyMatrix4(this.projectionMatrixInverse),t.set($i.x,$i.y).multiplyScalar(-e/$i.z),$i.set(1,1,.5).applyMatrix4(this.projectionMatrixInverse),n.set($i.x,$i.y).multiplyScalar(-e/$i.z)}getViewSize(e,t){return this.getViewBounds(e,_f,gf),t.subVectors(gf,_f)}setViewOffset(e,t,n,i,s,o){this.aspect=e/t,this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=this.near;let t=e*Math.tan(Cl*.5*this.fov)/this.zoom,n=2*t,i=this.aspect*n,s=-.5*i;const o=this.view;if(this.view!==null&&this.view.enabled){const l=o.fullWidth,c=o.fullHeight;s+=o.offsetX*i/l,t-=o.offsetY*n/c,i*=o.width/l,n*=o.height/c}const a=this.filmOffset;a!==0&&(s+=e*a/this.getFilmWidth()),this.projectionMatrix.makePerspective(s,s+i,t,t-n,e,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.fov=this.fov,t.object.zoom=this.zoom,t.object.near=this.near,t.object.far=this.far,t.object.focus=this.focus,t.object.aspect=this.aspect,this.view!==null&&(t.object.view=Object.assign({},this.view)),t.object.filmGauge=this.filmGauge,t.object.filmOffset=this.filmOffset,t}}const cs=-90,us=1;class h0 extends An{constructor(e,t,n){super(),this.type="CubeCamera",this.renderTarget=n,this.coordinateSystem=null,this.activeMipmapLevel=0;const i=new Kn(cs,us,e,t);i.layers=this.layers,this.add(i);const s=new Kn(cs,us,e,t);s.layers=this.layers,this.add(s);const o=new Kn(cs,us,e,t);o.layers=this.layers,this.add(o);const a=new Kn(cs,us,e,t);a.layers=this.layers,this.add(a);const l=new Kn(cs,us,e,t);l.layers=this.layers,this.add(l);const c=new Kn(cs,us,e,t);c.layers=this.layers,this.add(c)}updateCoordinateSystem(){const e=this.coordinateSystem,t=this.children.concat(),[n,i,s,o,a,l]=t;for(const c of t)this.remove(c);if(e===Ni)n.up.set(0,1,0),n.lookAt(1,0,0),i.up.set(0,1,0),i.lookAt(-1,0,0),s.up.set(0,0,-1),s.lookAt(0,1,0),o.up.set(0,0,1),o.lookAt(0,-1,0),a.up.set(0,1,0),a.lookAt(0,0,1),l.up.set(0,1,0),l.lookAt(0,0,-1);else if(e===el)n.up.set(0,-1,0),n.lookAt(-1,0,0),i.up.set(0,-1,0),i.lookAt(1,0,0),s.up.set(0,0,1),s.lookAt(0,1,0),o.up.set(0,0,-1),o.lookAt(0,-1,0),a.up.set(0,-1,0),a.lookAt(0,0,1),l.up.set(0,-1,0),l.lookAt(0,0,-1);else throw new Error("THREE.CubeCamera.updateCoordinateSystem(): Invalid coordinate system: "+e);for(const c of t)this.add(c),c.updateMatrixWorld()}update(e,t){this.parent===null&&this.updateMatrixWorld();const{renderTarget:n,activeMipmapLevel:i}=this;this.coordinateSystem!==e.coordinateSystem&&(this.coordinateSystem=e.coordinateSystem,this.updateCoordinateSystem());const[s,o,a,l,c,u]=this.children,f=e.getRenderTarget(),h=e.getActiveCubeFace(),d=e.getActiveMipmapLevel(),_=e.xr.enabled;e.xr.enabled=!1;const g=n.texture.generateMipmaps;n.texture.generateMipmaps=!1,e.setRenderTarget(n,0,i),e.render(t,s),e.setRenderTarget(n,1,i),e.render(t,o),e.setRenderTarget(n,2,i),e.render(t,a),e.setRenderTarget(n,3,i),e.render(t,l),e.setRenderTarget(n,4,i),e.render(t,c),n.texture.generateMipmaps=g,e.setRenderTarget(n,5,i),e.render(t,u),e.setRenderTarget(f,h,d),e.xr.enabled=_,n.texture.needsPMREMUpdate=!0}}class Hp extends gn{constructor(e,t,n,i,s,o,a,l,c,u){e=e!==void 0?e:[],t=t!==void 0?t:Os,super(e,t,n,i,s,o,a,l,c,u),this.isCubeTexture=!0,this.flipY=!1}get images(){return this.image}set images(e){this.image=e}}class f0 extends Xr{constructor(e=1,t={}){super(e,e,t),this.isWebGLCubeRenderTarget=!0;const n={width:e,height:e,depth:1},i=[n,n,n,n,n,n];this.texture=new Hp(i,t.mapping,t.wrapS,t.wrapT,t.magFilter,t.minFilter,t.format,t.type,t.anisotropy,t.colorSpace),this.texture.isRenderTargetTexture=!0,this.texture.generateMipmaps=t.generateMipmaps!==void 0?t.generateMipmaps:!1,this.texture.minFilter=t.minFilter!==void 0?t.minFilter:li}fromEquirectangularTexture(e,t){this.texture.type=t.type,this.texture.colorSpace=t.colorSpace,this.texture.generateMipmaps=t.generateMipmaps,this.texture.minFilter=t.minFilter,this.texture.magFilter=t.magFilter;const n={uniforms:{tEquirect:{value:null}},vertexShader:`

				varying vec3 vWorldDirection;

				vec3 transformDirection( in vec3 dir, in mat4 matrix ) {

					return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );

				}

				void main() {

					vWorldDirection = transformDirection( position, modelMatrix );

					#include <begin_vertex>
					#include <project_vertex>

				}
			`,fragmentShader:`

				uniform sampler2D tEquirect;

				varying vec3 vWorldDirection;

				#include <common>

				void main() {

					vec3 direction = normalize( vWorldDirection );

					vec2 sampleUV = equirectUv( direction );

					gl_FragColor = texture2D( tEquirect, sampleUV );

				}
			`},i=new Oo(5,5,5),s=new ei({name:"CubemapFromEquirect",uniforms:Hs(n.uniforms),vertexShader:n.vertexShader,fragmentShader:n.fragmentShader,side:_n,blending:sr});s.uniforms.tEquirect.value=t;const o=new hi(i,s),a=t.minFilter;return t.minFilter===Dr&&(t.minFilter=li),new h0(1,10,this).update(e,o),t.minFilter=a,o.geometry.dispose(),o.material.dispose(),this}clear(e,t,n,i){const s=e.getRenderTarget();for(let o=0;o<6;o++)e.setRenderTarget(this,o),e.clear(t,n,i);e.setRenderTarget(s)}}const jl=new Y,d0=new Y,p0=new Ke;class br{constructor(e=new Y(1,0,0),t=0){this.isPlane=!0,this.normal=e,this.constant=t}set(e,t){return this.normal.copy(e),this.constant=t,this}setComponents(e,t,n,i){return this.normal.set(e,t,n),this.constant=i,this}setFromNormalAndCoplanarPoint(e,t){return this.normal.copy(e),this.constant=-t.dot(this.normal),this}setFromCoplanarPoints(e,t,n){const i=jl.subVectors(n,t).cross(d0.subVectors(e,t)).normalize();return this.setFromNormalAndCoplanarPoint(i,e),this}copy(e){return this.normal.copy(e.normal),this.constant=e.constant,this}normalize(){const e=1/this.normal.length();return this.normal.multiplyScalar(e),this.constant*=e,this}negate(){return this.constant*=-1,this.normal.negate(),this}distanceToPoint(e){return this.normal.dot(e)+this.constant}distanceToSphere(e){return this.distanceToPoint(e.center)-e.radius}projectPoint(e,t){return t.copy(e).addScaledVector(this.normal,-this.distanceToPoint(e))}intersectLine(e,t){const n=e.delta(jl),i=this.normal.dot(n);if(i===0)return this.distanceToPoint(e.start)===0?t.copy(e.start):null;const s=-(e.start.dot(this.normal)+this.constant)/i;return s<0||s>1?null:t.copy(e.start).addScaledVector(n,s)}intersectsLine(e){const t=this.distanceToPoint(e.start),n=this.distanceToPoint(e.end);return t<0&&n>0||n<0&&t>0}intersectsBox(e){return e.intersectsPlane(this)}intersectsSphere(e){return e.intersectsPlane(this)}coplanarPoint(e){return e.copy(this.normal).multiplyScalar(-this.constant)}applyMatrix4(e,t){const n=t||p0.getNormalMatrix(e),i=this.coplanarPoint(jl).applyMatrix4(e),s=this.normal.applyMatrix3(n).normalize();return this.constant=-i.dot(s),this}translate(e){return this.constant-=e.dot(this.normal),this}equals(e){return e.normal.equals(this.normal)&&e.constant===this.constant}clone(){return new this.constructor().copy(this)}}const xr=new cl,_a=new Y;class Gp{constructor(e=new br,t=new br,n=new br,i=new br,s=new br,o=new br){this.planes=[e,t,n,i,s,o]}set(e,t,n,i,s,o){const a=this.planes;return a[0].copy(e),a[1].copy(t),a[2].copy(n),a[3].copy(i),a[4].copy(s),a[5].copy(o),this}copy(e){const t=this.planes;for(let n=0;n<6;n++)t[n].copy(e.planes[n]);return this}setFromProjectionMatrix(e,t=Ni){const n=this.planes,i=e.elements,s=i[0],o=i[1],a=i[2],l=i[3],c=i[4],u=i[5],f=i[6],h=i[7],d=i[8],_=i[9],g=i[10],p=i[11],m=i[12],y=i[13],x=i[14],M=i[15];if(n[0].setComponents(l-s,h-c,p-d,M-m).normalize(),n[1].setComponents(l+s,h+c,p+d,M+m).normalize(),n[2].setComponents(l+o,h+u,p+_,M+y).normalize(),n[3].setComponents(l-o,h-u,p-_,M-y).normalize(),n[4].setComponents(l-a,h-f,p-g,M-x).normalize(),t===Ni)n[5].setComponents(l+a,h+f,p+g,M+x).normalize();else if(t===el)n[5].setComponents(a,f,g,x).normalize();else throw new Error("THREE.Frustum.setFromProjectionMatrix(): Invalid coordinate system: "+t);return this}intersectsObject(e){if(e.boundingSphere!==void 0)e.boundingSphere===null&&e.computeBoundingSphere(),xr.copy(e.boundingSphere).applyMatrix4(e.matrixWorld);else{const t=e.geometry;t.boundingSphere===null&&t.computeBoundingSphere(),xr.copy(t.boundingSphere).applyMatrix4(e.matrixWorld)}return this.intersectsSphere(xr)}intersectsSprite(e){return xr.center.set(0,0,0),xr.radius=.7071067811865476,xr.applyMatrix4(e.matrixWorld),this.intersectsSphere(xr)}intersectsSphere(e){const t=this.planes,n=e.center,i=-e.radius;for(let s=0;s<6;s++)if(t[s].distanceToPoint(n)<i)return!1;return!0}intersectsBox(e){const t=this.planes;for(let n=0;n<6;n++){const i=t[n];if(_a.x=i.normal.x>0?e.max.x:e.min.x,_a.y=i.normal.y>0?e.max.y:e.min.y,_a.z=i.normal.z>0?e.max.z:e.min.z,i.distanceToPoint(_a)<0)return!1}return!0}containsPoint(e){const t=this.planes;for(let n=0;n<6;n++)if(t[n].distanceToPoint(e)<0)return!1;return!0}clone(){return new this.constructor().copy(this)}}function Vp(){let r=null,e=!1,t=null,n=null;function i(s,o){t(s,o),n=r.requestAnimationFrame(i)}return{start:function(){e!==!0&&t!==null&&(n=r.requestAnimationFrame(i),e=!0)},stop:function(){r.cancelAnimationFrame(n),e=!1},setAnimationLoop:function(s){t=s},setContext:function(s){r=s}}}function m0(r){const e=new WeakMap;function t(a,l){const c=a.array,u=a.usage,f=c.byteLength,h=r.createBuffer();r.bindBuffer(l,h),r.bufferData(l,c,u),a.onUploadCallback();let d;if(c instanceof Float32Array)d=r.FLOAT;else if(c instanceof Uint16Array)a.isFloat16BufferAttribute?d=r.HALF_FLOAT:d=r.UNSIGNED_SHORT;else if(c instanceof Int16Array)d=r.SHORT;else if(c instanceof Uint32Array)d=r.UNSIGNED_INT;else if(c instanceof Int32Array)d=r.INT;else if(c instanceof Int8Array)d=r.BYTE;else if(c instanceof Uint8Array)d=r.UNSIGNED_BYTE;else if(c instanceof Uint8ClampedArray)d=r.UNSIGNED_BYTE;else throw new Error("THREE.WebGLAttributes: Unsupported buffer data format: "+c);return{buffer:h,type:d,bytesPerElement:c.BYTES_PER_ELEMENT,version:a.version,size:f}}function n(a,l,c){const u=l.array,f=l.updateRanges;if(r.bindBuffer(c,a),f.length===0)r.bufferSubData(c,0,u);else{f.sort((d,_)=>d.start-_.start);let h=0;for(let d=1;d<f.length;d++){const _=f[h],g=f[d];g.start<=_.start+_.count+1?_.count=Math.max(_.count,g.start+g.count-_.start):(++h,f[h]=g)}f.length=h+1;for(let d=0,_=f.length;d<_;d++){const g=f[d];r.bufferSubData(c,g.start*u.BYTES_PER_ELEMENT,u,g.start,g.count)}l.clearUpdateRanges()}l.onUploadCallback()}function i(a){return a.isInterleavedBufferAttribute&&(a=a.data),e.get(a)}function s(a){a.isInterleavedBufferAttribute&&(a=a.data);const l=e.get(a);l&&(r.deleteBuffer(l.buffer),e.delete(a))}function o(a,l){if(a.isInterleavedBufferAttribute&&(a=a.data),a.isGLBufferAttribute){const u=e.get(a);(!u||u.version<a.version)&&e.set(a,{buffer:a.buffer,type:a.type,bytesPerElement:a.elementSize,version:a.version});return}const c=e.get(a);if(c===void 0)e.set(a,t(a,l));else if(c.version<a.version){if(c.size!==a.array.byteLength)throw new Error("THREE.WebGLAttributes: The size of the buffer attribute's array buffer does not match the original size. Resizing buffer attributes is not supported.");n(c.buffer,a,l),c.version=a.version}}return{get:i,remove:s,update:o}}class Bo extends fi{constructor(e=1,t=1,n=1,i=1){super(),this.type="PlaneGeometry",this.parameters={width:e,height:t,widthSegments:n,heightSegments:i};const s=e/2,o=t/2,a=Math.floor(n),l=Math.floor(i),c=a+1,u=l+1,f=e/a,h=t/l,d=[],_=[],g=[],p=[];for(let m=0;m<u;m++){const y=m*h-o;for(let x=0;x<c;x++){const M=x*f-s;_.push(M,-y,0),g.push(0,0,1),p.push(x/a),p.push(1-m/l)}}for(let m=0;m<l;m++)for(let y=0;y<a;y++){const x=y+c*m,M=y+c*(m+1),R=y+1+c*(m+1),w=y+1+c*m;d.push(x,M,w),d.push(M,R,w)}this.setIndex(d),this.setAttribute("position",new Si(_,3)),this.setAttribute("normal",new Si(g,3)),this.setAttribute("uv",new Si(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new Bo(e.width,e.height,e.widthSegments,e.heightSegments)}}var _0=`#ifdef USE_ALPHAHASH
	if ( diffuseColor.a < getAlphaHashThreshold( vPosition ) ) discard;
#endif`,g0=`#ifdef USE_ALPHAHASH
	const float ALPHA_HASH_SCALE = 0.05;
	float hash2D( vec2 value ) {
		return fract( 1.0e4 * sin( 17.0 * value.x + 0.1 * value.y ) * ( 0.1 + abs( sin( 13.0 * value.y + value.x ) ) ) );
	}
	float hash3D( vec3 value ) {
		return hash2D( vec2( hash2D( value.xy ), value.z ) );
	}
	float getAlphaHashThreshold( vec3 position ) {
		float maxDeriv = max(
			length( dFdx( position.xyz ) ),
			length( dFdy( position.xyz ) )
		);
		float pixScale = 1.0 / ( ALPHA_HASH_SCALE * maxDeriv );
		vec2 pixScales = vec2(
			exp2( floor( log2( pixScale ) ) ),
			exp2( ceil( log2( pixScale ) ) )
		);
		vec2 alpha = vec2(
			hash3D( floor( pixScales.x * position.xyz ) ),
			hash3D( floor( pixScales.y * position.xyz ) )
		);
		float lerpFactor = fract( log2( pixScale ) );
		float x = ( 1.0 - lerpFactor ) * alpha.x + lerpFactor * alpha.y;
		float a = min( lerpFactor, 1.0 - lerpFactor );
		vec3 cases = vec3(
			x * x / ( 2.0 * a * ( 1.0 - a ) ),
			( x - 0.5 * a ) / ( 1.0 - a ),
			1.0 - ( ( 1.0 - x ) * ( 1.0 - x ) / ( 2.0 * a * ( 1.0 - a ) ) )
		);
		float threshold = ( x < ( 1.0 - a ) )
			? ( ( x < a ) ? cases.x : cases.y )
			: cases.z;
		return clamp( threshold , 1.0e-6, 1.0 );
	}
#endif`,v0=`#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, vAlphaMapUv ).g;
#endif`,x0=`#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,S0=`#ifdef USE_ALPHATEST
	#ifdef ALPHA_TO_COVERAGE
	diffuseColor.a = smoothstep( alphaTest, alphaTest + fwidth( diffuseColor.a ), diffuseColor.a );
	if ( diffuseColor.a == 0.0 ) discard;
	#else
	if ( diffuseColor.a < alphaTest ) discard;
	#endif
#endif`,M0=`#ifdef USE_ALPHATEST
	uniform float alphaTest;
#endif`,y0=`#ifdef USE_AOMAP
	float ambientOcclusion = ( texture2D( aoMap, vAoMapUv ).r - 1.0 ) * aoMapIntensity + 1.0;
	reflectedLight.indirectDiffuse *= ambientOcclusion;
	#if defined( USE_CLEARCOAT ) 
		clearcoatSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_SHEEN ) 
		sheenSpecularIndirect *= ambientOcclusion;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD )
		float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
		reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );
	#endif
#endif`,E0=`#ifdef USE_AOMAP
	uniform sampler2D aoMap;
	uniform float aoMapIntensity;
#endif`,T0=`#ifdef USE_BATCHING
	#if ! defined( GL_ANGLE_multi_draw )
	#define gl_DrawID _gl_DrawID
	uniform int _gl_DrawID;
	#endif
	uniform highp sampler2D batchingTexture;
	uniform highp usampler2D batchingIdTexture;
	mat4 getBatchingMatrix( const in float i ) {
		int size = textureSize( batchingTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( batchingTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( batchingTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( batchingTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( batchingTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
	float getIndirectIndex( const in int i ) {
		int size = textureSize( batchingIdTexture, 0 ).x;
		int x = i % size;
		int y = i / size;
		return float( texelFetch( batchingIdTexture, ivec2( x, y ), 0 ).r );
	}
#endif
#ifdef USE_BATCHING_COLOR
	uniform sampler2D batchingColorTexture;
	vec3 getBatchingColor( const in float i ) {
		int size = textureSize( batchingColorTexture, 0 ).x;
		int j = int( i );
		int x = j % size;
		int y = j / size;
		return texelFetch( batchingColorTexture, ivec2( x, y ), 0 ).rgb;
	}
#endif`,b0=`#ifdef USE_BATCHING
	mat4 batchingMatrix = getBatchingMatrix( getIndirectIndex( gl_DrawID ) );
#endif`,w0=`vec3 transformed = vec3( position );
#ifdef USE_ALPHAHASH
	vPosition = vec3( position );
#endif`,A0=`vec3 objectNormal = vec3( normal );
#ifdef USE_TANGENT
	vec3 objectTangent = vec3( tangent.xyz );
#endif`,R0=`float G_BlinnPhong_Implicit( ) {
	return 0.25;
}
float D_BlinnPhong( const in float shininess, const in float dotNH ) {
	return RECIPROCAL_PI * ( shininess * 0.5 + 1.0 ) * pow( dotNH, shininess );
}
vec3 BRDF_BlinnPhong( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in vec3 specularColor, const in float shininess ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( specularColor, 1.0, dotVH );
	float G = G_BlinnPhong_Implicit( );
	float D = D_BlinnPhong( shininess, dotNH );
	return F * ( G * D );
} // validated`,C0=`#ifdef USE_IRIDESCENCE
	const mat3 XYZ_TO_REC709 = mat3(
		 3.2404542, -0.9692660,  0.0556434,
		-1.5371385,  1.8760108, -0.2040259,
		-0.4985314,  0.0415560,  1.0572252
	);
	vec3 Fresnel0ToIor( vec3 fresnel0 ) {
		vec3 sqrtF0 = sqrt( fresnel0 );
		return ( vec3( 1.0 ) + sqrtF0 ) / ( vec3( 1.0 ) - sqrtF0 );
	}
	vec3 IorToFresnel0( vec3 transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - vec3( incidentIor ) ) / ( transmittedIor + vec3( incidentIor ) ) );
	}
	float IorToFresnel0( float transmittedIor, float incidentIor ) {
		return pow2( ( transmittedIor - incidentIor ) / ( transmittedIor + incidentIor ));
	}
	vec3 evalSensitivity( float OPD, vec3 shift ) {
		float phase = 2.0 * PI * OPD * 1.0e-9;
		vec3 val = vec3( 5.4856e-13, 4.4201e-13, 5.2481e-13 );
		vec3 pos = vec3( 1.6810e+06, 1.7953e+06, 2.2084e+06 );
		vec3 var = vec3( 4.3278e+09, 9.3046e+09, 6.6121e+09 );
		vec3 xyz = val * sqrt( 2.0 * PI * var ) * cos( pos * phase + shift ) * exp( - pow2( phase ) * var );
		xyz.x += 9.7470e-14 * sqrt( 2.0 * PI * 4.5282e+09 ) * cos( 2.2399e+06 * phase + shift[ 0 ] ) * exp( - 4.5282e+09 * pow2( phase ) );
		xyz /= 1.0685e-7;
		vec3 rgb = XYZ_TO_REC709 * xyz;
		return rgb;
	}
	vec3 evalIridescence( float outsideIOR, float eta2, float cosTheta1, float thinFilmThickness, vec3 baseF0 ) {
		vec3 I;
		float iridescenceIOR = mix( outsideIOR, eta2, smoothstep( 0.0, 0.03, thinFilmThickness ) );
		float sinTheta2Sq = pow2( outsideIOR / iridescenceIOR ) * ( 1.0 - pow2( cosTheta1 ) );
		float cosTheta2Sq = 1.0 - sinTheta2Sq;
		if ( cosTheta2Sq < 0.0 ) {
			return vec3( 1.0 );
		}
		float cosTheta2 = sqrt( cosTheta2Sq );
		float R0 = IorToFresnel0( iridescenceIOR, outsideIOR );
		float R12 = F_Schlick( R0, 1.0, cosTheta1 );
		float T121 = 1.0 - R12;
		float phi12 = 0.0;
		if ( iridescenceIOR < outsideIOR ) phi12 = PI;
		float phi21 = PI - phi12;
		vec3 baseIOR = Fresnel0ToIor( clamp( baseF0, 0.0, 0.9999 ) );		vec3 R1 = IorToFresnel0( baseIOR, iridescenceIOR );
		vec3 R23 = F_Schlick( R1, 1.0, cosTheta2 );
		vec3 phi23 = vec3( 0.0 );
		if ( baseIOR[ 0 ] < iridescenceIOR ) phi23[ 0 ] = PI;
		if ( baseIOR[ 1 ] < iridescenceIOR ) phi23[ 1 ] = PI;
		if ( baseIOR[ 2 ] < iridescenceIOR ) phi23[ 2 ] = PI;
		float OPD = 2.0 * iridescenceIOR * thinFilmThickness * cosTheta2;
		vec3 phi = vec3( phi21 ) + phi23;
		vec3 R123 = clamp( R12 * R23, 1e-5, 0.9999 );
		vec3 r123 = sqrt( R123 );
		vec3 Rs = pow2( T121 ) * R23 / ( vec3( 1.0 ) - R123 );
		vec3 C0 = R12 + Rs;
		I = C0;
		vec3 Cm = Rs - T121;
		for ( int m = 1; m <= 2; ++ m ) {
			Cm *= r123;
			vec3 Sm = 2.0 * evalSensitivity( float( m ) * OPD, float( m ) * phi );
			I += Cm * Sm;
		}
		return max( I, vec3( 0.0 ) );
	}
#endif`,P0=`#ifdef USE_BUMPMAP
	uniform sampler2D bumpMap;
	uniform float bumpScale;
	vec2 dHdxy_fwd() {
		vec2 dSTdx = dFdx( vBumpMapUv );
		vec2 dSTdy = dFdy( vBumpMapUv );
		float Hll = bumpScale * texture2D( bumpMap, vBumpMapUv ).x;
		float dBx = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdx ).x - Hll;
		float dBy = bumpScale * texture2D( bumpMap, vBumpMapUv + dSTdy ).x - Hll;
		return vec2( dBx, dBy );
	}
	vec3 perturbNormalArb( vec3 surf_pos, vec3 surf_norm, vec2 dHdxy, float faceDirection ) {
		vec3 vSigmaX = normalize( dFdx( surf_pos.xyz ) );
		vec3 vSigmaY = normalize( dFdy( surf_pos.xyz ) );
		vec3 vN = surf_norm;
		vec3 R1 = cross( vSigmaY, vN );
		vec3 R2 = cross( vN, vSigmaX );
		float fDet = dot( vSigmaX, R1 ) * faceDirection;
		vec3 vGrad = sign( fDet ) * ( dHdxy.x * R1 + dHdxy.y * R2 );
		return normalize( abs( fDet ) * surf_norm - vGrad );
	}
#endif`,D0=`#if NUM_CLIPPING_PLANES > 0
	vec4 plane;
	#ifdef ALPHA_TO_COVERAGE
		float distanceToPlane, distanceGradient;
		float clipOpacity = 1.0;
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
			distanceGradient = fwidth( distanceToPlane ) / 2.0;
			clipOpacity *= smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			if ( clipOpacity == 0.0 ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			float unionClipOpacity = 1.0;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				distanceToPlane = - dot( vClipPosition, plane.xyz ) + plane.w;
				distanceGradient = fwidth( distanceToPlane ) / 2.0;
				unionClipOpacity *= 1.0 - smoothstep( - distanceGradient, distanceGradient, distanceToPlane );
			}
			#pragma unroll_loop_end
			clipOpacity *= 1.0 - unionClipOpacity;
		#endif
		diffuseColor.a *= clipOpacity;
		if ( diffuseColor.a == 0.0 ) discard;
	#else
		#pragma unroll_loop_start
		for ( int i = 0; i < UNION_CLIPPING_PLANES; i ++ ) {
			plane = clippingPlanes[ i ];
			if ( dot( vClipPosition, plane.xyz ) > plane.w ) discard;
		}
		#pragma unroll_loop_end
		#if UNION_CLIPPING_PLANES < NUM_CLIPPING_PLANES
			bool clipped = true;
			#pragma unroll_loop_start
			for ( int i = UNION_CLIPPING_PLANES; i < NUM_CLIPPING_PLANES; i ++ ) {
				plane = clippingPlanes[ i ];
				clipped = ( dot( vClipPosition, plane.xyz ) > plane.w ) && clipped;
			}
			#pragma unroll_loop_end
			if ( clipped ) discard;
		#endif
	#endif
#endif`,L0=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
	uniform vec4 clippingPlanes[ NUM_CLIPPING_PLANES ];
#endif`,I0=`#if NUM_CLIPPING_PLANES > 0
	varying vec3 vClipPosition;
#endif`,U0=`#if NUM_CLIPPING_PLANES > 0
	vClipPosition = - mvPosition.xyz;
#endif`,N0=`#if defined( USE_COLOR_ALPHA )
	diffuseColor *= vColor;
#elif defined( USE_COLOR )
	diffuseColor.rgb *= vColor;
#endif`,F0=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR )
	varying vec3 vColor;
#endif`,O0=`#if defined( USE_COLOR_ALPHA )
	varying vec4 vColor;
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	varying vec3 vColor;
#endif`,B0=`#if defined( USE_COLOR_ALPHA )
	vColor = vec4( 1.0 );
#elif defined( USE_COLOR ) || defined( USE_INSTANCING_COLOR ) || defined( USE_BATCHING_COLOR )
	vColor = vec3( 1.0 );
#endif
#ifdef USE_COLOR
	vColor *= color;
#endif
#ifdef USE_INSTANCING_COLOR
	vColor.xyz *= instanceColor.xyz;
#endif
#ifdef USE_BATCHING_COLOR
	vec3 batchingColor = getBatchingColor( getIndirectIndex( gl_DrawID ) );
	vColor.xyz *= batchingColor.xyz;
#endif`,z0=`#define PI 3.141592653589793
#define PI2 6.283185307179586
#define PI_HALF 1.5707963267948966
#define RECIPROCAL_PI 0.3183098861837907
#define RECIPROCAL_PI2 0.15915494309189535
#define EPSILON 1e-6
#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
#define whiteComplement( a ) ( 1.0 - saturate( a ) )
float pow2( const in float x ) { return x*x; }
vec3 pow2( const in vec3 x ) { return x*x; }
float pow3( const in float x ) { return x*x*x; }
float pow4( const in float x ) { float x2 = x*x; return x2*x2; }
float max3( const in vec3 v ) { return max( max( v.x, v.y ), v.z ); }
float average( const in vec3 v ) { return dot( v, vec3( 0.3333333 ) ); }
highp float rand( const in vec2 uv ) {
	const highp float a = 12.9898, b = 78.233, c = 43758.5453;
	highp float dt = dot( uv.xy, vec2( a,b ) ), sn = mod( dt, PI );
	return fract( sin( sn ) * c );
}
#ifdef HIGH_PRECISION
	float precisionSafeLength( vec3 v ) { return length( v ); }
#else
	float precisionSafeLength( vec3 v ) {
		float maxComponent = max3( abs( v ) );
		return length( v / maxComponent ) * maxComponent;
	}
#endif
struct IncidentLight {
	vec3 color;
	vec3 direction;
	bool visible;
};
struct ReflectedLight {
	vec3 directDiffuse;
	vec3 directSpecular;
	vec3 indirectDiffuse;
	vec3 indirectSpecular;
};
#ifdef USE_ALPHAHASH
	varying vec3 vPosition;
#endif
vec3 transformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( matrix * vec4( dir, 0.0 ) ).xyz );
}
vec3 inverseTransformDirection( in vec3 dir, in mat4 matrix ) {
	return normalize( ( vec4( dir, 0.0 ) * matrix ).xyz );
}
mat3 transposeMat3( const in mat3 m ) {
	mat3 tmp;
	tmp[ 0 ] = vec3( m[ 0 ].x, m[ 1 ].x, m[ 2 ].x );
	tmp[ 1 ] = vec3( m[ 0 ].y, m[ 1 ].y, m[ 2 ].y );
	tmp[ 2 ] = vec3( m[ 0 ].z, m[ 1 ].z, m[ 2 ].z );
	return tmp;
}
bool isPerspectiveMatrix( mat4 m ) {
	return m[ 2 ][ 3 ] == - 1.0;
}
vec2 equirectUv( in vec3 dir ) {
	float u = atan( dir.z, dir.x ) * RECIPROCAL_PI2 + 0.5;
	float v = asin( clamp( dir.y, - 1.0, 1.0 ) ) * RECIPROCAL_PI + 0.5;
	return vec2( u, v );
}
vec3 BRDF_Lambert( const in vec3 diffuseColor ) {
	return RECIPROCAL_PI * diffuseColor;
}
vec3 F_Schlick( const in vec3 f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
}
float F_Schlick( const in float f0, const in float f90, const in float dotVH ) {
	float fresnel = exp2( ( - 5.55473 * dotVH - 6.98316 ) * dotVH );
	return f0 * ( 1.0 - fresnel ) + ( f90 * fresnel );
} // validated`,k0=`#ifdef ENVMAP_TYPE_CUBE_UV
	#define cubeUV_minMipLevel 4.0
	#define cubeUV_minTileSize 16.0
	float getFace( vec3 direction ) {
		vec3 absDirection = abs( direction );
		float face = - 1.0;
		if ( absDirection.x > absDirection.z ) {
			if ( absDirection.x > absDirection.y )
				face = direction.x > 0.0 ? 0.0 : 3.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		} else {
			if ( absDirection.z > absDirection.y )
				face = direction.z > 0.0 ? 2.0 : 5.0;
			else
				face = direction.y > 0.0 ? 1.0 : 4.0;
		}
		return face;
	}
	vec2 getUV( vec3 direction, float face ) {
		vec2 uv;
		if ( face == 0.0 ) {
			uv = vec2( direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 1.0 ) {
			uv = vec2( - direction.x, - direction.z ) / abs( direction.y );
		} else if ( face == 2.0 ) {
			uv = vec2( - direction.x, direction.y ) / abs( direction.z );
		} else if ( face == 3.0 ) {
			uv = vec2( - direction.z, direction.y ) / abs( direction.x );
		} else if ( face == 4.0 ) {
			uv = vec2( - direction.x, direction.z ) / abs( direction.y );
		} else {
			uv = vec2( direction.x, direction.y ) / abs( direction.z );
		}
		return 0.5 * ( uv + 1.0 );
	}
	vec3 bilinearCubeUV( sampler2D envMap, vec3 direction, float mipInt ) {
		float face = getFace( direction );
		float filterInt = max( cubeUV_minMipLevel - mipInt, 0.0 );
		mipInt = max( mipInt, cubeUV_minMipLevel );
		float faceSize = exp2( mipInt );
		highp vec2 uv = getUV( direction, face ) * ( faceSize - 2.0 ) + 1.0;
		if ( face > 2.0 ) {
			uv.y += faceSize;
			face -= 3.0;
		}
		uv.x += face * faceSize;
		uv.x += filterInt * 3.0 * cubeUV_minTileSize;
		uv.y += 4.0 * ( exp2( CUBEUV_MAX_MIP ) - faceSize );
		uv.x *= CUBEUV_TEXEL_WIDTH;
		uv.y *= CUBEUV_TEXEL_HEIGHT;
		#ifdef texture2DGradEXT
			return texture2DGradEXT( envMap, uv, vec2( 0.0 ), vec2( 0.0 ) ).rgb;
		#else
			return texture2D( envMap, uv ).rgb;
		#endif
	}
	#define cubeUV_r0 1.0
	#define cubeUV_m0 - 2.0
	#define cubeUV_r1 0.8
	#define cubeUV_m1 - 1.0
	#define cubeUV_r4 0.4
	#define cubeUV_m4 2.0
	#define cubeUV_r5 0.305
	#define cubeUV_m5 3.0
	#define cubeUV_r6 0.21
	#define cubeUV_m6 4.0
	float roughnessToMip( float roughness ) {
		float mip = 0.0;
		if ( roughness >= cubeUV_r1 ) {
			mip = ( cubeUV_r0 - roughness ) * ( cubeUV_m1 - cubeUV_m0 ) / ( cubeUV_r0 - cubeUV_r1 ) + cubeUV_m0;
		} else if ( roughness >= cubeUV_r4 ) {
			mip = ( cubeUV_r1 - roughness ) * ( cubeUV_m4 - cubeUV_m1 ) / ( cubeUV_r1 - cubeUV_r4 ) + cubeUV_m1;
		} else if ( roughness >= cubeUV_r5 ) {
			mip = ( cubeUV_r4 - roughness ) * ( cubeUV_m5 - cubeUV_m4 ) / ( cubeUV_r4 - cubeUV_r5 ) + cubeUV_m4;
		} else if ( roughness >= cubeUV_r6 ) {
			mip = ( cubeUV_r5 - roughness ) * ( cubeUV_m6 - cubeUV_m5 ) / ( cubeUV_r5 - cubeUV_r6 ) + cubeUV_m5;
		} else {
			mip = - 2.0 * log2( 1.16 * roughness );		}
		return mip;
	}
	vec4 textureCubeUV( sampler2D envMap, vec3 sampleDir, float roughness ) {
		float mip = clamp( roughnessToMip( roughness ), cubeUV_m0, CUBEUV_MAX_MIP );
		float mipF = fract( mip );
		float mipInt = floor( mip );
		vec3 color0 = bilinearCubeUV( envMap, sampleDir, mipInt );
		if ( mipF == 0.0 ) {
			return vec4( color0, 1.0 );
		} else {
			vec3 color1 = bilinearCubeUV( envMap, sampleDir, mipInt + 1.0 );
			return vec4( mix( color0, color1, mipF ), 1.0 );
		}
	}
#endif`,H0=`vec3 transformedNormal = objectNormal;
#ifdef USE_TANGENT
	vec3 transformedTangent = objectTangent;
#endif
#ifdef USE_BATCHING
	mat3 bm = mat3( batchingMatrix );
	transformedNormal /= vec3( dot( bm[ 0 ], bm[ 0 ] ), dot( bm[ 1 ], bm[ 1 ] ), dot( bm[ 2 ], bm[ 2 ] ) );
	transformedNormal = bm * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = bm * transformedTangent;
	#endif
#endif
#ifdef USE_INSTANCING
	mat3 im = mat3( instanceMatrix );
	transformedNormal /= vec3( dot( im[ 0 ], im[ 0 ] ), dot( im[ 1 ], im[ 1 ] ), dot( im[ 2 ], im[ 2 ] ) );
	transformedNormal = im * transformedNormal;
	#ifdef USE_TANGENT
		transformedTangent = im * transformedTangent;
	#endif
#endif
transformedNormal = normalMatrix * transformedNormal;
#ifdef FLIP_SIDED
	transformedNormal = - transformedNormal;
#endif
#ifdef USE_TANGENT
	transformedTangent = ( modelViewMatrix * vec4( transformedTangent, 0.0 ) ).xyz;
	#ifdef FLIP_SIDED
		transformedTangent = - transformedTangent;
	#endif
#endif`,G0=`#ifdef USE_DISPLACEMENTMAP
	uniform sampler2D displacementMap;
	uniform float displacementScale;
	uniform float displacementBias;
#endif`,V0=`#ifdef USE_DISPLACEMENTMAP
	transformed += normalize( objectNormal ) * ( texture2D( displacementMap, vDisplacementMapUv ).x * displacementScale + displacementBias );
#endif`,W0=`#ifdef USE_EMISSIVEMAP
	vec4 emissiveColor = texture2D( emissiveMap, vEmissiveMapUv );
	totalEmissiveRadiance *= emissiveColor.rgb;
#endif`,X0=`#ifdef USE_EMISSIVEMAP
	uniform sampler2D emissiveMap;
#endif`,Y0="gl_FragColor = linearToOutputTexel( gl_FragColor );",q0=`
const mat3 LINEAR_SRGB_TO_LINEAR_DISPLAY_P3 = mat3(
	vec3( 0.8224621, 0.177538, 0.0 ),
	vec3( 0.0331941, 0.9668058, 0.0 ),
	vec3( 0.0170827, 0.0723974, 0.9105199 )
);
const mat3 LINEAR_DISPLAY_P3_TO_LINEAR_SRGB = mat3(
	vec3( 1.2249401, - 0.2249404, 0.0 ),
	vec3( - 0.0420569, 1.0420571, 0.0 ),
	vec3( - 0.0196376, - 0.0786361, 1.0982735 )
);
vec4 LinearSRGBToLinearDisplayP3( in vec4 value ) {
	return vec4( value.rgb * LINEAR_SRGB_TO_LINEAR_DISPLAY_P3, value.a );
}
vec4 LinearDisplayP3ToLinearSRGB( in vec4 value ) {
	return vec4( value.rgb * LINEAR_DISPLAY_P3_TO_LINEAR_SRGB, value.a );
}
vec4 LinearTransferOETF( in vec4 value ) {
	return value;
}
vec4 sRGBTransferOETF( in vec4 value ) {
	return vec4( mix( pow( value.rgb, vec3( 0.41666 ) ) * 1.055 - vec3( 0.055 ), value.rgb * 12.92, vec3( lessThanEqual( value.rgb, vec3( 0.0031308 ) ) ) ), value.a );
}`,$0=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vec3 cameraToFrag;
		if ( isOrthographic ) {
			cameraToFrag = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToFrag = normalize( vWorldPosition - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vec3 reflectVec = reflect( cameraToFrag, worldNormal );
		#else
			vec3 reflectVec = refract( cameraToFrag, worldNormal, refractionRatio );
		#endif
	#else
		vec3 reflectVec = vReflect;
	#endif
	#ifdef ENVMAP_TYPE_CUBE
		vec4 envColor = textureCube( envMap, envMapRotation * vec3( flipEnvMap * reflectVec.x, reflectVec.yz ) );
	#else
		vec4 envColor = vec4( 0.0 );
	#endif
	#ifdef ENVMAP_BLENDING_MULTIPLY
		outgoingLight = mix( outgoingLight, outgoingLight * envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_MIX )
		outgoingLight = mix( outgoingLight, envColor.xyz, specularStrength * reflectivity );
	#elif defined( ENVMAP_BLENDING_ADD )
		outgoingLight += envColor.xyz * specularStrength * reflectivity;
	#endif
#endif`,K0=`#ifdef USE_ENVMAP
	uniform float envMapIntensity;
	uniform float flipEnvMap;
	uniform mat3 envMapRotation;
	#ifdef ENVMAP_TYPE_CUBE
		uniform samplerCube envMap;
	#else
		uniform sampler2D envMap;
	#endif
	
#endif`,Z0=`#ifdef USE_ENVMAP
	uniform float reflectivity;
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		varying vec3 vWorldPosition;
		uniform float refractionRatio;
	#else
		varying vec3 vReflect;
	#endif
#endif`,j0=`#ifdef USE_ENVMAP
	#if defined( USE_BUMPMAP ) || defined( USE_NORMALMAP ) || defined( PHONG ) || defined( LAMBERT )
		#define ENV_WORLDPOS
	#endif
	#ifdef ENV_WORLDPOS
		
		varying vec3 vWorldPosition;
	#else
		varying vec3 vReflect;
		uniform float refractionRatio;
	#endif
#endif`,J0=`#ifdef USE_ENVMAP
	#ifdef ENV_WORLDPOS
		vWorldPosition = worldPosition.xyz;
	#else
		vec3 cameraToVertex;
		if ( isOrthographic ) {
			cameraToVertex = normalize( vec3( - viewMatrix[ 0 ][ 2 ], - viewMatrix[ 1 ][ 2 ], - viewMatrix[ 2 ][ 2 ] ) );
		} else {
			cameraToVertex = normalize( worldPosition.xyz - cameraPosition );
		}
		vec3 worldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
		#ifdef ENVMAP_MODE_REFLECTION
			vReflect = reflect( cameraToVertex, worldNormal );
		#else
			vReflect = refract( cameraToVertex, worldNormal, refractionRatio );
		#endif
	#endif
#endif`,Q0=`#ifdef USE_FOG
	vFogDepth = - mvPosition.z;
#endif`,ev=`#ifdef USE_FOG
	varying float vFogDepth;
#endif`,tv=`#ifdef USE_FOG
	#ifdef FOG_EXP2
		float fogFactor = 1.0 - exp( - fogDensity * fogDensity * vFogDepth * vFogDepth );
	#else
		float fogFactor = smoothstep( fogNear, fogFar, vFogDepth );
	#endif
	gl_FragColor.rgb = mix( gl_FragColor.rgb, fogColor, fogFactor );
#endif`,nv=`#ifdef USE_FOG
	uniform vec3 fogColor;
	varying float vFogDepth;
	#ifdef FOG_EXP2
		uniform float fogDensity;
	#else
		uniform float fogNear;
		uniform float fogFar;
	#endif
#endif`,iv=`#ifdef USE_GRADIENTMAP
	uniform sampler2D gradientMap;
#endif
vec3 getGradientIrradiance( vec3 normal, vec3 lightDirection ) {
	float dotNL = dot( normal, lightDirection );
	vec2 coord = vec2( dotNL * 0.5 + 0.5, 0.0 );
	#ifdef USE_GRADIENTMAP
		return vec3( texture2D( gradientMap, coord ).r );
	#else
		vec2 fw = fwidth( coord ) * 0.5;
		return mix( vec3( 0.7 ), vec3( 1.0 ), smoothstep( 0.7 - fw.x, 0.7 + fw.x, coord.x ) );
	#endif
}`,rv=`#ifdef USE_LIGHTMAP
	uniform sampler2D lightMap;
	uniform float lightMapIntensity;
#endif`,sv=`LambertMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularStrength = specularStrength;`,ov=`varying vec3 vViewPosition;
struct LambertMaterial {
	vec3 diffuseColor;
	float specularStrength;
};
void RE_Direct_Lambert( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Lambert( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in LambertMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Lambert
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Lambert`,av=`uniform bool receiveShadow;
uniform vec3 ambientLightColor;
#if defined( USE_LIGHT_PROBES )
	uniform vec3 lightProbe[ 9 ];
#endif
vec3 shGetIrradianceAt( in vec3 normal, in vec3 shCoefficients[ 9 ] ) {
	float x = normal.x, y = normal.y, z = normal.z;
	vec3 result = shCoefficients[ 0 ] * 0.886227;
	result += shCoefficients[ 1 ] * 2.0 * 0.511664 * y;
	result += shCoefficients[ 2 ] * 2.0 * 0.511664 * z;
	result += shCoefficients[ 3 ] * 2.0 * 0.511664 * x;
	result += shCoefficients[ 4 ] * 2.0 * 0.429043 * x * y;
	result += shCoefficients[ 5 ] * 2.0 * 0.429043 * y * z;
	result += shCoefficients[ 6 ] * ( 0.743125 * z * z - 0.247708 );
	result += shCoefficients[ 7 ] * 2.0 * 0.429043 * x * z;
	result += shCoefficients[ 8 ] * 0.429043 * ( x * x - y * y );
	return result;
}
vec3 getLightProbeIrradiance( const in vec3 lightProbe[ 9 ], const in vec3 normal ) {
	vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
	vec3 irradiance = shGetIrradianceAt( worldNormal, lightProbe );
	return irradiance;
}
vec3 getAmbientLightIrradiance( const in vec3 ambientLightColor ) {
	vec3 irradiance = ambientLightColor;
	return irradiance;
}
float getDistanceAttenuation( const in float lightDistance, const in float cutoffDistance, const in float decayExponent ) {
	float distanceFalloff = 1.0 / max( pow( lightDistance, decayExponent ), 0.01 );
	if ( cutoffDistance > 0.0 ) {
		distanceFalloff *= pow2( saturate( 1.0 - pow4( lightDistance / cutoffDistance ) ) );
	}
	return distanceFalloff;
}
float getSpotAttenuation( const in float coneCosine, const in float penumbraCosine, const in float angleCosine ) {
	return smoothstep( coneCosine, penumbraCosine, angleCosine );
}
#if NUM_DIR_LIGHTS > 0
	struct DirectionalLight {
		vec3 direction;
		vec3 color;
	};
	uniform DirectionalLight directionalLights[ NUM_DIR_LIGHTS ];
	void getDirectionalLightInfo( const in DirectionalLight directionalLight, out IncidentLight light ) {
		light.color = directionalLight.color;
		light.direction = directionalLight.direction;
		light.visible = true;
	}
#endif
#if NUM_POINT_LIGHTS > 0
	struct PointLight {
		vec3 position;
		vec3 color;
		float distance;
		float decay;
	};
	uniform PointLight pointLights[ NUM_POINT_LIGHTS ];
	void getPointLightInfo( const in PointLight pointLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = pointLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float lightDistance = length( lVector );
		light.color = pointLight.color;
		light.color *= getDistanceAttenuation( lightDistance, pointLight.distance, pointLight.decay );
		light.visible = ( light.color != vec3( 0.0 ) );
	}
#endif
#if NUM_SPOT_LIGHTS > 0
	struct SpotLight {
		vec3 position;
		vec3 direction;
		vec3 color;
		float distance;
		float decay;
		float coneCos;
		float penumbraCos;
	};
	uniform SpotLight spotLights[ NUM_SPOT_LIGHTS ];
	void getSpotLightInfo( const in SpotLight spotLight, const in vec3 geometryPosition, out IncidentLight light ) {
		vec3 lVector = spotLight.position - geometryPosition;
		light.direction = normalize( lVector );
		float angleCos = dot( light.direction, spotLight.direction );
		float spotAttenuation = getSpotAttenuation( spotLight.coneCos, spotLight.penumbraCos, angleCos );
		if ( spotAttenuation > 0.0 ) {
			float lightDistance = length( lVector );
			light.color = spotLight.color * spotAttenuation;
			light.color *= getDistanceAttenuation( lightDistance, spotLight.distance, spotLight.decay );
			light.visible = ( light.color != vec3( 0.0 ) );
		} else {
			light.color = vec3( 0.0 );
			light.visible = false;
		}
	}
#endif
#if NUM_RECT_AREA_LIGHTS > 0
	struct RectAreaLight {
		vec3 color;
		vec3 position;
		vec3 halfWidth;
		vec3 halfHeight;
	};
	uniform sampler2D ltc_1;	uniform sampler2D ltc_2;
	uniform RectAreaLight rectAreaLights[ NUM_RECT_AREA_LIGHTS ];
#endif
#if NUM_HEMI_LIGHTS > 0
	struct HemisphereLight {
		vec3 direction;
		vec3 skyColor;
		vec3 groundColor;
	};
	uniform HemisphereLight hemisphereLights[ NUM_HEMI_LIGHTS ];
	vec3 getHemisphereLightIrradiance( const in HemisphereLight hemiLight, const in vec3 normal ) {
		float dotNL = dot( normal, hemiLight.direction );
		float hemiDiffuseWeight = 0.5 * dotNL + 0.5;
		vec3 irradiance = mix( hemiLight.groundColor, hemiLight.skyColor, hemiDiffuseWeight );
		return irradiance;
	}
#endif`,lv=`#ifdef USE_ENVMAP
	vec3 getIBLIrradiance( const in vec3 normal ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 worldNormal = inverseTransformDirection( normal, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * worldNormal, 1.0 );
			return PI * envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	vec3 getIBLRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness ) {
		#ifdef ENVMAP_TYPE_CUBE_UV
			vec3 reflectVec = reflect( - viewDir, normal );
			reflectVec = normalize( mix( reflectVec, normal, roughness * roughness) );
			reflectVec = inverseTransformDirection( reflectVec, viewMatrix );
			vec4 envMapColor = textureCubeUV( envMap, envMapRotation * reflectVec, roughness );
			return envMapColor.rgb * envMapIntensity;
		#else
			return vec3( 0.0 );
		#endif
	}
	#ifdef USE_ANISOTROPY
		vec3 getIBLAnisotropyRadiance( const in vec3 viewDir, const in vec3 normal, const in float roughness, const in vec3 bitangent, const in float anisotropy ) {
			#ifdef ENVMAP_TYPE_CUBE_UV
				vec3 bentNormal = cross( bitangent, viewDir );
				bentNormal = normalize( cross( bentNormal, bitangent ) );
				bentNormal = normalize( mix( bentNormal, normal, pow2( pow2( 1.0 - anisotropy * ( 1.0 - roughness ) ) ) ) );
				return getIBLRadiance( viewDir, bentNormal, roughness );
			#else
				return vec3( 0.0 );
			#endif
		}
	#endif
#endif`,cv=`ToonMaterial material;
material.diffuseColor = diffuseColor.rgb;`,uv=`varying vec3 vViewPosition;
struct ToonMaterial {
	vec3 diffuseColor;
};
void RE_Direct_Toon( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	vec3 irradiance = getGradientIrradiance( geometryNormal, directLight.direction ) * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Toon( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in ToonMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_Toon
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Toon`,hv=`BlinnPhongMaterial material;
material.diffuseColor = diffuseColor.rgb;
material.specularColor = specular;
material.specularShininess = shininess;
material.specularStrength = specularStrength;`,fv=`varying vec3 vViewPosition;
struct BlinnPhongMaterial {
	vec3 diffuseColor;
	vec3 specularColor;
	float specularShininess;
	float specularStrength;
};
void RE_Direct_BlinnPhong( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
	reflectedLight.directSpecular += irradiance * BRDF_BlinnPhong( directLight.direction, geometryViewDir, geometryNormal, material.specularColor, material.specularShininess ) * material.specularStrength;
}
void RE_IndirectDiffuse_BlinnPhong( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in BlinnPhongMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
#define RE_Direct				RE_Direct_BlinnPhong
#define RE_IndirectDiffuse		RE_IndirectDiffuse_BlinnPhong`,dv=`PhysicalMaterial material;
material.diffuseColor = diffuseColor.rgb * ( 1.0 - metalnessFactor );
vec3 dxy = max( abs( dFdx( nonPerturbedNormal ) ), abs( dFdy( nonPerturbedNormal ) ) );
float geometryRoughness = max( max( dxy.x, dxy.y ), dxy.z );
material.roughness = max( roughnessFactor, 0.0525 );material.roughness += geometryRoughness;
material.roughness = min( material.roughness, 1.0 );
#ifdef IOR
	material.ior = ior;
	#ifdef USE_SPECULAR
		float specularIntensityFactor = specularIntensity;
		vec3 specularColorFactor = specularColor;
		#ifdef USE_SPECULAR_COLORMAP
			specularColorFactor *= texture2D( specularColorMap, vSpecularColorMapUv ).rgb;
		#endif
		#ifdef USE_SPECULAR_INTENSITYMAP
			specularIntensityFactor *= texture2D( specularIntensityMap, vSpecularIntensityMapUv ).a;
		#endif
		material.specularF90 = mix( specularIntensityFactor, 1.0, metalnessFactor );
	#else
		float specularIntensityFactor = 1.0;
		vec3 specularColorFactor = vec3( 1.0 );
		material.specularF90 = 1.0;
	#endif
	material.specularColor = mix( min( pow2( ( material.ior - 1.0 ) / ( material.ior + 1.0 ) ) * specularColorFactor, vec3( 1.0 ) ) * specularIntensityFactor, diffuseColor.rgb, metalnessFactor );
#else
	material.specularColor = mix( vec3( 0.04 ), diffuseColor.rgb, metalnessFactor );
	material.specularF90 = 1.0;
#endif
#ifdef USE_CLEARCOAT
	material.clearcoat = clearcoat;
	material.clearcoatRoughness = clearcoatRoughness;
	material.clearcoatF0 = vec3( 0.04 );
	material.clearcoatF90 = 1.0;
	#ifdef USE_CLEARCOATMAP
		material.clearcoat *= texture2D( clearcoatMap, vClearcoatMapUv ).x;
	#endif
	#ifdef USE_CLEARCOAT_ROUGHNESSMAP
		material.clearcoatRoughness *= texture2D( clearcoatRoughnessMap, vClearcoatRoughnessMapUv ).y;
	#endif
	material.clearcoat = saturate( material.clearcoat );	material.clearcoatRoughness = max( material.clearcoatRoughness, 0.0525 );
	material.clearcoatRoughness += geometryRoughness;
	material.clearcoatRoughness = min( material.clearcoatRoughness, 1.0 );
#endif
#ifdef USE_DISPERSION
	material.dispersion = dispersion;
#endif
#ifdef USE_IRIDESCENCE
	material.iridescence = iridescence;
	material.iridescenceIOR = iridescenceIOR;
	#ifdef USE_IRIDESCENCEMAP
		material.iridescence *= texture2D( iridescenceMap, vIridescenceMapUv ).r;
	#endif
	#ifdef USE_IRIDESCENCE_THICKNESSMAP
		material.iridescenceThickness = (iridescenceThicknessMaximum - iridescenceThicknessMinimum) * texture2D( iridescenceThicknessMap, vIridescenceThicknessMapUv ).g + iridescenceThicknessMinimum;
	#else
		material.iridescenceThickness = iridescenceThicknessMaximum;
	#endif
#endif
#ifdef USE_SHEEN
	material.sheenColor = sheenColor;
	#ifdef USE_SHEEN_COLORMAP
		material.sheenColor *= texture2D( sheenColorMap, vSheenColorMapUv ).rgb;
	#endif
	material.sheenRoughness = clamp( sheenRoughness, 0.07, 1.0 );
	#ifdef USE_SHEEN_ROUGHNESSMAP
		material.sheenRoughness *= texture2D( sheenRoughnessMap, vSheenRoughnessMapUv ).a;
	#endif
#endif
#ifdef USE_ANISOTROPY
	#ifdef USE_ANISOTROPYMAP
		mat2 anisotropyMat = mat2( anisotropyVector.x, anisotropyVector.y, - anisotropyVector.y, anisotropyVector.x );
		vec3 anisotropyPolar = texture2D( anisotropyMap, vAnisotropyMapUv ).rgb;
		vec2 anisotropyV = anisotropyMat * normalize( 2.0 * anisotropyPolar.rg - vec2( 1.0 ) ) * anisotropyPolar.b;
	#else
		vec2 anisotropyV = anisotropyVector;
	#endif
	material.anisotropy = length( anisotropyV );
	if( material.anisotropy == 0.0 ) {
		anisotropyV = vec2( 1.0, 0.0 );
	} else {
		anisotropyV /= material.anisotropy;
		material.anisotropy = saturate( material.anisotropy );
	}
	material.alphaT = mix( pow2( material.roughness ), 1.0, pow2( material.anisotropy ) );
	material.anisotropyT = tbn[ 0 ] * anisotropyV.x + tbn[ 1 ] * anisotropyV.y;
	material.anisotropyB = tbn[ 1 ] * anisotropyV.x - tbn[ 0 ] * anisotropyV.y;
#endif`,pv=`struct PhysicalMaterial {
	vec3 diffuseColor;
	float roughness;
	vec3 specularColor;
	float specularF90;
	float dispersion;
	#ifdef USE_CLEARCOAT
		float clearcoat;
		float clearcoatRoughness;
		vec3 clearcoatF0;
		float clearcoatF90;
	#endif
	#ifdef USE_IRIDESCENCE
		float iridescence;
		float iridescenceIOR;
		float iridescenceThickness;
		vec3 iridescenceFresnel;
		vec3 iridescenceF0;
	#endif
	#ifdef USE_SHEEN
		vec3 sheenColor;
		float sheenRoughness;
	#endif
	#ifdef IOR
		float ior;
	#endif
	#ifdef USE_TRANSMISSION
		float transmission;
		float transmissionAlpha;
		float thickness;
		float attenuationDistance;
		vec3 attenuationColor;
	#endif
	#ifdef USE_ANISOTROPY
		float anisotropy;
		float alphaT;
		vec3 anisotropyT;
		vec3 anisotropyB;
	#endif
};
vec3 clearcoatSpecularDirect = vec3( 0.0 );
vec3 clearcoatSpecularIndirect = vec3( 0.0 );
vec3 sheenSpecularDirect = vec3( 0.0 );
vec3 sheenSpecularIndirect = vec3(0.0 );
vec3 Schlick_to_F0( const in vec3 f, const in float f90, const in float dotVH ) {
    float x = clamp( 1.0 - dotVH, 0.0, 1.0 );
    float x2 = x * x;
    float x5 = clamp( x * x2 * x2, 0.0, 0.9999 );
    return ( f - vec3( f90 ) * x5 ) / ( 1.0 - x5 );
}
float V_GGX_SmithCorrelated( const in float alpha, const in float dotNL, const in float dotNV ) {
	float a2 = pow2( alpha );
	float gv = dotNL * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNV ) );
	float gl = dotNV * sqrt( a2 + ( 1.0 - a2 ) * pow2( dotNL ) );
	return 0.5 / max( gv + gl, EPSILON );
}
float D_GGX( const in float alpha, const in float dotNH ) {
	float a2 = pow2( alpha );
	float denom = pow2( dotNH ) * ( a2 - 1.0 ) + 1.0;
	return RECIPROCAL_PI * a2 / pow2( denom );
}
#ifdef USE_ANISOTROPY
	float V_GGX_SmithCorrelated_Anisotropic( const in float alphaT, const in float alphaB, const in float dotTV, const in float dotBV, const in float dotTL, const in float dotBL, const in float dotNV, const in float dotNL ) {
		float gv = dotNL * length( vec3( alphaT * dotTV, alphaB * dotBV, dotNV ) );
		float gl = dotNV * length( vec3( alphaT * dotTL, alphaB * dotBL, dotNL ) );
		float v = 0.5 / ( gv + gl );
		return saturate(v);
	}
	float D_GGX_Anisotropic( const in float alphaT, const in float alphaB, const in float dotNH, const in float dotTH, const in float dotBH ) {
		float a2 = alphaT * alphaB;
		highp vec3 v = vec3( alphaB * dotTH, alphaT * dotBH, a2 * dotNH );
		highp float v2 = dot( v, v );
		float w2 = a2 / v2;
		return RECIPROCAL_PI * a2 * pow2 ( w2 );
	}
#endif
#ifdef USE_CLEARCOAT
	vec3 BRDF_GGX_Clearcoat( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material) {
		vec3 f0 = material.clearcoatF0;
		float f90 = material.clearcoatF90;
		float roughness = material.clearcoatRoughness;
		float alpha = pow2( roughness );
		vec3 halfDir = normalize( lightDir + viewDir );
		float dotNL = saturate( dot( normal, lightDir ) );
		float dotNV = saturate( dot( normal, viewDir ) );
		float dotNH = saturate( dot( normal, halfDir ) );
		float dotVH = saturate( dot( viewDir, halfDir ) );
		vec3 F = F_Schlick( f0, f90, dotVH );
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
		return F * ( V * D );
	}
#endif
vec3 BRDF_GGX( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, const in PhysicalMaterial material ) {
	vec3 f0 = material.specularColor;
	float f90 = material.specularF90;
	float roughness = material.roughness;
	float alpha = pow2( roughness );
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float dotVH = saturate( dot( viewDir, halfDir ) );
	vec3 F = F_Schlick( f0, f90, dotVH );
	#ifdef USE_IRIDESCENCE
		F = mix( F, material.iridescenceFresnel, material.iridescence );
	#endif
	#ifdef USE_ANISOTROPY
		float dotTL = dot( material.anisotropyT, lightDir );
		float dotTV = dot( material.anisotropyT, viewDir );
		float dotTH = dot( material.anisotropyT, halfDir );
		float dotBL = dot( material.anisotropyB, lightDir );
		float dotBV = dot( material.anisotropyB, viewDir );
		float dotBH = dot( material.anisotropyB, halfDir );
		float V = V_GGX_SmithCorrelated_Anisotropic( material.alphaT, alpha, dotTV, dotBV, dotTL, dotBL, dotNV, dotNL );
		float D = D_GGX_Anisotropic( material.alphaT, alpha, dotNH, dotTH, dotBH );
	#else
		float V = V_GGX_SmithCorrelated( alpha, dotNL, dotNV );
		float D = D_GGX( alpha, dotNH );
	#endif
	return F * ( V * D );
}
vec2 LTC_Uv( const in vec3 N, const in vec3 V, const in float roughness ) {
	const float LUT_SIZE = 64.0;
	const float LUT_SCALE = ( LUT_SIZE - 1.0 ) / LUT_SIZE;
	const float LUT_BIAS = 0.5 / LUT_SIZE;
	float dotNV = saturate( dot( N, V ) );
	vec2 uv = vec2( roughness, sqrt( 1.0 - dotNV ) );
	uv = uv * LUT_SCALE + LUT_BIAS;
	return uv;
}
float LTC_ClippedSphereFormFactor( const in vec3 f ) {
	float l = length( f );
	return max( ( l * l + f.z ) / ( l + 1.0 ), 0.0 );
}
vec3 LTC_EdgeVectorFormFactor( const in vec3 v1, const in vec3 v2 ) {
	float x = dot( v1, v2 );
	float y = abs( x );
	float a = 0.8543985 + ( 0.4965155 + 0.0145206 * y ) * y;
	float b = 3.4175940 + ( 4.1616724 + y ) * y;
	float v = a / b;
	float theta_sintheta = ( x > 0.0 ) ? v : 0.5 * inversesqrt( max( 1.0 - x * x, 1e-7 ) ) - v;
	return cross( v1, v2 ) * theta_sintheta;
}
vec3 LTC_Evaluate( const in vec3 N, const in vec3 V, const in vec3 P, const in mat3 mInv, const in vec3 rectCoords[ 4 ] ) {
	vec3 v1 = rectCoords[ 1 ] - rectCoords[ 0 ];
	vec3 v2 = rectCoords[ 3 ] - rectCoords[ 0 ];
	vec3 lightNormal = cross( v1, v2 );
	if( dot( lightNormal, P - rectCoords[ 0 ] ) < 0.0 ) return vec3( 0.0 );
	vec3 T1, T2;
	T1 = normalize( V - N * dot( V, N ) );
	T2 = - cross( N, T1 );
	mat3 mat = mInv * transposeMat3( mat3( T1, T2, N ) );
	vec3 coords[ 4 ];
	coords[ 0 ] = mat * ( rectCoords[ 0 ] - P );
	coords[ 1 ] = mat * ( rectCoords[ 1 ] - P );
	coords[ 2 ] = mat * ( rectCoords[ 2 ] - P );
	coords[ 3 ] = mat * ( rectCoords[ 3 ] - P );
	coords[ 0 ] = normalize( coords[ 0 ] );
	coords[ 1 ] = normalize( coords[ 1 ] );
	coords[ 2 ] = normalize( coords[ 2 ] );
	coords[ 3 ] = normalize( coords[ 3 ] );
	vec3 vectorFormFactor = vec3( 0.0 );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 0 ], coords[ 1 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 1 ], coords[ 2 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 2 ], coords[ 3 ] );
	vectorFormFactor += LTC_EdgeVectorFormFactor( coords[ 3 ], coords[ 0 ] );
	float result = LTC_ClippedSphereFormFactor( vectorFormFactor );
	return vec3( result );
}
#if defined( USE_SHEEN )
float D_Charlie( float roughness, float dotNH ) {
	float alpha = pow2( roughness );
	float invAlpha = 1.0 / alpha;
	float cos2h = dotNH * dotNH;
	float sin2h = max( 1.0 - cos2h, 0.0078125 );
	return ( 2.0 + invAlpha ) * pow( sin2h, invAlpha * 0.5 ) / ( 2.0 * PI );
}
float V_Neubelt( float dotNV, float dotNL ) {
	return saturate( 1.0 / ( 4.0 * ( dotNL + dotNV - dotNL * dotNV ) ) );
}
vec3 BRDF_Sheen( const in vec3 lightDir, const in vec3 viewDir, const in vec3 normal, vec3 sheenColor, const in float sheenRoughness ) {
	vec3 halfDir = normalize( lightDir + viewDir );
	float dotNL = saturate( dot( normal, lightDir ) );
	float dotNV = saturate( dot( normal, viewDir ) );
	float dotNH = saturate( dot( normal, halfDir ) );
	float D = D_Charlie( sheenRoughness, dotNH );
	float V = V_Neubelt( dotNV, dotNL );
	return sheenColor * ( D * V );
}
#endif
float IBLSheenBRDF( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	float r2 = roughness * roughness;
	float a = roughness < 0.25 ? -339.2 * r2 + 161.4 * roughness - 25.9 : -8.48 * r2 + 14.3 * roughness - 9.95;
	float b = roughness < 0.25 ? 44.0 * r2 - 23.7 * roughness + 3.26 : 1.97 * r2 - 3.27 * roughness + 0.72;
	float DG = exp( a * dotNV + b ) + ( roughness < 0.25 ? 0.0 : 0.1 * ( roughness - 0.25 ) );
	return saturate( DG * RECIPROCAL_PI );
}
vec2 DFGApprox( const in vec3 normal, const in vec3 viewDir, const in float roughness ) {
	float dotNV = saturate( dot( normal, viewDir ) );
	const vec4 c0 = vec4( - 1, - 0.0275, - 0.572, 0.022 );
	const vec4 c1 = vec4( 1, 0.0425, 1.04, - 0.04 );
	vec4 r = roughness * c0 + c1;
	float a004 = min( r.x * r.x, exp2( - 9.28 * dotNV ) ) * r.x + r.y;
	vec2 fab = vec2( - 1.04, 1.04 ) * a004 + r.zw;
	return fab;
}
vec3 EnvironmentBRDF( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness ) {
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	return specularColor * fab.x + specularF90 * fab.y;
}
#ifdef USE_IRIDESCENCE
void computeMultiscatteringIridescence( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float iridescence, const in vec3 iridescenceF0, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#else
void computeMultiscattering( const in vec3 normal, const in vec3 viewDir, const in vec3 specularColor, const in float specularF90, const in float roughness, inout vec3 singleScatter, inout vec3 multiScatter ) {
#endif
	vec2 fab = DFGApprox( normal, viewDir, roughness );
	#ifdef USE_IRIDESCENCE
		vec3 Fr = mix( specularColor, iridescenceF0, iridescence );
	#else
		vec3 Fr = specularColor;
	#endif
	vec3 FssEss = Fr * fab.x + specularF90 * fab.y;
	float Ess = fab.x + fab.y;
	float Ems = 1.0 - Ess;
	vec3 Favg = Fr + ( 1.0 - Fr ) * 0.047619;	vec3 Fms = FssEss * Favg / ( 1.0 - Ems * Favg );
	singleScatter += FssEss;
	multiScatter += Fms * Ems;
}
#if NUM_RECT_AREA_LIGHTS > 0
	void RE_Direct_RectArea_Physical( const in RectAreaLight rectAreaLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
		vec3 normal = geometryNormal;
		vec3 viewDir = geometryViewDir;
		vec3 position = geometryPosition;
		vec3 lightPos = rectAreaLight.position;
		vec3 halfWidth = rectAreaLight.halfWidth;
		vec3 halfHeight = rectAreaLight.halfHeight;
		vec3 lightColor = rectAreaLight.color;
		float roughness = material.roughness;
		vec3 rectCoords[ 4 ];
		rectCoords[ 0 ] = lightPos + halfWidth - halfHeight;		rectCoords[ 1 ] = lightPos - halfWidth - halfHeight;
		rectCoords[ 2 ] = lightPos - halfWidth + halfHeight;
		rectCoords[ 3 ] = lightPos + halfWidth + halfHeight;
		vec2 uv = LTC_Uv( normal, viewDir, roughness );
		vec4 t1 = texture2D( ltc_1, uv );
		vec4 t2 = texture2D( ltc_2, uv );
		mat3 mInv = mat3(
			vec3( t1.x, 0, t1.y ),
			vec3(    0, 1,    0 ),
			vec3( t1.z, 0, t1.w )
		);
		vec3 fresnel = ( material.specularColor * t2.x + ( vec3( 1.0 ) - material.specularColor ) * t2.y );
		reflectedLight.directSpecular += lightColor * fresnel * LTC_Evaluate( normal, viewDir, position, mInv, rectCoords );
		reflectedLight.directDiffuse += lightColor * material.diffuseColor * LTC_Evaluate( normal, viewDir, position, mat3( 1.0 ), rectCoords );
	}
#endif
void RE_Direct_Physical( const in IncidentLight directLight, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	float dotNL = saturate( dot( geometryNormal, directLight.direction ) );
	vec3 irradiance = dotNL * directLight.color;
	#ifdef USE_CLEARCOAT
		float dotNLcc = saturate( dot( geometryClearcoatNormal, directLight.direction ) );
		vec3 ccIrradiance = dotNLcc * directLight.color;
		clearcoatSpecularDirect += ccIrradiance * BRDF_GGX_Clearcoat( directLight.direction, geometryViewDir, geometryClearcoatNormal, material );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularDirect += irradiance * BRDF_Sheen( directLight.direction, geometryViewDir, geometryNormal, material.sheenColor, material.sheenRoughness );
	#endif
	reflectedLight.directSpecular += irradiance * BRDF_GGX( directLight.direction, geometryViewDir, geometryNormal, material );
	reflectedLight.directDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectDiffuse_Physical( const in vec3 irradiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight ) {
	reflectedLight.indirectDiffuse += irradiance * BRDF_Lambert( material.diffuseColor );
}
void RE_IndirectSpecular_Physical( const in vec3 radiance, const in vec3 irradiance, const in vec3 clearcoatRadiance, const in vec3 geometryPosition, const in vec3 geometryNormal, const in vec3 geometryViewDir, const in vec3 geometryClearcoatNormal, const in PhysicalMaterial material, inout ReflectedLight reflectedLight) {
	#ifdef USE_CLEARCOAT
		clearcoatSpecularIndirect += clearcoatRadiance * EnvironmentBRDF( geometryClearcoatNormal, geometryViewDir, material.clearcoatF0, material.clearcoatF90, material.clearcoatRoughness );
	#endif
	#ifdef USE_SHEEN
		sheenSpecularIndirect += irradiance * material.sheenColor * IBLSheenBRDF( geometryNormal, geometryViewDir, material.sheenRoughness );
	#endif
	vec3 singleScattering = vec3( 0.0 );
	vec3 multiScattering = vec3( 0.0 );
	vec3 cosineWeightedIrradiance = irradiance * RECIPROCAL_PI;
	#ifdef USE_IRIDESCENCE
		computeMultiscatteringIridescence( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.iridescence, material.iridescenceFresnel, material.roughness, singleScattering, multiScattering );
	#else
		computeMultiscattering( geometryNormal, geometryViewDir, material.specularColor, material.specularF90, material.roughness, singleScattering, multiScattering );
	#endif
	vec3 totalScattering = singleScattering + multiScattering;
	vec3 diffuse = material.diffuseColor * ( 1.0 - max( max( totalScattering.r, totalScattering.g ), totalScattering.b ) );
	reflectedLight.indirectSpecular += radiance * singleScattering;
	reflectedLight.indirectSpecular += multiScattering * cosineWeightedIrradiance;
	reflectedLight.indirectDiffuse += diffuse * cosineWeightedIrradiance;
}
#define RE_Direct				RE_Direct_Physical
#define RE_Direct_RectArea		RE_Direct_RectArea_Physical
#define RE_IndirectDiffuse		RE_IndirectDiffuse_Physical
#define RE_IndirectSpecular		RE_IndirectSpecular_Physical
float computeSpecularOcclusion( const in float dotNV, const in float ambientOcclusion, const in float roughness ) {
	return saturate( pow( dotNV + ambientOcclusion, exp2( - 16.0 * roughness - 1.0 ) ) - 1.0 + ambientOcclusion );
}`,mv=`
vec3 geometryPosition = - vViewPosition;
vec3 geometryNormal = normal;
vec3 geometryViewDir = ( isOrthographic ) ? vec3( 0, 0, 1 ) : normalize( vViewPosition );
vec3 geometryClearcoatNormal = vec3( 0.0 );
#ifdef USE_CLEARCOAT
	geometryClearcoatNormal = clearcoatNormal;
#endif
#ifdef USE_IRIDESCENCE
	float dotNVi = saturate( dot( normal, geometryViewDir ) );
	if ( material.iridescenceThickness == 0.0 ) {
		material.iridescence = 0.0;
	} else {
		material.iridescence = saturate( material.iridescence );
	}
	if ( material.iridescence > 0.0 ) {
		material.iridescenceFresnel = evalIridescence( 1.0, material.iridescenceIOR, dotNVi, material.iridescenceThickness, material.specularColor );
		material.iridescenceF0 = Schlick_to_F0( material.iridescenceFresnel, 1.0, dotNVi );
	}
#endif
IncidentLight directLight;
#if ( NUM_POINT_LIGHTS > 0 ) && defined( RE_Direct )
	PointLight pointLight;
	#if defined( USE_SHADOWMAP ) && NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHTS; i ++ ) {
		pointLight = pointLights[ i ];
		getPointLightInfo( pointLight, geometryPosition, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_POINT_LIGHT_SHADOWS )
		pointLightShadow = pointLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getPointShadow( pointShadowMap[ i ], pointLightShadow.shadowMapSize, pointLightShadow.shadowIntensity, pointLightShadow.shadowBias, pointLightShadow.shadowRadius, vPointShadowCoord[ i ], pointLightShadow.shadowCameraNear, pointLightShadow.shadowCameraFar ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_SPOT_LIGHTS > 0 ) && defined( RE_Direct )
	SpotLight spotLight;
	vec4 spotColor;
	vec3 spotLightCoord;
	bool inSpotLightMap;
	#if defined( USE_SHADOWMAP ) && NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHTS; i ++ ) {
		spotLight = spotLights[ i ];
		getSpotLightInfo( spotLight, geometryPosition, directLight );
		#if ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#define SPOT_LIGHT_MAP_INDEX UNROLLED_LOOP_INDEX
		#elif ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		#define SPOT_LIGHT_MAP_INDEX NUM_SPOT_LIGHT_MAPS
		#else
		#define SPOT_LIGHT_MAP_INDEX ( UNROLLED_LOOP_INDEX - NUM_SPOT_LIGHT_SHADOWS + NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS )
		#endif
		#if ( SPOT_LIGHT_MAP_INDEX < NUM_SPOT_LIGHT_MAPS )
			spotLightCoord = vSpotLightCoord[ i ].xyz / vSpotLightCoord[ i ].w;
			inSpotLightMap = all( lessThan( abs( spotLightCoord * 2. - 1. ), vec3( 1.0 ) ) );
			spotColor = texture2D( spotLightMap[ SPOT_LIGHT_MAP_INDEX ], spotLightCoord.xy );
			directLight.color = inSpotLightMap ? directLight.color * spotColor.rgb : directLight.color;
		#endif
		#undef SPOT_LIGHT_MAP_INDEX
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
		spotLightShadow = spotLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( spotShadowMap[ i ], spotLightShadow.shadowMapSize, spotLightShadow.shadowIntensity, spotLightShadow.shadowBias, spotLightShadow.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_DIR_LIGHTS > 0 ) && defined( RE_Direct )
	DirectionalLight directionalLight;
	#if defined( USE_SHADOWMAP ) && NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLightShadow;
	#endif
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHTS; i ++ ) {
		directionalLight = directionalLights[ i ];
		getDirectionalLightInfo( directionalLight, directLight );
		#if defined( USE_SHADOWMAP ) && ( UNROLLED_LOOP_INDEX < NUM_DIR_LIGHT_SHADOWS )
		directionalLightShadow = directionalLightShadows[ i ];
		directLight.color *= ( directLight.visible && receiveShadow ) ? getShadow( directionalShadowMap[ i ], directionalLightShadow.shadowMapSize, directionalLightShadow.shadowIntensity, directionalLightShadow.shadowBias, directionalLightShadow.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
		#endif
		RE_Direct( directLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if ( NUM_RECT_AREA_LIGHTS > 0 ) && defined( RE_Direct_RectArea )
	RectAreaLight rectAreaLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_RECT_AREA_LIGHTS; i ++ ) {
		rectAreaLight = rectAreaLights[ i ];
		RE_Direct_RectArea( rectAreaLight, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
	}
	#pragma unroll_loop_end
#endif
#if defined( RE_IndirectDiffuse )
	vec3 iblIrradiance = vec3( 0.0 );
	vec3 irradiance = getAmbientLightIrradiance( ambientLightColor );
	#if defined( USE_LIGHT_PROBES )
		irradiance += getLightProbeIrradiance( lightProbe, geometryNormal );
	#endif
	#if ( NUM_HEMI_LIGHTS > 0 )
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_HEMI_LIGHTS; i ++ ) {
			irradiance += getHemisphereLightIrradiance( hemisphereLights[ i ], geometryNormal );
		}
		#pragma unroll_loop_end
	#endif
#endif
#if defined( RE_IndirectSpecular )
	vec3 radiance = vec3( 0.0 );
	vec3 clearcoatRadiance = vec3( 0.0 );
#endif`,_v=`#if defined( RE_IndirectDiffuse )
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		vec3 lightMapIrradiance = lightMapTexel.rgb * lightMapIntensity;
		irradiance += lightMapIrradiance;
	#endif
	#if defined( USE_ENVMAP ) && defined( STANDARD ) && defined( ENVMAP_TYPE_CUBE_UV )
		iblIrradiance += getIBLIrradiance( geometryNormal );
	#endif
#endif
#if defined( USE_ENVMAP ) && defined( RE_IndirectSpecular )
	#ifdef USE_ANISOTROPY
		radiance += getIBLAnisotropyRadiance( geometryViewDir, geometryNormal, material.roughness, material.anisotropyB, material.anisotropy );
	#else
		radiance += getIBLRadiance( geometryViewDir, geometryNormal, material.roughness );
	#endif
	#ifdef USE_CLEARCOAT
		clearcoatRadiance += getIBLRadiance( geometryViewDir, geometryClearcoatNormal, material.clearcoatRoughness );
	#endif
#endif`,gv=`#if defined( RE_IndirectDiffuse )
	RE_IndirectDiffuse( irradiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif
#if defined( RE_IndirectSpecular )
	RE_IndirectSpecular( radiance, iblIrradiance, clearcoatRadiance, geometryPosition, geometryNormal, geometryViewDir, geometryClearcoatNormal, material, reflectedLight );
#endif`,vv=`#if defined( USE_LOGDEPTHBUF )
	gl_FragDepth = vIsPerspective == 0.0 ? gl_FragCoord.z : log2( vFragDepth ) * logDepthBufFC * 0.5;
#endif`,xv=`#if defined( USE_LOGDEPTHBUF )
	uniform float logDepthBufFC;
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,Sv=`#ifdef USE_LOGDEPTHBUF
	varying float vFragDepth;
	varying float vIsPerspective;
#endif`,Mv=`#ifdef USE_LOGDEPTHBUF
	vFragDepth = 1.0 + gl_Position.w;
	vIsPerspective = float( isPerspectiveMatrix( projectionMatrix ) );
#endif`,yv=`#ifdef USE_MAP
	vec4 sampledDiffuseColor = texture2D( map, vMapUv );
	#ifdef DECODE_VIDEO_TEXTURE
		sampledDiffuseColor = vec4( mix( pow( sampledDiffuseColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), sampledDiffuseColor.rgb * 0.0773993808, vec3( lessThanEqual( sampledDiffuseColor.rgb, vec3( 0.04045 ) ) ) ), sampledDiffuseColor.w );
	
	#endif
	diffuseColor *= sampledDiffuseColor;
#endif`,Ev=`#ifdef USE_MAP
	uniform sampler2D map;
#endif`,Tv=`#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
	#if defined( USE_POINTS_UV )
		vec2 uv = vUv;
	#else
		vec2 uv = ( uvTransform * vec3( gl_PointCoord.x, 1.0 - gl_PointCoord.y, 1 ) ).xy;
	#endif
#endif
#ifdef USE_MAP
	diffuseColor *= texture2D( map, uv );
#endif
#ifdef USE_ALPHAMAP
	diffuseColor.a *= texture2D( alphaMap, uv ).g;
#endif`,bv=`#if defined( USE_POINTS_UV )
	varying vec2 vUv;
#else
	#if defined( USE_MAP ) || defined( USE_ALPHAMAP )
		uniform mat3 uvTransform;
	#endif
#endif
#ifdef USE_MAP
	uniform sampler2D map;
#endif
#ifdef USE_ALPHAMAP
	uniform sampler2D alphaMap;
#endif`,wv=`float metalnessFactor = metalness;
#ifdef USE_METALNESSMAP
	vec4 texelMetalness = texture2D( metalnessMap, vMetalnessMapUv );
	metalnessFactor *= texelMetalness.b;
#endif`,Av=`#ifdef USE_METALNESSMAP
	uniform sampler2D metalnessMap;
#endif`,Rv=`#ifdef USE_INSTANCING_MORPH
	float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	float morphTargetBaseInfluence = texelFetch( morphTexture, ivec2( 0, gl_InstanceID ), 0 ).r;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		morphTargetInfluences[i] =  texelFetch( morphTexture, ivec2( i + 1, gl_InstanceID ), 0 ).r;
	}
#endif`,Cv=`#if defined( USE_MORPHCOLORS )
	vColor *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		#if defined( USE_COLOR_ALPHA )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ) * morphTargetInfluences[ i ];
		#elif defined( USE_COLOR )
			if ( morphTargetInfluences[ i ] != 0.0 ) vColor += getMorph( gl_VertexID, i, 2 ).rgb * morphTargetInfluences[ i ];
		#endif
	}
#endif`,Pv=`#ifdef USE_MORPHNORMALS
	objectNormal *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) objectNormal += getMorph( gl_VertexID, i, 1 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,Dv=`#ifdef USE_MORPHTARGETS
	#ifndef USE_INSTANCING_MORPH
		uniform float morphTargetBaseInfluence;
		uniform float morphTargetInfluences[ MORPHTARGETS_COUNT ];
	#endif
	uniform sampler2DArray morphTargetsTexture;
	uniform ivec2 morphTargetsTextureSize;
	vec4 getMorph( const in int vertexIndex, const in int morphTargetIndex, const in int offset ) {
		int texelIndex = vertexIndex * MORPHTARGETS_TEXTURE_STRIDE + offset;
		int y = texelIndex / morphTargetsTextureSize.x;
		int x = texelIndex - y * morphTargetsTextureSize.x;
		ivec3 morphUV = ivec3( x, y, morphTargetIndex );
		return texelFetch( morphTargetsTexture, morphUV, 0 );
	}
#endif`,Lv=`#ifdef USE_MORPHTARGETS
	transformed *= morphTargetBaseInfluence;
	for ( int i = 0; i < MORPHTARGETS_COUNT; i ++ ) {
		if ( morphTargetInfluences[ i ] != 0.0 ) transformed += getMorph( gl_VertexID, i, 0 ).xyz * morphTargetInfluences[ i ];
	}
#endif`,Iv=`float faceDirection = gl_FrontFacing ? 1.0 : - 1.0;
#ifdef FLAT_SHADED
	vec3 fdx = dFdx( vViewPosition );
	vec3 fdy = dFdy( vViewPosition );
	vec3 normal = normalize( cross( fdx, fdy ) );
#else
	vec3 normal = normalize( vNormal );
	#ifdef DOUBLE_SIDED
		normal *= faceDirection;
	#endif
#endif
#if defined( USE_NORMALMAP_TANGENTSPACE ) || defined( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY )
	#ifdef USE_TANGENT
		mat3 tbn = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn = getTangentFrame( - vViewPosition, normal,
		#if defined( USE_NORMALMAP )
			vNormalMapUv
		#elif defined( USE_CLEARCOAT_NORMALMAP )
			vClearcoatNormalMapUv
		#else
			vUv
		#endif
		);
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn[0] *= faceDirection;
		tbn[1] *= faceDirection;
	#endif
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	#ifdef USE_TANGENT
		mat3 tbn2 = mat3( normalize( vTangent ), normalize( vBitangent ), normal );
	#else
		mat3 tbn2 = getTangentFrame( - vViewPosition, normal, vClearcoatNormalMapUv );
	#endif
	#if defined( DOUBLE_SIDED ) && ! defined( FLAT_SHADED )
		tbn2[0] *= faceDirection;
		tbn2[1] *= faceDirection;
	#endif
#endif
vec3 nonPerturbedNormal = normal;`,Uv=`#ifdef USE_NORMALMAP_OBJECTSPACE
	normal = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	#ifdef FLIP_SIDED
		normal = - normal;
	#endif
	#ifdef DOUBLE_SIDED
		normal = normal * faceDirection;
	#endif
	normal = normalize( normalMatrix * normal );
#elif defined( USE_NORMALMAP_TANGENTSPACE )
	vec3 mapN = texture2D( normalMap, vNormalMapUv ).xyz * 2.0 - 1.0;
	mapN.xy *= normalScale;
	normal = normalize( tbn * mapN );
#elif defined( USE_BUMPMAP )
	normal = perturbNormalArb( - vViewPosition, normal, dHdxy_fwd(), faceDirection );
#endif`,Nv=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Fv=`#ifndef FLAT_SHADED
	varying vec3 vNormal;
	#ifdef USE_TANGENT
		varying vec3 vTangent;
		varying vec3 vBitangent;
	#endif
#endif`,Ov=`#ifndef FLAT_SHADED
	vNormal = normalize( transformedNormal );
	#ifdef USE_TANGENT
		vTangent = normalize( transformedTangent );
		vBitangent = normalize( cross( vNormal, vTangent ) * tangent.w );
	#endif
#endif`,Bv=`#ifdef USE_NORMALMAP
	uniform sampler2D normalMap;
	uniform vec2 normalScale;
#endif
#ifdef USE_NORMALMAP_OBJECTSPACE
	uniform mat3 normalMatrix;
#endif
#if ! defined ( USE_TANGENT ) && ( defined ( USE_NORMALMAP_TANGENTSPACE ) || defined ( USE_CLEARCOAT_NORMALMAP ) || defined( USE_ANISOTROPY ) )
	mat3 getTangentFrame( vec3 eye_pos, vec3 surf_norm, vec2 uv ) {
		vec3 q0 = dFdx( eye_pos.xyz );
		vec3 q1 = dFdy( eye_pos.xyz );
		vec2 st0 = dFdx( uv.st );
		vec2 st1 = dFdy( uv.st );
		vec3 N = surf_norm;
		vec3 q1perp = cross( q1, N );
		vec3 q0perp = cross( N, q0 );
		vec3 T = q1perp * st0.x + q0perp * st1.x;
		vec3 B = q1perp * st0.y + q0perp * st1.y;
		float det = max( dot( T, T ), dot( B, B ) );
		float scale = ( det == 0.0 ) ? 0.0 : inversesqrt( det );
		return mat3( T * scale, B * scale, N );
	}
#endif`,zv=`#ifdef USE_CLEARCOAT
	vec3 clearcoatNormal = nonPerturbedNormal;
#endif`,kv=`#ifdef USE_CLEARCOAT_NORMALMAP
	vec3 clearcoatMapN = texture2D( clearcoatNormalMap, vClearcoatNormalMapUv ).xyz * 2.0 - 1.0;
	clearcoatMapN.xy *= clearcoatNormalScale;
	clearcoatNormal = normalize( tbn2 * clearcoatMapN );
#endif`,Hv=`#ifdef USE_CLEARCOATMAP
	uniform sampler2D clearcoatMap;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform sampler2D clearcoatNormalMap;
	uniform vec2 clearcoatNormalScale;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform sampler2D clearcoatRoughnessMap;
#endif`,Gv=`#ifdef USE_IRIDESCENCEMAP
	uniform sampler2D iridescenceMap;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform sampler2D iridescenceThicknessMap;
#endif`,Vv=`#ifdef OPAQUE
diffuseColor.a = 1.0;
#endif
#ifdef USE_TRANSMISSION
diffuseColor.a *= material.transmissionAlpha;
#endif
gl_FragColor = vec4( outgoingLight, diffuseColor.a );`,Wv=`vec3 packNormalToRGB( const in vec3 normal ) {
	return normalize( normal ) * 0.5 + 0.5;
}
vec3 unpackRGBToNormal( const in vec3 rgb ) {
	return 2.0 * rgb.xyz - 1.0;
}
const float PackUpscale = 256. / 255.;const float UnpackDownscale = 255. / 256.;const float ShiftRight8 = 1. / 256.;
const float Inv255 = 1. / 255.;
const vec4 PackFactors = vec4( 1.0, 256.0, 256.0 * 256.0, 256.0 * 256.0 * 256.0 );
const vec2 UnpackFactors2 = vec2( UnpackDownscale, 1.0 / PackFactors.g );
const vec3 UnpackFactors3 = vec3( UnpackDownscale / PackFactors.rg, 1.0 / PackFactors.b );
const vec4 UnpackFactors4 = vec4( UnpackDownscale / PackFactors.rgb, 1.0 / PackFactors.a );
vec4 packDepthToRGBA( const in float v ) {
	if( v <= 0.0 )
		return vec4( 0., 0., 0., 0. );
	if( v >= 1.0 )
		return vec4( 1., 1., 1., 1. );
	float vuf;
	float af = modf( v * PackFactors.a, vuf );
	float bf = modf( vuf * ShiftRight8, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec4( vuf * Inv255, gf * PackUpscale, bf * PackUpscale, af );
}
vec3 packDepthToRGB( const in float v ) {
	if( v <= 0.0 )
		return vec3( 0., 0., 0. );
	if( v >= 1.0 )
		return vec3( 1., 1., 1. );
	float vuf;
	float bf = modf( v * PackFactors.b, vuf );
	float gf = modf( vuf * ShiftRight8, vuf );
	return vec3( vuf * Inv255, gf * PackUpscale, bf );
}
vec2 packDepthToRG( const in float v ) {
	if( v <= 0.0 )
		return vec2( 0., 0. );
	if( v >= 1.0 )
		return vec2( 1., 1. );
	float vuf;
	float gf = modf( v * 256., vuf );
	return vec2( vuf * Inv255, gf );
}
float unpackRGBAToDepth( const in vec4 v ) {
	return dot( v, UnpackFactors4 );
}
float unpackRGBToDepth( const in vec3 v ) {
	return dot( v, UnpackFactors3 );
}
float unpackRGToDepth( const in vec2 v ) {
	return v.r * UnpackFactors2.r + v.g * UnpackFactors2.g;
}
vec4 pack2HalfToRGBA( const in vec2 v ) {
	vec4 r = vec4( v.x, fract( v.x * 255.0 ), v.y, fract( v.y * 255.0 ) );
	return vec4( r.x - r.y / 255.0, r.y, r.z - r.w / 255.0, r.w );
}
vec2 unpackRGBATo2Half( const in vec4 v ) {
	return vec2( v.x + ( v.y / 255.0 ), v.z + ( v.w / 255.0 ) );
}
float viewZToOrthographicDepth( const in float viewZ, const in float near, const in float far ) {
	return ( viewZ + near ) / ( near - far );
}
float orthographicDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return depth * ( near - far ) - near;
}
float viewZToPerspectiveDepth( const in float viewZ, const in float near, const in float far ) {
	return ( ( near + viewZ ) * far ) / ( ( far - near ) * viewZ );
}
float perspectiveDepthToViewZ( const in float depth, const in float near, const in float far ) {
	return ( near * far ) / ( ( far - near ) * depth - far );
}`,Xv=`#ifdef PREMULTIPLIED_ALPHA
	gl_FragColor.rgb *= gl_FragColor.a;
#endif`,Yv=`vec4 mvPosition = vec4( transformed, 1.0 );
#ifdef USE_BATCHING
	mvPosition = batchingMatrix * mvPosition;
#endif
#ifdef USE_INSTANCING
	mvPosition = instanceMatrix * mvPosition;
#endif
mvPosition = modelViewMatrix * mvPosition;
gl_Position = projectionMatrix * mvPosition;`,qv=`#ifdef DITHERING
	gl_FragColor.rgb = dithering( gl_FragColor.rgb );
#endif`,$v=`#ifdef DITHERING
	vec3 dithering( vec3 color ) {
		float grid_position = rand( gl_FragCoord.xy );
		vec3 dither_shift_RGB = vec3( 0.25 / 255.0, -0.25 / 255.0, 0.25 / 255.0 );
		dither_shift_RGB = mix( 2.0 * dither_shift_RGB, -2.0 * dither_shift_RGB, grid_position );
		return color + dither_shift_RGB;
	}
#endif`,Kv=`float roughnessFactor = roughness;
#ifdef USE_ROUGHNESSMAP
	vec4 texelRoughness = texture2D( roughnessMap, vRoughnessMapUv );
	roughnessFactor *= texelRoughness.g;
#endif`,Zv=`#ifdef USE_ROUGHNESSMAP
	uniform sampler2D roughnessMap;
#endif`,jv=`#if NUM_SPOT_LIGHT_COORDS > 0
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#if NUM_SPOT_LIGHT_MAPS > 0
	uniform sampler2D spotLightMap[ NUM_SPOT_LIGHT_MAPS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform sampler2D directionalShadowMap[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		uniform sampler2D spotShadowMap[ NUM_SPOT_LIGHT_SHADOWS ];
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform sampler2D pointShadowMap[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
	float texture2DCompare( sampler2D depths, vec2 uv, float compare ) {
		return step( compare, unpackRGBAToDepth( texture2D( depths, uv ) ) );
	}
	vec2 texture2DDistribution( sampler2D shadow, vec2 uv ) {
		return unpackRGBATo2Half( texture2D( shadow, uv ) );
	}
	float VSMShadow (sampler2D shadow, vec2 uv, float compare ){
		float occlusion = 1.0;
		vec2 distribution = texture2DDistribution( shadow, uv );
		float hard_shadow = step( compare , distribution.x );
		if (hard_shadow != 1.0 ) {
			float distance = compare - distribution.x ;
			float variance = max( 0.00000, distribution.y * distribution.y );
			float softness_probability = variance / (variance + distance * distance );			softness_probability = clamp( ( softness_probability - 0.3 ) / ( 0.95 - 0.3 ), 0.0, 1.0 );			occlusion = clamp( max( hard_shadow, softness_probability ), 0.0, 1.0 );
		}
		return occlusion;
	}
	float getShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord ) {
		float shadow = 1.0;
		shadowCoord.xyz /= shadowCoord.w;
		shadowCoord.z += shadowBias;
		bool inFrustum = shadowCoord.x >= 0.0 && shadowCoord.x <= 1.0 && shadowCoord.y >= 0.0 && shadowCoord.y <= 1.0;
		bool frustumTest = inFrustum && shadowCoord.z <= 1.0;
		if ( frustumTest ) {
		#if defined( SHADOWMAP_TYPE_PCF )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx0 = - texelSize.x * shadowRadius;
			float dy0 = - texelSize.y * shadowRadius;
			float dx1 = + texelSize.x * shadowRadius;
			float dy1 = + texelSize.y * shadowRadius;
			float dx2 = dx0 / 2.0;
			float dy2 = dy0 / 2.0;
			float dx3 = dx1 / 2.0;
			float dy3 = dy1 / 2.0;
			shadow = (
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy2 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx2, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx3, dy3 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( 0.0, dy1 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, shadowCoord.xy + vec2( dx1, dy1 ), shadowCoord.z )
			) * ( 1.0 / 17.0 );
		#elif defined( SHADOWMAP_TYPE_PCF_SOFT )
			vec2 texelSize = vec2( 1.0 ) / shadowMapSize;
			float dx = texelSize.x;
			float dy = texelSize.y;
			vec2 uv = shadowCoord.xy;
			vec2 f = fract( uv * shadowMapSize + 0.5 );
			uv -= f * texelSize;
			shadow = (
				texture2DCompare( shadowMap, uv, shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( dx, 0.0 ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + vec2( 0.0, dy ), shadowCoord.z ) +
				texture2DCompare( shadowMap, uv + texelSize, shadowCoord.z ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, 0.0 ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 0.0 ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( -dx, dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, dy ), shadowCoord.z ),
					 f.x ) +
				mix( texture2DCompare( shadowMap, uv + vec2( 0.0, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( 0.0, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( texture2DCompare( shadowMap, uv + vec2( dx, -dy ), shadowCoord.z ),
					 texture2DCompare( shadowMap, uv + vec2( dx, 2.0 * dy ), shadowCoord.z ),
					 f.y ) +
				mix( mix( texture2DCompare( shadowMap, uv + vec2( -dx, -dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, -dy ), shadowCoord.z ),
						  f.x ),
					 mix( texture2DCompare( shadowMap, uv + vec2( -dx, 2.0 * dy ), shadowCoord.z ),
						  texture2DCompare( shadowMap, uv + vec2( 2.0 * dx, 2.0 * dy ), shadowCoord.z ),
						  f.x ),
					 f.y )
			) * ( 1.0 / 9.0 );
		#elif defined( SHADOWMAP_TYPE_VSM )
			shadow = VSMShadow( shadowMap, shadowCoord.xy, shadowCoord.z );
		#else
			shadow = texture2DCompare( shadowMap, shadowCoord.xy, shadowCoord.z );
		#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
	vec2 cubeToUV( vec3 v, float texelSizeY ) {
		vec3 absV = abs( v );
		float scaleToCube = 1.0 / max( absV.x, max( absV.y, absV.z ) );
		absV *= scaleToCube;
		v *= scaleToCube * ( 1.0 - 2.0 * texelSizeY );
		vec2 planar = v.xy;
		float almostATexel = 1.5 * texelSizeY;
		float almostOne = 1.0 - almostATexel;
		if ( absV.z >= almostOne ) {
			if ( v.z > 0.0 )
				planar.x = 4.0 - v.x;
		} else if ( absV.x >= almostOne ) {
			float signX = sign( v.x );
			planar.x = v.z * signX + 2.0 * signX;
		} else if ( absV.y >= almostOne ) {
			float signY = sign( v.y );
			planar.x = v.x + 2.0 * signY + 2.0;
			planar.y = v.z * signY - 2.0;
		}
		return vec2( 0.125, 0.25 ) * planar + vec2( 0.375, 0.75 );
	}
	float getPointShadow( sampler2D shadowMap, vec2 shadowMapSize, float shadowIntensity, float shadowBias, float shadowRadius, vec4 shadowCoord, float shadowCameraNear, float shadowCameraFar ) {
		float shadow = 1.0;
		vec3 lightToPosition = shadowCoord.xyz;
		
		float lightToPositionLength = length( lightToPosition );
		if ( lightToPositionLength - shadowCameraFar <= 0.0 && lightToPositionLength - shadowCameraNear >= 0.0 ) {
			float dp = ( lightToPositionLength - shadowCameraNear ) / ( shadowCameraFar - shadowCameraNear );			dp += shadowBias;
			vec3 bd3D = normalize( lightToPosition );
			vec2 texelSize = vec2( 1.0 ) / ( shadowMapSize * vec2( 4.0, 2.0 ) );
			#if defined( SHADOWMAP_TYPE_PCF ) || defined( SHADOWMAP_TYPE_PCF_SOFT ) || defined( SHADOWMAP_TYPE_VSM )
				vec2 offset = vec2( - 1, 1 ) * shadowRadius * texelSize.y;
				shadow = (
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yyx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxy, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.xxx, texelSize.y ), dp ) +
					texture2DCompare( shadowMap, cubeToUV( bd3D + offset.yxx, texelSize.y ), dp )
				) * ( 1.0 / 9.0 );
			#else
				shadow = texture2DCompare( shadowMap, cubeToUV( bd3D, texelSize.y ), dp );
			#endif
		}
		return mix( 1.0, shadow, shadowIntensity );
	}
#endif`,Jv=`#if NUM_SPOT_LIGHT_COORDS > 0
	uniform mat4 spotLightMatrix[ NUM_SPOT_LIGHT_COORDS ];
	varying vec4 vSpotLightCoord[ NUM_SPOT_LIGHT_COORDS ];
#endif
#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
		uniform mat4 directionalShadowMatrix[ NUM_DIR_LIGHT_SHADOWS ];
		varying vec4 vDirectionalShadowCoord[ NUM_DIR_LIGHT_SHADOWS ];
		struct DirectionalLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform DirectionalLightShadow directionalLightShadows[ NUM_DIR_LIGHT_SHADOWS ];
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
		struct SpotLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
		};
		uniform SpotLightShadow spotLightShadows[ NUM_SPOT_LIGHT_SHADOWS ];
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		uniform mat4 pointShadowMatrix[ NUM_POINT_LIGHT_SHADOWS ];
		varying vec4 vPointShadowCoord[ NUM_POINT_LIGHT_SHADOWS ];
		struct PointLightShadow {
			float shadowIntensity;
			float shadowBias;
			float shadowNormalBias;
			float shadowRadius;
			vec2 shadowMapSize;
			float shadowCameraNear;
			float shadowCameraFar;
		};
		uniform PointLightShadow pointLightShadows[ NUM_POINT_LIGHT_SHADOWS ];
	#endif
#endif`,Qv=`#if ( defined( USE_SHADOWMAP ) && ( NUM_DIR_LIGHT_SHADOWS > 0 || NUM_POINT_LIGHT_SHADOWS > 0 ) ) || ( NUM_SPOT_LIGHT_COORDS > 0 )
	vec3 shadowWorldNormal = inverseTransformDirection( transformedNormal, viewMatrix );
	vec4 shadowWorldPosition;
#endif
#if defined( USE_SHADOWMAP )
	#if NUM_DIR_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * directionalLightShadows[ i ].shadowNormalBias, 0 );
			vDirectionalShadowCoord[ i ] = directionalShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
		#pragma unroll_loop_start
		for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
			shadowWorldPosition = worldPosition + vec4( shadowWorldNormal * pointLightShadows[ i ].shadowNormalBias, 0 );
			vPointShadowCoord[ i ] = pointShadowMatrix[ i ] * shadowWorldPosition;
		}
		#pragma unroll_loop_end
	#endif
#endif
#if NUM_SPOT_LIGHT_COORDS > 0
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_COORDS; i ++ ) {
		shadowWorldPosition = worldPosition;
		#if ( defined( USE_SHADOWMAP ) && UNROLLED_LOOP_INDEX < NUM_SPOT_LIGHT_SHADOWS )
			shadowWorldPosition.xyz += shadowWorldNormal * spotLightShadows[ i ].shadowNormalBias;
		#endif
		vSpotLightCoord[ i ] = spotLightMatrix[ i ] * shadowWorldPosition;
	}
	#pragma unroll_loop_end
#endif`,ex=`float getShadowMask() {
	float shadow = 1.0;
	#ifdef USE_SHADOWMAP
	#if NUM_DIR_LIGHT_SHADOWS > 0
	DirectionalLightShadow directionalLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_DIR_LIGHT_SHADOWS; i ++ ) {
		directionalLight = directionalLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( directionalShadowMap[ i ], directionalLight.shadowMapSize, directionalLight.shadowIntensity, directionalLight.shadowBias, directionalLight.shadowRadius, vDirectionalShadowCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_SPOT_LIGHT_SHADOWS > 0
	SpotLightShadow spotLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_SPOT_LIGHT_SHADOWS; i ++ ) {
		spotLight = spotLightShadows[ i ];
		shadow *= receiveShadow ? getShadow( spotShadowMap[ i ], spotLight.shadowMapSize, spotLight.shadowIntensity, spotLight.shadowBias, spotLight.shadowRadius, vSpotLightCoord[ i ] ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#if NUM_POINT_LIGHT_SHADOWS > 0
	PointLightShadow pointLight;
	#pragma unroll_loop_start
	for ( int i = 0; i < NUM_POINT_LIGHT_SHADOWS; i ++ ) {
		pointLight = pointLightShadows[ i ];
		shadow *= receiveShadow ? getPointShadow( pointShadowMap[ i ], pointLight.shadowMapSize, pointLight.shadowIntensity, pointLight.shadowBias, pointLight.shadowRadius, vPointShadowCoord[ i ], pointLight.shadowCameraNear, pointLight.shadowCameraFar ) : 1.0;
	}
	#pragma unroll_loop_end
	#endif
	#endif
	return shadow;
}`,tx=`#ifdef USE_SKINNING
	mat4 boneMatX = getBoneMatrix( skinIndex.x );
	mat4 boneMatY = getBoneMatrix( skinIndex.y );
	mat4 boneMatZ = getBoneMatrix( skinIndex.z );
	mat4 boneMatW = getBoneMatrix( skinIndex.w );
#endif`,nx=`#ifdef USE_SKINNING
	uniform mat4 bindMatrix;
	uniform mat4 bindMatrixInverse;
	uniform highp sampler2D boneTexture;
	mat4 getBoneMatrix( const in float i ) {
		int size = textureSize( boneTexture, 0 ).x;
		int j = int( i ) * 4;
		int x = j % size;
		int y = j / size;
		vec4 v1 = texelFetch( boneTexture, ivec2( x, y ), 0 );
		vec4 v2 = texelFetch( boneTexture, ivec2( x + 1, y ), 0 );
		vec4 v3 = texelFetch( boneTexture, ivec2( x + 2, y ), 0 );
		vec4 v4 = texelFetch( boneTexture, ivec2( x + 3, y ), 0 );
		return mat4( v1, v2, v3, v4 );
	}
#endif`,ix=`#ifdef USE_SKINNING
	vec4 skinVertex = bindMatrix * vec4( transformed, 1.0 );
	vec4 skinned = vec4( 0.0 );
	skinned += boneMatX * skinVertex * skinWeight.x;
	skinned += boneMatY * skinVertex * skinWeight.y;
	skinned += boneMatZ * skinVertex * skinWeight.z;
	skinned += boneMatW * skinVertex * skinWeight.w;
	transformed = ( bindMatrixInverse * skinned ).xyz;
#endif`,rx=`#ifdef USE_SKINNING
	mat4 skinMatrix = mat4( 0.0 );
	skinMatrix += skinWeight.x * boneMatX;
	skinMatrix += skinWeight.y * boneMatY;
	skinMatrix += skinWeight.z * boneMatZ;
	skinMatrix += skinWeight.w * boneMatW;
	skinMatrix = bindMatrixInverse * skinMatrix * bindMatrix;
	objectNormal = vec4( skinMatrix * vec4( objectNormal, 0.0 ) ).xyz;
	#ifdef USE_TANGENT
		objectTangent = vec4( skinMatrix * vec4( objectTangent, 0.0 ) ).xyz;
	#endif
#endif`,sx=`float specularStrength;
#ifdef USE_SPECULARMAP
	vec4 texelSpecular = texture2D( specularMap, vSpecularMapUv );
	specularStrength = texelSpecular.r;
#else
	specularStrength = 1.0;
#endif`,ox=`#ifdef USE_SPECULARMAP
	uniform sampler2D specularMap;
#endif`,ax=`#if defined( TONE_MAPPING )
	gl_FragColor.rgb = toneMapping( gl_FragColor.rgb );
#endif`,lx=`#ifndef saturate
#define saturate( a ) clamp( a, 0.0, 1.0 )
#endif
uniform float toneMappingExposure;
vec3 LinearToneMapping( vec3 color ) {
	return saturate( toneMappingExposure * color );
}
vec3 ReinhardToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	return saturate( color / ( vec3( 1.0 ) + color ) );
}
vec3 CineonToneMapping( vec3 color ) {
	color *= toneMappingExposure;
	color = max( vec3( 0.0 ), color - 0.004 );
	return pow( ( color * ( 6.2 * color + 0.5 ) ) / ( color * ( 6.2 * color + 1.7 ) + 0.06 ), vec3( 2.2 ) );
}
vec3 RRTAndODTFit( vec3 v ) {
	vec3 a = v * ( v + 0.0245786 ) - 0.000090537;
	vec3 b = v * ( 0.983729 * v + 0.4329510 ) + 0.238081;
	return a / b;
}
vec3 ACESFilmicToneMapping( vec3 color ) {
	const mat3 ACESInputMat = mat3(
		vec3( 0.59719, 0.07600, 0.02840 ),		vec3( 0.35458, 0.90834, 0.13383 ),
		vec3( 0.04823, 0.01566, 0.83777 )
	);
	const mat3 ACESOutputMat = mat3(
		vec3(  1.60475, -0.10208, -0.00327 ),		vec3( -0.53108,  1.10813, -0.07276 ),
		vec3( -0.07367, -0.00605,  1.07602 )
	);
	color *= toneMappingExposure / 0.6;
	color = ACESInputMat * color;
	color = RRTAndODTFit( color );
	color = ACESOutputMat * color;
	return saturate( color );
}
const mat3 LINEAR_REC2020_TO_LINEAR_SRGB = mat3(
	vec3( 1.6605, - 0.1246, - 0.0182 ),
	vec3( - 0.5876, 1.1329, - 0.1006 ),
	vec3( - 0.0728, - 0.0083, 1.1187 )
);
const mat3 LINEAR_SRGB_TO_LINEAR_REC2020 = mat3(
	vec3( 0.6274, 0.0691, 0.0164 ),
	vec3( 0.3293, 0.9195, 0.0880 ),
	vec3( 0.0433, 0.0113, 0.8956 )
);
vec3 agxDefaultContrastApprox( vec3 x ) {
	vec3 x2 = x * x;
	vec3 x4 = x2 * x2;
	return + 15.5 * x4 * x2
		- 40.14 * x4 * x
		+ 31.96 * x4
		- 6.868 * x2 * x
		+ 0.4298 * x2
		+ 0.1191 * x
		- 0.00232;
}
vec3 AgXToneMapping( vec3 color ) {
	const mat3 AgXInsetMatrix = mat3(
		vec3( 0.856627153315983, 0.137318972929847, 0.11189821299995 ),
		vec3( 0.0951212405381588, 0.761241990602591, 0.0767994186031903 ),
		vec3( 0.0482516061458583, 0.101439036467562, 0.811302368396859 )
	);
	const mat3 AgXOutsetMatrix = mat3(
		vec3( 1.1271005818144368, - 0.1413297634984383, - 0.14132976349843826 ),
		vec3( - 0.11060664309660323, 1.157823702216272, - 0.11060664309660294 ),
		vec3( - 0.016493938717834573, - 0.016493938717834257, 1.2519364065950405 )
	);
	const float AgxMinEv = - 12.47393;	const float AgxMaxEv = 4.026069;
	color *= toneMappingExposure;
	color = LINEAR_SRGB_TO_LINEAR_REC2020 * color;
	color = AgXInsetMatrix * color;
	color = max( color, 1e-10 );	color = log2( color );
	color = ( color - AgxMinEv ) / ( AgxMaxEv - AgxMinEv );
	color = clamp( color, 0.0, 1.0 );
	color = agxDefaultContrastApprox( color );
	color = AgXOutsetMatrix * color;
	color = pow( max( vec3( 0.0 ), color ), vec3( 2.2 ) );
	color = LINEAR_REC2020_TO_LINEAR_SRGB * color;
	color = clamp( color, 0.0, 1.0 );
	return color;
}
vec3 NeutralToneMapping( vec3 color ) {
	const float StartCompression = 0.8 - 0.04;
	const float Desaturation = 0.15;
	color *= toneMappingExposure;
	float x = min( color.r, min( color.g, color.b ) );
	float offset = x < 0.08 ? x - 6.25 * x * x : 0.04;
	color -= offset;
	float peak = max( color.r, max( color.g, color.b ) );
	if ( peak < StartCompression ) return color;
	float d = 1. - StartCompression;
	float newPeak = 1. - d * d / ( peak + d - StartCompression );
	color *= newPeak / peak;
	float g = 1. - 1. / ( Desaturation * ( peak - newPeak ) + 1. );
	return mix( color, vec3( newPeak ), g );
}
vec3 CustomToneMapping( vec3 color ) { return color; }`,cx=`#ifdef USE_TRANSMISSION
	material.transmission = transmission;
	material.transmissionAlpha = 1.0;
	material.thickness = thickness;
	material.attenuationDistance = attenuationDistance;
	material.attenuationColor = attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		material.transmission *= texture2D( transmissionMap, vTransmissionMapUv ).r;
	#endif
	#ifdef USE_THICKNESSMAP
		material.thickness *= texture2D( thicknessMap, vThicknessMapUv ).g;
	#endif
	vec3 pos = vWorldPosition;
	vec3 v = normalize( cameraPosition - pos );
	vec3 n = inverseTransformDirection( normal, viewMatrix );
	vec4 transmitted = getIBLVolumeRefraction(
		n, v, material.roughness, material.diffuseColor, material.specularColor, material.specularF90,
		pos, modelMatrix, viewMatrix, projectionMatrix, material.dispersion, material.ior, material.thickness,
		material.attenuationColor, material.attenuationDistance );
	material.transmissionAlpha = mix( material.transmissionAlpha, transmitted.a, material.transmission );
	totalDiffuse = mix( totalDiffuse, transmitted.rgb, material.transmission );
#endif`,ux=`#ifdef USE_TRANSMISSION
	uniform float transmission;
	uniform float thickness;
	uniform float attenuationDistance;
	uniform vec3 attenuationColor;
	#ifdef USE_TRANSMISSIONMAP
		uniform sampler2D transmissionMap;
	#endif
	#ifdef USE_THICKNESSMAP
		uniform sampler2D thicknessMap;
	#endif
	uniform vec2 transmissionSamplerSize;
	uniform sampler2D transmissionSamplerMap;
	uniform mat4 modelMatrix;
	uniform mat4 projectionMatrix;
	varying vec3 vWorldPosition;
	float w0( float a ) {
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - a + 3.0 ) - 3.0 ) + 1.0 );
	}
	float w1( float a ) {
		return ( 1.0 / 6.0 ) * ( a *  a * ( 3.0 * a - 6.0 ) + 4.0 );
	}
	float w2( float a ){
		return ( 1.0 / 6.0 ) * ( a * ( a * ( - 3.0 * a + 3.0 ) + 3.0 ) + 1.0 );
	}
	float w3( float a ) {
		return ( 1.0 / 6.0 ) * ( a * a * a );
	}
	float g0( float a ) {
		return w0( a ) + w1( a );
	}
	float g1( float a ) {
		return w2( a ) + w3( a );
	}
	float h0( float a ) {
		return - 1.0 + w1( a ) / ( w0( a ) + w1( a ) );
	}
	float h1( float a ) {
		return 1.0 + w3( a ) / ( w2( a ) + w3( a ) );
	}
	vec4 bicubic( sampler2D tex, vec2 uv, vec4 texelSize, float lod ) {
		uv = uv * texelSize.zw + 0.5;
		vec2 iuv = floor( uv );
		vec2 fuv = fract( uv );
		float g0x = g0( fuv.x );
		float g1x = g1( fuv.x );
		float h0x = h0( fuv.x );
		float h1x = h1( fuv.x );
		float h0y = h0( fuv.y );
		float h1y = h1( fuv.y );
		vec2 p0 = ( vec2( iuv.x + h0x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p1 = ( vec2( iuv.x + h1x, iuv.y + h0y ) - 0.5 ) * texelSize.xy;
		vec2 p2 = ( vec2( iuv.x + h0x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		vec2 p3 = ( vec2( iuv.x + h1x, iuv.y + h1y ) - 0.5 ) * texelSize.xy;
		return g0( fuv.y ) * ( g0x * textureLod( tex, p0, lod ) + g1x * textureLod( tex, p1, lod ) ) +
			g1( fuv.y ) * ( g0x * textureLod( tex, p2, lod ) + g1x * textureLod( tex, p3, lod ) );
	}
	vec4 textureBicubic( sampler2D sampler, vec2 uv, float lod ) {
		vec2 fLodSize = vec2( textureSize( sampler, int( lod ) ) );
		vec2 cLodSize = vec2( textureSize( sampler, int( lod + 1.0 ) ) );
		vec2 fLodSizeInv = 1.0 / fLodSize;
		vec2 cLodSizeInv = 1.0 / cLodSize;
		vec4 fSample = bicubic( sampler, uv, vec4( fLodSizeInv, fLodSize ), floor( lod ) );
		vec4 cSample = bicubic( sampler, uv, vec4( cLodSizeInv, cLodSize ), ceil( lod ) );
		return mix( fSample, cSample, fract( lod ) );
	}
	vec3 getVolumeTransmissionRay( const in vec3 n, const in vec3 v, const in float thickness, const in float ior, const in mat4 modelMatrix ) {
		vec3 refractionVector = refract( - v, normalize( n ), 1.0 / ior );
		vec3 modelScale;
		modelScale.x = length( vec3( modelMatrix[ 0 ].xyz ) );
		modelScale.y = length( vec3( modelMatrix[ 1 ].xyz ) );
		modelScale.z = length( vec3( modelMatrix[ 2 ].xyz ) );
		return normalize( refractionVector ) * thickness * modelScale;
	}
	float applyIorToRoughness( const in float roughness, const in float ior ) {
		return roughness * clamp( ior * 2.0 - 2.0, 0.0, 1.0 );
	}
	vec4 getTransmissionSample( const in vec2 fragCoord, const in float roughness, const in float ior ) {
		float lod = log2( transmissionSamplerSize.x ) * applyIorToRoughness( roughness, ior );
		return textureBicubic( transmissionSamplerMap, fragCoord.xy, lod );
	}
	vec3 volumeAttenuation( const in float transmissionDistance, const in vec3 attenuationColor, const in float attenuationDistance ) {
		if ( isinf( attenuationDistance ) ) {
			return vec3( 1.0 );
		} else {
			vec3 attenuationCoefficient = -log( attenuationColor ) / attenuationDistance;
			vec3 transmittance = exp( - attenuationCoefficient * transmissionDistance );			return transmittance;
		}
	}
	vec4 getIBLVolumeRefraction( const in vec3 n, const in vec3 v, const in float roughness, const in vec3 diffuseColor,
		const in vec3 specularColor, const in float specularF90, const in vec3 position, const in mat4 modelMatrix,
		const in mat4 viewMatrix, const in mat4 projMatrix, const in float dispersion, const in float ior, const in float thickness,
		const in vec3 attenuationColor, const in float attenuationDistance ) {
		vec4 transmittedLight;
		vec3 transmittance;
		#ifdef USE_DISPERSION
			float halfSpread = ( ior - 1.0 ) * 0.025 * dispersion;
			vec3 iors = vec3( ior - halfSpread, ior, ior + halfSpread );
			for ( int i = 0; i < 3; i ++ ) {
				vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, iors[ i ], modelMatrix );
				vec3 refractedRayExit = position + transmissionRay;
		
				vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
				vec2 refractionCoords = ndcPos.xy / ndcPos.w;
				refractionCoords += 1.0;
				refractionCoords /= 2.0;
		
				vec4 transmissionSample = getTransmissionSample( refractionCoords, roughness, iors[ i ] );
				transmittedLight[ i ] = transmissionSample[ i ];
				transmittedLight.a += transmissionSample.a;
				transmittance[ i ] = diffuseColor[ i ] * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance )[ i ];
			}
			transmittedLight.a /= 3.0;
		
		#else
		
			vec3 transmissionRay = getVolumeTransmissionRay( n, v, thickness, ior, modelMatrix );
			vec3 refractedRayExit = position + transmissionRay;
			vec4 ndcPos = projMatrix * viewMatrix * vec4( refractedRayExit, 1.0 );
			vec2 refractionCoords = ndcPos.xy / ndcPos.w;
			refractionCoords += 1.0;
			refractionCoords /= 2.0;
			transmittedLight = getTransmissionSample( refractionCoords, roughness, ior );
			transmittance = diffuseColor * volumeAttenuation( length( transmissionRay ), attenuationColor, attenuationDistance );
		
		#endif
		vec3 attenuatedColor = transmittance * transmittedLight.rgb;
		vec3 F = EnvironmentBRDF( n, v, specularColor, specularF90, roughness );
		float transmittanceFactor = ( transmittance.r + transmittance.g + transmittance.b ) / 3.0;
		return vec4( ( 1.0 - F ) * attenuatedColor, 1.0 - ( 1.0 - transmittedLight.a ) * transmittanceFactor );
	}
#endif`,hx=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_SPECULARMAP
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,fx=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	varying vec2 vUv;
#endif
#ifdef USE_MAP
	uniform mat3 mapTransform;
	varying vec2 vMapUv;
#endif
#ifdef USE_ALPHAMAP
	uniform mat3 alphaMapTransform;
	varying vec2 vAlphaMapUv;
#endif
#ifdef USE_LIGHTMAP
	uniform mat3 lightMapTransform;
	varying vec2 vLightMapUv;
#endif
#ifdef USE_AOMAP
	uniform mat3 aoMapTransform;
	varying vec2 vAoMapUv;
#endif
#ifdef USE_BUMPMAP
	uniform mat3 bumpMapTransform;
	varying vec2 vBumpMapUv;
#endif
#ifdef USE_NORMALMAP
	uniform mat3 normalMapTransform;
	varying vec2 vNormalMapUv;
#endif
#ifdef USE_DISPLACEMENTMAP
	uniform mat3 displacementMapTransform;
	varying vec2 vDisplacementMapUv;
#endif
#ifdef USE_EMISSIVEMAP
	uniform mat3 emissiveMapTransform;
	varying vec2 vEmissiveMapUv;
#endif
#ifdef USE_METALNESSMAP
	uniform mat3 metalnessMapTransform;
	varying vec2 vMetalnessMapUv;
#endif
#ifdef USE_ROUGHNESSMAP
	uniform mat3 roughnessMapTransform;
	varying vec2 vRoughnessMapUv;
#endif
#ifdef USE_ANISOTROPYMAP
	uniform mat3 anisotropyMapTransform;
	varying vec2 vAnisotropyMapUv;
#endif
#ifdef USE_CLEARCOATMAP
	uniform mat3 clearcoatMapTransform;
	varying vec2 vClearcoatMapUv;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	uniform mat3 clearcoatNormalMapTransform;
	varying vec2 vClearcoatNormalMapUv;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	uniform mat3 clearcoatRoughnessMapTransform;
	varying vec2 vClearcoatRoughnessMapUv;
#endif
#ifdef USE_SHEEN_COLORMAP
	uniform mat3 sheenColorMapTransform;
	varying vec2 vSheenColorMapUv;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	uniform mat3 sheenRoughnessMapTransform;
	varying vec2 vSheenRoughnessMapUv;
#endif
#ifdef USE_IRIDESCENCEMAP
	uniform mat3 iridescenceMapTransform;
	varying vec2 vIridescenceMapUv;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	uniform mat3 iridescenceThicknessMapTransform;
	varying vec2 vIridescenceThicknessMapUv;
#endif
#ifdef USE_SPECULARMAP
	uniform mat3 specularMapTransform;
	varying vec2 vSpecularMapUv;
#endif
#ifdef USE_SPECULAR_COLORMAP
	uniform mat3 specularColorMapTransform;
	varying vec2 vSpecularColorMapUv;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	uniform mat3 specularIntensityMapTransform;
	varying vec2 vSpecularIntensityMapUv;
#endif
#ifdef USE_TRANSMISSIONMAP
	uniform mat3 transmissionMapTransform;
	varying vec2 vTransmissionMapUv;
#endif
#ifdef USE_THICKNESSMAP
	uniform mat3 thicknessMapTransform;
	varying vec2 vThicknessMapUv;
#endif`,dx=`#if defined( USE_UV ) || defined( USE_ANISOTROPY )
	vUv = vec3( uv, 1 ).xy;
#endif
#ifdef USE_MAP
	vMapUv = ( mapTransform * vec3( MAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ALPHAMAP
	vAlphaMapUv = ( alphaMapTransform * vec3( ALPHAMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_LIGHTMAP
	vLightMapUv = ( lightMapTransform * vec3( LIGHTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_AOMAP
	vAoMapUv = ( aoMapTransform * vec3( AOMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_BUMPMAP
	vBumpMapUv = ( bumpMapTransform * vec3( BUMPMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_NORMALMAP
	vNormalMapUv = ( normalMapTransform * vec3( NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_DISPLACEMENTMAP
	vDisplacementMapUv = ( displacementMapTransform * vec3( DISPLACEMENTMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_EMISSIVEMAP
	vEmissiveMapUv = ( emissiveMapTransform * vec3( EMISSIVEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_METALNESSMAP
	vMetalnessMapUv = ( metalnessMapTransform * vec3( METALNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ROUGHNESSMAP
	vRoughnessMapUv = ( roughnessMapTransform * vec3( ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_ANISOTROPYMAP
	vAnisotropyMapUv = ( anisotropyMapTransform * vec3( ANISOTROPYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOATMAP
	vClearcoatMapUv = ( clearcoatMapTransform * vec3( CLEARCOATMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_NORMALMAP
	vClearcoatNormalMapUv = ( clearcoatNormalMapTransform * vec3( CLEARCOAT_NORMALMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_CLEARCOAT_ROUGHNESSMAP
	vClearcoatRoughnessMapUv = ( clearcoatRoughnessMapTransform * vec3( CLEARCOAT_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCEMAP
	vIridescenceMapUv = ( iridescenceMapTransform * vec3( IRIDESCENCEMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_IRIDESCENCE_THICKNESSMAP
	vIridescenceThicknessMapUv = ( iridescenceThicknessMapTransform * vec3( IRIDESCENCE_THICKNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_COLORMAP
	vSheenColorMapUv = ( sheenColorMapTransform * vec3( SHEEN_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SHEEN_ROUGHNESSMAP
	vSheenRoughnessMapUv = ( sheenRoughnessMapTransform * vec3( SHEEN_ROUGHNESSMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULARMAP
	vSpecularMapUv = ( specularMapTransform * vec3( SPECULARMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_COLORMAP
	vSpecularColorMapUv = ( specularColorMapTransform * vec3( SPECULAR_COLORMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_SPECULAR_INTENSITYMAP
	vSpecularIntensityMapUv = ( specularIntensityMapTransform * vec3( SPECULAR_INTENSITYMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_TRANSMISSIONMAP
	vTransmissionMapUv = ( transmissionMapTransform * vec3( TRANSMISSIONMAP_UV, 1 ) ).xy;
#endif
#ifdef USE_THICKNESSMAP
	vThicknessMapUv = ( thicknessMapTransform * vec3( THICKNESSMAP_UV, 1 ) ).xy;
#endif`,px=`#if defined( USE_ENVMAP ) || defined( DISTANCE ) || defined ( USE_SHADOWMAP ) || defined ( USE_TRANSMISSION ) || NUM_SPOT_LIGHT_COORDS > 0
	vec4 worldPosition = vec4( transformed, 1.0 );
	#ifdef USE_BATCHING
		worldPosition = batchingMatrix * worldPosition;
	#endif
	#ifdef USE_INSTANCING
		worldPosition = instanceMatrix * worldPosition;
	#endif
	worldPosition = modelMatrix * worldPosition;
#endif`;const mx=`varying vec2 vUv;
uniform mat3 uvTransform;
void main() {
	vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	gl_Position = vec4( position.xy, 1.0, 1.0 );
}`,_x=`uniform sampler2D t2D;
uniform float backgroundIntensity;
varying vec2 vUv;
void main() {
	vec4 texColor = texture2D( t2D, vUv );
	#ifdef DECODE_VIDEO_TEXTURE
		texColor = vec4( mix( pow( texColor.rgb * 0.9478672986 + vec3( 0.0521327014 ), vec3( 2.4 ) ), texColor.rgb * 0.0773993808, vec3( lessThanEqual( texColor.rgb, vec3( 0.04045 ) ) ) ), texColor.w );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,gx=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,vx=`#ifdef ENVMAP_TYPE_CUBE
	uniform samplerCube envMap;
#elif defined( ENVMAP_TYPE_CUBE_UV )
	uniform sampler2D envMap;
#endif
uniform float flipEnvMap;
uniform float backgroundBlurriness;
uniform float backgroundIntensity;
uniform mat3 backgroundRotation;
varying vec3 vWorldDirection;
#include <cube_uv_reflection_fragment>
void main() {
	#ifdef ENVMAP_TYPE_CUBE
		vec4 texColor = textureCube( envMap, backgroundRotation * vec3( flipEnvMap * vWorldDirection.x, vWorldDirection.yz ) );
	#elif defined( ENVMAP_TYPE_CUBE_UV )
		vec4 texColor = textureCubeUV( envMap, backgroundRotation * vWorldDirection, backgroundBlurriness );
	#else
		vec4 texColor = vec4( 0.0, 0.0, 0.0, 1.0 );
	#endif
	texColor.rgb *= backgroundIntensity;
	gl_FragColor = texColor;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,xx=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
	gl_Position.z = gl_Position.w;
}`,Sx=`uniform samplerCube tCube;
uniform float tFlip;
uniform float opacity;
varying vec3 vWorldDirection;
void main() {
	vec4 texColor = textureCube( tCube, vec3( tFlip * vWorldDirection.x, vWorldDirection.yz ) );
	gl_FragColor = texColor;
	gl_FragColor.a *= opacity;
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Mx=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
varying vec2 vHighPrecisionZW;
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vHighPrecisionZW = gl_Position.zw;
}`,yx=`#if DEPTH_PACKING == 3200
	uniform float opacity;
#endif
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
varying vec2 vHighPrecisionZW;
void main() {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#if DEPTH_PACKING == 3200
		diffuseColor.a = opacity;
	#endif
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <logdepthbuf_fragment>
	float fragCoordZ = 0.5 * vHighPrecisionZW[0] / vHighPrecisionZW[1] + 0.5;
	#if DEPTH_PACKING == 3200
		gl_FragColor = vec4( vec3( 1.0 - fragCoordZ ), opacity );
	#elif DEPTH_PACKING == 3201
		gl_FragColor = packDepthToRGBA( fragCoordZ );
	#elif DEPTH_PACKING == 3202
		gl_FragColor = vec4( packDepthToRGB( fragCoordZ ), 1.0 );
	#elif DEPTH_PACKING == 3203
		gl_FragColor = vec4( packDepthToRG( fragCoordZ ), 0.0, 1.0 );
	#endif
}`,Ex=`#define DISTANCE
varying vec3 vWorldPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <skinbase_vertex>
	#include <morphinstance_vertex>
	#ifdef USE_DISPLACEMENTMAP
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <worldpos_vertex>
	#include <clipping_planes_vertex>
	vWorldPosition = worldPosition.xyz;
}`,Tx=`#define DISTANCE
uniform vec3 referencePosition;
uniform float nearDistance;
uniform float farDistance;
varying vec3 vWorldPosition;
#include <common>
#include <packing>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <clipping_planes_pars_fragment>
void main () {
	vec4 diffuseColor = vec4( 1.0 );
	#include <clipping_planes_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	float dist = length( vWorldPosition - referencePosition );
	dist = ( dist - nearDistance ) / ( farDistance - nearDistance );
	dist = saturate( dist );
	gl_FragColor = packDepthToRGBA( dist );
}`,bx=`varying vec3 vWorldDirection;
#include <common>
void main() {
	vWorldDirection = transformDirection( position, modelMatrix );
	#include <begin_vertex>
	#include <project_vertex>
}`,wx=`uniform sampler2D tEquirect;
varying vec3 vWorldDirection;
#include <common>
void main() {
	vec3 direction = normalize( vWorldDirection );
	vec2 sampleUV = equirectUv( direction );
	gl_FragColor = texture2D( tEquirect, sampleUV );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
}`,Ax=`uniform float scale;
attribute float lineDistance;
varying float vLineDistance;
#include <common>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	vLineDistance = scale * lineDistance;
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,Rx=`uniform vec3 diffuse;
uniform float opacity;
uniform float dashSize;
uniform float totalSize;
varying float vLineDistance;
#include <common>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	if ( mod( vLineDistance, totalSize ) > dashSize ) {
		discard;
	}
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Cx=`#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#if defined ( USE_ENVMAP ) || defined ( USE_SKINNING )
		#include <beginnormal_vertex>
		#include <morphnormal_vertex>
		#include <skinbase_vertex>
		#include <skinnormal_vertex>
		#include <defaultnormal_vertex>
	#endif
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <fog_vertex>
}`,Px=`uniform vec3 diffuse;
uniform float opacity;
#ifndef FLAT_SHADED
	varying vec3 vNormal;
#endif
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	#ifdef USE_LIGHTMAP
		vec4 lightMapTexel = texture2D( lightMap, vLightMapUv );
		reflectedLight.indirectDiffuse += lightMapTexel.rgb * lightMapIntensity * RECIPROCAL_PI;
	#else
		reflectedLight.indirectDiffuse += vec3( 1.0 );
	#endif
	#include <aomap_fragment>
	reflectedLight.indirectDiffuse *= diffuseColor.rgb;
	vec3 outgoingLight = reflectedLight.indirectDiffuse;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Dx=`#define LAMBERT
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Lx=`#define LAMBERT
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_lambert_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_lambert_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Ix=`#define MATCAP
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <color_pars_vertex>
#include <displacementmap_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
	vViewPosition = - mvPosition.xyz;
}`,Ux=`#define MATCAP
uniform vec3 diffuse;
uniform float opacity;
uniform sampler2D matcap;
varying vec3 vViewPosition;
#include <common>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	vec3 viewDir = normalize( vViewPosition );
	vec3 x = normalize( vec3( viewDir.z, 0.0, - viewDir.x ) );
	vec3 y = cross( viewDir, x );
	vec2 uv = vec2( dot( x, normal ), dot( y, normal ) ) * 0.495 + 0.5;
	#ifdef USE_MATCAP
		vec4 matcapColor = texture2D( matcap, uv );
	#else
		vec4 matcapColor = vec4( vec3( mix( 0.2, 0.8, uv.y ) ), 1.0 );
	#endif
	vec3 outgoingLight = diffuseColor.rgb * matcapColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Nx=`#define NORMAL
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	vViewPosition = - mvPosition.xyz;
#endif
}`,Fx=`#define NORMAL
uniform float opacity;
#if defined( FLAT_SHADED ) || defined( USE_BUMPMAP ) || defined( USE_NORMALMAP_TANGENTSPACE )
	varying vec3 vViewPosition;
#endif
#include <packing>
#include <uv_pars_fragment>
#include <normal_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( 0.0, 0.0, 0.0, opacity );
	#include <clipping_planes_fragment>
	#include <logdepthbuf_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	gl_FragColor = vec4( packNormalToRGB( normal ), diffuseColor.a );
	#ifdef OPAQUE
		gl_FragColor.a = 1.0;
	#endif
}`,Ox=`#define PHONG
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <envmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <envmap_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Bx=`#define PHONG
uniform vec3 diffuse;
uniform vec3 emissive;
uniform vec3 specular;
uniform float shininess;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_phong_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <specularmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <specularmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_phong_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + reflectedLight.directSpecular + reflectedLight.indirectSpecular + totalEmissiveRadiance;
	#include <envmap_fragment>
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,zx=`#define STANDARD
varying vec3 vViewPosition;
#ifdef USE_TRANSMISSION
	varying vec3 vWorldPosition;
#endif
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
#ifdef USE_TRANSMISSION
	vWorldPosition = worldPosition.xyz;
#endif
}`,kx=`#define STANDARD
#ifdef PHYSICAL
	#define IOR
	#define USE_SPECULAR
#endif
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float roughness;
uniform float metalness;
uniform float opacity;
#ifdef IOR
	uniform float ior;
#endif
#ifdef USE_SPECULAR
	uniform float specularIntensity;
	uniform vec3 specularColor;
	#ifdef USE_SPECULAR_COLORMAP
		uniform sampler2D specularColorMap;
	#endif
	#ifdef USE_SPECULAR_INTENSITYMAP
		uniform sampler2D specularIntensityMap;
	#endif
#endif
#ifdef USE_CLEARCOAT
	uniform float clearcoat;
	uniform float clearcoatRoughness;
#endif
#ifdef USE_DISPERSION
	uniform float dispersion;
#endif
#ifdef USE_IRIDESCENCE
	uniform float iridescence;
	uniform float iridescenceIOR;
	uniform float iridescenceThicknessMinimum;
	uniform float iridescenceThicknessMaximum;
#endif
#ifdef USE_SHEEN
	uniform vec3 sheenColor;
	uniform float sheenRoughness;
	#ifdef USE_SHEEN_COLORMAP
		uniform sampler2D sheenColorMap;
	#endif
	#ifdef USE_SHEEN_ROUGHNESSMAP
		uniform sampler2D sheenRoughnessMap;
	#endif
#endif
#ifdef USE_ANISOTROPY
	uniform vec2 anisotropyVector;
	#ifdef USE_ANISOTROPYMAP
		uniform sampler2D anisotropyMap;
	#endif
#endif
varying vec3 vViewPosition;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <iridescence_fragment>
#include <cube_uv_reflection_fragment>
#include <envmap_common_pars_fragment>
#include <envmap_physical_pars_fragment>
#include <fog_pars_fragment>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_physical_pars_fragment>
#include <transmission_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <clearcoat_pars_fragment>
#include <iridescence_pars_fragment>
#include <roughnessmap_pars_fragment>
#include <metalnessmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <roughnessmap_fragment>
	#include <metalnessmap_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <clearcoat_normal_fragment_begin>
	#include <clearcoat_normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_physical_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 totalDiffuse = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse;
	vec3 totalSpecular = reflectedLight.directSpecular + reflectedLight.indirectSpecular;
	#include <transmission_fragment>
	vec3 outgoingLight = totalDiffuse + totalSpecular + totalEmissiveRadiance;
	#ifdef USE_SHEEN
		float sheenEnergyComp = 1.0 - 0.157 * max3( material.sheenColor );
		outgoingLight = outgoingLight * sheenEnergyComp + sheenSpecularDirect + sheenSpecularIndirect;
	#endif
	#ifdef USE_CLEARCOAT
		float dotNVcc = saturate( dot( geometryClearcoatNormal, geometryViewDir ) );
		vec3 Fcc = F_Schlick( material.clearcoatF0, material.clearcoatF90, dotNVcc );
		outgoingLight = outgoingLight * ( 1.0 - material.clearcoat * Fcc ) + ( clearcoatSpecularDirect + clearcoatSpecularIndirect ) * material.clearcoat;
	#endif
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Hx=`#define TOON
varying vec3 vViewPosition;
#include <common>
#include <batching_pars_vertex>
#include <uv_pars_vertex>
#include <displacementmap_pars_vertex>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <normal_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <shadowmap_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <normal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <displacementmap_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	vViewPosition = - mvPosition.xyz;
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Gx=`#define TOON
uniform vec3 diffuse;
uniform vec3 emissive;
uniform float opacity;
#include <common>
#include <packing>
#include <dithering_pars_fragment>
#include <color_pars_fragment>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <aomap_pars_fragment>
#include <lightmap_pars_fragment>
#include <emissivemap_pars_fragment>
#include <gradientmap_pars_fragment>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <normal_pars_fragment>
#include <lights_toon_pars_fragment>
#include <shadowmap_pars_fragment>
#include <bumpmap_pars_fragment>
#include <normalmap_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	ReflectedLight reflectedLight = ReflectedLight( vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ), vec3( 0.0 ) );
	vec3 totalEmissiveRadiance = emissive;
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <color_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	#include <normal_fragment_begin>
	#include <normal_fragment_maps>
	#include <emissivemap_fragment>
	#include <lights_toon_fragment>
	#include <lights_fragment_begin>
	#include <lights_fragment_maps>
	#include <lights_fragment_end>
	#include <aomap_fragment>
	vec3 outgoingLight = reflectedLight.directDiffuse + reflectedLight.indirectDiffuse + totalEmissiveRadiance;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
	#include <dithering_fragment>
}`,Vx=`uniform float size;
uniform float scale;
#include <common>
#include <color_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
#ifdef USE_POINTS_UV
	varying vec2 vUv;
	uniform mat3 uvTransform;
#endif
void main() {
	#ifdef USE_POINTS_UV
		vUv = ( uvTransform * vec3( uv, 1 ) ).xy;
	#endif
	#include <color_vertex>
	#include <morphinstance_vertex>
	#include <morphcolor_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <project_vertex>
	gl_PointSize = size;
	#ifdef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) gl_PointSize *= ( scale / - mvPosition.z );
	#endif
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <worldpos_vertex>
	#include <fog_vertex>
}`,Wx=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <color_pars_fragment>
#include <map_particle_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_particle_fragment>
	#include <color_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
	#include <premultiplied_alpha_fragment>
}`,Xx=`#include <common>
#include <batching_pars_vertex>
#include <fog_pars_vertex>
#include <morphtarget_pars_vertex>
#include <skinning_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <shadowmap_pars_vertex>
void main() {
	#include <batching_vertex>
	#include <beginnormal_vertex>
	#include <morphinstance_vertex>
	#include <morphnormal_vertex>
	#include <skinbase_vertex>
	#include <skinnormal_vertex>
	#include <defaultnormal_vertex>
	#include <begin_vertex>
	#include <morphtarget_vertex>
	#include <skinning_vertex>
	#include <project_vertex>
	#include <logdepthbuf_vertex>
	#include <worldpos_vertex>
	#include <shadowmap_vertex>
	#include <fog_vertex>
}`,Yx=`uniform vec3 color;
uniform float opacity;
#include <common>
#include <packing>
#include <fog_pars_fragment>
#include <bsdfs>
#include <lights_pars_begin>
#include <logdepthbuf_pars_fragment>
#include <shadowmap_pars_fragment>
#include <shadowmask_pars_fragment>
void main() {
	#include <logdepthbuf_fragment>
	gl_FragColor = vec4( color, opacity * ( 1.0 - getShadowMask() ) );
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,qx=`uniform float rotation;
uniform vec2 center;
#include <common>
#include <uv_pars_vertex>
#include <fog_pars_vertex>
#include <logdepthbuf_pars_vertex>
#include <clipping_planes_pars_vertex>
void main() {
	#include <uv_vertex>
	vec4 mvPosition = modelViewMatrix[ 3 ];
	vec2 scale = vec2( length( modelMatrix[ 0 ].xyz ), length( modelMatrix[ 1 ].xyz ) );
	#ifndef USE_SIZEATTENUATION
		bool isPerspective = isPerspectiveMatrix( projectionMatrix );
		if ( isPerspective ) scale *= - mvPosition.z;
	#endif
	vec2 alignedPosition = ( position.xy - ( center - vec2( 0.5 ) ) ) * scale;
	vec2 rotatedPosition;
	rotatedPosition.x = cos( rotation ) * alignedPosition.x - sin( rotation ) * alignedPosition.y;
	rotatedPosition.y = sin( rotation ) * alignedPosition.x + cos( rotation ) * alignedPosition.y;
	mvPosition.xy += rotatedPosition;
	gl_Position = projectionMatrix * mvPosition;
	#include <logdepthbuf_vertex>
	#include <clipping_planes_vertex>
	#include <fog_vertex>
}`,$x=`uniform vec3 diffuse;
uniform float opacity;
#include <common>
#include <uv_pars_fragment>
#include <map_pars_fragment>
#include <alphamap_pars_fragment>
#include <alphatest_pars_fragment>
#include <alphahash_pars_fragment>
#include <fog_pars_fragment>
#include <logdepthbuf_pars_fragment>
#include <clipping_planes_pars_fragment>
void main() {
	vec4 diffuseColor = vec4( diffuse, opacity );
	#include <clipping_planes_fragment>
	vec3 outgoingLight = vec3( 0.0 );
	#include <logdepthbuf_fragment>
	#include <map_fragment>
	#include <alphamap_fragment>
	#include <alphatest_fragment>
	#include <alphahash_fragment>
	outgoingLight = diffuseColor.rgb;
	#include <opaque_fragment>
	#include <tonemapping_fragment>
	#include <colorspace_fragment>
	#include <fog_fragment>
}`,$e={alphahash_fragment:_0,alphahash_pars_fragment:g0,alphamap_fragment:v0,alphamap_pars_fragment:x0,alphatest_fragment:S0,alphatest_pars_fragment:M0,aomap_fragment:y0,aomap_pars_fragment:E0,batching_pars_vertex:T0,batching_vertex:b0,begin_vertex:w0,beginnormal_vertex:A0,bsdfs:R0,iridescence_fragment:C0,bumpmap_pars_fragment:P0,clipping_planes_fragment:D0,clipping_planes_pars_fragment:L0,clipping_planes_pars_vertex:I0,clipping_planes_vertex:U0,color_fragment:N0,color_pars_fragment:F0,color_pars_vertex:O0,color_vertex:B0,common:z0,cube_uv_reflection_fragment:k0,defaultnormal_vertex:H0,displacementmap_pars_vertex:G0,displacementmap_vertex:V0,emissivemap_fragment:W0,emissivemap_pars_fragment:X0,colorspace_fragment:Y0,colorspace_pars_fragment:q0,envmap_fragment:$0,envmap_common_pars_fragment:K0,envmap_pars_fragment:Z0,envmap_pars_vertex:j0,envmap_physical_pars_fragment:lv,envmap_vertex:J0,fog_vertex:Q0,fog_pars_vertex:ev,fog_fragment:tv,fog_pars_fragment:nv,gradientmap_pars_fragment:iv,lightmap_pars_fragment:rv,lights_lambert_fragment:sv,lights_lambert_pars_fragment:ov,lights_pars_begin:av,lights_toon_fragment:cv,lights_toon_pars_fragment:uv,lights_phong_fragment:hv,lights_phong_pars_fragment:fv,lights_physical_fragment:dv,lights_physical_pars_fragment:pv,lights_fragment_begin:mv,lights_fragment_maps:_v,lights_fragment_end:gv,logdepthbuf_fragment:vv,logdepthbuf_pars_fragment:xv,logdepthbuf_pars_vertex:Sv,logdepthbuf_vertex:Mv,map_fragment:yv,map_pars_fragment:Ev,map_particle_fragment:Tv,map_particle_pars_fragment:bv,metalnessmap_fragment:wv,metalnessmap_pars_fragment:Av,morphinstance_vertex:Rv,morphcolor_vertex:Cv,morphnormal_vertex:Pv,morphtarget_pars_vertex:Dv,morphtarget_vertex:Lv,normal_fragment_begin:Iv,normal_fragment_maps:Uv,normal_pars_fragment:Nv,normal_pars_vertex:Fv,normal_vertex:Ov,normalmap_pars_fragment:Bv,clearcoat_normal_fragment_begin:zv,clearcoat_normal_fragment_maps:kv,clearcoat_pars_fragment:Hv,iridescence_pars_fragment:Gv,opaque_fragment:Vv,packing:Wv,premultiplied_alpha_fragment:Xv,project_vertex:Yv,dithering_fragment:qv,dithering_pars_fragment:$v,roughnessmap_fragment:Kv,roughnessmap_pars_fragment:Zv,shadowmap_pars_fragment:jv,shadowmap_pars_vertex:Jv,shadowmap_vertex:Qv,shadowmask_pars_fragment:ex,skinbase_vertex:tx,skinning_pars_vertex:nx,skinning_vertex:ix,skinnormal_vertex:rx,specularmap_fragment:sx,specularmap_pars_fragment:ox,tonemapping_fragment:ax,tonemapping_pars_fragment:lx,transmission_fragment:cx,transmission_pars_fragment:ux,uv_pars_fragment:hx,uv_pars_vertex:fx,uv_vertex:dx,worldpos_vertex:px,background_vert:mx,background_frag:_x,backgroundCube_vert:gx,backgroundCube_frag:vx,cube_vert:xx,cube_frag:Sx,depth_vert:Mx,depth_frag:yx,distanceRGBA_vert:Ex,distanceRGBA_frag:Tx,equirect_vert:bx,equirect_frag:wx,linedashed_vert:Ax,linedashed_frag:Rx,meshbasic_vert:Cx,meshbasic_frag:Px,meshlambert_vert:Dx,meshlambert_frag:Lx,meshmatcap_vert:Ix,meshmatcap_frag:Ux,meshnormal_vert:Nx,meshnormal_frag:Fx,meshphong_vert:Ox,meshphong_frag:Bx,meshphysical_vert:zx,meshphysical_frag:kx,meshtoon_vert:Hx,meshtoon_frag:Gx,points_vert:Vx,points_frag:Wx,shadow_vert:Xx,shadow_frag:Yx,sprite_vert:qx,sprite_frag:$x},me={common:{diffuse:{value:new at(16777215)},opacity:{value:1},map:{value:null},mapTransform:{value:new Ke},alphaMap:{value:null},alphaMapTransform:{value:new Ke},alphaTest:{value:0}},specularmap:{specularMap:{value:null},specularMapTransform:{value:new Ke}},envmap:{envMap:{value:null},envMapRotation:{value:new Ke},flipEnvMap:{value:-1},reflectivity:{value:1},ior:{value:1.5},refractionRatio:{value:.98}},aomap:{aoMap:{value:null},aoMapIntensity:{value:1},aoMapTransform:{value:new Ke}},lightmap:{lightMap:{value:null},lightMapIntensity:{value:1},lightMapTransform:{value:new Ke}},bumpmap:{bumpMap:{value:null},bumpMapTransform:{value:new Ke},bumpScale:{value:1}},normalmap:{normalMap:{value:null},normalMapTransform:{value:new Ke},normalScale:{value:new St(1,1)}},displacementmap:{displacementMap:{value:null},displacementMapTransform:{value:new Ke},displacementScale:{value:1},displacementBias:{value:0}},emissivemap:{emissiveMap:{value:null},emissiveMapTransform:{value:new Ke}},metalnessmap:{metalnessMap:{value:null},metalnessMapTransform:{value:new Ke}},roughnessmap:{roughnessMap:{value:null},roughnessMapTransform:{value:new Ke}},gradientmap:{gradientMap:{value:null}},fog:{fogDensity:{value:25e-5},fogNear:{value:1},fogFar:{value:2e3},fogColor:{value:new at(16777215)}},lights:{ambientLightColor:{value:[]},lightProbe:{value:[]},directionalLights:{value:[],properties:{direction:{},color:{}}},directionalLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},directionalShadowMap:{value:[]},directionalShadowMatrix:{value:[]},spotLights:{value:[],properties:{color:{},position:{},direction:{},distance:{},coneCos:{},penumbraCos:{},decay:{}}},spotLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{}}},spotLightMap:{value:[]},spotShadowMap:{value:[]},spotLightMatrix:{value:[]},pointLights:{value:[],properties:{color:{},position:{},decay:{},distance:{}}},pointLightShadows:{value:[],properties:{shadowIntensity:1,shadowBias:{},shadowNormalBias:{},shadowRadius:{},shadowMapSize:{},shadowCameraNear:{},shadowCameraFar:{}}},pointShadowMap:{value:[]},pointShadowMatrix:{value:[]},hemisphereLights:{value:[],properties:{direction:{},skyColor:{},groundColor:{}}},rectAreaLights:{value:[],properties:{color:{},position:{},width:{},height:{}}},ltc_1:{value:null},ltc_2:{value:null}},points:{diffuse:{value:new at(16777215)},opacity:{value:1},size:{value:1},scale:{value:1},map:{value:null},alphaMap:{value:null},alphaMapTransform:{value:new Ke},alphaTest:{value:0},uvTransform:{value:new Ke}},sprite:{diffuse:{value:new at(16777215)},opacity:{value:1},center:{value:new St(.5,.5)},rotation:{value:0},map:{value:null},mapTransform:{value:new Ke},alphaMap:{value:null},alphaMapTransform:{value:new Ke},alphaTest:{value:0}}},mi={basic:{uniforms:hn([me.common,me.specularmap,me.envmap,me.aomap,me.lightmap,me.fog]),vertexShader:$e.meshbasic_vert,fragmentShader:$e.meshbasic_frag},lambert:{uniforms:hn([me.common,me.specularmap,me.envmap,me.aomap,me.lightmap,me.emissivemap,me.bumpmap,me.normalmap,me.displacementmap,me.fog,me.lights,{emissive:{value:new at(0)}}]),vertexShader:$e.meshlambert_vert,fragmentShader:$e.meshlambert_frag},phong:{uniforms:hn([me.common,me.specularmap,me.envmap,me.aomap,me.lightmap,me.emissivemap,me.bumpmap,me.normalmap,me.displacementmap,me.fog,me.lights,{emissive:{value:new at(0)},specular:{value:new at(1118481)},shininess:{value:30}}]),vertexShader:$e.meshphong_vert,fragmentShader:$e.meshphong_frag},standard:{uniforms:hn([me.common,me.envmap,me.aomap,me.lightmap,me.emissivemap,me.bumpmap,me.normalmap,me.displacementmap,me.roughnessmap,me.metalnessmap,me.fog,me.lights,{emissive:{value:new at(0)},roughness:{value:1},metalness:{value:0},envMapIntensity:{value:1}}]),vertexShader:$e.meshphysical_vert,fragmentShader:$e.meshphysical_frag},toon:{uniforms:hn([me.common,me.aomap,me.lightmap,me.emissivemap,me.bumpmap,me.normalmap,me.displacementmap,me.gradientmap,me.fog,me.lights,{emissive:{value:new at(0)}}]),vertexShader:$e.meshtoon_vert,fragmentShader:$e.meshtoon_frag},matcap:{uniforms:hn([me.common,me.bumpmap,me.normalmap,me.displacementmap,me.fog,{matcap:{value:null}}]),vertexShader:$e.meshmatcap_vert,fragmentShader:$e.meshmatcap_frag},points:{uniforms:hn([me.points,me.fog]),vertexShader:$e.points_vert,fragmentShader:$e.points_frag},dashed:{uniforms:hn([me.common,me.fog,{scale:{value:1},dashSize:{value:1},totalSize:{value:2}}]),vertexShader:$e.linedashed_vert,fragmentShader:$e.linedashed_frag},depth:{uniforms:hn([me.common,me.displacementmap]),vertexShader:$e.depth_vert,fragmentShader:$e.depth_frag},normal:{uniforms:hn([me.common,me.bumpmap,me.normalmap,me.displacementmap,{opacity:{value:1}}]),vertexShader:$e.meshnormal_vert,fragmentShader:$e.meshnormal_frag},sprite:{uniforms:hn([me.sprite,me.fog]),vertexShader:$e.sprite_vert,fragmentShader:$e.sprite_frag},background:{uniforms:{uvTransform:{value:new Ke},t2D:{value:null},backgroundIntensity:{value:1}},vertexShader:$e.background_vert,fragmentShader:$e.background_frag},backgroundCube:{uniforms:{envMap:{value:null},flipEnvMap:{value:-1},backgroundBlurriness:{value:0},backgroundIntensity:{value:1},backgroundRotation:{value:new Ke}},vertexShader:$e.backgroundCube_vert,fragmentShader:$e.backgroundCube_frag},cube:{uniforms:{tCube:{value:null},tFlip:{value:-1},opacity:{value:1}},vertexShader:$e.cube_vert,fragmentShader:$e.cube_frag},equirect:{uniforms:{tEquirect:{value:null}},vertexShader:$e.equirect_vert,fragmentShader:$e.equirect_frag},distanceRGBA:{uniforms:hn([me.common,me.displacementmap,{referencePosition:{value:new Y},nearDistance:{value:1},farDistance:{value:1e3}}]),vertexShader:$e.distanceRGBA_vert,fragmentShader:$e.distanceRGBA_frag},shadow:{uniforms:hn([me.lights,me.fog,{color:{value:new at(0)},opacity:{value:1}}]),vertexShader:$e.shadow_vert,fragmentShader:$e.shadow_frag}};mi.physical={uniforms:hn([mi.standard.uniforms,{clearcoat:{value:0},clearcoatMap:{value:null},clearcoatMapTransform:{value:new Ke},clearcoatNormalMap:{value:null},clearcoatNormalMapTransform:{value:new Ke},clearcoatNormalScale:{value:new St(1,1)},clearcoatRoughness:{value:0},clearcoatRoughnessMap:{value:null},clearcoatRoughnessMapTransform:{value:new Ke},dispersion:{value:0},iridescence:{value:0},iridescenceMap:{value:null},iridescenceMapTransform:{value:new Ke},iridescenceIOR:{value:1.3},iridescenceThicknessMinimum:{value:100},iridescenceThicknessMaximum:{value:400},iridescenceThicknessMap:{value:null},iridescenceThicknessMapTransform:{value:new Ke},sheen:{value:0},sheenColor:{value:new at(0)},sheenColorMap:{value:null},sheenColorMapTransform:{value:new Ke},sheenRoughness:{value:1},sheenRoughnessMap:{value:null},sheenRoughnessMapTransform:{value:new Ke},transmission:{value:0},transmissionMap:{value:null},transmissionMapTransform:{value:new Ke},transmissionSamplerSize:{value:new St},transmissionSamplerMap:{value:null},thickness:{value:0},thicknessMap:{value:null},thicknessMapTransform:{value:new Ke},attenuationDistance:{value:0},attenuationColor:{value:new at(0)},specularColor:{value:new at(1,1,1)},specularColorMap:{value:null},specularColorMapTransform:{value:new Ke},specularIntensity:{value:1},specularIntensityMap:{value:null},specularIntensityMapTransform:{value:new Ke},anisotropyVector:{value:new St},anisotropyMap:{value:null},anisotropyMapTransform:{value:new Ke}}]),vertexShader:$e.meshphysical_vert,fragmentShader:$e.meshphysical_frag};const ga={r:0,b:0,g:0},Sr=new ki,Kx=new Ot;function Zx(r,e,t,n,i,s,o){const a=new at(0);let l=s===!0?0:1,c,u,f=null,h=0,d=null;function _(y){let x=y.isScene===!0?y.background:null;return x&&x.isTexture&&(x=(y.backgroundBlurriness>0?t:e).get(x)),x}function g(y){let x=!1;const M=_(y);M===null?m(a,l):M&&M.isColor&&(m(M,1),x=!0);const R=r.xr.getEnvironmentBlendMode();R==="additive"?n.buffers.color.setClear(0,0,0,1,o):R==="alpha-blend"&&n.buffers.color.setClear(0,0,0,0,o),(r.autoClear||x)&&(n.buffers.depth.setTest(!0),n.buffers.depth.setMask(!0),n.buffers.color.setMask(!0),r.clear(r.autoClearColor,r.autoClearDepth,r.autoClearStencil))}function p(y,x){const M=_(x);M&&(M.isCubeTexture||M.mapping===al)?(u===void 0&&(u=new hi(new Oo(1,1,1),new ei({name:"BackgroundCubeMaterial",uniforms:Hs(mi.backgroundCube.uniforms),vertexShader:mi.backgroundCube.vertexShader,fragmentShader:mi.backgroundCube.fragmentShader,side:_n,depthTest:!1,depthWrite:!1,fog:!1})),u.geometry.deleteAttribute("normal"),u.geometry.deleteAttribute("uv"),u.onBeforeRender=function(R,w,E){this.matrixWorld.copyPosition(E.matrixWorld)},Object.defineProperty(u.material,"envMap",{get:function(){return this.uniforms.envMap.value}}),i.update(u)),Sr.copy(x.backgroundRotation),Sr.x*=-1,Sr.y*=-1,Sr.z*=-1,M.isCubeTexture&&M.isRenderTargetTexture===!1&&(Sr.y*=-1,Sr.z*=-1),u.material.uniforms.envMap.value=M,u.material.uniforms.flipEnvMap.value=M.isCubeTexture&&M.isRenderTargetTexture===!1?-1:1,u.material.uniforms.backgroundBlurriness.value=x.backgroundBlurriness,u.material.uniforms.backgroundIntensity.value=x.backgroundIntensity,u.material.uniforms.backgroundRotation.value.setFromMatrix4(Kx.makeRotationFromEuler(Sr)),u.material.toneMapped=ft.getTransfer(M.colorSpace)!==Et,(f!==M||h!==M.version||d!==r.toneMapping)&&(u.material.needsUpdate=!0,f=M,h=M.version,d=r.toneMapping),u.layers.enableAll(),y.unshift(u,u.geometry,u.material,0,0,null)):M&&M.isTexture&&(c===void 0&&(c=new hi(new Bo(2,2),new ei({name:"BackgroundMaterial",uniforms:Hs(mi.background.uniforms),vertexShader:mi.background.vertexShader,fragmentShader:mi.background.fragmentShader,side:hr,depthTest:!1,depthWrite:!1,fog:!1})),c.geometry.deleteAttribute("normal"),Object.defineProperty(c.material,"map",{get:function(){return this.uniforms.t2D.value}}),i.update(c)),c.material.uniforms.t2D.value=M,c.material.uniforms.backgroundIntensity.value=x.backgroundIntensity,c.material.toneMapped=ft.getTransfer(M.colorSpace)!==Et,M.matrixAutoUpdate===!0&&M.updateMatrix(),c.material.uniforms.uvTransform.value.copy(M.matrix),(f!==M||h!==M.version||d!==r.toneMapping)&&(c.material.needsUpdate=!0,f=M,h=M.version,d=r.toneMapping),c.layers.enableAll(),y.unshift(c,c.geometry,c.material,0,0,null))}function m(y,x){y.getRGB(ga,zp(r)),n.buffers.color.setClear(ga.r,ga.g,ga.b,x,o)}return{getClearColor:function(){return a},setClearColor:function(y,x=1){a.set(y),l=x,m(a,l)},getClearAlpha:function(){return l},setClearAlpha:function(y){l=y,m(a,l)},render:g,addToRenderList:p}}function jx(r,e){const t=r.getParameter(r.MAX_VERTEX_ATTRIBS),n={},i=h(null);let s=i,o=!1;function a(v,T,N,z,W){let K=!1;const G=f(z,N,T);s!==G&&(s=G,c(s.object)),K=d(v,z,N,W),K&&_(v,z,N,W),W!==null&&e.update(W,r.ELEMENT_ARRAY_BUFFER),(K||o)&&(o=!1,M(v,T,N,z),W!==null&&r.bindBuffer(r.ELEMENT_ARRAY_BUFFER,e.get(W).buffer))}function l(){return r.createVertexArray()}function c(v){return r.bindVertexArray(v)}function u(v){return r.deleteVertexArray(v)}function f(v,T,N){const z=N.wireframe===!0;let W=n[v.id];W===void 0&&(W={},n[v.id]=W);let K=W[T.id];K===void 0&&(K={},W[T.id]=K);let G=K[z];return G===void 0&&(G=h(l()),K[z]=G),G}function h(v){const T=[],N=[],z=[];for(let W=0;W<t;W++)T[W]=0,N[W]=0,z[W]=0;return{geometry:null,program:null,wireframe:!1,newAttributes:T,enabledAttributes:N,attributeDivisors:z,object:v,attributes:{},index:null}}function d(v,T,N,z){const W=s.attributes,K=T.attributes;let G=0;const X=N.getAttributes();for(const V in X)if(X[V].location>=0){const C=W[V];let ae=K[V];if(ae===void 0&&(V==="instanceMatrix"&&v.instanceMatrix&&(ae=v.instanceMatrix),V==="instanceColor"&&v.instanceColor&&(ae=v.instanceColor)),C===void 0||C.attribute!==ae||ae&&C.data!==ae.data)return!0;G++}return s.attributesNum!==G||s.index!==z}function _(v,T,N,z){const W={},K=T.attributes;let G=0;const X=N.getAttributes();for(const V in X)if(X[V].location>=0){let C=K[V];C===void 0&&(V==="instanceMatrix"&&v.instanceMatrix&&(C=v.instanceMatrix),V==="instanceColor"&&v.instanceColor&&(C=v.instanceColor));const ae={};ae.attribute=C,C&&C.data&&(ae.data=C.data),W[V]=ae,G++}s.attributes=W,s.attributesNum=G,s.index=z}function g(){const v=s.newAttributes;for(let T=0,N=v.length;T<N;T++)v[T]=0}function p(v){m(v,0)}function m(v,T){const N=s.newAttributes,z=s.enabledAttributes,W=s.attributeDivisors;N[v]=1,z[v]===0&&(r.enableVertexAttribArray(v),z[v]=1),W[v]!==T&&(r.vertexAttribDivisor(v,T),W[v]=T)}function y(){const v=s.newAttributes,T=s.enabledAttributes;for(let N=0,z=T.length;N<z;N++)T[N]!==v[N]&&(r.disableVertexAttribArray(N),T[N]=0)}function x(v,T,N,z,W,K,G){G===!0?r.vertexAttribIPointer(v,T,N,W,K):r.vertexAttribPointer(v,T,N,z,W,K)}function M(v,T,N,z){g();const W=z.attributes,K=N.getAttributes(),G=T.defaultAttributeValues;for(const X in K){const V=K[X];if(V.location>=0){let re=W[X];if(re===void 0&&(X==="instanceMatrix"&&v.instanceMatrix&&(re=v.instanceMatrix),X==="instanceColor"&&v.instanceColor&&(re=v.instanceColor)),re!==void 0){const C=re.normalized,ae=re.itemSize,Be=e.get(re);if(Be===void 0)continue;const We=Be.buffer,q=Be.type,Q=Be.bytesPerElement,fe=q===r.INT||q===r.UNSIGNED_INT||re.gpuType===Qu;if(re.isInterleavedBufferAttribute){const oe=re.data,we=oe.stride,ye=re.offset;if(oe.isInstancedInterleavedBuffer){for(let Ve=0;Ve<V.locationSize;Ve++)m(V.location+Ve,oe.meshPerAttribute);v.isInstancedMesh!==!0&&z._maxInstanceCount===void 0&&(z._maxInstanceCount=oe.meshPerAttribute*oe.count)}else for(let Ve=0;Ve<V.locationSize;Ve++)p(V.location+Ve);r.bindBuffer(r.ARRAY_BUFFER,We);for(let Ve=0;Ve<V.locationSize;Ve++)x(V.location+Ve,ae/V.locationSize,q,C,we*Q,(ye+ae/V.locationSize*Ve)*Q,fe)}else{if(re.isInstancedBufferAttribute){for(let oe=0;oe<V.locationSize;oe++)m(V.location+oe,re.meshPerAttribute);v.isInstancedMesh!==!0&&z._maxInstanceCount===void 0&&(z._maxInstanceCount=re.meshPerAttribute*re.count)}else for(let oe=0;oe<V.locationSize;oe++)p(V.location+oe);r.bindBuffer(r.ARRAY_BUFFER,We);for(let oe=0;oe<V.locationSize;oe++)x(V.location+oe,ae/V.locationSize,q,C,ae*Q,ae/V.locationSize*oe*Q,fe)}}else if(G!==void 0){const C=G[X];if(C!==void 0)switch(C.length){case 2:r.vertexAttrib2fv(V.location,C);break;case 3:r.vertexAttrib3fv(V.location,C);break;case 4:r.vertexAttrib4fv(V.location,C);break;default:r.vertexAttrib1fv(V.location,C)}}}}y()}function R(){D();for(const v in n){const T=n[v];for(const N in T){const z=T[N];for(const W in z)u(z[W].object),delete z[W];delete T[N]}delete n[v]}}function w(v){if(n[v.id]===void 0)return;const T=n[v.id];for(const N in T){const z=T[N];for(const W in z)u(z[W].object),delete z[W];delete T[N]}delete n[v.id]}function E(v){for(const T in n){const N=n[T];if(N[v.id]===void 0)continue;const z=N[v.id];for(const W in z)u(z[W].object),delete z[W];delete N[v.id]}}function D(){O(),o=!0,s!==i&&(s=i,c(s.object))}function O(){i.geometry=null,i.program=null,i.wireframe=!1}return{setup:a,reset:D,resetDefaultState:O,dispose:R,releaseStatesOfGeometry:w,releaseStatesOfProgram:E,initAttributes:g,enableAttribute:p,disableUnusedAttributes:y}}function Jx(r,e,t){let n;function i(c){n=c}function s(c,u){r.drawArrays(n,c,u),t.update(u,n,1)}function o(c,u,f){f!==0&&(r.drawArraysInstanced(n,c,u,f),t.update(u,n,f))}function a(c,u,f){if(f===0)return;e.get("WEBGL_multi_draw").multiDrawArraysWEBGL(n,c,0,u,0,f);let d=0;for(let _=0;_<f;_++)d+=u[_];t.update(d,n,1)}function l(c,u,f,h){if(f===0)return;const d=e.get("WEBGL_multi_draw");if(d===null)for(let _=0;_<c.length;_++)o(c[_],u[_],h[_]);else{d.multiDrawArraysInstancedWEBGL(n,c,0,u,0,h,0,f);let _=0;for(let g=0;g<f;g++)_+=u[g];for(let g=0;g<h.length;g++)t.update(_,n,h[g])}}this.setMode=i,this.render=s,this.renderInstances=o,this.renderMultiDraw=a,this.renderMultiDrawInstances=l}function Qx(r,e,t,n){let i;function s(){if(i!==void 0)return i;if(e.has("EXT_texture_filter_anisotropic")===!0){const E=e.get("EXT_texture_filter_anisotropic");i=r.getParameter(E.MAX_TEXTURE_MAX_ANISOTROPY_EXT)}else i=0;return i}function o(E){return!(E!==ui&&n.convert(E)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_FORMAT))}function a(E){const D=E===Lo&&(e.has("EXT_color_buffer_half_float")||e.has("EXT_color_buffer_float"));return!(E!==zi&&n.convert(E)!==r.getParameter(r.IMPLEMENTATION_COLOR_READ_TYPE)&&E!==Ui&&!D)}function l(E){if(E==="highp"){if(r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.HIGH_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.HIGH_FLOAT).precision>0)return"highp";E="mediump"}return E==="mediump"&&r.getShaderPrecisionFormat(r.VERTEX_SHADER,r.MEDIUM_FLOAT).precision>0&&r.getShaderPrecisionFormat(r.FRAGMENT_SHADER,r.MEDIUM_FLOAT).precision>0?"mediump":"lowp"}let c=t.precision!==void 0?t.precision:"highp";const u=l(c);u!==c&&(console.warn("THREE.WebGLRenderer:",c,"not supported, using",u,"instead."),c=u);const f=t.logarithmicDepthBuffer===!0,h=t.reverseDepthBuffer===!0&&e.has("EXT_clip_control");if(h===!0){const E=e.get("EXT_clip_control");E.clipControlEXT(E.LOWER_LEFT_EXT,E.ZERO_TO_ONE_EXT)}const d=r.getParameter(r.MAX_TEXTURE_IMAGE_UNITS),_=r.getParameter(r.MAX_VERTEX_TEXTURE_IMAGE_UNITS),g=r.getParameter(r.MAX_TEXTURE_SIZE),p=r.getParameter(r.MAX_CUBE_MAP_TEXTURE_SIZE),m=r.getParameter(r.MAX_VERTEX_ATTRIBS),y=r.getParameter(r.MAX_VERTEX_UNIFORM_VECTORS),x=r.getParameter(r.MAX_VARYING_VECTORS),M=r.getParameter(r.MAX_FRAGMENT_UNIFORM_VECTORS),R=_>0,w=r.getParameter(r.MAX_SAMPLES);return{isWebGL2:!0,getMaxAnisotropy:s,getMaxPrecision:l,textureFormatReadable:o,textureTypeReadable:a,precision:c,logarithmicDepthBuffer:f,reverseDepthBuffer:h,maxTextures:d,maxVertexTextures:_,maxTextureSize:g,maxCubemapSize:p,maxAttributes:m,maxVertexUniforms:y,maxVaryings:x,maxFragmentUniforms:M,vertexTextures:R,maxSamples:w}}function eS(r){const e=this;let t=null,n=0,i=!1,s=!1;const o=new br,a=new Ke,l={value:null,needsUpdate:!1};this.uniform=l,this.numPlanes=0,this.numIntersection=0,this.init=function(f,h){const d=f.length!==0||h||n!==0||i;return i=h,n=f.length,d},this.beginShadows=function(){s=!0,u(null)},this.endShadows=function(){s=!1},this.setGlobalState=function(f,h){t=u(f,h,0)},this.setState=function(f,h,d){const _=f.clippingPlanes,g=f.clipIntersection,p=f.clipShadows,m=r.get(f);if(!i||_===null||_.length===0||s&&!p)s?u(null):c();else{const y=s?0:n,x=y*4;let M=m.clippingState||null;l.value=M,M=u(_,h,x,d);for(let R=0;R!==x;++R)M[R]=t[R];m.clippingState=M,this.numIntersection=g?this.numPlanes:0,this.numPlanes+=y}};function c(){l.value!==t&&(l.value=t,l.needsUpdate=n>0),e.numPlanes=n,e.numIntersection=0}function u(f,h,d,_){const g=f!==null?f.length:0;let p=null;if(g!==0){if(p=l.value,_!==!0||p===null){const m=d+g*4,y=h.matrixWorldInverse;a.getNormalMatrix(y),(p===null||p.length<m)&&(p=new Float32Array(m));for(let x=0,M=d;x!==g;++x,M+=4)o.copy(f[x]).applyMatrix4(y,a),o.normal.toArray(p,M),p[M+3]=o.constant}l.value=p,l.needsUpdate=!0}return e.numPlanes=g,e.numIntersection=0,p}}function tS(r){let e=new WeakMap;function t(o,a){return a===Wc?o.mapping=Os:a===Xc&&(o.mapping=Bs),o}function n(o){if(o&&o.isTexture){const a=o.mapping;if(a===Wc||a===Xc)if(e.has(o)){const l=e.get(o).texture;return t(l,o.mapping)}else{const l=o.image;if(l&&l.height>0){const c=new f0(l.height);return c.fromEquirectangularTexture(r,o),e.set(o,c),o.addEventListener("dispose",i),t(c.texture,o.mapping)}else return null}}return o}function i(o){const a=o.target;a.removeEventListener("dispose",i);const l=e.get(a);l!==void 0&&(e.delete(a),l.dispose())}function s(){e=new WeakMap}return{get:n,dispose:s}}class nS extends kp{constructor(e=-1,t=1,n=1,i=-1,s=.1,o=2e3){super(),this.isOrthographicCamera=!0,this.type="OrthographicCamera",this.zoom=1,this.view=null,this.left=e,this.right=t,this.top=n,this.bottom=i,this.near=s,this.far=o,this.updateProjectionMatrix()}copy(e,t){return super.copy(e,t),this.left=e.left,this.right=e.right,this.top=e.top,this.bottom=e.bottom,this.near=e.near,this.far=e.far,this.zoom=e.zoom,this.view=e.view===null?null:Object.assign({},e.view),this}setViewOffset(e,t,n,i,s,o){this.view===null&&(this.view={enabled:!0,fullWidth:1,fullHeight:1,offsetX:0,offsetY:0,width:1,height:1}),this.view.enabled=!0,this.view.fullWidth=e,this.view.fullHeight=t,this.view.offsetX=n,this.view.offsetY=i,this.view.width=s,this.view.height=o,this.updateProjectionMatrix()}clearViewOffset(){this.view!==null&&(this.view.enabled=!1),this.updateProjectionMatrix()}updateProjectionMatrix(){const e=(this.right-this.left)/(2*this.zoom),t=(this.top-this.bottom)/(2*this.zoom),n=(this.right+this.left)/2,i=(this.top+this.bottom)/2;let s=n-e,o=n+e,a=i+t,l=i-t;if(this.view!==null&&this.view.enabled){const c=(this.right-this.left)/this.view.fullWidth/this.zoom,u=(this.top-this.bottom)/this.view.fullHeight/this.zoom;s+=c*this.view.offsetX,o=s+c*this.view.width,a-=u*this.view.offsetY,l=a-u*this.view.height}this.projectionMatrix.makeOrthographic(s,o,a,l,this.near,this.far,this.coordinateSystem),this.projectionMatrixInverse.copy(this.projectionMatrix).invert()}toJSON(e){const t=super.toJSON(e);return t.object.zoom=this.zoom,t.object.left=this.left,t.object.right=this.right,t.object.top=this.top,t.object.bottom=this.bottom,t.object.near=this.near,t.object.far=this.far,this.view!==null&&(t.object.view=Object.assign({},this.view)),t}}const xs=4,vf=[.125,.215,.35,.446,.526,.582],Rr=20,Jl=new nS,xf=new at;let Ql=null,ec=0,tc=0,nc=!1;const wr=(1+Math.sqrt(5))/2,hs=1/wr,Sf=[new Y(-wr,hs,0),new Y(wr,hs,0),new Y(-hs,0,wr),new Y(hs,0,wr),new Y(0,wr,-hs),new Y(0,wr,hs),new Y(-1,1,-1),new Y(1,1,-1),new Y(-1,1,1),new Y(1,1,1)];class Mf{constructor(e){this._renderer=e,this._pingPongRenderTarget=null,this._lodMax=0,this._cubeSize=0,this._lodPlanes=[],this._sizeLods=[],this._sigmas=[],this._blurMaterial=null,this._cubemapMaterial=null,this._equirectMaterial=null,this._compileMaterial(this._blurMaterial)}fromScene(e,t=0,n=.1,i=100){Ql=this._renderer.getRenderTarget(),ec=this._renderer.getActiveCubeFace(),tc=this._renderer.getActiveMipmapLevel(),nc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1,this._setSize(256);const s=this._allocateTargets();return s.depthBuffer=!0,this._sceneToCubeUV(e,n,i,s),t>0&&this._blur(s,0,0,t),this._applyPMREM(s),this._cleanup(s),s}fromEquirectangular(e,t=null){return this._fromTexture(e,t)}fromCubemap(e,t=null){return this._fromTexture(e,t)}compileCubemapShader(){this._cubemapMaterial===null&&(this._cubemapMaterial=Tf(),this._compileMaterial(this._cubemapMaterial))}compileEquirectangularShader(){this._equirectMaterial===null&&(this._equirectMaterial=Ef(),this._compileMaterial(this._equirectMaterial))}dispose(){this._dispose(),this._cubemapMaterial!==null&&this._cubemapMaterial.dispose(),this._equirectMaterial!==null&&this._equirectMaterial.dispose()}_setSize(e){this._lodMax=Math.floor(Math.log2(e)),this._cubeSize=Math.pow(2,this._lodMax)}_dispose(){this._blurMaterial!==null&&this._blurMaterial.dispose(),this._pingPongRenderTarget!==null&&this._pingPongRenderTarget.dispose();for(let e=0;e<this._lodPlanes.length;e++)this._lodPlanes[e].dispose()}_cleanup(e){this._renderer.setRenderTarget(Ql,ec,tc),this._renderer.xr.enabled=nc,e.scissorTest=!1,va(e,0,0,e.width,e.height)}_fromTexture(e,t){e.mapping===Os||e.mapping===Bs?this._setSize(e.image.length===0?16:e.image[0].width||e.image[0].image.width):this._setSize(e.image.width/4),Ql=this._renderer.getRenderTarget(),ec=this._renderer.getActiveCubeFace(),tc=this._renderer.getActiveMipmapLevel(),nc=this._renderer.xr.enabled,this._renderer.xr.enabled=!1;const n=t||this._allocateTargets();return this._textureToCubeUV(e,n),this._applyPMREM(n),this._cleanup(n),n}_allocateTargets(){const e=3*Math.max(this._cubeSize,112),t=4*this._cubeSize,n={magFilter:li,minFilter:li,generateMipmaps:!1,type:Lo,format:ui,colorSpace:dr,depthBuffer:!1},i=yf(e,t,n);if(this._pingPongRenderTarget===null||this._pingPongRenderTarget.width!==e||this._pingPongRenderTarget.height!==t){this._pingPongRenderTarget!==null&&this._dispose(),this._pingPongRenderTarget=yf(e,t,n);const{_lodMax:s}=this;({sizeLods:this._sizeLods,lodPlanes:this._lodPlanes,sigmas:this._sigmas}=iS(s)),this._blurMaterial=rS(s,e,t)}return i}_compileMaterial(e){const t=new hi(this._lodPlanes[0],e);this._renderer.compile(t,Jl)}_sceneToCubeUV(e,t,n,i){const a=new Kn(90,1,t,n),l=[1,-1,1,1,1,1],c=[1,1,1,-1,-1,-1],u=this._renderer,f=u.autoClear,h=u.toneMapping;u.getClearColor(xf),u.toneMapping=or,u.autoClear=!1;const d=new Fp({name:"PMREM.Background",side:_n,depthWrite:!1,depthTest:!1}),_=new hi(new Oo,d);let g=!1;const p=e.background;p?p.isColor&&(d.color.copy(p),e.background=null,g=!0):(d.color.copy(xf),g=!0);for(let m=0;m<6;m++){const y=m%3;y===0?(a.up.set(0,l[m],0),a.lookAt(c[m],0,0)):y===1?(a.up.set(0,0,l[m]),a.lookAt(0,c[m],0)):(a.up.set(0,l[m],0),a.lookAt(0,0,c[m]));const x=this._cubeSize;va(i,y*x,m>2?x:0,x,x),u.setRenderTarget(i),g&&u.render(_,a),u.render(e,a)}_.geometry.dispose(),_.material.dispose(),u.toneMapping=h,u.autoClear=f,e.background=p}_textureToCubeUV(e,t){const n=this._renderer,i=e.mapping===Os||e.mapping===Bs;i?(this._cubemapMaterial===null&&(this._cubemapMaterial=Tf()),this._cubemapMaterial.uniforms.flipEnvMap.value=e.isRenderTargetTexture===!1?-1:1):this._equirectMaterial===null&&(this._equirectMaterial=Ef());const s=i?this._cubemapMaterial:this._equirectMaterial,o=new hi(this._lodPlanes[0],s),a=s.uniforms;a.envMap.value=e;const l=this._cubeSize;va(t,0,0,3*l,2*l),n.setRenderTarget(t),n.render(o,Jl)}_applyPMREM(e){const t=this._renderer,n=t.autoClear;t.autoClear=!1;const i=this._lodPlanes.length;for(let s=1;s<i;s++){const o=Math.sqrt(this._sigmas[s]*this._sigmas[s]-this._sigmas[s-1]*this._sigmas[s-1]),a=Sf[(i-s-1)%Sf.length];this._blur(e,s-1,s,o,a)}t.autoClear=n}_blur(e,t,n,i,s){const o=this._pingPongRenderTarget;this._halfBlur(e,o,t,n,i,"latitudinal",s),this._halfBlur(o,e,n,n,i,"longitudinal",s)}_halfBlur(e,t,n,i,s,o,a){const l=this._renderer,c=this._blurMaterial;o!=="latitudinal"&&o!=="longitudinal"&&console.error("blur direction must be either latitudinal or longitudinal!");const u=3,f=new hi(this._lodPlanes[i],c),h=c.uniforms,d=this._sizeLods[n]-1,_=isFinite(s)?Math.PI/(2*d):2*Math.PI/(2*Rr-1),g=s/_,p=isFinite(s)?1+Math.floor(u*g):Rr;p>Rr&&console.warn(`sigmaRadians, ${s}, is too large and will clip, as it requested ${p} samples when the maximum is set to ${Rr}`);const m=[];let y=0;for(let E=0;E<Rr;++E){const D=E/g,O=Math.exp(-D*D/2);m.push(O),E===0?y+=O:E<p&&(y+=2*O)}for(let E=0;E<m.length;E++)m[E]=m[E]/y;h.envMap.value=e.texture,h.samples.value=p,h.weights.value=m,h.latitudinal.value=o==="latitudinal",a&&(h.poleAxis.value=a);const{_lodMax:x}=this;h.dTheta.value=_,h.mipInt.value=x-n;const M=this._sizeLods[i],R=3*M*(i>x-xs?i-x+xs:0),w=4*(this._cubeSize-M);va(t,R,w,3*M,2*M),l.setRenderTarget(t),l.render(f,Jl)}}function iS(r){const e=[],t=[],n=[];let i=r;const s=r-xs+1+vf.length;for(let o=0;o<s;o++){const a=Math.pow(2,i);t.push(a);let l=1/a;o>r-xs?l=vf[o-r+xs-1]:o===0&&(l=0),n.push(l);const c=1/(a-2),u=-c,f=1+c,h=[u,u,f,u,f,f,u,u,f,f,u,f],d=6,_=6,g=3,p=2,m=1,y=new Float32Array(g*_*d),x=new Float32Array(p*_*d),M=new Float32Array(m*_*d);for(let w=0;w<d;w++){const E=w%3*2/3-1,D=w>2?0:-1,O=[E,D,0,E+2/3,D,0,E+2/3,D+1,0,E,D,0,E+2/3,D+1,0,E,D+1,0];y.set(O,g*_*w),x.set(h,p*_*w);const v=[w,w,w,w,w,w];M.set(v,m*_*w)}const R=new fi;R.setAttribute("position",new Zt(y,g)),R.setAttribute("uv",new Zt(x,p)),R.setAttribute("faceIndex",new Zt(M,m)),e.push(R),i>xs&&i--}return{lodPlanes:e,sizeLods:t,sigmas:n}}function yf(r,e,t){const n=new Xr(r,e,t);return n.texture.mapping=al,n.texture.name="PMREM.cubeUv",n.scissorTest=!0,n}function va(r,e,t,n,i){r.viewport.set(e,t,n,i),r.scissor.set(e,t,n,i)}function rS(r,e,t){const n=new Float32Array(Rr),i=new Y(0,1,0);return new ei({name:"SphericalGaussianBlur",defines:{n:Rr,CUBEUV_TEXEL_WIDTH:1/e,CUBEUV_TEXEL_HEIGHT:1/t,CUBEUV_MAX_MIP:`${r}.0`},uniforms:{envMap:{value:null},samples:{value:1},weights:{value:n},latitudinal:{value:!1},dTheta:{value:0},mipInt:{value:0},poleAxis:{value:i}},vertexShader:oh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;
			uniform int samples;
			uniform float weights[ n ];
			uniform bool latitudinal;
			uniform float dTheta;
			uniform float mipInt;
			uniform vec3 poleAxis;

			#define ENVMAP_TYPE_CUBE_UV
			#include <cube_uv_reflection_fragment>

			vec3 getSample( float theta, vec3 axis ) {

				float cosTheta = cos( theta );
				// Rodrigues' axis-angle rotation
				vec3 sampleDirection = vOutputDirection * cosTheta
					+ cross( axis, vOutputDirection ) * sin( theta )
					+ axis * dot( axis, vOutputDirection ) * ( 1.0 - cosTheta );

				return bilinearCubeUV( envMap, sampleDirection, mipInt );

			}

			void main() {

				vec3 axis = latitudinal ? poleAxis : cross( poleAxis, vOutputDirection );

				if ( all( equal( axis, vec3( 0.0 ) ) ) ) {

					axis = vec3( vOutputDirection.z, 0.0, - vOutputDirection.x );

				}

				axis = normalize( axis );

				gl_FragColor = vec4( 0.0, 0.0, 0.0, 1.0 );
				gl_FragColor.rgb += weights[ 0 ] * getSample( 0.0, axis );

				for ( int i = 1; i < n; i++ ) {

					if ( i >= samples ) {

						break;

					}

					float theta = dTheta * float( i );
					gl_FragColor.rgb += weights[ i ] * getSample( -1.0 * theta, axis );
					gl_FragColor.rgb += weights[ i ] * getSample( theta, axis );

				}

			}
		`,blending:sr,depthTest:!1,depthWrite:!1})}function Ef(){return new ei({name:"EquirectangularToCubeUV",uniforms:{envMap:{value:null}},vertexShader:oh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			varying vec3 vOutputDirection;

			uniform sampler2D envMap;

			#include <common>

			void main() {

				vec3 outputDirection = normalize( vOutputDirection );
				vec2 uv = equirectUv( outputDirection );

				gl_FragColor = vec4( texture2D ( envMap, uv ).rgb, 1.0 );

			}
		`,blending:sr,depthTest:!1,depthWrite:!1})}function Tf(){return new ei({name:"CubemapToCubeUV",uniforms:{envMap:{value:null},flipEnvMap:{value:-1}},vertexShader:oh(),fragmentShader:`

			precision mediump float;
			precision mediump int;

			uniform float flipEnvMap;

			varying vec3 vOutputDirection;

			uniform samplerCube envMap;

			void main() {

				gl_FragColor = textureCube( envMap, vec3( flipEnvMap * vOutputDirection.x, vOutputDirection.yz ) );

			}
		`,blending:sr,depthTest:!1,depthWrite:!1})}function oh(){return`

		precision mediump float;
		precision mediump int;

		attribute float faceIndex;

		varying vec3 vOutputDirection;

		// RH coordinate system; PMREM face-indexing convention
		vec3 getDirection( vec2 uv, float face ) {

			uv = 2.0 * uv - 1.0;

			vec3 direction = vec3( uv, 1.0 );

			if ( face == 0.0 ) {

				direction = direction.zyx; // ( 1, v, u ) pos x

			} else if ( face == 1.0 ) {

				direction = direction.xzy;
				direction.xz *= -1.0; // ( -u, 1, -v ) pos y

			} else if ( face == 2.0 ) {

				direction.x *= -1.0; // ( -u, v, 1 ) pos z

			} else if ( face == 3.0 ) {

				direction = direction.zyx;
				direction.xz *= -1.0; // ( -1, v, -u ) neg x

			} else if ( face == 4.0 ) {

				direction = direction.xzy;
				direction.xy *= -1.0; // ( -u, -1, v ) neg y

			} else if ( face == 5.0 ) {

				direction.z *= -1.0; // ( u, v, -1 ) neg z

			}

			return direction;

		}

		void main() {

			vOutputDirection = getDirection( uv, faceIndex );
			gl_Position = vec4( position, 1.0 );

		}
	`}function sS(r){let e=new WeakMap,t=null;function n(a){if(a&&a.isTexture){const l=a.mapping,c=l===Wc||l===Xc,u=l===Os||l===Bs;if(c||u){let f=e.get(a);const h=f!==void 0?f.texture.pmremVersion:0;if(a.isRenderTargetTexture&&a.pmremVersion!==h)return t===null&&(t=new Mf(r)),f=c?t.fromEquirectangular(a,f):t.fromCubemap(a,f),f.texture.pmremVersion=a.pmremVersion,e.set(a,f),f.texture;if(f!==void 0)return f.texture;{const d=a.image;return c&&d&&d.height>0||u&&d&&i(d)?(t===null&&(t=new Mf(r)),f=c?t.fromEquirectangular(a):t.fromCubemap(a),f.texture.pmremVersion=a.pmremVersion,e.set(a,f),a.addEventListener("dispose",s),f.texture):null}}}return a}function i(a){let l=0;const c=6;for(let u=0;u<c;u++)a[u]!==void 0&&l++;return l===c}function s(a){const l=a.target;l.removeEventListener("dispose",s);const c=e.get(l);c!==void 0&&(e.delete(l),c.dispose())}function o(){e=new WeakMap,t!==null&&(t.dispose(),t=null)}return{get:n,dispose:o}}function oS(r){const e={};function t(n){if(e[n]!==void 0)return e[n];let i;switch(n){case"WEBGL_depth_texture":i=r.getExtension("WEBGL_depth_texture")||r.getExtension("MOZ_WEBGL_depth_texture")||r.getExtension("WEBKIT_WEBGL_depth_texture");break;case"EXT_texture_filter_anisotropic":i=r.getExtension("EXT_texture_filter_anisotropic")||r.getExtension("MOZ_EXT_texture_filter_anisotropic")||r.getExtension("WEBKIT_EXT_texture_filter_anisotropic");break;case"WEBGL_compressed_texture_s3tc":i=r.getExtension("WEBGL_compressed_texture_s3tc")||r.getExtension("MOZ_WEBGL_compressed_texture_s3tc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_s3tc");break;case"WEBGL_compressed_texture_pvrtc":i=r.getExtension("WEBGL_compressed_texture_pvrtc")||r.getExtension("WEBKIT_WEBGL_compressed_texture_pvrtc");break;default:i=r.getExtension(n)}return e[n]=i,i}return{has:function(n){return t(n)!==null},init:function(){t("EXT_color_buffer_float"),t("WEBGL_clip_cull_distance"),t("OES_texture_float_linear"),t("EXT_color_buffer_half_float"),t("WEBGL_multisampled_render_to_texture"),t("WEBGL_render_shared_exponent")},get:function(n){const i=t(n);return i===null&&Oa("THREE.WebGLRenderer: "+n+" extension not supported."),i}}}function aS(r,e,t,n){const i={},s=new WeakMap;function o(f){const h=f.target;h.index!==null&&e.remove(h.index);for(const _ in h.attributes)e.remove(h.attributes[_]);for(const _ in h.morphAttributes){const g=h.morphAttributes[_];for(let p=0,m=g.length;p<m;p++)e.remove(g[p])}h.removeEventListener("dispose",o),delete i[h.id];const d=s.get(h);d&&(e.remove(d),s.delete(h)),n.releaseStatesOfGeometry(h),h.isInstancedBufferGeometry===!0&&delete h._maxInstanceCount,t.memory.geometries--}function a(f,h){return i[h.id]===!0||(h.addEventListener("dispose",o),i[h.id]=!0,t.memory.geometries++),h}function l(f){const h=f.attributes;for(const _ in h)e.update(h[_],r.ARRAY_BUFFER);const d=f.morphAttributes;for(const _ in d){const g=d[_];for(let p=0,m=g.length;p<m;p++)e.update(g[p],r.ARRAY_BUFFER)}}function c(f){const h=[],d=f.index,_=f.attributes.position;let g=0;if(d!==null){const y=d.array;g=d.version;for(let x=0,M=y.length;x<M;x+=3){const R=y[x+0],w=y[x+1],E=y[x+2];h.push(R,w,w,E,E,R)}}else if(_!==void 0){const y=_.array;g=_.version;for(let x=0,M=y.length/3-1;x<M;x+=3){const R=x+0,w=x+1,E=x+2;h.push(R,w,w,E,E,R)}}else return;const p=new(Pp(h)?Bp:Op)(h,1);p.version=g;const m=s.get(f);m&&e.remove(m),s.set(f,p)}function u(f){const h=s.get(f);if(h){const d=f.index;d!==null&&h.version<d.version&&c(f)}else c(f);return s.get(f)}return{get:a,update:l,getWireframeAttribute:u}}function lS(r,e,t){let n;function i(h){n=h}let s,o;function a(h){s=h.type,o=h.bytesPerElement}function l(h,d){r.drawElements(n,d,s,h*o),t.update(d,n,1)}function c(h,d,_){_!==0&&(r.drawElementsInstanced(n,d,s,h*o,_),t.update(d,n,_))}function u(h,d,_){if(_===0)return;e.get("WEBGL_multi_draw").multiDrawElementsWEBGL(n,d,0,s,h,0,_);let p=0;for(let m=0;m<_;m++)p+=d[m];t.update(p,n,1)}function f(h,d,_,g){if(_===0)return;const p=e.get("WEBGL_multi_draw");if(p===null)for(let m=0;m<h.length;m++)c(h[m]/o,d[m],g[m]);else{p.multiDrawElementsInstancedWEBGL(n,d,0,s,h,0,g,0,_);let m=0;for(let y=0;y<_;y++)m+=d[y];for(let y=0;y<g.length;y++)t.update(m,n,g[y])}}this.setMode=i,this.setIndex=a,this.render=l,this.renderInstances=c,this.renderMultiDraw=u,this.renderMultiDrawInstances=f}function cS(r){const e={geometries:0,textures:0},t={frame:0,calls:0,triangles:0,points:0,lines:0};function n(s,o,a){switch(t.calls++,o){case r.TRIANGLES:t.triangles+=a*(s/3);break;case r.LINES:t.lines+=a*(s/2);break;case r.LINE_STRIP:t.lines+=a*(s-1);break;case r.LINE_LOOP:t.lines+=a*s;break;case r.POINTS:t.points+=a*s;break;default:console.error("THREE.WebGLInfo: Unknown draw mode:",o);break}}function i(){t.calls=0,t.triangles=0,t.points=0,t.lines=0}return{memory:e,render:t,programs:null,autoReset:!0,reset:i,update:n}}function uS(r,e,t){const n=new WeakMap,i=new Nt;function s(o,a,l){const c=o.morphTargetInfluences,u=a.morphAttributes.position||a.morphAttributes.normal||a.morphAttributes.color,f=u!==void 0?u.length:0;let h=n.get(a);if(h===void 0||h.count!==f){let v=function(){D.dispose(),n.delete(a),a.removeEventListener("dispose",v)};var d=v;h!==void 0&&h.texture.dispose();const _=a.morphAttributes.position!==void 0,g=a.morphAttributes.normal!==void 0,p=a.morphAttributes.color!==void 0,m=a.morphAttributes.position||[],y=a.morphAttributes.normal||[],x=a.morphAttributes.color||[];let M=0;_===!0&&(M=1),g===!0&&(M=2),p===!0&&(M=3);let R=a.attributes.position.count*M,w=1;R>e.maxTextureSize&&(w=Math.ceil(R/e.maxTextureSize),R=e.maxTextureSize);const E=new Float32Array(R*w*4*f),D=new Lp(E,R,w,f);D.type=Ui,D.needsUpdate=!0;const O=M*4;for(let T=0;T<f;T++){const N=m[T],z=y[T],W=x[T],K=R*w*4*T;for(let G=0;G<N.count;G++){const X=G*O;_===!0&&(i.fromBufferAttribute(N,G),E[K+X+0]=i.x,E[K+X+1]=i.y,E[K+X+2]=i.z,E[K+X+3]=0),g===!0&&(i.fromBufferAttribute(z,G),E[K+X+4]=i.x,E[K+X+5]=i.y,E[K+X+6]=i.z,E[K+X+7]=0),p===!0&&(i.fromBufferAttribute(W,G),E[K+X+8]=i.x,E[K+X+9]=i.y,E[K+X+10]=i.z,E[K+X+11]=W.itemSize===4?i.w:1)}}h={count:f,texture:D,size:new St(R,w)},n.set(a,h),a.addEventListener("dispose",v)}if(o.isInstancedMesh===!0&&o.morphTexture!==null)l.getUniforms().setValue(r,"morphTexture",o.morphTexture,t);else{let _=0;for(let p=0;p<c.length;p++)_+=c[p];const g=a.morphTargetsRelative?1:1-_;l.getUniforms().setValue(r,"morphTargetBaseInfluence",g),l.getUniforms().setValue(r,"morphTargetInfluences",c)}l.getUniforms().setValue(r,"morphTargetsTexture",h.texture,t),l.getUniforms().setValue(r,"morphTargetsTextureSize",h.size)}return{update:s}}function hS(r,e,t,n){let i=new WeakMap;function s(l){const c=n.render.frame,u=l.geometry,f=e.get(l,u);if(i.get(f)!==c&&(e.update(f),i.set(f,c)),l.isInstancedMesh&&(l.hasEventListener("dispose",a)===!1&&l.addEventListener("dispose",a),i.get(l)!==c&&(t.update(l.instanceMatrix,r.ARRAY_BUFFER),l.instanceColor!==null&&t.update(l.instanceColor,r.ARRAY_BUFFER),i.set(l,c))),l.isSkinnedMesh){const h=l.skeleton;i.get(h)!==c&&(h.update(),i.set(h,c))}return f}function o(){i=new WeakMap}function a(l){const c=l.target;c.removeEventListener("dispose",a),t.remove(c.instanceMatrix),c.instanceColor!==null&&t.remove(c.instanceColor)}return{update:s,dispose:o}}class Wp extends gn{constructor(e,t,n,i,s,o,a,l,c,u=As){if(u!==As&&u!==ks)throw new Error("DepthTexture format must be either THREE.DepthFormat or THREE.DepthStencilFormat");n===void 0&&u===As&&(n=Wr),n===void 0&&u===ks&&(n=zs),super(null,i,s,o,a,l,u,n,c),this.isDepthTexture=!0,this.image={width:e,height:t},this.magFilter=a!==void 0?a:Jn,this.minFilter=l!==void 0?l:Jn,this.flipY=!1,this.generateMipmaps=!1,this.compareFunction=null}copy(e){return super.copy(e),this.compareFunction=e.compareFunction,this}toJSON(e){const t=super.toJSON(e);return this.compareFunction!==null&&(t.compareFunction=this.compareFunction),t}}const Xp=new gn,bf=new Wp(1,1),Yp=new Lp,qp=new Zg,$p=new Hp,wf=[],Af=[],Rf=new Float32Array(16),Cf=new Float32Array(9),Pf=new Float32Array(4);function Vs(r,e,t){const n=r[0];if(n<=0||n>0)return r;const i=e*t;let s=wf[i];if(s===void 0&&(s=new Float32Array(i),wf[i]=s),e!==0){n.toArray(s,0);for(let o=1,a=0;o!==e;++o)a+=t,r[o].toArray(s,a)}return s}function Vt(r,e){if(r.length!==e.length)return!1;for(let t=0,n=r.length;t<n;t++)if(r[t]!==e[t])return!1;return!0}function Wt(r,e){for(let t=0,n=e.length;t<n;t++)r[t]=e[t]}function ul(r,e){let t=Af[e];t===void 0&&(t=new Int32Array(e),Af[e]=t);for(let n=0;n!==e;++n)t[n]=r.allocateTextureUnit();return t}function fS(r,e){const t=this.cache;t[0]!==e&&(r.uniform1f(this.addr,e),t[0]=e)}function dS(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2f(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Vt(t,e))return;r.uniform2fv(this.addr,e),Wt(t,e)}}function pS(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3f(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else if(e.r!==void 0)(t[0]!==e.r||t[1]!==e.g||t[2]!==e.b)&&(r.uniform3f(this.addr,e.r,e.g,e.b),t[0]=e.r,t[1]=e.g,t[2]=e.b);else{if(Vt(t,e))return;r.uniform3fv(this.addr,e),Wt(t,e)}}function mS(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4f(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Vt(t,e))return;r.uniform4fv(this.addr,e),Wt(t,e)}}function _S(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(Vt(t,e))return;r.uniformMatrix2fv(this.addr,!1,e),Wt(t,e)}else{if(Vt(t,n))return;Pf.set(n),r.uniformMatrix2fv(this.addr,!1,Pf),Wt(t,n)}}function gS(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(Vt(t,e))return;r.uniformMatrix3fv(this.addr,!1,e),Wt(t,e)}else{if(Vt(t,n))return;Cf.set(n),r.uniformMatrix3fv(this.addr,!1,Cf),Wt(t,n)}}function vS(r,e){const t=this.cache,n=e.elements;if(n===void 0){if(Vt(t,e))return;r.uniformMatrix4fv(this.addr,!1,e),Wt(t,e)}else{if(Vt(t,n))return;Rf.set(n),r.uniformMatrix4fv(this.addr,!1,Rf),Wt(t,n)}}function xS(r,e){const t=this.cache;t[0]!==e&&(r.uniform1i(this.addr,e),t[0]=e)}function SS(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2i(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Vt(t,e))return;r.uniform2iv(this.addr,e),Wt(t,e)}}function MS(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3i(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Vt(t,e))return;r.uniform3iv(this.addr,e),Wt(t,e)}}function yS(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4i(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Vt(t,e))return;r.uniform4iv(this.addr,e),Wt(t,e)}}function ES(r,e){const t=this.cache;t[0]!==e&&(r.uniform1ui(this.addr,e),t[0]=e)}function TS(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y)&&(r.uniform2ui(this.addr,e.x,e.y),t[0]=e.x,t[1]=e.y);else{if(Vt(t,e))return;r.uniform2uiv(this.addr,e),Wt(t,e)}}function bS(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z)&&(r.uniform3ui(this.addr,e.x,e.y,e.z),t[0]=e.x,t[1]=e.y,t[2]=e.z);else{if(Vt(t,e))return;r.uniform3uiv(this.addr,e),Wt(t,e)}}function wS(r,e){const t=this.cache;if(e.x!==void 0)(t[0]!==e.x||t[1]!==e.y||t[2]!==e.z||t[3]!==e.w)&&(r.uniform4ui(this.addr,e.x,e.y,e.z,e.w),t[0]=e.x,t[1]=e.y,t[2]=e.z,t[3]=e.w);else{if(Vt(t,e))return;r.uniform4uiv(this.addr,e),Wt(t,e)}}function AS(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i);let s;this.type===r.SAMPLER_2D_SHADOW?(bf.compareFunction=Cp,s=bf):s=Xp,t.setTexture2D(e||s,i)}function RS(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture3D(e||qp,i)}function CS(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTextureCube(e||$p,i)}function PS(r,e,t){const n=this.cache,i=t.allocateTextureUnit();n[0]!==i&&(r.uniform1i(this.addr,i),n[0]=i),t.setTexture2DArray(e||Yp,i)}function DS(r){switch(r){case 5126:return fS;case 35664:return dS;case 35665:return pS;case 35666:return mS;case 35674:return _S;case 35675:return gS;case 35676:return vS;case 5124:case 35670:return xS;case 35667:case 35671:return SS;case 35668:case 35672:return MS;case 35669:case 35673:return yS;case 5125:return ES;case 36294:return TS;case 36295:return bS;case 36296:return wS;case 35678:case 36198:case 36298:case 36306:case 35682:return AS;case 35679:case 36299:case 36307:return RS;case 35680:case 36300:case 36308:case 36293:return CS;case 36289:case 36303:case 36311:case 36292:return PS}}function LS(r,e){r.uniform1fv(this.addr,e)}function IS(r,e){const t=Vs(e,this.size,2);r.uniform2fv(this.addr,t)}function US(r,e){const t=Vs(e,this.size,3);r.uniform3fv(this.addr,t)}function NS(r,e){const t=Vs(e,this.size,4);r.uniform4fv(this.addr,t)}function FS(r,e){const t=Vs(e,this.size,4);r.uniformMatrix2fv(this.addr,!1,t)}function OS(r,e){const t=Vs(e,this.size,9);r.uniformMatrix3fv(this.addr,!1,t)}function BS(r,e){const t=Vs(e,this.size,16);r.uniformMatrix4fv(this.addr,!1,t)}function zS(r,e){r.uniform1iv(this.addr,e)}function kS(r,e){r.uniform2iv(this.addr,e)}function HS(r,e){r.uniform3iv(this.addr,e)}function GS(r,e){r.uniform4iv(this.addr,e)}function VS(r,e){r.uniform1uiv(this.addr,e)}function WS(r,e){r.uniform2uiv(this.addr,e)}function XS(r,e){r.uniform3uiv(this.addr,e)}function YS(r,e){r.uniform4uiv(this.addr,e)}function qS(r,e,t){const n=this.cache,i=e.length,s=ul(t,i);Vt(n,s)||(r.uniform1iv(this.addr,s),Wt(n,s));for(let o=0;o!==i;++o)t.setTexture2D(e[o]||Xp,s[o])}function $S(r,e,t){const n=this.cache,i=e.length,s=ul(t,i);Vt(n,s)||(r.uniform1iv(this.addr,s),Wt(n,s));for(let o=0;o!==i;++o)t.setTexture3D(e[o]||qp,s[o])}function KS(r,e,t){const n=this.cache,i=e.length,s=ul(t,i);Vt(n,s)||(r.uniform1iv(this.addr,s),Wt(n,s));for(let o=0;o!==i;++o)t.setTextureCube(e[o]||$p,s[o])}function ZS(r,e,t){const n=this.cache,i=e.length,s=ul(t,i);Vt(n,s)||(r.uniform1iv(this.addr,s),Wt(n,s));for(let o=0;o!==i;++o)t.setTexture2DArray(e[o]||Yp,s[o])}function jS(r){switch(r){case 5126:return LS;case 35664:return IS;case 35665:return US;case 35666:return NS;case 35674:return FS;case 35675:return OS;case 35676:return BS;case 5124:case 35670:return zS;case 35667:case 35671:return kS;case 35668:case 35672:return HS;case 35669:case 35673:return GS;case 5125:return VS;case 36294:return WS;case 36295:return XS;case 36296:return YS;case 35678:case 36198:case 36298:case 36306:case 35682:return qS;case 35679:case 36299:case 36307:return $S;case 35680:case 36300:case 36308:case 36293:return KS;case 36289:case 36303:case 36311:case 36292:return ZS}}class JS{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.setValue=DS(t.type)}}class QS{constructor(e,t,n){this.id=e,this.addr=n,this.cache=[],this.type=t.type,this.size=t.size,this.setValue=jS(t.type)}}class eM{constructor(e){this.id=e,this.seq=[],this.map={}}setValue(e,t,n){const i=this.seq;for(let s=0,o=i.length;s!==o;++s){const a=i[s];a.setValue(e,t[a.id],n)}}}const ic=/(\w+)(\])?(\[|\.)?/g;function Df(r,e){r.seq.push(e),r.map[e.id]=e}function tM(r,e,t){const n=r.name,i=n.length;for(ic.lastIndex=0;;){const s=ic.exec(n),o=ic.lastIndex;let a=s[1];const l=s[2]==="]",c=s[3];if(l&&(a=a|0),c===void 0||c==="["&&o+2===i){Df(t,c===void 0?new JS(a,r,e):new QS(a,r,e));break}else{let f=t.map[a];f===void 0&&(f=new eM(a),Df(t,f)),t=f}}}class Ba{constructor(e,t){this.seq=[],this.map={};const n=e.getProgramParameter(t,e.ACTIVE_UNIFORMS);for(let i=0;i<n;++i){const s=e.getActiveUniform(t,i),o=e.getUniformLocation(t,s.name);tM(s,o,this)}}setValue(e,t,n,i){const s=this.map[t];s!==void 0&&s.setValue(e,n,i)}setOptional(e,t,n){const i=t[n];i!==void 0&&this.setValue(e,n,i)}static upload(e,t,n,i){for(let s=0,o=t.length;s!==o;++s){const a=t[s],l=n[a.id];l.needsUpdate!==!1&&a.setValue(e,l.value,i)}}static seqWithValue(e,t){const n=[];for(let i=0,s=e.length;i!==s;++i){const o=e[i];o.id in t&&n.push(o)}return n}}function Lf(r,e,t){const n=r.createShader(e);return r.shaderSource(n,t),r.compileShader(n),n}const nM=37297;let iM=0;function rM(r,e){const t=r.split(`
`),n=[],i=Math.max(e-6,0),s=Math.min(e+6,t.length);for(let o=i;o<s;o++){const a=o+1;n.push(`${a===e?">":" "} ${a}: ${t[o]}`)}return n.join(`
`)}function sM(r){const e=ft.getPrimaries(ft.workingColorSpace),t=ft.getPrimaries(r);let n;switch(e===t?n="":e===Qa&&t===Ja?n="LinearDisplayP3ToLinearSRGB":e===Ja&&t===Qa&&(n="LinearSRGBToLinearDisplayP3"),r){case dr:case ll:return[n,"LinearTransferOETF"];case ai:case sh:return[n,"sRGBTransferOETF"];default:return console.warn("THREE.WebGLProgram: Unsupported color space:",r),[n,"LinearTransferOETF"]}}function If(r,e,t){const n=r.getShaderParameter(e,r.COMPILE_STATUS),i=r.getShaderInfoLog(e).trim();if(n&&i==="")return"";const s=/ERROR: 0:(\d+)/.exec(i);if(s){const o=parseInt(s[1]);return t.toUpperCase()+`

`+i+`

`+rM(r.getShaderSource(e),o)}else return i}function oM(r,e){const t=sM(e);return`vec4 ${r}( vec4 value ) { return ${t[0]}( ${t[1]}( value ) ); }`}function aM(r,e){let t;switch(e){case Mg:t="Linear";break;case yg:t="Reinhard";break;case Eg:t="Cineon";break;case Tg:t="ACESFilmic";break;case wg:t="AgX";break;case Ag:t="Neutral";break;case bg:t="Custom";break;default:console.warn("THREE.WebGLProgram: Unsupported toneMapping:",e),t="Linear"}return"vec3 "+r+"( vec3 color ) { return "+t+"ToneMapping( color ); }"}const xa=new Y;function lM(){ft.getLuminanceCoefficients(xa);const r=xa.x.toFixed(4),e=xa.y.toFixed(4),t=xa.z.toFixed(4);return["float luminance( const in vec3 rgb ) {",`	const vec3 weights = vec3( ${r}, ${e}, ${t} );`,"	return dot( weights, rgb );","}"].join(`
`)}function cM(r){return[r.extensionClipCullDistance?"#extension GL_ANGLE_clip_cull_distance : require":"",r.extensionMultiDraw?"#extension GL_ANGLE_multi_draw : require":""].filter(oo).join(`
`)}function uM(r){const e=[];for(const t in r){const n=r[t];n!==!1&&e.push("#define "+t+" "+n)}return e.join(`
`)}function hM(r,e){const t={},n=r.getProgramParameter(e,r.ACTIVE_ATTRIBUTES);for(let i=0;i<n;i++){const s=r.getActiveAttrib(e,i),o=s.name;let a=1;s.type===r.FLOAT_MAT2&&(a=2),s.type===r.FLOAT_MAT3&&(a=3),s.type===r.FLOAT_MAT4&&(a=4),t[o]={type:s.type,location:r.getAttribLocation(e,o),locationSize:a}}return t}function oo(r){return r!==""}function Uf(r,e){const t=e.numSpotLightShadows+e.numSpotLightMaps-e.numSpotLightShadowsWithMaps;return r.replace(/NUM_DIR_LIGHTS/g,e.numDirLights).replace(/NUM_SPOT_LIGHTS/g,e.numSpotLights).replace(/NUM_SPOT_LIGHT_MAPS/g,e.numSpotLightMaps).replace(/NUM_SPOT_LIGHT_COORDS/g,t).replace(/NUM_RECT_AREA_LIGHTS/g,e.numRectAreaLights).replace(/NUM_POINT_LIGHTS/g,e.numPointLights).replace(/NUM_HEMI_LIGHTS/g,e.numHemiLights).replace(/NUM_DIR_LIGHT_SHADOWS/g,e.numDirLightShadows).replace(/NUM_SPOT_LIGHT_SHADOWS_WITH_MAPS/g,e.numSpotLightShadowsWithMaps).replace(/NUM_SPOT_LIGHT_SHADOWS/g,e.numSpotLightShadows).replace(/NUM_POINT_LIGHT_SHADOWS/g,e.numPointLightShadows)}function Nf(r,e){return r.replace(/NUM_CLIPPING_PLANES/g,e.numClippingPlanes).replace(/UNION_CLIPPING_PLANES/g,e.numClippingPlanes-e.numClipIntersection)}const fM=/^[ \t]*#include +<([\w\d./]+)>/gm;function Mu(r){return r.replace(fM,pM)}const dM=new Map;function pM(r,e){let t=$e[e];if(t===void 0){const n=dM.get(e);if(n!==void 0)t=$e[n],console.warn('THREE.WebGLRenderer: Shader chunk "%s" has been deprecated. Use "%s" instead.',e,n);else throw new Error("Can not resolve #include <"+e+">")}return Mu(t)}const mM=/#pragma unroll_loop_start\s+for\s*\(\s*int\s+i\s*=\s*(\d+)\s*;\s*i\s*<\s*(\d+)\s*;\s*i\s*\+\+\s*\)\s*{([\s\S]+?)}\s+#pragma unroll_loop_end/g;function Ff(r){return r.replace(mM,_M)}function _M(r,e,t,n){let i="";for(let s=parseInt(e);s<parseInt(t);s++)i+=n.replace(/\[\s*i\s*\]/g,"[ "+s+" ]").replace(/UNROLLED_LOOP_INDEX/g,s);return i}function Of(r){let e=`precision ${r.precision} float;
	precision ${r.precision} int;
	precision ${r.precision} sampler2D;
	precision ${r.precision} samplerCube;
	precision ${r.precision} sampler3D;
	precision ${r.precision} sampler2DArray;
	precision ${r.precision} sampler2DShadow;
	precision ${r.precision} samplerCubeShadow;
	precision ${r.precision} sampler2DArrayShadow;
	precision ${r.precision} isampler2D;
	precision ${r.precision} isampler3D;
	precision ${r.precision} isamplerCube;
	precision ${r.precision} isampler2DArray;
	precision ${r.precision} usampler2D;
	precision ${r.precision} usampler3D;
	precision ${r.precision} usamplerCube;
	precision ${r.precision} usampler2DArray;
	`;return r.precision==="highp"?e+=`
#define HIGH_PRECISION`:r.precision==="mediump"?e+=`
#define MEDIUM_PRECISION`:r.precision==="lowp"&&(e+=`
#define LOW_PRECISION`),e}function gM(r){let e="SHADOWMAP_TYPE_BASIC";return r.shadowMapType===_p?e="SHADOWMAP_TYPE_PCF":r.shadowMapType===eg?e="SHADOWMAP_TYPE_PCF_SOFT":r.shadowMapType===Ai&&(e="SHADOWMAP_TYPE_VSM"),e}function vM(r){let e="ENVMAP_TYPE_CUBE";if(r.envMap)switch(r.envMapMode){case Os:case Bs:e="ENVMAP_TYPE_CUBE";break;case al:e="ENVMAP_TYPE_CUBE_UV";break}return e}function xM(r){let e="ENVMAP_MODE_REFLECTION";if(r.envMap)switch(r.envMapMode){case Bs:e="ENVMAP_MODE_REFRACTION";break}return e}function SM(r){let e="ENVMAP_BLENDING_NONE";if(r.envMap)switch(r.combine){case gp:e="ENVMAP_BLENDING_MULTIPLY";break;case xg:e="ENVMAP_BLENDING_MIX";break;case Sg:e="ENVMAP_BLENDING_ADD";break}return e}function MM(r){const e=r.envMapCubeUVHeight;if(e===null)return null;const t=Math.log2(e)-2,n=1/e;return{texelWidth:1/(3*Math.max(Math.pow(2,t),7*16)),texelHeight:n,maxMip:t}}function yM(r,e,t,n){const i=r.getContext(),s=t.defines;let o=t.vertexShader,a=t.fragmentShader;const l=gM(t),c=vM(t),u=xM(t),f=SM(t),h=MM(t),d=cM(t),_=uM(s),g=i.createProgram();let p,m,y=t.glslVersion?"#version "+t.glslVersion+`
`:"";t.isRawShaderMaterial?(p=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_].filter(oo).join(`
`),p.length>0&&(p+=`
`),m=["#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_].filter(oo).join(`
`),m.length>0&&(m+=`
`)):(p=[Of(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_,t.extensionClipCullDistance?"#define USE_CLIP_DISTANCE":"",t.batching?"#define USE_BATCHING":"",t.batchingColor?"#define USE_BATCHING_COLOR":"",t.instancing?"#define USE_INSTANCING":"",t.instancingColor?"#define USE_INSTANCING_COLOR":"",t.instancingMorph?"#define USE_INSTANCING_MORPH":"",t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.map?"#define USE_MAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+u:"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.displacementMap?"#define USE_DISPLACEMENTMAP":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.mapUv?"#define MAP_UV "+t.mapUv:"",t.alphaMapUv?"#define ALPHAMAP_UV "+t.alphaMapUv:"",t.lightMapUv?"#define LIGHTMAP_UV "+t.lightMapUv:"",t.aoMapUv?"#define AOMAP_UV "+t.aoMapUv:"",t.emissiveMapUv?"#define EMISSIVEMAP_UV "+t.emissiveMapUv:"",t.bumpMapUv?"#define BUMPMAP_UV "+t.bumpMapUv:"",t.normalMapUv?"#define NORMALMAP_UV "+t.normalMapUv:"",t.displacementMapUv?"#define DISPLACEMENTMAP_UV "+t.displacementMapUv:"",t.metalnessMapUv?"#define METALNESSMAP_UV "+t.metalnessMapUv:"",t.roughnessMapUv?"#define ROUGHNESSMAP_UV "+t.roughnessMapUv:"",t.anisotropyMapUv?"#define ANISOTROPYMAP_UV "+t.anisotropyMapUv:"",t.clearcoatMapUv?"#define CLEARCOATMAP_UV "+t.clearcoatMapUv:"",t.clearcoatNormalMapUv?"#define CLEARCOAT_NORMALMAP_UV "+t.clearcoatNormalMapUv:"",t.clearcoatRoughnessMapUv?"#define CLEARCOAT_ROUGHNESSMAP_UV "+t.clearcoatRoughnessMapUv:"",t.iridescenceMapUv?"#define IRIDESCENCEMAP_UV "+t.iridescenceMapUv:"",t.iridescenceThicknessMapUv?"#define IRIDESCENCE_THICKNESSMAP_UV "+t.iridescenceThicknessMapUv:"",t.sheenColorMapUv?"#define SHEEN_COLORMAP_UV "+t.sheenColorMapUv:"",t.sheenRoughnessMapUv?"#define SHEEN_ROUGHNESSMAP_UV "+t.sheenRoughnessMapUv:"",t.specularMapUv?"#define SPECULARMAP_UV "+t.specularMapUv:"",t.specularColorMapUv?"#define SPECULAR_COLORMAP_UV "+t.specularColorMapUv:"",t.specularIntensityMapUv?"#define SPECULAR_INTENSITYMAP_UV "+t.specularIntensityMapUv:"",t.transmissionMapUv?"#define TRANSMISSIONMAP_UV "+t.transmissionMapUv:"",t.thicknessMapUv?"#define THICKNESSMAP_UV "+t.thicknessMapUv:"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.flatShading?"#define FLAT_SHADED":"",t.skinning?"#define USE_SKINNING":"",t.morphTargets?"#define USE_MORPHTARGETS":"",t.morphNormals&&t.flatShading===!1?"#define USE_MORPHNORMALS":"",t.morphColors?"#define USE_MORPHCOLORS":"",t.morphTargetsCount>0?"#define MORPHTARGETS_TEXTURE_STRIDE "+t.morphTextureStride:"",t.morphTargetsCount>0?"#define MORPHTARGETS_COUNT "+t.morphTargetsCount:"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.sizeAttenuation?"#define USE_SIZEATTENUATION":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 modelMatrix;","uniform mat4 modelViewMatrix;","uniform mat4 projectionMatrix;","uniform mat4 viewMatrix;","uniform mat3 normalMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;","#ifdef USE_INSTANCING","	attribute mat4 instanceMatrix;","#endif","#ifdef USE_INSTANCING_COLOR","	attribute vec3 instanceColor;","#endif","#ifdef USE_INSTANCING_MORPH","	uniform sampler2D morphTexture;","#endif","attribute vec3 position;","attribute vec3 normal;","attribute vec2 uv;","#ifdef USE_UV1","	attribute vec2 uv1;","#endif","#ifdef USE_UV2","	attribute vec2 uv2;","#endif","#ifdef USE_UV3","	attribute vec2 uv3;","#endif","#ifdef USE_TANGENT","	attribute vec4 tangent;","#endif","#if defined( USE_COLOR_ALPHA )","	attribute vec4 color;","#elif defined( USE_COLOR )","	attribute vec3 color;","#endif","#ifdef USE_SKINNING","	attribute vec4 skinIndex;","	attribute vec4 skinWeight;","#endif",`
`].filter(oo).join(`
`),m=[Of(t),"#define SHADER_TYPE "+t.shaderType,"#define SHADER_NAME "+t.shaderName,_,t.useFog&&t.fog?"#define USE_FOG":"",t.useFog&&t.fogExp2?"#define FOG_EXP2":"",t.alphaToCoverage?"#define ALPHA_TO_COVERAGE":"",t.map?"#define USE_MAP":"",t.matcap?"#define USE_MATCAP":"",t.envMap?"#define USE_ENVMAP":"",t.envMap?"#define "+c:"",t.envMap?"#define "+u:"",t.envMap?"#define "+f:"",h?"#define CUBEUV_TEXEL_WIDTH "+h.texelWidth:"",h?"#define CUBEUV_TEXEL_HEIGHT "+h.texelHeight:"",h?"#define CUBEUV_MAX_MIP "+h.maxMip+".0":"",t.lightMap?"#define USE_LIGHTMAP":"",t.aoMap?"#define USE_AOMAP":"",t.bumpMap?"#define USE_BUMPMAP":"",t.normalMap?"#define USE_NORMALMAP":"",t.normalMapObjectSpace?"#define USE_NORMALMAP_OBJECTSPACE":"",t.normalMapTangentSpace?"#define USE_NORMALMAP_TANGENTSPACE":"",t.emissiveMap?"#define USE_EMISSIVEMAP":"",t.anisotropy?"#define USE_ANISOTROPY":"",t.anisotropyMap?"#define USE_ANISOTROPYMAP":"",t.clearcoat?"#define USE_CLEARCOAT":"",t.clearcoatMap?"#define USE_CLEARCOATMAP":"",t.clearcoatRoughnessMap?"#define USE_CLEARCOAT_ROUGHNESSMAP":"",t.clearcoatNormalMap?"#define USE_CLEARCOAT_NORMALMAP":"",t.dispersion?"#define USE_DISPERSION":"",t.iridescence?"#define USE_IRIDESCENCE":"",t.iridescenceMap?"#define USE_IRIDESCENCEMAP":"",t.iridescenceThicknessMap?"#define USE_IRIDESCENCE_THICKNESSMAP":"",t.specularMap?"#define USE_SPECULARMAP":"",t.specularColorMap?"#define USE_SPECULAR_COLORMAP":"",t.specularIntensityMap?"#define USE_SPECULAR_INTENSITYMAP":"",t.roughnessMap?"#define USE_ROUGHNESSMAP":"",t.metalnessMap?"#define USE_METALNESSMAP":"",t.alphaMap?"#define USE_ALPHAMAP":"",t.alphaTest?"#define USE_ALPHATEST":"",t.alphaHash?"#define USE_ALPHAHASH":"",t.sheen?"#define USE_SHEEN":"",t.sheenColorMap?"#define USE_SHEEN_COLORMAP":"",t.sheenRoughnessMap?"#define USE_SHEEN_ROUGHNESSMAP":"",t.transmission?"#define USE_TRANSMISSION":"",t.transmissionMap?"#define USE_TRANSMISSIONMAP":"",t.thicknessMap?"#define USE_THICKNESSMAP":"",t.vertexTangents&&t.flatShading===!1?"#define USE_TANGENT":"",t.vertexColors||t.instancingColor||t.batchingColor?"#define USE_COLOR":"",t.vertexAlphas?"#define USE_COLOR_ALPHA":"",t.vertexUv1s?"#define USE_UV1":"",t.vertexUv2s?"#define USE_UV2":"",t.vertexUv3s?"#define USE_UV3":"",t.pointsUvs?"#define USE_POINTS_UV":"",t.gradientMap?"#define USE_GRADIENTMAP":"",t.flatShading?"#define FLAT_SHADED":"",t.doubleSided?"#define DOUBLE_SIDED":"",t.flipSided?"#define FLIP_SIDED":"",t.shadowMapEnabled?"#define USE_SHADOWMAP":"",t.shadowMapEnabled?"#define "+l:"",t.premultipliedAlpha?"#define PREMULTIPLIED_ALPHA":"",t.numLightProbes>0?"#define USE_LIGHT_PROBES":"",t.decodeVideoTexture?"#define DECODE_VIDEO_TEXTURE":"",t.logarithmicDepthBuffer?"#define USE_LOGDEPTHBUF":"",t.reverseDepthBuffer?"#define USE_REVERSEDEPTHBUF":"","uniform mat4 viewMatrix;","uniform vec3 cameraPosition;","uniform bool isOrthographic;",t.toneMapping!==or?"#define TONE_MAPPING":"",t.toneMapping!==or?$e.tonemapping_pars_fragment:"",t.toneMapping!==or?aM("toneMapping",t.toneMapping):"",t.dithering?"#define DITHERING":"",t.opaque?"#define OPAQUE":"",$e.colorspace_pars_fragment,oM("linearToOutputTexel",t.outputColorSpace),lM(),t.useDepthPacking?"#define DEPTH_PACKING "+t.depthPacking:"",`
`].filter(oo).join(`
`)),o=Mu(o),o=Uf(o,t),o=Nf(o,t),a=Mu(a),a=Uf(a,t),a=Nf(a,t),o=Ff(o),a=Ff(a),t.isRawShaderMaterial!==!0&&(y=`#version 300 es
`,p=[d,"#define attribute in","#define varying out","#define texture2D texture"].join(`
`)+`
`+p,m=["#define varying in",t.glslVersion===Qh?"":"layout(location = 0) out highp vec4 pc_fragColor;",t.glslVersion===Qh?"":"#define gl_FragColor pc_fragColor","#define gl_FragDepthEXT gl_FragDepth","#define texture2D texture","#define textureCube texture","#define texture2DProj textureProj","#define texture2DLodEXT textureLod","#define texture2DProjLodEXT textureProjLod","#define textureCubeLodEXT textureLod","#define texture2DGradEXT textureGrad","#define texture2DProjGradEXT textureProjGrad","#define textureCubeGradEXT textureGrad"].join(`
`)+`
`+m);const x=y+p+o,M=y+m+a,R=Lf(i,i.VERTEX_SHADER,x),w=Lf(i,i.FRAGMENT_SHADER,M);i.attachShader(g,R),i.attachShader(g,w),t.index0AttributeName!==void 0?i.bindAttribLocation(g,0,t.index0AttributeName):t.morphTargets===!0&&i.bindAttribLocation(g,0,"position"),i.linkProgram(g);function E(T){if(r.debug.checkShaderErrors){const N=i.getProgramInfoLog(g).trim(),z=i.getShaderInfoLog(R).trim(),W=i.getShaderInfoLog(w).trim();let K=!0,G=!0;if(i.getProgramParameter(g,i.LINK_STATUS)===!1)if(K=!1,typeof r.debug.onShaderError=="function")r.debug.onShaderError(i,g,R,w);else{const X=If(i,R,"vertex"),V=If(i,w,"fragment");console.error("THREE.WebGLProgram: Shader Error "+i.getError()+" - VALIDATE_STATUS "+i.getProgramParameter(g,i.VALIDATE_STATUS)+`

Material Name: `+T.name+`
Material Type: `+T.type+`

Program Info Log: `+N+`
`+X+`
`+V)}else N!==""?console.warn("THREE.WebGLProgram: Program Info Log:",N):(z===""||W==="")&&(G=!1);G&&(T.diagnostics={runnable:K,programLog:N,vertexShader:{log:z,prefix:p},fragmentShader:{log:W,prefix:m}})}i.deleteShader(R),i.deleteShader(w),D=new Ba(i,g),O=hM(i,g)}let D;this.getUniforms=function(){return D===void 0&&E(this),D};let O;this.getAttributes=function(){return O===void 0&&E(this),O};let v=t.rendererExtensionParallelShaderCompile===!1;return this.isReady=function(){return v===!1&&(v=i.getProgramParameter(g,nM)),v},this.destroy=function(){n.releaseStatesOfProgram(this),i.deleteProgram(g),this.program=void 0},this.type=t.shaderType,this.name=t.shaderName,this.id=iM++,this.cacheKey=e,this.usedTimes=1,this.program=g,this.vertexShader=R,this.fragmentShader=w,this}let EM=0;class TM{constructor(){this.shaderCache=new Map,this.materialCache=new Map}update(e){const t=e.vertexShader,n=e.fragmentShader,i=this._getShaderStage(t),s=this._getShaderStage(n),o=this._getShaderCacheForMaterial(e);return o.has(i)===!1&&(o.add(i),i.usedTimes++),o.has(s)===!1&&(o.add(s),s.usedTimes++),this}remove(e){const t=this.materialCache.get(e);for(const n of t)n.usedTimes--,n.usedTimes===0&&this.shaderCache.delete(n.code);return this.materialCache.delete(e),this}getVertexShaderID(e){return this._getShaderStage(e.vertexShader).id}getFragmentShaderID(e){return this._getShaderStage(e.fragmentShader).id}dispose(){this.shaderCache.clear(),this.materialCache.clear()}_getShaderCacheForMaterial(e){const t=this.materialCache;let n=t.get(e);return n===void 0&&(n=new Set,t.set(e,n)),n}_getShaderStage(e){const t=this.shaderCache;let n=t.get(e);return n===void 0&&(n=new bM(e),t.set(e,n)),n}}class bM{constructor(e){this.id=EM++,this.code=e,this.usedTimes=0}}function wM(r,e,t,n,i,s,o){const a=new Up,l=new TM,c=new Set,u=[],f=i.logarithmicDepthBuffer,h=i.reverseDepthBuffer,d=i.vertexTextures;let _=i.precision;const g={MeshDepthMaterial:"depth",MeshDistanceMaterial:"distanceRGBA",MeshNormalMaterial:"normal",MeshBasicMaterial:"basic",MeshLambertMaterial:"lambert",MeshPhongMaterial:"phong",MeshToonMaterial:"toon",MeshStandardMaterial:"physical",MeshPhysicalMaterial:"physical",MeshMatcapMaterial:"matcap",LineBasicMaterial:"basic",LineDashedMaterial:"dashed",PointsMaterial:"points",ShadowMaterial:"shadow",SpriteMaterial:"sprite"};function p(v){return c.add(v),v===0?"uv":`uv${v}`}function m(v,T,N,z,W){const K=z.fog,G=W.geometry,X=v.isMeshStandardMaterial?z.environment:null,V=(v.isMeshStandardMaterial?t:e).get(v.envMap||X),re=V&&V.mapping===al?V.image.height:null,C=g[v.type];v.precision!==null&&(_=i.getMaxPrecision(v.precision),_!==v.precision&&console.warn("THREE.WebGLProgram.getParameters:",v.precision,"not supported, using",_,"instead."));const ae=G.morphAttributes.position||G.morphAttributes.normal||G.morphAttributes.color,Be=ae!==void 0?ae.length:0;let We=0;G.morphAttributes.position!==void 0&&(We=1),G.morphAttributes.normal!==void 0&&(We=2),G.morphAttributes.color!==void 0&&(We=3);let q,Q,fe,oe;if(C){const Re=mi[C];q=Re.vertexShader,Q=Re.fragmentShader}else q=v.vertexShader,Q=v.fragmentShader,l.update(v),fe=l.getVertexShaderID(v),oe=l.getFragmentShaderID(v);const we=r.getRenderTarget(),ye=W.isInstancedMesh===!0,Ve=W.isBatchedMesh===!0,Ge=!!v.map,Ne=!!v.matcap,P=!!V,rt=!!v.aoMap,Fe=!!v.lightMap,ze=!!v.bumpMap,F=!!v.normalMap,je=!!v.displacementMap,De=!!v.emissiveMap,A=!!v.metalnessMap,S=!!v.roughnessMap,H=v.anisotropy>0,j=v.clearcoat>0,te=v.dispersion>0,Z=v.iridescence>0,Se=v.sheen>0,ie=v.transmission>0,de=H&&!!v.anisotropyMap,He=j&&!!v.clearcoatMap,ne=j&&!!v.clearcoatNormalMap,ve=j&&!!v.clearcoatRoughnessMap,xe=Z&&!!v.iridescenceMap,Ie=Z&&!!v.iridescenceThicknessMap,ge=Se&&!!v.sheenColorMap,Xe=Se&&!!v.sheenRoughnessMap,Oe=!!v.specularMap,st=!!v.specularColorMap,L=!!v.specularIntensityMap,ee=ie&&!!v.transmissionMap,$=ie&&!!v.thicknessMap,J=!!v.gradientMap,le=!!v.alphaMap,ce=v.alphaTest>0,Ye=!!v.alphaHash,_t=!!v.extensions;let Tt=or;v.toneMapped&&(we===null||we.isXRRenderTarget===!0)&&(Tt=r.toneMapping);const nt={shaderID:C,shaderType:v.type,shaderName:v.name,vertexShader:q,fragmentShader:Q,defines:v.defines,customVertexShaderID:fe,customFragmentShaderID:oe,isRawShaderMaterial:v.isRawShaderMaterial===!0,glslVersion:v.glslVersion,precision:_,batching:Ve,batchingColor:Ve&&W._colorsTexture!==null,instancing:ye,instancingColor:ye&&W.instanceColor!==null,instancingMorph:ye&&W.morphTexture!==null,supportsVertexTextures:d,outputColorSpace:we===null?r.outputColorSpace:we.isXRRenderTarget===!0?we.texture.colorSpace:dr,alphaToCoverage:!!v.alphaToCoverage,map:Ge,matcap:Ne,envMap:P,envMapMode:P&&V.mapping,envMapCubeUVHeight:re,aoMap:rt,lightMap:Fe,bumpMap:ze,normalMap:F,displacementMap:d&&je,emissiveMap:De,normalMapObjectSpace:F&&v.normalMapType===Lg,normalMapTangentSpace:F&&v.normalMapType===Dg,metalnessMap:A,roughnessMap:S,anisotropy:H,anisotropyMap:de,clearcoat:j,clearcoatMap:He,clearcoatNormalMap:ne,clearcoatRoughnessMap:ve,dispersion:te,iridescence:Z,iridescenceMap:xe,iridescenceThicknessMap:Ie,sheen:Se,sheenColorMap:ge,sheenRoughnessMap:Xe,specularMap:Oe,specularColorMap:st,specularIntensityMap:L,transmission:ie,transmissionMap:ee,thicknessMap:$,gradientMap:J,opaque:v.transparent===!1&&v.blending===zr&&v.alphaToCoverage===!1,alphaMap:le,alphaTest:ce,alphaHash:Ye,combine:v.combine,mapUv:Ge&&p(v.map.channel),aoMapUv:rt&&p(v.aoMap.channel),lightMapUv:Fe&&p(v.lightMap.channel),bumpMapUv:ze&&p(v.bumpMap.channel),normalMapUv:F&&p(v.normalMap.channel),displacementMapUv:je&&p(v.displacementMap.channel),emissiveMapUv:De&&p(v.emissiveMap.channel),metalnessMapUv:A&&p(v.metalnessMap.channel),roughnessMapUv:S&&p(v.roughnessMap.channel),anisotropyMapUv:de&&p(v.anisotropyMap.channel),clearcoatMapUv:He&&p(v.clearcoatMap.channel),clearcoatNormalMapUv:ne&&p(v.clearcoatNormalMap.channel),clearcoatRoughnessMapUv:ve&&p(v.clearcoatRoughnessMap.channel),iridescenceMapUv:xe&&p(v.iridescenceMap.channel),iridescenceThicknessMapUv:Ie&&p(v.iridescenceThicknessMap.channel),sheenColorMapUv:ge&&p(v.sheenColorMap.channel),sheenRoughnessMapUv:Xe&&p(v.sheenRoughnessMap.channel),specularMapUv:Oe&&p(v.specularMap.channel),specularColorMapUv:st&&p(v.specularColorMap.channel),specularIntensityMapUv:L&&p(v.specularIntensityMap.channel),transmissionMapUv:ee&&p(v.transmissionMap.channel),thicknessMapUv:$&&p(v.thicknessMap.channel),alphaMapUv:le&&p(v.alphaMap.channel),vertexTangents:!!G.attributes.tangent&&(F||H),vertexColors:v.vertexColors,vertexAlphas:v.vertexColors===!0&&!!G.attributes.color&&G.attributes.color.itemSize===4,pointsUvs:W.isPoints===!0&&!!G.attributes.uv&&(Ge||le),fog:!!K,useFog:v.fog===!0,fogExp2:!!K&&K.isFogExp2,flatShading:v.flatShading===!0,sizeAttenuation:v.sizeAttenuation===!0,logarithmicDepthBuffer:f,reverseDepthBuffer:h,skinning:W.isSkinnedMesh===!0,morphTargets:G.morphAttributes.position!==void 0,morphNormals:G.morphAttributes.normal!==void 0,morphColors:G.morphAttributes.color!==void 0,morphTargetsCount:Be,morphTextureStride:We,numDirLights:T.directional.length,numPointLights:T.point.length,numSpotLights:T.spot.length,numSpotLightMaps:T.spotLightMap.length,numRectAreaLights:T.rectArea.length,numHemiLights:T.hemi.length,numDirLightShadows:T.directionalShadowMap.length,numPointLightShadows:T.pointShadowMap.length,numSpotLightShadows:T.spotShadowMap.length,numSpotLightShadowsWithMaps:T.numSpotLightShadowsWithMaps,numLightProbes:T.numLightProbes,numClippingPlanes:o.numPlanes,numClipIntersection:o.numIntersection,dithering:v.dithering,shadowMapEnabled:r.shadowMap.enabled&&N.length>0,shadowMapType:r.shadowMap.type,toneMapping:Tt,decodeVideoTexture:Ge&&v.map.isVideoTexture===!0&&ft.getTransfer(v.map.colorSpace)===Et,premultipliedAlpha:v.premultipliedAlpha,doubleSided:v.side===Di,flipSided:v.side===_n,useDepthPacking:v.depthPacking>=0,depthPacking:v.depthPacking||0,index0AttributeName:v.index0AttributeName,extensionClipCullDistance:_t&&v.extensions.clipCullDistance===!0&&n.has("WEBGL_clip_cull_distance"),extensionMultiDraw:(_t&&v.extensions.multiDraw===!0||Ve)&&n.has("WEBGL_multi_draw"),rendererExtensionParallelShaderCompile:n.has("KHR_parallel_shader_compile"),customProgramCacheKey:v.customProgramCacheKey()};return nt.vertexUv1s=c.has(1),nt.vertexUv2s=c.has(2),nt.vertexUv3s=c.has(3),c.clear(),nt}function y(v){const T=[];if(v.shaderID?T.push(v.shaderID):(T.push(v.customVertexShaderID),T.push(v.customFragmentShaderID)),v.defines!==void 0)for(const N in v.defines)T.push(N),T.push(v.defines[N]);return v.isRawShaderMaterial===!1&&(x(T,v),M(T,v),T.push(r.outputColorSpace)),T.push(v.customProgramCacheKey),T.join()}function x(v,T){v.push(T.precision),v.push(T.outputColorSpace),v.push(T.envMapMode),v.push(T.envMapCubeUVHeight),v.push(T.mapUv),v.push(T.alphaMapUv),v.push(T.lightMapUv),v.push(T.aoMapUv),v.push(T.bumpMapUv),v.push(T.normalMapUv),v.push(T.displacementMapUv),v.push(T.emissiveMapUv),v.push(T.metalnessMapUv),v.push(T.roughnessMapUv),v.push(T.anisotropyMapUv),v.push(T.clearcoatMapUv),v.push(T.clearcoatNormalMapUv),v.push(T.clearcoatRoughnessMapUv),v.push(T.iridescenceMapUv),v.push(T.iridescenceThicknessMapUv),v.push(T.sheenColorMapUv),v.push(T.sheenRoughnessMapUv),v.push(T.specularMapUv),v.push(T.specularColorMapUv),v.push(T.specularIntensityMapUv),v.push(T.transmissionMapUv),v.push(T.thicknessMapUv),v.push(T.combine),v.push(T.fogExp2),v.push(T.sizeAttenuation),v.push(T.morphTargetsCount),v.push(T.morphAttributeCount),v.push(T.numDirLights),v.push(T.numPointLights),v.push(T.numSpotLights),v.push(T.numSpotLightMaps),v.push(T.numHemiLights),v.push(T.numRectAreaLights),v.push(T.numDirLightShadows),v.push(T.numPointLightShadows),v.push(T.numSpotLightShadows),v.push(T.numSpotLightShadowsWithMaps),v.push(T.numLightProbes),v.push(T.shadowMapType),v.push(T.toneMapping),v.push(T.numClippingPlanes),v.push(T.numClipIntersection),v.push(T.depthPacking)}function M(v,T){a.disableAll(),T.supportsVertexTextures&&a.enable(0),T.instancing&&a.enable(1),T.instancingColor&&a.enable(2),T.instancingMorph&&a.enable(3),T.matcap&&a.enable(4),T.envMap&&a.enable(5),T.normalMapObjectSpace&&a.enable(6),T.normalMapTangentSpace&&a.enable(7),T.clearcoat&&a.enable(8),T.iridescence&&a.enable(9),T.alphaTest&&a.enable(10),T.vertexColors&&a.enable(11),T.vertexAlphas&&a.enable(12),T.vertexUv1s&&a.enable(13),T.vertexUv2s&&a.enable(14),T.vertexUv3s&&a.enable(15),T.vertexTangents&&a.enable(16),T.anisotropy&&a.enable(17),T.alphaHash&&a.enable(18),T.batching&&a.enable(19),T.dispersion&&a.enable(20),T.batchingColor&&a.enable(21),v.push(a.mask),a.disableAll(),T.fog&&a.enable(0),T.useFog&&a.enable(1),T.flatShading&&a.enable(2),T.logarithmicDepthBuffer&&a.enable(3),T.reverseDepthBuffer&&a.enable(4),T.skinning&&a.enable(5),T.morphTargets&&a.enable(6),T.morphNormals&&a.enable(7),T.morphColors&&a.enable(8),T.premultipliedAlpha&&a.enable(9),T.shadowMapEnabled&&a.enable(10),T.doubleSided&&a.enable(11),T.flipSided&&a.enable(12),T.useDepthPacking&&a.enable(13),T.dithering&&a.enable(14),T.transmission&&a.enable(15),T.sheen&&a.enable(16),T.opaque&&a.enable(17),T.pointsUvs&&a.enable(18),T.decodeVideoTexture&&a.enable(19),T.alphaToCoverage&&a.enable(20),v.push(a.mask)}function R(v){const T=g[v.type];let N;if(T){const z=mi[T];N=l0.clone(z.uniforms)}else N=v.uniforms;return N}function w(v,T){let N;for(let z=0,W=u.length;z<W;z++){const K=u[z];if(K.cacheKey===T){N=K,++N.usedTimes;break}}return N===void 0&&(N=new yM(r,T,v,s),u.push(N)),N}function E(v){if(--v.usedTimes===0){const T=u.indexOf(v);u[T]=u[u.length-1],u.pop(),v.destroy()}}function D(v){l.remove(v)}function O(){l.dispose()}return{getParameters:m,getProgramCacheKey:y,getUniforms:R,acquireProgram:w,releaseProgram:E,releaseShaderCache:D,programs:u,dispose:O}}function AM(){let r=new WeakMap;function e(o){return r.has(o)}function t(o){let a=r.get(o);return a===void 0&&(a={},r.set(o,a)),a}function n(o){r.delete(o)}function i(o,a,l){r.get(o)[a]=l}function s(){r=new WeakMap}return{has:e,get:t,remove:n,update:i,dispose:s}}function RM(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.material.id!==e.material.id?r.material.id-e.material.id:r.z!==e.z?r.z-e.z:r.id-e.id}function Bf(r,e){return r.groupOrder!==e.groupOrder?r.groupOrder-e.groupOrder:r.renderOrder!==e.renderOrder?r.renderOrder-e.renderOrder:r.z!==e.z?e.z-r.z:r.id-e.id}function zf(){const r=[];let e=0;const t=[],n=[],i=[];function s(){e=0,t.length=0,n.length=0,i.length=0}function o(f,h,d,_,g,p){let m=r[e];return m===void 0?(m={id:f.id,object:f,geometry:h,material:d,groupOrder:_,renderOrder:f.renderOrder,z:g,group:p},r[e]=m):(m.id=f.id,m.object=f,m.geometry=h,m.material=d,m.groupOrder=_,m.renderOrder=f.renderOrder,m.z=g,m.group=p),e++,m}function a(f,h,d,_,g,p){const m=o(f,h,d,_,g,p);d.transmission>0?n.push(m):d.transparent===!0?i.push(m):t.push(m)}function l(f,h,d,_,g,p){const m=o(f,h,d,_,g,p);d.transmission>0?n.unshift(m):d.transparent===!0?i.unshift(m):t.unshift(m)}function c(f,h){t.length>1&&t.sort(f||RM),n.length>1&&n.sort(h||Bf),i.length>1&&i.sort(h||Bf)}function u(){for(let f=e,h=r.length;f<h;f++){const d=r[f];if(d.id===null)break;d.id=null,d.object=null,d.geometry=null,d.material=null,d.group=null}}return{opaque:t,transmissive:n,transparent:i,init:s,push:a,unshift:l,finish:u,sort:c}}function CM(){let r=new WeakMap;function e(n,i){const s=r.get(n);let o;return s===void 0?(o=new zf,r.set(n,[o])):i>=s.length?(o=new zf,s.push(o)):o=s[i],o}function t(){r=new WeakMap}return{get:e,dispose:t}}function PM(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={direction:new Y,color:new at};break;case"SpotLight":t={position:new Y,direction:new Y,color:new at,distance:0,coneCos:0,penumbraCos:0,decay:0};break;case"PointLight":t={position:new Y,color:new at,distance:0,decay:0};break;case"HemisphereLight":t={direction:new Y,skyColor:new at,groundColor:new at};break;case"RectAreaLight":t={color:new at,position:new Y,halfWidth:new Y,halfHeight:new Y};break}return r[e.id]=t,t}}}function DM(){const r={};return{get:function(e){if(r[e.id]!==void 0)return r[e.id];let t;switch(e.type){case"DirectionalLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new St};break;case"SpotLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new St};break;case"PointLight":t={shadowIntensity:1,shadowBias:0,shadowNormalBias:0,shadowRadius:1,shadowMapSize:new St,shadowCameraNear:1,shadowCameraFar:1e3};break}return r[e.id]=t,t}}}let LM=0;function IM(r,e){return(e.castShadow?2:0)-(r.castShadow?2:0)+(e.map?1:0)-(r.map?1:0)}function UM(r){const e=new PM,t=DM(),n={version:0,hash:{directionalLength:-1,pointLength:-1,spotLength:-1,rectAreaLength:-1,hemiLength:-1,numDirectionalShadows:-1,numPointShadows:-1,numSpotShadows:-1,numSpotMaps:-1,numLightProbes:-1},ambient:[0,0,0],probe:[],directional:[],directionalShadow:[],directionalShadowMap:[],directionalShadowMatrix:[],spot:[],spotLightMap:[],spotShadow:[],spotShadowMap:[],spotLightMatrix:[],rectArea:[],rectAreaLTC1:null,rectAreaLTC2:null,point:[],pointShadow:[],pointShadowMap:[],pointShadowMatrix:[],hemi:[],numSpotLightShadowsWithMaps:0,numLightProbes:0};for(let c=0;c<9;c++)n.probe.push(new Y);const i=new Y,s=new Ot,o=new Ot;function a(c){let u=0,f=0,h=0;for(let O=0;O<9;O++)n.probe[O].set(0,0,0);let d=0,_=0,g=0,p=0,m=0,y=0,x=0,M=0,R=0,w=0,E=0;c.sort(IM);for(let O=0,v=c.length;O<v;O++){const T=c[O],N=T.color,z=T.intensity,W=T.distance,K=T.shadow&&T.shadow.map?T.shadow.map.texture:null;if(T.isAmbientLight)u+=N.r*z,f+=N.g*z,h+=N.b*z;else if(T.isLightProbe){for(let G=0;G<9;G++)n.probe[G].addScaledVector(T.sh.coefficients[G],z);E++}else if(T.isDirectionalLight){const G=e.get(T);if(G.color.copy(T.color).multiplyScalar(T.intensity),T.castShadow){const X=T.shadow,V=t.get(T);V.shadowIntensity=X.intensity,V.shadowBias=X.bias,V.shadowNormalBias=X.normalBias,V.shadowRadius=X.radius,V.shadowMapSize=X.mapSize,n.directionalShadow[d]=V,n.directionalShadowMap[d]=K,n.directionalShadowMatrix[d]=T.shadow.matrix,y++}n.directional[d]=G,d++}else if(T.isSpotLight){const G=e.get(T);G.position.setFromMatrixPosition(T.matrixWorld),G.color.copy(N).multiplyScalar(z),G.distance=W,G.coneCos=Math.cos(T.angle),G.penumbraCos=Math.cos(T.angle*(1-T.penumbra)),G.decay=T.decay,n.spot[g]=G;const X=T.shadow;if(T.map&&(n.spotLightMap[R]=T.map,R++,X.updateMatrices(T),T.castShadow&&w++),n.spotLightMatrix[g]=X.matrix,T.castShadow){const V=t.get(T);V.shadowIntensity=X.intensity,V.shadowBias=X.bias,V.shadowNormalBias=X.normalBias,V.shadowRadius=X.radius,V.shadowMapSize=X.mapSize,n.spotShadow[g]=V,n.spotShadowMap[g]=K,M++}g++}else if(T.isRectAreaLight){const G=e.get(T);G.color.copy(N).multiplyScalar(z),G.halfWidth.set(T.width*.5,0,0),G.halfHeight.set(0,T.height*.5,0),n.rectArea[p]=G,p++}else if(T.isPointLight){const G=e.get(T);if(G.color.copy(T.color).multiplyScalar(T.intensity),G.distance=T.distance,G.decay=T.decay,T.castShadow){const X=T.shadow,V=t.get(T);V.shadowIntensity=X.intensity,V.shadowBias=X.bias,V.shadowNormalBias=X.normalBias,V.shadowRadius=X.radius,V.shadowMapSize=X.mapSize,V.shadowCameraNear=X.camera.near,V.shadowCameraFar=X.camera.far,n.pointShadow[_]=V,n.pointShadowMap[_]=K,n.pointShadowMatrix[_]=T.shadow.matrix,x++}n.point[_]=G,_++}else if(T.isHemisphereLight){const G=e.get(T);G.skyColor.copy(T.color).multiplyScalar(z),G.groundColor.copy(T.groundColor).multiplyScalar(z),n.hemi[m]=G,m++}}p>0&&(r.has("OES_texture_float_linear")===!0?(n.rectAreaLTC1=me.LTC_FLOAT_1,n.rectAreaLTC2=me.LTC_FLOAT_2):(n.rectAreaLTC1=me.LTC_HALF_1,n.rectAreaLTC2=me.LTC_HALF_2)),n.ambient[0]=u,n.ambient[1]=f,n.ambient[2]=h;const D=n.hash;(D.directionalLength!==d||D.pointLength!==_||D.spotLength!==g||D.rectAreaLength!==p||D.hemiLength!==m||D.numDirectionalShadows!==y||D.numPointShadows!==x||D.numSpotShadows!==M||D.numSpotMaps!==R||D.numLightProbes!==E)&&(n.directional.length=d,n.spot.length=g,n.rectArea.length=p,n.point.length=_,n.hemi.length=m,n.directionalShadow.length=y,n.directionalShadowMap.length=y,n.pointShadow.length=x,n.pointShadowMap.length=x,n.spotShadow.length=M,n.spotShadowMap.length=M,n.directionalShadowMatrix.length=y,n.pointShadowMatrix.length=x,n.spotLightMatrix.length=M+R-w,n.spotLightMap.length=R,n.numSpotLightShadowsWithMaps=w,n.numLightProbes=E,D.directionalLength=d,D.pointLength=_,D.spotLength=g,D.rectAreaLength=p,D.hemiLength=m,D.numDirectionalShadows=y,D.numPointShadows=x,D.numSpotShadows=M,D.numSpotMaps=R,D.numLightProbes=E,n.version=LM++)}function l(c,u){let f=0,h=0,d=0,_=0,g=0;const p=u.matrixWorldInverse;for(let m=0,y=c.length;m<y;m++){const x=c[m];if(x.isDirectionalLight){const M=n.directional[f];M.direction.setFromMatrixPosition(x.matrixWorld),i.setFromMatrixPosition(x.target.matrixWorld),M.direction.sub(i),M.direction.transformDirection(p),f++}else if(x.isSpotLight){const M=n.spot[d];M.position.setFromMatrixPosition(x.matrixWorld),M.position.applyMatrix4(p),M.direction.setFromMatrixPosition(x.matrixWorld),i.setFromMatrixPosition(x.target.matrixWorld),M.direction.sub(i),M.direction.transformDirection(p),d++}else if(x.isRectAreaLight){const M=n.rectArea[_];M.position.setFromMatrixPosition(x.matrixWorld),M.position.applyMatrix4(p),o.identity(),s.copy(x.matrixWorld),s.premultiply(p),o.extractRotation(s),M.halfWidth.set(x.width*.5,0,0),M.halfHeight.set(0,x.height*.5,0),M.halfWidth.applyMatrix4(o),M.halfHeight.applyMatrix4(o),_++}else if(x.isPointLight){const M=n.point[h];M.position.setFromMatrixPosition(x.matrixWorld),M.position.applyMatrix4(p),h++}else if(x.isHemisphereLight){const M=n.hemi[g];M.direction.setFromMatrixPosition(x.matrixWorld),M.direction.transformDirection(p),g++}}}return{setup:a,setupView:l,state:n}}function kf(r){const e=new UM(r),t=[],n=[];function i(u){c.camera=u,t.length=0,n.length=0}function s(u){t.push(u)}function o(u){n.push(u)}function a(){e.setup(t)}function l(u){e.setupView(t,u)}const c={lightsArray:t,shadowsArray:n,camera:null,lights:e,transmissionRenderTarget:{}};return{init:i,state:c,setupLights:a,setupLightsView:l,pushLight:s,pushShadow:o}}function NM(r){let e=new WeakMap;function t(i,s=0){const o=e.get(i);let a;return o===void 0?(a=new kf(r),e.set(i,[a])):s>=o.length?(a=new kf(r),o.push(a)):a=o[s],a}function n(){e=new WeakMap}return{get:t,dispose:n}}class FM extends Fo{constructor(e){super(),this.isMeshDepthMaterial=!0,this.type="MeshDepthMaterial",this.depthPacking=Cg,this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.wireframe=!1,this.wireframeLinewidth=1,this.setValues(e)}copy(e){return super.copy(e),this.depthPacking=e.depthPacking,this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this.wireframe=e.wireframe,this.wireframeLinewidth=e.wireframeLinewidth,this}}class OM extends Fo{constructor(e){super(),this.isMeshDistanceMaterial=!0,this.type="MeshDistanceMaterial",this.map=null,this.alphaMap=null,this.displacementMap=null,this.displacementScale=1,this.displacementBias=0,this.setValues(e)}copy(e){return super.copy(e),this.map=e.map,this.alphaMap=e.alphaMap,this.displacementMap=e.displacementMap,this.displacementScale=e.displacementScale,this.displacementBias=e.displacementBias,this}}const BM=`void main() {
	gl_Position = vec4( position, 1.0 );
}`,zM=`uniform sampler2D shadow_pass;
uniform vec2 resolution;
uniform float radius;
#include <packing>
void main() {
	const float samples = float( VSM_SAMPLES );
	float mean = 0.0;
	float squared_mean = 0.0;
	float uvStride = samples <= 1.0 ? 0.0 : 2.0 / ( samples - 1.0 );
	float uvStart = samples <= 1.0 ? 0.0 : - 1.0;
	for ( float i = 0.0; i < samples; i ++ ) {
		float uvOffset = uvStart + i * uvStride;
		#ifdef HORIZONTAL_PASS
			vec2 distribution = unpackRGBATo2Half( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( uvOffset, 0.0 ) * radius ) / resolution ) );
			mean += distribution.x;
			squared_mean += distribution.y * distribution.y + distribution.x * distribution.x;
		#else
			float depth = unpackRGBAToDepth( texture2D( shadow_pass, ( gl_FragCoord.xy + vec2( 0.0, uvOffset ) * radius ) / resolution ) );
			mean += depth;
			squared_mean += depth * depth;
		#endif
	}
	mean = mean / samples;
	squared_mean = squared_mean / samples;
	float std_dev = sqrt( squared_mean - mean * mean );
	gl_FragColor = pack2HalfToRGBA( vec2( mean, std_dev ) );
}`;function kM(r,e,t){let n=new Gp;const i=new St,s=new St,o=new Nt,a=new FM({depthPacking:Pg}),l=new OM,c={},u=t.maxTextureSize,f={[hr]:_n,[_n]:hr,[Di]:Di},h=new ei({defines:{VSM_SAMPLES:8},uniforms:{shadow_pass:{value:null},resolution:{value:new St},radius:{value:4}},vertexShader:BM,fragmentShader:zM}),d=h.clone();d.defines.HORIZONTAL_PASS=1;const _=new fi;_.setAttribute("position",new Zt(new Float32Array([-1,-1,.5,3,-1,.5,-1,3,.5]),3));const g=new hi(_,h),p=this;this.enabled=!1,this.autoUpdate=!0,this.needsUpdate=!1,this.type=_p;let m=this.type;this.render=function(w,E,D){if(p.enabled===!1||p.autoUpdate===!1&&p.needsUpdate===!1||w.length===0)return;const O=r.getRenderTarget(),v=r.getActiveCubeFace(),T=r.getActiveMipmapLevel(),N=r.state;N.setBlending(sr),N.buffers.color.setClear(1,1,1,1),N.buffers.depth.setTest(!0),N.setScissorTest(!1);const z=m!==Ai&&this.type===Ai,W=m===Ai&&this.type!==Ai;for(let K=0,G=w.length;K<G;K++){const X=w[K],V=X.shadow;if(V===void 0){console.warn("THREE.WebGLShadowMap:",X,"has no shadow.");continue}if(V.autoUpdate===!1&&V.needsUpdate===!1)continue;i.copy(V.mapSize);const re=V.getFrameExtents();if(i.multiply(re),s.copy(V.mapSize),(i.x>u||i.y>u)&&(i.x>u&&(s.x=Math.floor(u/re.x),i.x=s.x*re.x,V.mapSize.x=s.x),i.y>u&&(s.y=Math.floor(u/re.y),i.y=s.y*re.y,V.mapSize.y=s.y)),V.map===null||z===!0||W===!0){const ae=this.type!==Ai?{minFilter:Jn,magFilter:Jn}:{};V.map!==null&&V.map.dispose(),V.map=new Xr(i.x,i.y,ae),V.map.texture.name=X.name+".shadowMap",V.camera.updateProjectionMatrix()}r.setRenderTarget(V.map),r.clear();const C=V.getViewportCount();for(let ae=0;ae<C;ae++){const Be=V.getViewport(ae);o.set(s.x*Be.x,s.y*Be.y,s.x*Be.z,s.y*Be.w),N.viewport(o),V.updateMatrices(X,ae),n=V.getFrustum(),M(E,D,V.camera,X,this.type)}V.isPointLightShadow!==!0&&this.type===Ai&&y(V,D),V.needsUpdate=!1}m=this.type,p.needsUpdate=!1,r.setRenderTarget(O,v,T)};function y(w,E){const D=e.update(g);h.defines.VSM_SAMPLES!==w.blurSamples&&(h.defines.VSM_SAMPLES=w.blurSamples,d.defines.VSM_SAMPLES=w.blurSamples,h.needsUpdate=!0,d.needsUpdate=!0),w.mapPass===null&&(w.mapPass=new Xr(i.x,i.y)),h.uniforms.shadow_pass.value=w.map.texture,h.uniforms.resolution.value=w.mapSize,h.uniforms.radius.value=w.radius,r.setRenderTarget(w.mapPass),r.clear(),r.renderBufferDirect(E,null,D,h,g,null),d.uniforms.shadow_pass.value=w.mapPass.texture,d.uniforms.resolution.value=w.mapSize,d.uniforms.radius.value=w.radius,r.setRenderTarget(w.map),r.clear(),r.renderBufferDirect(E,null,D,d,g,null)}function x(w,E,D,O){let v=null;const T=D.isPointLight===!0?w.customDistanceMaterial:w.customDepthMaterial;if(T!==void 0)v=T;else if(v=D.isPointLight===!0?l:a,r.localClippingEnabled&&E.clipShadows===!0&&Array.isArray(E.clippingPlanes)&&E.clippingPlanes.length!==0||E.displacementMap&&E.displacementScale!==0||E.alphaMap&&E.alphaTest>0||E.map&&E.alphaTest>0){const N=v.uuid,z=E.uuid;let W=c[N];W===void 0&&(W={},c[N]=W);let K=W[z];K===void 0&&(K=v.clone(),W[z]=K,E.addEventListener("dispose",R)),v=K}if(v.visible=E.visible,v.wireframe=E.wireframe,O===Ai?v.side=E.shadowSide!==null?E.shadowSide:E.side:v.side=E.shadowSide!==null?E.shadowSide:f[E.side],v.alphaMap=E.alphaMap,v.alphaTest=E.alphaTest,v.map=E.map,v.clipShadows=E.clipShadows,v.clippingPlanes=E.clippingPlanes,v.clipIntersection=E.clipIntersection,v.displacementMap=E.displacementMap,v.displacementScale=E.displacementScale,v.displacementBias=E.displacementBias,v.wireframeLinewidth=E.wireframeLinewidth,v.linewidth=E.linewidth,D.isPointLight===!0&&v.isMeshDistanceMaterial===!0){const N=r.properties.get(v);N.light=D}return v}function M(w,E,D,O,v){if(w.visible===!1)return;if(w.layers.test(E.layers)&&(w.isMesh||w.isLine||w.isPoints)&&(w.castShadow||w.receiveShadow&&v===Ai)&&(!w.frustumCulled||n.intersectsObject(w))){w.modelViewMatrix.multiplyMatrices(D.matrixWorldInverse,w.matrixWorld);const z=e.update(w),W=w.material;if(Array.isArray(W)){const K=z.groups;for(let G=0,X=K.length;G<X;G++){const V=K[G],re=W[V.materialIndex];if(re&&re.visible){const C=x(w,re,O,v);w.onBeforeShadow(r,w,E,D,z,C,V),r.renderBufferDirect(D,null,z,C,w,V),w.onAfterShadow(r,w,E,D,z,C,V)}}}else if(W.visible){const K=x(w,W,O,v);w.onBeforeShadow(r,w,E,D,z,K,null),r.renderBufferDirect(D,null,z,K,w,null),w.onAfterShadow(r,w,E,D,z,K,null)}}const N=w.children;for(let z=0,W=N.length;z<W;z++)M(N[z],E,D,O,v)}function R(w){w.target.removeEventListener("dispose",R);for(const D in c){const O=c[D],v=w.target.uuid;v in O&&(O[v].dispose(),delete O[v])}}}const HM={[Oc]:Bc,[zc]:Gc,[kc]:Vc,[Fs]:Hc,[Bc]:Oc,[Gc]:zc,[Vc]:kc,[Hc]:Fs};function GM(r){function e(){let L=!1;const ee=new Nt;let $=null;const J=new Nt(0,0,0,0);return{setMask:function(le){$!==le&&!L&&(r.colorMask(le,le,le,le),$=le)},setLocked:function(le){L=le},setClear:function(le,ce,Ye,_t,Tt){Tt===!0&&(le*=_t,ce*=_t,Ye*=_t),ee.set(le,ce,Ye,_t),J.equals(ee)===!1&&(r.clearColor(le,ce,Ye,_t),J.copy(ee))},reset:function(){L=!1,$=null,J.set(-1,0,0,0)}}}function t(){let L=!1,ee=!1,$=null,J=null,le=null;return{setReversed:function(ce){ee=ce},setTest:function(ce){ce?fe(r.DEPTH_TEST):oe(r.DEPTH_TEST)},setMask:function(ce){$!==ce&&!L&&(r.depthMask(ce),$=ce)},setFunc:function(ce){if(ee&&(ce=HM[ce]),J!==ce){switch(ce){case Oc:r.depthFunc(r.NEVER);break;case Bc:r.depthFunc(r.ALWAYS);break;case zc:r.depthFunc(r.LESS);break;case Fs:r.depthFunc(r.LEQUAL);break;case kc:r.depthFunc(r.EQUAL);break;case Hc:r.depthFunc(r.GEQUAL);break;case Gc:r.depthFunc(r.GREATER);break;case Vc:r.depthFunc(r.NOTEQUAL);break;default:r.depthFunc(r.LEQUAL)}J=ce}},setLocked:function(ce){L=ce},setClear:function(ce){le!==ce&&(r.clearDepth(ce),le=ce)},reset:function(){L=!1,$=null,J=null,le=null}}}function n(){let L=!1,ee=null,$=null,J=null,le=null,ce=null,Ye=null,_t=null,Tt=null;return{setTest:function(nt){L||(nt?fe(r.STENCIL_TEST):oe(r.STENCIL_TEST))},setMask:function(nt){ee!==nt&&!L&&(r.stencilMask(nt),ee=nt)},setFunc:function(nt,Re,Te){($!==nt||J!==Re||le!==Te)&&(r.stencilFunc(nt,Re,Te),$=nt,J=Re,le=Te)},setOp:function(nt,Re,Te){(ce!==nt||Ye!==Re||_t!==Te)&&(r.stencilOp(nt,Re,Te),ce=nt,Ye=Re,_t=Te)},setLocked:function(nt){L=nt},setClear:function(nt){Tt!==nt&&(r.clearStencil(nt),Tt=nt)},reset:function(){L=!1,ee=null,$=null,J=null,le=null,ce=null,Ye=null,_t=null,Tt=null}}}const i=new e,s=new t,o=new n,a=new WeakMap,l=new WeakMap;let c={},u={},f=new WeakMap,h=[],d=null,_=!1,g=null,p=null,m=null,y=null,x=null,M=null,R=null,w=new at(0,0,0),E=0,D=!1,O=null,v=null,T=null,N=null,z=null;const W=r.getParameter(r.MAX_COMBINED_TEXTURE_IMAGE_UNITS);let K=!1,G=0;const X=r.getParameter(r.VERSION);X.indexOf("WebGL")!==-1?(G=parseFloat(/^WebGL (\d)/.exec(X)[1]),K=G>=1):X.indexOf("OpenGL ES")!==-1&&(G=parseFloat(/^OpenGL ES (\d)/.exec(X)[1]),K=G>=2);let V=null,re={};const C=r.getParameter(r.SCISSOR_BOX),ae=r.getParameter(r.VIEWPORT),Be=new Nt().fromArray(C),We=new Nt().fromArray(ae);function q(L,ee,$,J){const le=new Uint8Array(4),ce=r.createTexture();r.bindTexture(L,ce),r.texParameteri(L,r.TEXTURE_MIN_FILTER,r.NEAREST),r.texParameteri(L,r.TEXTURE_MAG_FILTER,r.NEAREST);for(let Ye=0;Ye<$;Ye++)L===r.TEXTURE_3D||L===r.TEXTURE_2D_ARRAY?r.texImage3D(ee,0,r.RGBA,1,1,J,0,r.RGBA,r.UNSIGNED_BYTE,le):r.texImage2D(ee+Ye,0,r.RGBA,1,1,0,r.RGBA,r.UNSIGNED_BYTE,le);return ce}const Q={};Q[r.TEXTURE_2D]=q(r.TEXTURE_2D,r.TEXTURE_2D,1),Q[r.TEXTURE_CUBE_MAP]=q(r.TEXTURE_CUBE_MAP,r.TEXTURE_CUBE_MAP_POSITIVE_X,6),Q[r.TEXTURE_2D_ARRAY]=q(r.TEXTURE_2D_ARRAY,r.TEXTURE_2D_ARRAY,1,1),Q[r.TEXTURE_3D]=q(r.TEXTURE_3D,r.TEXTURE_3D,1,1),i.setClear(0,0,0,1),s.setClear(1),o.setClear(0),fe(r.DEPTH_TEST),s.setFunc(Fs),Fe(!1),ze($h),fe(r.CULL_FACE),P(sr);function fe(L){c[L]!==!0&&(r.enable(L),c[L]=!0)}function oe(L){c[L]!==!1&&(r.disable(L),c[L]=!1)}function we(L,ee){return u[L]!==ee?(r.bindFramebuffer(L,ee),u[L]=ee,L===r.DRAW_FRAMEBUFFER&&(u[r.FRAMEBUFFER]=ee),L===r.FRAMEBUFFER&&(u[r.DRAW_FRAMEBUFFER]=ee),!0):!1}function ye(L,ee){let $=h,J=!1;if(L){$=f.get(ee),$===void 0&&($=[],f.set(ee,$));const le=L.textures;if($.length!==le.length||$[0]!==r.COLOR_ATTACHMENT0){for(let ce=0,Ye=le.length;ce<Ye;ce++)$[ce]=r.COLOR_ATTACHMENT0+ce;$.length=le.length,J=!0}}else $[0]!==r.BACK&&($[0]=r.BACK,J=!0);J&&r.drawBuffers($)}function Ve(L){return d!==L?(r.useProgram(L),d=L,!0):!1}const Ge={[Ar]:r.FUNC_ADD,[ng]:r.FUNC_SUBTRACT,[ig]:r.FUNC_REVERSE_SUBTRACT};Ge[rg]=r.MIN,Ge[sg]=r.MAX;const Ne={[og]:r.ZERO,[ag]:r.ONE,[lg]:r.SRC_COLOR,[Nc]:r.SRC_ALPHA,[pg]:r.SRC_ALPHA_SATURATE,[fg]:r.DST_COLOR,[ug]:r.DST_ALPHA,[cg]:r.ONE_MINUS_SRC_COLOR,[Fc]:r.ONE_MINUS_SRC_ALPHA,[dg]:r.ONE_MINUS_DST_COLOR,[hg]:r.ONE_MINUS_DST_ALPHA,[mg]:r.CONSTANT_COLOR,[_g]:r.ONE_MINUS_CONSTANT_COLOR,[gg]:r.CONSTANT_ALPHA,[vg]:r.ONE_MINUS_CONSTANT_ALPHA};function P(L,ee,$,J,le,ce,Ye,_t,Tt,nt){if(L===sr){_===!0&&(oe(r.BLEND),_=!1);return}if(_===!1&&(fe(r.BLEND),_=!0),L!==tg){if(L!==g||nt!==D){if((p!==Ar||x!==Ar)&&(r.blendEquation(r.FUNC_ADD),p=Ar,x=Ar),nt)switch(L){case zr:r.blendFuncSeparate(r.ONE,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Uc:r.blendFunc(r.ONE,r.ONE);break;case Kh:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Zh:r.blendFuncSeparate(r.ZERO,r.SRC_COLOR,r.ZERO,r.SRC_ALPHA);break;default:console.error("THREE.WebGLState: Invalid blending: ",L);break}else switch(L){case zr:r.blendFuncSeparate(r.SRC_ALPHA,r.ONE_MINUS_SRC_ALPHA,r.ONE,r.ONE_MINUS_SRC_ALPHA);break;case Uc:r.blendFunc(r.SRC_ALPHA,r.ONE);break;case Kh:r.blendFuncSeparate(r.ZERO,r.ONE_MINUS_SRC_COLOR,r.ZERO,r.ONE);break;case Zh:r.blendFunc(r.ZERO,r.SRC_COLOR);break;default:console.error("THREE.WebGLState: Invalid blending: ",L);break}m=null,y=null,M=null,R=null,w.set(0,0,0),E=0,g=L,D=nt}return}le=le||ee,ce=ce||$,Ye=Ye||J,(ee!==p||le!==x)&&(r.blendEquationSeparate(Ge[ee],Ge[le]),p=ee,x=le),($!==m||J!==y||ce!==M||Ye!==R)&&(r.blendFuncSeparate(Ne[$],Ne[J],Ne[ce],Ne[Ye]),m=$,y=J,M=ce,R=Ye),(_t.equals(w)===!1||Tt!==E)&&(r.blendColor(_t.r,_t.g,_t.b,Tt),w.copy(_t),E=Tt),g=L,D=!1}function rt(L,ee){L.side===Di?oe(r.CULL_FACE):fe(r.CULL_FACE);let $=L.side===_n;ee&&($=!$),Fe($),L.blending===zr&&L.transparent===!1?P(sr):P(L.blending,L.blendEquation,L.blendSrc,L.blendDst,L.blendEquationAlpha,L.blendSrcAlpha,L.blendDstAlpha,L.blendColor,L.blendAlpha,L.premultipliedAlpha),s.setFunc(L.depthFunc),s.setTest(L.depthTest),s.setMask(L.depthWrite),i.setMask(L.colorWrite);const J=L.stencilWrite;o.setTest(J),J&&(o.setMask(L.stencilWriteMask),o.setFunc(L.stencilFunc,L.stencilRef,L.stencilFuncMask),o.setOp(L.stencilFail,L.stencilZFail,L.stencilZPass)),je(L.polygonOffset,L.polygonOffsetFactor,L.polygonOffsetUnits),L.alphaToCoverage===!0?fe(r.SAMPLE_ALPHA_TO_COVERAGE):oe(r.SAMPLE_ALPHA_TO_COVERAGE)}function Fe(L){O!==L&&(L?r.frontFace(r.CW):r.frontFace(r.CCW),O=L)}function ze(L){L!==J_?(fe(r.CULL_FACE),L!==v&&(L===$h?r.cullFace(r.BACK):L===Q_?r.cullFace(r.FRONT):r.cullFace(r.FRONT_AND_BACK))):oe(r.CULL_FACE),v=L}function F(L){L!==T&&(K&&r.lineWidth(L),T=L)}function je(L,ee,$){L?(fe(r.POLYGON_OFFSET_FILL),(N!==ee||z!==$)&&(r.polygonOffset(ee,$),N=ee,z=$)):oe(r.POLYGON_OFFSET_FILL)}function De(L){L?fe(r.SCISSOR_TEST):oe(r.SCISSOR_TEST)}function A(L){L===void 0&&(L=r.TEXTURE0+W-1),V!==L&&(r.activeTexture(L),V=L)}function S(L,ee,$){$===void 0&&(V===null?$=r.TEXTURE0+W-1:$=V);let J=re[$];J===void 0&&(J={type:void 0,texture:void 0},re[$]=J),(J.type!==L||J.texture!==ee)&&(V!==$&&(r.activeTexture($),V=$),r.bindTexture(L,ee||Q[L]),J.type=L,J.texture=ee)}function H(){const L=re[V];L!==void 0&&L.type!==void 0&&(r.bindTexture(L.type,null),L.type=void 0,L.texture=void 0)}function j(){try{r.compressedTexImage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function te(){try{r.compressedTexImage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function Z(){try{r.texSubImage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function Se(){try{r.texSubImage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function ie(){try{r.compressedTexSubImage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function de(){try{r.compressedTexSubImage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function He(){try{r.texStorage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function ne(){try{r.texStorage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function ve(){try{r.texImage2D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function xe(){try{r.texImage3D.apply(r,arguments)}catch(L){console.error("THREE.WebGLState:",L)}}function Ie(L){Be.equals(L)===!1&&(r.scissor(L.x,L.y,L.z,L.w),Be.copy(L))}function ge(L){We.equals(L)===!1&&(r.viewport(L.x,L.y,L.z,L.w),We.copy(L))}function Xe(L,ee){let $=l.get(ee);$===void 0&&($=new WeakMap,l.set(ee,$));let J=$.get(L);J===void 0&&(J=r.getUniformBlockIndex(ee,L.name),$.set(L,J))}function Oe(L,ee){const J=l.get(ee).get(L);a.get(ee)!==J&&(r.uniformBlockBinding(ee,J,L.__bindingPointIndex),a.set(ee,J))}function st(){r.disable(r.BLEND),r.disable(r.CULL_FACE),r.disable(r.DEPTH_TEST),r.disable(r.POLYGON_OFFSET_FILL),r.disable(r.SCISSOR_TEST),r.disable(r.STENCIL_TEST),r.disable(r.SAMPLE_ALPHA_TO_COVERAGE),r.blendEquation(r.FUNC_ADD),r.blendFunc(r.ONE,r.ZERO),r.blendFuncSeparate(r.ONE,r.ZERO,r.ONE,r.ZERO),r.blendColor(0,0,0,0),r.colorMask(!0,!0,!0,!0),r.clearColor(0,0,0,0),r.depthMask(!0),r.depthFunc(r.LESS),r.clearDepth(1),r.stencilMask(4294967295),r.stencilFunc(r.ALWAYS,0,4294967295),r.stencilOp(r.KEEP,r.KEEP,r.KEEP),r.clearStencil(0),r.cullFace(r.BACK),r.frontFace(r.CCW),r.polygonOffset(0,0),r.activeTexture(r.TEXTURE0),r.bindFramebuffer(r.FRAMEBUFFER,null),r.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),r.bindFramebuffer(r.READ_FRAMEBUFFER,null),r.useProgram(null),r.lineWidth(1),r.scissor(0,0,r.canvas.width,r.canvas.height),r.viewport(0,0,r.canvas.width,r.canvas.height),c={},V=null,re={},u={},f=new WeakMap,h=[],d=null,_=!1,g=null,p=null,m=null,y=null,x=null,M=null,R=null,w=new at(0,0,0),E=0,D=!1,O=null,v=null,T=null,N=null,z=null,Be.set(0,0,r.canvas.width,r.canvas.height),We.set(0,0,r.canvas.width,r.canvas.height),i.reset(),s.reset(),o.reset()}return{buffers:{color:i,depth:s,stencil:o},enable:fe,disable:oe,bindFramebuffer:we,drawBuffers:ye,useProgram:Ve,setBlending:P,setMaterial:rt,setFlipSided:Fe,setCullFace:ze,setLineWidth:F,setPolygonOffset:je,setScissorTest:De,activeTexture:A,bindTexture:S,unbindTexture:H,compressedTexImage2D:j,compressedTexImage3D:te,texImage2D:ve,texImage3D:xe,updateUBOMapping:Xe,uniformBlockBinding:Oe,texStorage2D:He,texStorage3D:ne,texSubImage2D:Z,texSubImage3D:Se,compressedTexSubImage2D:ie,compressedTexSubImage3D:de,scissor:Ie,viewport:ge,reset:st}}function Hf(r,e,t,n){const i=VM(n);switch(t){case yp:return r*e;case Tp:return r*e;case bp:return r*e*2;case wp:return r*e/i.components*i.byteLength;case nh:return r*e/i.components*i.byteLength;case Ap:return r*e*2/i.components*i.byteLength;case ih:return r*e*2/i.components*i.byteLength;case Ep:return r*e*3/i.components*i.byteLength;case ui:return r*e*4/i.components*i.byteLength;case rh:return r*e*4/i.components*i.byteLength;case La:case Ia:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case Ua:case Na:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case Kc:case jc:return Math.max(r,16)*Math.max(e,8)/4;case $c:case Zc:return Math.max(r,8)*Math.max(e,8)/2;case Jc:case Qc:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*8;case eu:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case tu:return Math.floor((r+3)/4)*Math.floor((e+3)/4)*16;case nu:return Math.floor((r+4)/5)*Math.floor((e+3)/4)*16;case iu:return Math.floor((r+4)/5)*Math.floor((e+4)/5)*16;case ru:return Math.floor((r+5)/6)*Math.floor((e+4)/5)*16;case su:return Math.floor((r+5)/6)*Math.floor((e+5)/6)*16;case ou:return Math.floor((r+7)/8)*Math.floor((e+4)/5)*16;case au:return Math.floor((r+7)/8)*Math.floor((e+5)/6)*16;case lu:return Math.floor((r+7)/8)*Math.floor((e+7)/8)*16;case cu:return Math.floor((r+9)/10)*Math.floor((e+4)/5)*16;case uu:return Math.floor((r+9)/10)*Math.floor((e+5)/6)*16;case hu:return Math.floor((r+9)/10)*Math.floor((e+7)/8)*16;case fu:return Math.floor((r+9)/10)*Math.floor((e+9)/10)*16;case du:return Math.floor((r+11)/12)*Math.floor((e+9)/10)*16;case pu:return Math.floor((r+11)/12)*Math.floor((e+11)/12)*16;case Fa:case mu:case _u:return Math.ceil(r/4)*Math.ceil(e/4)*16;case Rp:case gu:return Math.ceil(r/4)*Math.ceil(e/4)*8;case vu:case xu:return Math.ceil(r/4)*Math.ceil(e/4)*16}throw new Error(`Unable to determine texture byte length for ${t} format.`)}function VM(r){switch(r){case zi:case xp:return{byteLength:1,components:1};case Po:case Sp:case Lo:return{byteLength:2,components:1};case eh:case th:return{byteLength:2,components:4};case Wr:case Qu:case Ui:return{byteLength:4,components:1};case Mp:return{byteLength:4,components:3}}throw new Error(`Unknown texture type ${r}.`)}function WM(r,e,t,n,i,s,o){const a=e.has("WEBGL_multisampled_render_to_texture")?e.get("WEBGL_multisampled_render_to_texture"):null,l=typeof navigator>"u"?!1:/OculusBrowser/g.test(navigator.userAgent),c=new St,u=new WeakMap;let f;const h=new WeakMap;let d=!1;try{d=typeof OffscreenCanvas<"u"&&new OffscreenCanvas(1,1).getContext("2d")!==null}catch{}function _(A,S){return d?new OffscreenCanvas(A,S):tl("canvas")}function g(A,S,H){let j=1;const te=De(A);if((te.width>H||te.height>H)&&(j=H/Math.max(te.width,te.height)),j<1)if(typeof HTMLImageElement<"u"&&A instanceof HTMLImageElement||typeof HTMLCanvasElement<"u"&&A instanceof HTMLCanvasElement||typeof ImageBitmap<"u"&&A instanceof ImageBitmap||typeof VideoFrame<"u"&&A instanceof VideoFrame){const Z=Math.floor(j*te.width),Se=Math.floor(j*te.height);f===void 0&&(f=_(Z,Se));const ie=S?_(Z,Se):f;return ie.width=Z,ie.height=Se,ie.getContext("2d").drawImage(A,0,0,Z,Se),console.warn("THREE.WebGLRenderer: Texture has been resized from ("+te.width+"x"+te.height+") to ("+Z+"x"+Se+")."),ie}else return"data"in A&&console.warn("THREE.WebGLRenderer: Image in DataTexture is too big ("+te.width+"x"+te.height+")."),A;return A}function p(A){return A.generateMipmaps&&A.minFilter!==Jn&&A.minFilter!==li}function m(A){r.generateMipmap(A)}function y(A,S,H,j,te=!1){if(A!==null){if(r[A]!==void 0)return r[A];console.warn("THREE.WebGLRenderer: Attempt to use non-existing WebGL internal format '"+A+"'")}let Z=S;if(S===r.RED&&(H===r.FLOAT&&(Z=r.R32F),H===r.HALF_FLOAT&&(Z=r.R16F),H===r.UNSIGNED_BYTE&&(Z=r.R8)),S===r.RED_INTEGER&&(H===r.UNSIGNED_BYTE&&(Z=r.R8UI),H===r.UNSIGNED_SHORT&&(Z=r.R16UI),H===r.UNSIGNED_INT&&(Z=r.R32UI),H===r.BYTE&&(Z=r.R8I),H===r.SHORT&&(Z=r.R16I),H===r.INT&&(Z=r.R32I)),S===r.RG&&(H===r.FLOAT&&(Z=r.RG32F),H===r.HALF_FLOAT&&(Z=r.RG16F),H===r.UNSIGNED_BYTE&&(Z=r.RG8)),S===r.RG_INTEGER&&(H===r.UNSIGNED_BYTE&&(Z=r.RG8UI),H===r.UNSIGNED_SHORT&&(Z=r.RG16UI),H===r.UNSIGNED_INT&&(Z=r.RG32UI),H===r.BYTE&&(Z=r.RG8I),H===r.SHORT&&(Z=r.RG16I),H===r.INT&&(Z=r.RG32I)),S===r.RGB_INTEGER&&(H===r.UNSIGNED_BYTE&&(Z=r.RGB8UI),H===r.UNSIGNED_SHORT&&(Z=r.RGB16UI),H===r.UNSIGNED_INT&&(Z=r.RGB32UI),H===r.BYTE&&(Z=r.RGB8I),H===r.SHORT&&(Z=r.RGB16I),H===r.INT&&(Z=r.RGB32I)),S===r.RGBA_INTEGER&&(H===r.UNSIGNED_BYTE&&(Z=r.RGBA8UI),H===r.UNSIGNED_SHORT&&(Z=r.RGBA16UI),H===r.UNSIGNED_INT&&(Z=r.RGBA32UI),H===r.BYTE&&(Z=r.RGBA8I),H===r.SHORT&&(Z=r.RGBA16I),H===r.INT&&(Z=r.RGBA32I)),S===r.RGB&&H===r.UNSIGNED_INT_5_9_9_9_REV&&(Z=r.RGB9_E5),S===r.RGBA){const Se=te?ja:ft.getTransfer(j);H===r.FLOAT&&(Z=r.RGBA32F),H===r.HALF_FLOAT&&(Z=r.RGBA16F),H===r.UNSIGNED_BYTE&&(Z=Se===Et?r.SRGB8_ALPHA8:r.RGBA8),H===r.UNSIGNED_SHORT_4_4_4_4&&(Z=r.RGBA4),H===r.UNSIGNED_SHORT_5_5_5_1&&(Z=r.RGB5_A1)}return(Z===r.R16F||Z===r.R32F||Z===r.RG16F||Z===r.RG32F||Z===r.RGBA16F||Z===r.RGBA32F)&&e.get("EXT_color_buffer_float"),Z}function x(A,S){let H;return A?S===null||S===Wr||S===zs?H=r.DEPTH24_STENCIL8:S===Ui?H=r.DEPTH32F_STENCIL8:S===Po&&(H=r.DEPTH24_STENCIL8,console.warn("DepthTexture: 16 bit depth attachment is not supported with stencil. Using 24-bit attachment.")):S===null||S===Wr||S===zs?H=r.DEPTH_COMPONENT24:S===Ui?H=r.DEPTH_COMPONENT32F:S===Po&&(H=r.DEPTH_COMPONENT16),H}function M(A,S){return p(A)===!0||A.isFramebufferTexture&&A.minFilter!==Jn&&A.minFilter!==li?Math.log2(Math.max(S.width,S.height))+1:A.mipmaps!==void 0&&A.mipmaps.length>0?A.mipmaps.length:A.isCompressedTexture&&Array.isArray(A.image)?S.mipmaps.length:1}function R(A){const S=A.target;S.removeEventListener("dispose",R),E(S),S.isVideoTexture&&u.delete(S)}function w(A){const S=A.target;S.removeEventListener("dispose",w),O(S)}function E(A){const S=n.get(A);if(S.__webglInit===void 0)return;const H=A.source,j=h.get(H);if(j){const te=j[S.__cacheKey];te.usedTimes--,te.usedTimes===0&&D(A),Object.keys(j).length===0&&h.delete(H)}n.remove(A)}function D(A){const S=n.get(A);r.deleteTexture(S.__webglTexture);const H=A.source,j=h.get(H);delete j[S.__cacheKey],o.memory.textures--}function O(A){const S=n.get(A);if(A.depthTexture&&A.depthTexture.dispose(),A.isWebGLCubeRenderTarget)for(let j=0;j<6;j++){if(Array.isArray(S.__webglFramebuffer[j]))for(let te=0;te<S.__webglFramebuffer[j].length;te++)r.deleteFramebuffer(S.__webglFramebuffer[j][te]);else r.deleteFramebuffer(S.__webglFramebuffer[j]);S.__webglDepthbuffer&&r.deleteRenderbuffer(S.__webglDepthbuffer[j])}else{if(Array.isArray(S.__webglFramebuffer))for(let j=0;j<S.__webglFramebuffer.length;j++)r.deleteFramebuffer(S.__webglFramebuffer[j]);else r.deleteFramebuffer(S.__webglFramebuffer);if(S.__webglDepthbuffer&&r.deleteRenderbuffer(S.__webglDepthbuffer),S.__webglMultisampledFramebuffer&&r.deleteFramebuffer(S.__webglMultisampledFramebuffer),S.__webglColorRenderbuffer)for(let j=0;j<S.__webglColorRenderbuffer.length;j++)S.__webglColorRenderbuffer[j]&&r.deleteRenderbuffer(S.__webglColorRenderbuffer[j]);S.__webglDepthRenderbuffer&&r.deleteRenderbuffer(S.__webglDepthRenderbuffer)}const H=A.textures;for(let j=0,te=H.length;j<te;j++){const Z=n.get(H[j]);Z.__webglTexture&&(r.deleteTexture(Z.__webglTexture),o.memory.textures--),n.remove(H[j])}n.remove(A)}let v=0;function T(){v=0}function N(){const A=v;return A>=i.maxTextures&&console.warn("THREE.WebGLTextures: Trying to use "+A+" texture units while this GPU supports only "+i.maxTextures),v+=1,A}function z(A){const S=[];return S.push(A.wrapS),S.push(A.wrapT),S.push(A.wrapR||0),S.push(A.magFilter),S.push(A.minFilter),S.push(A.anisotropy),S.push(A.internalFormat),S.push(A.format),S.push(A.type),S.push(A.generateMipmaps),S.push(A.premultiplyAlpha),S.push(A.flipY),S.push(A.unpackAlignment),S.push(A.colorSpace),S.join()}function W(A,S){const H=n.get(A);if(A.isVideoTexture&&F(A),A.isRenderTargetTexture===!1&&A.version>0&&H.__version!==A.version){const j=A.image;if(j===null)console.warn("THREE.WebGLRenderer: Texture marked for update but no image data found.");else if(j.complete===!1)console.warn("THREE.WebGLRenderer: Texture marked for update but image is incomplete");else{We(H,A,S);return}}t.bindTexture(r.TEXTURE_2D,H.__webglTexture,r.TEXTURE0+S)}function K(A,S){const H=n.get(A);if(A.version>0&&H.__version!==A.version){We(H,A,S);return}t.bindTexture(r.TEXTURE_2D_ARRAY,H.__webglTexture,r.TEXTURE0+S)}function G(A,S){const H=n.get(A);if(A.version>0&&H.__version!==A.version){We(H,A,S);return}t.bindTexture(r.TEXTURE_3D,H.__webglTexture,r.TEXTURE0+S)}function X(A,S){const H=n.get(A);if(A.version>0&&H.__version!==A.version){q(H,A,S);return}t.bindTexture(r.TEXTURE_CUBE_MAP,H.__webglTexture,r.TEXTURE0+S)}const V={[Yc]:r.REPEAT,[Ii]:r.CLAMP_TO_EDGE,[qc]:r.MIRRORED_REPEAT},re={[Jn]:r.NEAREST,[Rg]:r.NEAREST_MIPMAP_NEAREST,[Qo]:r.NEAREST_MIPMAP_LINEAR,[li]:r.LINEAR,[Rl]:r.LINEAR_MIPMAP_NEAREST,[Dr]:r.LINEAR_MIPMAP_LINEAR},C={[Ig]:r.NEVER,[zg]:r.ALWAYS,[Ug]:r.LESS,[Cp]:r.LEQUAL,[Ng]:r.EQUAL,[Bg]:r.GEQUAL,[Fg]:r.GREATER,[Og]:r.NOTEQUAL};function ae(A,S){if(S.type===Ui&&e.has("OES_texture_float_linear")===!1&&(S.magFilter===li||S.magFilter===Rl||S.magFilter===Qo||S.magFilter===Dr||S.minFilter===li||S.minFilter===Rl||S.minFilter===Qo||S.minFilter===Dr)&&console.warn("THREE.WebGLRenderer: Unable to use linear filtering with floating point textures. OES_texture_float_linear not supported on this device."),r.texParameteri(A,r.TEXTURE_WRAP_S,V[S.wrapS]),r.texParameteri(A,r.TEXTURE_WRAP_T,V[S.wrapT]),(A===r.TEXTURE_3D||A===r.TEXTURE_2D_ARRAY)&&r.texParameteri(A,r.TEXTURE_WRAP_R,V[S.wrapR]),r.texParameteri(A,r.TEXTURE_MAG_FILTER,re[S.magFilter]),r.texParameteri(A,r.TEXTURE_MIN_FILTER,re[S.minFilter]),S.compareFunction&&(r.texParameteri(A,r.TEXTURE_COMPARE_MODE,r.COMPARE_REF_TO_TEXTURE),r.texParameteri(A,r.TEXTURE_COMPARE_FUNC,C[S.compareFunction])),e.has("EXT_texture_filter_anisotropic")===!0){if(S.magFilter===Jn||S.minFilter!==Qo&&S.minFilter!==Dr||S.type===Ui&&e.has("OES_texture_float_linear")===!1)return;if(S.anisotropy>1||n.get(S).__currentAnisotropy){const H=e.get("EXT_texture_filter_anisotropic");r.texParameterf(A,H.TEXTURE_MAX_ANISOTROPY_EXT,Math.min(S.anisotropy,i.getMaxAnisotropy())),n.get(S).__currentAnisotropy=S.anisotropy}}}function Be(A,S){let H=!1;A.__webglInit===void 0&&(A.__webglInit=!0,S.addEventListener("dispose",R));const j=S.source;let te=h.get(j);te===void 0&&(te={},h.set(j,te));const Z=z(S);if(Z!==A.__cacheKey){te[Z]===void 0&&(te[Z]={texture:r.createTexture(),usedTimes:0},o.memory.textures++,H=!0),te[Z].usedTimes++;const Se=te[A.__cacheKey];Se!==void 0&&(te[A.__cacheKey].usedTimes--,Se.usedTimes===0&&D(S)),A.__cacheKey=Z,A.__webglTexture=te[Z].texture}return H}function We(A,S,H){let j=r.TEXTURE_2D;(S.isDataArrayTexture||S.isCompressedArrayTexture)&&(j=r.TEXTURE_2D_ARRAY),S.isData3DTexture&&(j=r.TEXTURE_3D);const te=Be(A,S),Z=S.source;t.bindTexture(j,A.__webglTexture,r.TEXTURE0+H);const Se=n.get(Z);if(Z.version!==Se.__version||te===!0){t.activeTexture(r.TEXTURE0+H);const ie=ft.getPrimaries(ft.workingColorSpace),de=S.colorSpace===Zi?null:ft.getPrimaries(S.colorSpace),He=S.colorSpace===Zi||ie===de?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,S.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,S.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,S.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,He);let ne=g(S.image,!1,i.maxTextureSize);ne=je(S,ne);const ve=s.convert(S.format,S.colorSpace),xe=s.convert(S.type);let Ie=y(S.internalFormat,ve,xe,S.colorSpace,S.isVideoTexture);ae(j,S);let ge;const Xe=S.mipmaps,Oe=S.isVideoTexture!==!0,st=Se.__version===void 0||te===!0,L=Z.dataReady,ee=M(S,ne);if(S.isDepthTexture)Ie=x(S.format===ks,S.type),st&&(Oe?t.texStorage2D(r.TEXTURE_2D,1,Ie,ne.width,ne.height):t.texImage2D(r.TEXTURE_2D,0,Ie,ne.width,ne.height,0,ve,xe,null));else if(S.isDataTexture)if(Xe.length>0){Oe&&st&&t.texStorage2D(r.TEXTURE_2D,ee,Ie,Xe[0].width,Xe[0].height);for(let $=0,J=Xe.length;$<J;$++)ge=Xe[$],Oe?L&&t.texSubImage2D(r.TEXTURE_2D,$,0,0,ge.width,ge.height,ve,xe,ge.data):t.texImage2D(r.TEXTURE_2D,$,Ie,ge.width,ge.height,0,ve,xe,ge.data);S.generateMipmaps=!1}else Oe?(st&&t.texStorage2D(r.TEXTURE_2D,ee,Ie,ne.width,ne.height),L&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,ne.width,ne.height,ve,xe,ne.data)):t.texImage2D(r.TEXTURE_2D,0,Ie,ne.width,ne.height,0,ve,xe,ne.data);else if(S.isCompressedTexture)if(S.isCompressedArrayTexture){Oe&&st&&t.texStorage3D(r.TEXTURE_2D_ARRAY,ee,Ie,Xe[0].width,Xe[0].height,ne.depth);for(let $=0,J=Xe.length;$<J;$++)if(ge=Xe[$],S.format!==ui)if(ve!==null)if(Oe){if(L)if(S.layerUpdates.size>0){const le=Hf(ge.width,ge.height,S.format,S.type);for(const ce of S.layerUpdates){const Ye=ge.data.subarray(ce*le/ge.data.BYTES_PER_ELEMENT,(ce+1)*le/ge.data.BYTES_PER_ELEMENT);t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,$,0,0,ce,ge.width,ge.height,1,ve,Ye,0,0)}S.clearLayerUpdates()}else t.compressedTexSubImage3D(r.TEXTURE_2D_ARRAY,$,0,0,0,ge.width,ge.height,ne.depth,ve,ge.data,0,0)}else t.compressedTexImage3D(r.TEXTURE_2D_ARRAY,$,Ie,ge.width,ge.height,ne.depth,0,ge.data,0,0);else console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()");else Oe?L&&t.texSubImage3D(r.TEXTURE_2D_ARRAY,$,0,0,0,ge.width,ge.height,ne.depth,ve,xe,ge.data):t.texImage3D(r.TEXTURE_2D_ARRAY,$,Ie,ge.width,ge.height,ne.depth,0,ve,xe,ge.data)}else{Oe&&st&&t.texStorage2D(r.TEXTURE_2D,ee,Ie,Xe[0].width,Xe[0].height);for(let $=0,J=Xe.length;$<J;$++)ge=Xe[$],S.format!==ui?ve!==null?Oe?L&&t.compressedTexSubImage2D(r.TEXTURE_2D,$,0,0,ge.width,ge.height,ve,ge.data):t.compressedTexImage2D(r.TEXTURE_2D,$,Ie,ge.width,ge.height,0,ge.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .uploadTexture()"):Oe?L&&t.texSubImage2D(r.TEXTURE_2D,$,0,0,ge.width,ge.height,ve,xe,ge.data):t.texImage2D(r.TEXTURE_2D,$,Ie,ge.width,ge.height,0,ve,xe,ge.data)}else if(S.isDataArrayTexture)if(Oe){if(st&&t.texStorage3D(r.TEXTURE_2D_ARRAY,ee,Ie,ne.width,ne.height,ne.depth),L)if(S.layerUpdates.size>0){const $=Hf(ne.width,ne.height,S.format,S.type);for(const J of S.layerUpdates){const le=ne.data.subarray(J*$/ne.data.BYTES_PER_ELEMENT,(J+1)*$/ne.data.BYTES_PER_ELEMENT);t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,J,ne.width,ne.height,1,ve,xe,le)}S.clearLayerUpdates()}else t.texSubImage3D(r.TEXTURE_2D_ARRAY,0,0,0,0,ne.width,ne.height,ne.depth,ve,xe,ne.data)}else t.texImage3D(r.TEXTURE_2D_ARRAY,0,Ie,ne.width,ne.height,ne.depth,0,ve,xe,ne.data);else if(S.isData3DTexture)Oe?(st&&t.texStorage3D(r.TEXTURE_3D,ee,Ie,ne.width,ne.height,ne.depth),L&&t.texSubImage3D(r.TEXTURE_3D,0,0,0,0,ne.width,ne.height,ne.depth,ve,xe,ne.data)):t.texImage3D(r.TEXTURE_3D,0,Ie,ne.width,ne.height,ne.depth,0,ve,xe,ne.data);else if(S.isFramebufferTexture){if(st)if(Oe)t.texStorage2D(r.TEXTURE_2D,ee,Ie,ne.width,ne.height);else{let $=ne.width,J=ne.height;for(let le=0;le<ee;le++)t.texImage2D(r.TEXTURE_2D,le,Ie,$,J,0,ve,xe,null),$>>=1,J>>=1}}else if(Xe.length>0){if(Oe&&st){const $=De(Xe[0]);t.texStorage2D(r.TEXTURE_2D,ee,Ie,$.width,$.height)}for(let $=0,J=Xe.length;$<J;$++)ge=Xe[$],Oe?L&&t.texSubImage2D(r.TEXTURE_2D,$,0,0,ve,xe,ge):t.texImage2D(r.TEXTURE_2D,$,Ie,ve,xe,ge);S.generateMipmaps=!1}else if(Oe){if(st){const $=De(ne);t.texStorage2D(r.TEXTURE_2D,ee,Ie,$.width,$.height)}L&&t.texSubImage2D(r.TEXTURE_2D,0,0,0,ve,xe,ne)}else t.texImage2D(r.TEXTURE_2D,0,Ie,ve,xe,ne);p(S)&&m(j),Se.__version=Z.version,S.onUpdate&&S.onUpdate(S)}A.__version=S.version}function q(A,S,H){if(S.image.length!==6)return;const j=Be(A,S),te=S.source;t.bindTexture(r.TEXTURE_CUBE_MAP,A.__webglTexture,r.TEXTURE0+H);const Z=n.get(te);if(te.version!==Z.__version||j===!0){t.activeTexture(r.TEXTURE0+H);const Se=ft.getPrimaries(ft.workingColorSpace),ie=S.colorSpace===Zi?null:ft.getPrimaries(S.colorSpace),de=S.colorSpace===Zi||Se===ie?r.NONE:r.BROWSER_DEFAULT_WEBGL;r.pixelStorei(r.UNPACK_FLIP_Y_WEBGL,S.flipY),r.pixelStorei(r.UNPACK_PREMULTIPLY_ALPHA_WEBGL,S.premultiplyAlpha),r.pixelStorei(r.UNPACK_ALIGNMENT,S.unpackAlignment),r.pixelStorei(r.UNPACK_COLORSPACE_CONVERSION_WEBGL,de);const He=S.isCompressedTexture||S.image[0].isCompressedTexture,ne=S.image[0]&&S.image[0].isDataTexture,ve=[];for(let J=0;J<6;J++)!He&&!ne?ve[J]=g(S.image[J],!0,i.maxCubemapSize):ve[J]=ne?S.image[J].image:S.image[J],ve[J]=je(S,ve[J]);const xe=ve[0],Ie=s.convert(S.format,S.colorSpace),ge=s.convert(S.type),Xe=y(S.internalFormat,Ie,ge,S.colorSpace),Oe=S.isVideoTexture!==!0,st=Z.__version===void 0||j===!0,L=te.dataReady;let ee=M(S,xe);ae(r.TEXTURE_CUBE_MAP,S);let $;if(He){Oe&&st&&t.texStorage2D(r.TEXTURE_CUBE_MAP,ee,Xe,xe.width,xe.height);for(let J=0;J<6;J++){$=ve[J].mipmaps;for(let le=0;le<$.length;le++){const ce=$[le];S.format!==ui?Ie!==null?Oe?L&&t.compressedTexSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,le,0,0,ce.width,ce.height,Ie,ce.data):t.compressedTexImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,le,Xe,ce.width,ce.height,0,ce.data):console.warn("THREE.WebGLRenderer: Attempt to load unsupported compressed texture format in .setTextureCube()"):Oe?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,le,0,0,ce.width,ce.height,Ie,ge,ce.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,le,Xe,ce.width,ce.height,0,Ie,ge,ce.data)}}}else{if($=S.mipmaps,Oe&&st){$.length>0&&ee++;const J=De(ve[0]);t.texStorage2D(r.TEXTURE_CUBE_MAP,ee,Xe,J.width,J.height)}for(let J=0;J<6;J++)if(ne){Oe?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,0,0,ve[J].width,ve[J].height,Ie,ge,ve[J].data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,Xe,ve[J].width,ve[J].height,0,Ie,ge,ve[J].data);for(let le=0;le<$.length;le++){const Ye=$[le].image[J].image;Oe?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,le+1,0,0,Ye.width,Ye.height,Ie,ge,Ye.data):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,le+1,Xe,Ye.width,Ye.height,0,Ie,ge,Ye.data)}}else{Oe?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,0,0,Ie,ge,ve[J]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,0,Xe,Ie,ge,ve[J]);for(let le=0;le<$.length;le++){const ce=$[le];Oe?L&&t.texSubImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,le+1,0,0,Ie,ge,ce.image[J]):t.texImage2D(r.TEXTURE_CUBE_MAP_POSITIVE_X+J,le+1,Xe,Ie,ge,ce.image[J])}}}p(S)&&m(r.TEXTURE_CUBE_MAP),Z.__version=te.version,S.onUpdate&&S.onUpdate(S)}A.__version=S.version}function Q(A,S,H,j,te,Z){const Se=s.convert(H.format,H.colorSpace),ie=s.convert(H.type),de=y(H.internalFormat,Se,ie,H.colorSpace);if(!n.get(S).__hasExternalTextures){const ne=Math.max(1,S.width>>Z),ve=Math.max(1,S.height>>Z);te===r.TEXTURE_3D||te===r.TEXTURE_2D_ARRAY?t.texImage3D(te,Z,de,ne,ve,S.depth,0,Se,ie,null):t.texImage2D(te,Z,de,ne,ve,0,Se,ie,null)}t.bindFramebuffer(r.FRAMEBUFFER,A),ze(S)?a.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,j,te,n.get(H).__webglTexture,0,Fe(S)):(te===r.TEXTURE_2D||te>=r.TEXTURE_CUBE_MAP_POSITIVE_X&&te<=r.TEXTURE_CUBE_MAP_NEGATIVE_Z)&&r.framebufferTexture2D(r.FRAMEBUFFER,j,te,n.get(H).__webglTexture,Z),t.bindFramebuffer(r.FRAMEBUFFER,null)}function fe(A,S,H){if(r.bindRenderbuffer(r.RENDERBUFFER,A),S.depthBuffer){const j=S.depthTexture,te=j&&j.isDepthTexture?j.type:null,Z=x(S.stencilBuffer,te),Se=S.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,ie=Fe(S);ze(S)?a.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,ie,Z,S.width,S.height):H?r.renderbufferStorageMultisample(r.RENDERBUFFER,ie,Z,S.width,S.height):r.renderbufferStorage(r.RENDERBUFFER,Z,S.width,S.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,Se,r.RENDERBUFFER,A)}else{const j=S.textures;for(let te=0;te<j.length;te++){const Z=j[te],Se=s.convert(Z.format,Z.colorSpace),ie=s.convert(Z.type),de=y(Z.internalFormat,Se,ie,Z.colorSpace),He=Fe(S);H&&ze(S)===!1?r.renderbufferStorageMultisample(r.RENDERBUFFER,He,de,S.width,S.height):ze(S)?a.renderbufferStorageMultisampleEXT(r.RENDERBUFFER,He,de,S.width,S.height):r.renderbufferStorage(r.RENDERBUFFER,de,S.width,S.height)}}r.bindRenderbuffer(r.RENDERBUFFER,null)}function oe(A,S){if(S&&S.isWebGLCubeRenderTarget)throw new Error("Depth Texture with cube render targets is not supported");if(t.bindFramebuffer(r.FRAMEBUFFER,A),!(S.depthTexture&&S.depthTexture.isDepthTexture))throw new Error("renderTarget.depthTexture must be an instance of THREE.DepthTexture");(!n.get(S.depthTexture).__webglTexture||S.depthTexture.image.width!==S.width||S.depthTexture.image.height!==S.height)&&(S.depthTexture.image.width=S.width,S.depthTexture.image.height=S.height,S.depthTexture.needsUpdate=!0),W(S.depthTexture,0);const j=n.get(S.depthTexture).__webglTexture,te=Fe(S);if(S.depthTexture.format===As)ze(S)?a.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,j,0,te):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_ATTACHMENT,r.TEXTURE_2D,j,0);else if(S.depthTexture.format===ks)ze(S)?a.framebufferTexture2DMultisampleEXT(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,j,0,te):r.framebufferTexture2D(r.FRAMEBUFFER,r.DEPTH_STENCIL_ATTACHMENT,r.TEXTURE_2D,j,0);else throw new Error("Unknown depthTexture format")}function we(A){const S=n.get(A),H=A.isWebGLCubeRenderTarget===!0;if(S.__boundDepthTexture!==A.depthTexture){const j=A.depthTexture;if(S.__depthDisposeCallback&&S.__depthDisposeCallback(),j){const te=()=>{delete S.__boundDepthTexture,delete S.__depthDisposeCallback,j.removeEventListener("dispose",te)};j.addEventListener("dispose",te),S.__depthDisposeCallback=te}S.__boundDepthTexture=j}if(A.depthTexture&&!S.__autoAllocateDepthBuffer){if(H)throw new Error("target.depthTexture not supported in Cube render targets");oe(S.__webglFramebuffer,A)}else if(H){S.__webglDepthbuffer=[];for(let j=0;j<6;j++)if(t.bindFramebuffer(r.FRAMEBUFFER,S.__webglFramebuffer[j]),S.__webglDepthbuffer[j]===void 0)S.__webglDepthbuffer[j]=r.createRenderbuffer(),fe(S.__webglDepthbuffer[j],A,!1);else{const te=A.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Z=S.__webglDepthbuffer[j];r.bindRenderbuffer(r.RENDERBUFFER,Z),r.framebufferRenderbuffer(r.FRAMEBUFFER,te,r.RENDERBUFFER,Z)}}else if(t.bindFramebuffer(r.FRAMEBUFFER,S.__webglFramebuffer),S.__webglDepthbuffer===void 0)S.__webglDepthbuffer=r.createRenderbuffer(),fe(S.__webglDepthbuffer,A,!1);else{const j=A.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,te=S.__webglDepthbuffer;r.bindRenderbuffer(r.RENDERBUFFER,te),r.framebufferRenderbuffer(r.FRAMEBUFFER,j,r.RENDERBUFFER,te)}t.bindFramebuffer(r.FRAMEBUFFER,null)}function ye(A,S,H){const j=n.get(A);S!==void 0&&Q(j.__webglFramebuffer,A,A.texture,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,0),H!==void 0&&we(A)}function Ve(A){const S=A.texture,H=n.get(A),j=n.get(S);A.addEventListener("dispose",w);const te=A.textures,Z=A.isWebGLCubeRenderTarget===!0,Se=te.length>1;if(Se||(j.__webglTexture===void 0&&(j.__webglTexture=r.createTexture()),j.__version=S.version,o.memory.textures++),Z){H.__webglFramebuffer=[];for(let ie=0;ie<6;ie++)if(S.mipmaps&&S.mipmaps.length>0){H.__webglFramebuffer[ie]=[];for(let de=0;de<S.mipmaps.length;de++)H.__webglFramebuffer[ie][de]=r.createFramebuffer()}else H.__webglFramebuffer[ie]=r.createFramebuffer()}else{if(S.mipmaps&&S.mipmaps.length>0){H.__webglFramebuffer=[];for(let ie=0;ie<S.mipmaps.length;ie++)H.__webglFramebuffer[ie]=r.createFramebuffer()}else H.__webglFramebuffer=r.createFramebuffer();if(Se)for(let ie=0,de=te.length;ie<de;ie++){const He=n.get(te[ie]);He.__webglTexture===void 0&&(He.__webglTexture=r.createTexture(),o.memory.textures++)}if(A.samples>0&&ze(A)===!1){H.__webglMultisampledFramebuffer=r.createFramebuffer(),H.__webglColorRenderbuffer=[],t.bindFramebuffer(r.FRAMEBUFFER,H.__webglMultisampledFramebuffer);for(let ie=0;ie<te.length;ie++){const de=te[ie];H.__webglColorRenderbuffer[ie]=r.createRenderbuffer(),r.bindRenderbuffer(r.RENDERBUFFER,H.__webglColorRenderbuffer[ie]);const He=s.convert(de.format,de.colorSpace),ne=s.convert(de.type),ve=y(de.internalFormat,He,ne,de.colorSpace,A.isXRRenderTarget===!0),xe=Fe(A);r.renderbufferStorageMultisample(r.RENDERBUFFER,xe,ve,A.width,A.height),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+ie,r.RENDERBUFFER,H.__webglColorRenderbuffer[ie])}r.bindRenderbuffer(r.RENDERBUFFER,null),A.depthBuffer&&(H.__webglDepthRenderbuffer=r.createRenderbuffer(),fe(H.__webglDepthRenderbuffer,A,!0)),t.bindFramebuffer(r.FRAMEBUFFER,null)}}if(Z){t.bindTexture(r.TEXTURE_CUBE_MAP,j.__webglTexture),ae(r.TEXTURE_CUBE_MAP,S);for(let ie=0;ie<6;ie++)if(S.mipmaps&&S.mipmaps.length>0)for(let de=0;de<S.mipmaps.length;de++)Q(H.__webglFramebuffer[ie][de],A,S,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,de);else Q(H.__webglFramebuffer[ie],A,S,r.COLOR_ATTACHMENT0,r.TEXTURE_CUBE_MAP_POSITIVE_X+ie,0);p(S)&&m(r.TEXTURE_CUBE_MAP),t.unbindTexture()}else if(Se){for(let ie=0,de=te.length;ie<de;ie++){const He=te[ie],ne=n.get(He);t.bindTexture(r.TEXTURE_2D,ne.__webglTexture),ae(r.TEXTURE_2D,He),Q(H.__webglFramebuffer,A,He,r.COLOR_ATTACHMENT0+ie,r.TEXTURE_2D,0),p(He)&&m(r.TEXTURE_2D)}t.unbindTexture()}else{let ie=r.TEXTURE_2D;if((A.isWebGL3DRenderTarget||A.isWebGLArrayRenderTarget)&&(ie=A.isWebGL3DRenderTarget?r.TEXTURE_3D:r.TEXTURE_2D_ARRAY),t.bindTexture(ie,j.__webglTexture),ae(ie,S),S.mipmaps&&S.mipmaps.length>0)for(let de=0;de<S.mipmaps.length;de++)Q(H.__webglFramebuffer[de],A,S,r.COLOR_ATTACHMENT0,ie,de);else Q(H.__webglFramebuffer,A,S,r.COLOR_ATTACHMENT0,ie,0);p(S)&&m(ie),t.unbindTexture()}A.depthBuffer&&we(A)}function Ge(A){const S=A.textures;for(let H=0,j=S.length;H<j;H++){const te=S[H];if(p(te)){const Z=A.isWebGLCubeRenderTarget?r.TEXTURE_CUBE_MAP:r.TEXTURE_2D,Se=n.get(te).__webglTexture;t.bindTexture(Z,Se),m(Z),t.unbindTexture()}}}const Ne=[],P=[];function rt(A){if(A.samples>0){if(ze(A)===!1){const S=A.textures,H=A.width,j=A.height;let te=r.COLOR_BUFFER_BIT;const Z=A.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT,Se=n.get(A),ie=S.length>1;if(ie)for(let de=0;de<S.length;de++)t.bindFramebuffer(r.FRAMEBUFFER,Se.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+de,r.RENDERBUFFER,null),t.bindFramebuffer(r.FRAMEBUFFER,Se.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+de,r.TEXTURE_2D,null,0);t.bindFramebuffer(r.READ_FRAMEBUFFER,Se.__webglMultisampledFramebuffer),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Se.__webglFramebuffer);for(let de=0;de<S.length;de++){if(A.resolveDepthBuffer&&(A.depthBuffer&&(te|=r.DEPTH_BUFFER_BIT),A.stencilBuffer&&A.resolveStencilBuffer&&(te|=r.STENCIL_BUFFER_BIT)),ie){r.framebufferRenderbuffer(r.READ_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.RENDERBUFFER,Se.__webglColorRenderbuffer[de]);const He=n.get(S[de]).__webglTexture;r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0,r.TEXTURE_2D,He,0)}r.blitFramebuffer(0,0,H,j,0,0,H,j,te,r.NEAREST),l===!0&&(Ne.length=0,P.length=0,Ne.push(r.COLOR_ATTACHMENT0+de),A.depthBuffer&&A.resolveDepthBuffer===!1&&(Ne.push(Z),P.push(Z),r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,P)),r.invalidateFramebuffer(r.READ_FRAMEBUFFER,Ne))}if(t.bindFramebuffer(r.READ_FRAMEBUFFER,null),t.bindFramebuffer(r.DRAW_FRAMEBUFFER,null),ie)for(let de=0;de<S.length;de++){t.bindFramebuffer(r.FRAMEBUFFER,Se.__webglMultisampledFramebuffer),r.framebufferRenderbuffer(r.FRAMEBUFFER,r.COLOR_ATTACHMENT0+de,r.RENDERBUFFER,Se.__webglColorRenderbuffer[de]);const He=n.get(S[de]).__webglTexture;t.bindFramebuffer(r.FRAMEBUFFER,Se.__webglFramebuffer),r.framebufferTexture2D(r.DRAW_FRAMEBUFFER,r.COLOR_ATTACHMENT0+de,r.TEXTURE_2D,He,0)}t.bindFramebuffer(r.DRAW_FRAMEBUFFER,Se.__webglMultisampledFramebuffer)}else if(A.depthBuffer&&A.resolveDepthBuffer===!1&&l){const S=A.stencilBuffer?r.DEPTH_STENCIL_ATTACHMENT:r.DEPTH_ATTACHMENT;r.invalidateFramebuffer(r.DRAW_FRAMEBUFFER,[S])}}}function Fe(A){return Math.min(i.maxSamples,A.samples)}function ze(A){const S=n.get(A);return A.samples>0&&e.has("WEBGL_multisampled_render_to_texture")===!0&&S.__useRenderToTexture!==!1}function F(A){const S=o.render.frame;u.get(A)!==S&&(u.set(A,S),A.update())}function je(A,S){const H=A.colorSpace,j=A.format,te=A.type;return A.isCompressedTexture===!0||A.isVideoTexture===!0||H!==dr&&H!==Zi&&(ft.getTransfer(H)===Et?(j!==ui||te!==zi)&&console.warn("THREE.WebGLTextures: sRGB encoded textures have to use RGBAFormat and UnsignedByteType."):console.error("THREE.WebGLTextures: Unsupported texture color space:",H)),S}function De(A){return typeof HTMLImageElement<"u"&&A instanceof HTMLImageElement?(c.width=A.naturalWidth||A.width,c.height=A.naturalHeight||A.height):typeof VideoFrame<"u"&&A instanceof VideoFrame?(c.width=A.displayWidth,c.height=A.displayHeight):(c.width=A.width,c.height=A.height),c}this.allocateTextureUnit=N,this.resetTextureUnits=T,this.setTexture2D=W,this.setTexture2DArray=K,this.setTexture3D=G,this.setTextureCube=X,this.rebindTextures=ye,this.setupRenderTarget=Ve,this.updateRenderTargetMipmap=Ge,this.updateMultisampleRenderTarget=rt,this.setupDepthRenderbuffer=we,this.setupFrameBufferTexture=Q,this.useMultisampledRTT=ze}function XM(r,e){function t(n,i=Zi){let s;const o=ft.getTransfer(i);if(n===zi)return r.UNSIGNED_BYTE;if(n===eh)return r.UNSIGNED_SHORT_4_4_4_4;if(n===th)return r.UNSIGNED_SHORT_5_5_5_1;if(n===Mp)return r.UNSIGNED_INT_5_9_9_9_REV;if(n===xp)return r.BYTE;if(n===Sp)return r.SHORT;if(n===Po)return r.UNSIGNED_SHORT;if(n===Qu)return r.INT;if(n===Wr)return r.UNSIGNED_INT;if(n===Ui)return r.FLOAT;if(n===Lo)return r.HALF_FLOAT;if(n===yp)return r.ALPHA;if(n===Ep)return r.RGB;if(n===ui)return r.RGBA;if(n===Tp)return r.LUMINANCE;if(n===bp)return r.LUMINANCE_ALPHA;if(n===As)return r.DEPTH_COMPONENT;if(n===ks)return r.DEPTH_STENCIL;if(n===wp)return r.RED;if(n===nh)return r.RED_INTEGER;if(n===Ap)return r.RG;if(n===ih)return r.RG_INTEGER;if(n===rh)return r.RGBA_INTEGER;if(n===La||n===Ia||n===Ua||n===Na)if(o===Et)if(s=e.get("WEBGL_compressed_texture_s3tc_srgb"),s!==null){if(n===La)return s.COMPRESSED_SRGB_S3TC_DXT1_EXT;if(n===Ia)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT1_EXT;if(n===Ua)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT3_EXT;if(n===Na)return s.COMPRESSED_SRGB_ALPHA_S3TC_DXT5_EXT}else return null;else if(s=e.get("WEBGL_compressed_texture_s3tc"),s!==null){if(n===La)return s.COMPRESSED_RGB_S3TC_DXT1_EXT;if(n===Ia)return s.COMPRESSED_RGBA_S3TC_DXT1_EXT;if(n===Ua)return s.COMPRESSED_RGBA_S3TC_DXT3_EXT;if(n===Na)return s.COMPRESSED_RGBA_S3TC_DXT5_EXT}else return null;if(n===$c||n===Kc||n===Zc||n===jc)if(s=e.get("WEBGL_compressed_texture_pvrtc"),s!==null){if(n===$c)return s.COMPRESSED_RGB_PVRTC_4BPPV1_IMG;if(n===Kc)return s.COMPRESSED_RGB_PVRTC_2BPPV1_IMG;if(n===Zc)return s.COMPRESSED_RGBA_PVRTC_4BPPV1_IMG;if(n===jc)return s.COMPRESSED_RGBA_PVRTC_2BPPV1_IMG}else return null;if(n===Jc||n===Qc||n===eu)if(s=e.get("WEBGL_compressed_texture_etc"),s!==null){if(n===Jc||n===Qc)return o===Et?s.COMPRESSED_SRGB8_ETC2:s.COMPRESSED_RGB8_ETC2;if(n===eu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ETC2_EAC:s.COMPRESSED_RGBA8_ETC2_EAC}else return null;if(n===tu||n===nu||n===iu||n===ru||n===su||n===ou||n===au||n===lu||n===cu||n===uu||n===hu||n===fu||n===du||n===pu)if(s=e.get("WEBGL_compressed_texture_astc"),s!==null){if(n===tu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_4x4_KHR:s.COMPRESSED_RGBA_ASTC_4x4_KHR;if(n===nu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x4_KHR:s.COMPRESSED_RGBA_ASTC_5x4_KHR;if(n===iu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_5x5_KHR:s.COMPRESSED_RGBA_ASTC_5x5_KHR;if(n===ru)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x5_KHR:s.COMPRESSED_RGBA_ASTC_6x5_KHR;if(n===su)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_6x6_KHR:s.COMPRESSED_RGBA_ASTC_6x6_KHR;if(n===ou)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x5_KHR:s.COMPRESSED_RGBA_ASTC_8x5_KHR;if(n===au)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x6_KHR:s.COMPRESSED_RGBA_ASTC_8x6_KHR;if(n===lu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_8x8_KHR:s.COMPRESSED_RGBA_ASTC_8x8_KHR;if(n===cu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x5_KHR:s.COMPRESSED_RGBA_ASTC_10x5_KHR;if(n===uu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x6_KHR:s.COMPRESSED_RGBA_ASTC_10x6_KHR;if(n===hu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x8_KHR:s.COMPRESSED_RGBA_ASTC_10x8_KHR;if(n===fu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_10x10_KHR:s.COMPRESSED_RGBA_ASTC_10x10_KHR;if(n===du)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x10_KHR:s.COMPRESSED_RGBA_ASTC_12x10_KHR;if(n===pu)return o===Et?s.COMPRESSED_SRGB8_ALPHA8_ASTC_12x12_KHR:s.COMPRESSED_RGBA_ASTC_12x12_KHR}else return null;if(n===Fa||n===mu||n===_u)if(s=e.get("EXT_texture_compression_bptc"),s!==null){if(n===Fa)return o===Et?s.COMPRESSED_SRGB_ALPHA_BPTC_UNORM_EXT:s.COMPRESSED_RGBA_BPTC_UNORM_EXT;if(n===mu)return s.COMPRESSED_RGB_BPTC_SIGNED_FLOAT_EXT;if(n===_u)return s.COMPRESSED_RGB_BPTC_UNSIGNED_FLOAT_EXT}else return null;if(n===Rp||n===gu||n===vu||n===xu)if(s=e.get("EXT_texture_compression_rgtc"),s!==null){if(n===Fa)return s.COMPRESSED_RED_RGTC1_EXT;if(n===gu)return s.COMPRESSED_SIGNED_RED_RGTC1_EXT;if(n===vu)return s.COMPRESSED_RED_GREEN_RGTC2_EXT;if(n===xu)return s.COMPRESSED_SIGNED_RED_GREEN_RGTC2_EXT}else return null;return n===zs?r.UNSIGNED_INT_24_8:r[n]!==void 0?r[n]:null}return{convert:t}}class YM extends Kn{constructor(e=[]){super(),this.isArrayCamera=!0,this.cameras=e}}class Sa extends An{constructor(){super(),this.isGroup=!0,this.type="Group"}}const qM={type:"move"};class rc{constructor(){this._targetRay=null,this._grip=null,this._hand=null}getHandSpace(){return this._hand===null&&(this._hand=new Sa,this._hand.matrixAutoUpdate=!1,this._hand.visible=!1,this._hand.joints={},this._hand.inputState={pinching:!1}),this._hand}getTargetRaySpace(){return this._targetRay===null&&(this._targetRay=new Sa,this._targetRay.matrixAutoUpdate=!1,this._targetRay.visible=!1,this._targetRay.hasLinearVelocity=!1,this._targetRay.linearVelocity=new Y,this._targetRay.hasAngularVelocity=!1,this._targetRay.angularVelocity=new Y),this._targetRay}getGripSpace(){return this._grip===null&&(this._grip=new Sa,this._grip.matrixAutoUpdate=!1,this._grip.visible=!1,this._grip.hasLinearVelocity=!1,this._grip.linearVelocity=new Y,this._grip.hasAngularVelocity=!1,this._grip.angularVelocity=new Y),this._grip}dispatchEvent(e){return this._targetRay!==null&&this._targetRay.dispatchEvent(e),this._grip!==null&&this._grip.dispatchEvent(e),this._hand!==null&&this._hand.dispatchEvent(e),this}connect(e){if(e&&e.hand){const t=this._hand;if(t)for(const n of e.hand.values())this._getHandJoint(t,n)}return this.dispatchEvent({type:"connected",data:e}),this}disconnect(e){return this.dispatchEvent({type:"disconnected",data:e}),this._targetRay!==null&&(this._targetRay.visible=!1),this._grip!==null&&(this._grip.visible=!1),this._hand!==null&&(this._hand.visible=!1),this}update(e,t,n){let i=null,s=null,o=null;const a=this._targetRay,l=this._grip,c=this._hand;if(e&&t.session.visibilityState!=="visible-blurred"){if(c&&e.hand){o=!0;for(const g of e.hand.values()){const p=t.getJointPose(g,n),m=this._getHandJoint(c,g);p!==null&&(m.matrix.fromArray(p.transform.matrix),m.matrix.decompose(m.position,m.rotation,m.scale),m.matrixWorldNeedsUpdate=!0,m.jointRadius=p.radius),m.visible=p!==null}const u=c.joints["index-finger-tip"],f=c.joints["thumb-tip"],h=u.position.distanceTo(f.position),d=.02,_=.005;c.inputState.pinching&&h>d+_?(c.inputState.pinching=!1,this.dispatchEvent({type:"pinchend",handedness:e.handedness,target:this})):!c.inputState.pinching&&h<=d-_&&(c.inputState.pinching=!0,this.dispatchEvent({type:"pinchstart",handedness:e.handedness,target:this}))}else l!==null&&e.gripSpace&&(s=t.getPose(e.gripSpace,n),s!==null&&(l.matrix.fromArray(s.transform.matrix),l.matrix.decompose(l.position,l.rotation,l.scale),l.matrixWorldNeedsUpdate=!0,s.linearVelocity?(l.hasLinearVelocity=!0,l.linearVelocity.copy(s.linearVelocity)):l.hasLinearVelocity=!1,s.angularVelocity?(l.hasAngularVelocity=!0,l.angularVelocity.copy(s.angularVelocity)):l.hasAngularVelocity=!1));a!==null&&(i=t.getPose(e.targetRaySpace,n),i===null&&s!==null&&(i=s),i!==null&&(a.matrix.fromArray(i.transform.matrix),a.matrix.decompose(a.position,a.rotation,a.scale),a.matrixWorldNeedsUpdate=!0,i.linearVelocity?(a.hasLinearVelocity=!0,a.linearVelocity.copy(i.linearVelocity)):a.hasLinearVelocity=!1,i.angularVelocity?(a.hasAngularVelocity=!0,a.angularVelocity.copy(i.angularVelocity)):a.hasAngularVelocity=!1,this.dispatchEvent(qM)))}return a!==null&&(a.visible=i!==null),l!==null&&(l.visible=s!==null),c!==null&&(c.visible=o!==null),this}_getHandJoint(e,t){if(e.joints[t.jointName]===void 0){const n=new Sa;n.matrixAutoUpdate=!1,n.visible=!1,e.joints[t.jointName]=n,e.add(n)}return e.joints[t.jointName]}}const $M=`
void main() {

	gl_Position = vec4( position, 1.0 );

}`,KM=`
uniform sampler2DArray depthColor;
uniform float depthWidth;
uniform float depthHeight;

void main() {

	vec2 coord = vec2( gl_FragCoord.x / depthWidth, gl_FragCoord.y / depthHeight );

	if ( coord.x >= 1.0 ) {

		gl_FragDepth = texture( depthColor, vec3( coord.x - 1.0, coord.y, 1 ) ).r;

	} else {

		gl_FragDepth = texture( depthColor, vec3( coord.x, coord.y, 0 ) ).r;

	}

}`;class ZM{constructor(){this.texture=null,this.mesh=null,this.depthNear=0,this.depthFar=0}init(e,t,n){if(this.texture===null){const i=new gn,s=e.properties.get(i);s.__webglTexture=t.texture,(t.depthNear!=n.depthNear||t.depthFar!=n.depthFar)&&(this.depthNear=t.depthNear,this.depthFar=t.depthFar),this.texture=i}}getMesh(e){if(this.texture!==null&&this.mesh===null){const t=e.cameras[0].viewport,n=new ei({vertexShader:$M,fragmentShader:KM,uniforms:{depthColor:{value:this.texture},depthWidth:{value:t.z},depthHeight:{value:t.w}}});this.mesh=new hi(new Bo(20,20),n)}return this.mesh}reset(){this.texture=null,this.mesh=null}getDepthTexture(){return this.texture}}class jM extends Gs{constructor(e,t){super();const n=this;let i=null,s=1,o=null,a="local-floor",l=1,c=null,u=null,f=null,h=null,d=null,_=null;const g=new ZM,p=t.getContextAttributes();let m=null,y=null;const x=[],M=[],R=new St;let w=null;const E=new Kn;E.layers.enable(1),E.viewport=new Nt;const D=new Kn;D.layers.enable(2),D.viewport=new Nt;const O=[E,D],v=new YM;v.layers.enable(1),v.layers.enable(2);let T=null,N=null;this.cameraAutoUpdate=!0,this.enabled=!1,this.isPresenting=!1,this.getController=function(q){let Q=x[q];return Q===void 0&&(Q=new rc,x[q]=Q),Q.getTargetRaySpace()},this.getControllerGrip=function(q){let Q=x[q];return Q===void 0&&(Q=new rc,x[q]=Q),Q.getGripSpace()},this.getHand=function(q){let Q=x[q];return Q===void 0&&(Q=new rc,x[q]=Q),Q.getHandSpace()};function z(q){const Q=M.indexOf(q.inputSource);if(Q===-1)return;const fe=x[Q];fe!==void 0&&(fe.update(q.inputSource,q.frame,c||o),fe.dispatchEvent({type:q.type,data:q.inputSource}))}function W(){i.removeEventListener("select",z),i.removeEventListener("selectstart",z),i.removeEventListener("selectend",z),i.removeEventListener("squeeze",z),i.removeEventListener("squeezestart",z),i.removeEventListener("squeezeend",z),i.removeEventListener("end",W),i.removeEventListener("inputsourceschange",K);for(let q=0;q<x.length;q++){const Q=M[q];Q!==null&&(M[q]=null,x[q].disconnect(Q))}T=null,N=null,g.reset(),e.setRenderTarget(m),d=null,h=null,f=null,i=null,y=null,We.stop(),n.isPresenting=!1,e.setPixelRatio(w),e.setSize(R.width,R.height,!1),n.dispatchEvent({type:"sessionend"})}this.setFramebufferScaleFactor=function(q){s=q,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change framebuffer scale while presenting.")},this.setReferenceSpaceType=function(q){a=q,n.isPresenting===!0&&console.warn("THREE.WebXRManager: Cannot change reference space type while presenting.")},this.getReferenceSpace=function(){return c||o},this.setReferenceSpace=function(q){c=q},this.getBaseLayer=function(){return h!==null?h:d},this.getBinding=function(){return f},this.getFrame=function(){return _},this.getSession=function(){return i},this.setSession=async function(q){if(i=q,i!==null){if(m=e.getRenderTarget(),i.addEventListener("select",z),i.addEventListener("selectstart",z),i.addEventListener("selectend",z),i.addEventListener("squeeze",z),i.addEventListener("squeezestart",z),i.addEventListener("squeezeend",z),i.addEventListener("end",W),i.addEventListener("inputsourceschange",K),p.xrCompatible!==!0&&await t.makeXRCompatible(),w=e.getPixelRatio(),e.getSize(R),i.renderState.layers===void 0){const Q={antialias:p.antialias,alpha:!0,depth:p.depth,stencil:p.stencil,framebufferScaleFactor:s};d=new XRWebGLLayer(i,t,Q),i.updateRenderState({baseLayer:d}),e.setPixelRatio(1),e.setSize(d.framebufferWidth,d.framebufferHeight,!1),y=new Xr(d.framebufferWidth,d.framebufferHeight,{format:ui,type:zi,colorSpace:e.outputColorSpace,stencilBuffer:p.stencil})}else{let Q=null,fe=null,oe=null;p.depth&&(oe=p.stencil?t.DEPTH24_STENCIL8:t.DEPTH_COMPONENT24,Q=p.stencil?ks:As,fe=p.stencil?zs:Wr);const we={colorFormat:t.RGBA8,depthFormat:oe,scaleFactor:s};f=new XRWebGLBinding(i,t),h=f.createProjectionLayer(we),i.updateRenderState({layers:[h]}),e.setPixelRatio(1),e.setSize(h.textureWidth,h.textureHeight,!1),y=new Xr(h.textureWidth,h.textureHeight,{format:ui,type:zi,depthTexture:new Wp(h.textureWidth,h.textureHeight,fe,void 0,void 0,void 0,void 0,void 0,void 0,Q),stencilBuffer:p.stencil,colorSpace:e.outputColorSpace,samples:p.antialias?4:0,resolveDepthBuffer:h.ignoreDepthValues===!1})}y.isXRRenderTarget=!0,this.setFoveation(l),c=null,o=await i.requestReferenceSpace(a),We.setContext(i),We.start(),n.isPresenting=!0,n.dispatchEvent({type:"sessionstart"})}},this.getEnvironmentBlendMode=function(){if(i!==null)return i.environmentBlendMode},this.getDepthTexture=function(){return g.getDepthTexture()};function K(q){for(let Q=0;Q<q.removed.length;Q++){const fe=q.removed[Q],oe=M.indexOf(fe);oe>=0&&(M[oe]=null,x[oe].disconnect(fe))}for(let Q=0;Q<q.added.length;Q++){const fe=q.added[Q];let oe=M.indexOf(fe);if(oe===-1){for(let ye=0;ye<x.length;ye++)if(ye>=M.length){M.push(fe),oe=ye;break}else if(M[ye]===null){M[ye]=fe,oe=ye;break}if(oe===-1)break}const we=x[oe];we&&we.connect(fe)}}const G=new Y,X=new Y;function V(q,Q,fe){G.setFromMatrixPosition(Q.matrixWorld),X.setFromMatrixPosition(fe.matrixWorld);const oe=G.distanceTo(X),we=Q.projectionMatrix.elements,ye=fe.projectionMatrix.elements,Ve=we[14]/(we[10]-1),Ge=we[14]/(we[10]+1),Ne=(we[9]+1)/we[5],P=(we[9]-1)/we[5],rt=(we[8]-1)/we[0],Fe=(ye[8]+1)/ye[0],ze=Ve*rt,F=Ve*Fe,je=oe/(-rt+Fe),De=je*-rt;if(Q.matrixWorld.decompose(q.position,q.quaternion,q.scale),q.translateX(De),q.translateZ(je),q.matrixWorld.compose(q.position,q.quaternion,q.scale),q.matrixWorldInverse.copy(q.matrixWorld).invert(),we[10]===-1)q.projectionMatrix.copy(Q.projectionMatrix),q.projectionMatrixInverse.copy(Q.projectionMatrixInverse);else{const A=Ve+je,S=Ge+je,H=ze-De,j=F+(oe-De),te=Ne*Ge/S*A,Z=P*Ge/S*A;q.projectionMatrix.makePerspective(H,j,te,Z,A,S),q.projectionMatrixInverse.copy(q.projectionMatrix).invert()}}function re(q,Q){Q===null?q.matrixWorld.copy(q.matrix):q.matrixWorld.multiplyMatrices(Q.matrixWorld,q.matrix),q.matrixWorldInverse.copy(q.matrixWorld).invert()}this.updateCamera=function(q){if(i===null)return;let Q=q.near,fe=q.far;g.texture!==null&&(g.depthNear>0&&(Q=g.depthNear),g.depthFar>0&&(fe=g.depthFar)),v.near=D.near=E.near=Q,v.far=D.far=E.far=fe,(T!==v.near||N!==v.far)&&(i.updateRenderState({depthNear:v.near,depthFar:v.far}),T=v.near,N=v.far);const oe=q.parent,we=v.cameras;re(v,oe);for(let ye=0;ye<we.length;ye++)re(we[ye],oe);we.length===2?V(v,E,D):v.projectionMatrix.copy(E.projectionMatrix),C(q,v,oe)};function C(q,Q,fe){fe===null?q.matrix.copy(Q.matrixWorld):(q.matrix.copy(fe.matrixWorld),q.matrix.invert(),q.matrix.multiply(Q.matrixWorld)),q.matrix.decompose(q.position,q.quaternion,q.scale),q.updateMatrixWorld(!0),q.projectionMatrix.copy(Q.projectionMatrix),q.projectionMatrixInverse.copy(Q.projectionMatrixInverse),q.isPerspectiveCamera&&(q.fov=Su*2*Math.atan(1/q.projectionMatrix.elements[5]),q.zoom=1)}this.getCamera=function(){return v},this.getFoveation=function(){if(!(h===null&&d===null))return l},this.setFoveation=function(q){l=q,h!==null&&(h.fixedFoveation=q),d!==null&&d.fixedFoveation!==void 0&&(d.fixedFoveation=q)},this.hasDepthSensing=function(){return g.texture!==null},this.getDepthSensingMesh=function(){return g.getMesh(v)};let ae=null;function Be(q,Q){if(u=Q.getViewerPose(c||o),_=Q,u!==null){const fe=u.views;d!==null&&(e.setRenderTargetFramebuffer(y,d.framebuffer),e.setRenderTarget(y));let oe=!1;fe.length!==v.cameras.length&&(v.cameras.length=0,oe=!0);for(let ye=0;ye<fe.length;ye++){const Ve=fe[ye];let Ge=null;if(d!==null)Ge=d.getViewport(Ve);else{const P=f.getViewSubImage(h,Ve);Ge=P.viewport,ye===0&&(e.setRenderTargetTextures(y,P.colorTexture,h.ignoreDepthValues?void 0:P.depthStencilTexture),e.setRenderTarget(y))}let Ne=O[ye];Ne===void 0&&(Ne=new Kn,Ne.layers.enable(ye),Ne.viewport=new Nt,O[ye]=Ne),Ne.matrix.fromArray(Ve.transform.matrix),Ne.matrix.decompose(Ne.position,Ne.quaternion,Ne.scale),Ne.projectionMatrix.fromArray(Ve.projectionMatrix),Ne.projectionMatrixInverse.copy(Ne.projectionMatrix).invert(),Ne.viewport.set(Ge.x,Ge.y,Ge.width,Ge.height),ye===0&&(v.matrix.copy(Ne.matrix),v.matrix.decompose(v.position,v.quaternion,v.scale)),oe===!0&&v.cameras.push(Ne)}const we=i.enabledFeatures;if(we&&we.includes("depth-sensing")){const ye=f.getDepthInformation(fe[0]);ye&&ye.isValid&&ye.texture&&g.init(e,ye,i.renderState)}}for(let fe=0;fe<x.length;fe++){const oe=M[fe],we=x[fe];oe!==null&&we!==void 0&&we.update(oe,Q,c||o)}ae&&ae(q,Q),Q.detectedPlanes&&n.dispatchEvent({type:"planesdetected",data:Q}),_=null}const We=new Vp;We.setAnimationLoop(Be),this.setAnimationLoop=function(q){ae=q},this.dispose=function(){}}}const Mr=new ki,JM=new Ot;function QM(r,e){function t(p,m){p.matrixAutoUpdate===!0&&p.updateMatrix(),m.value.copy(p.matrix)}function n(p,m){m.color.getRGB(p.fogColor.value,zp(r)),m.isFog?(p.fogNear.value=m.near,p.fogFar.value=m.far):m.isFogExp2&&(p.fogDensity.value=m.density)}function i(p,m,y,x,M){m.isMeshBasicMaterial||m.isMeshLambertMaterial?s(p,m):m.isMeshToonMaterial?(s(p,m),f(p,m)):m.isMeshPhongMaterial?(s(p,m),u(p,m)):m.isMeshStandardMaterial?(s(p,m),h(p,m),m.isMeshPhysicalMaterial&&d(p,m,M)):m.isMeshMatcapMaterial?(s(p,m),_(p,m)):m.isMeshDepthMaterial?s(p,m):m.isMeshDistanceMaterial?(s(p,m),g(p,m)):m.isMeshNormalMaterial?s(p,m):m.isLineBasicMaterial?(o(p,m),m.isLineDashedMaterial&&a(p,m)):m.isPointsMaterial?l(p,m,y,x):m.isSpriteMaterial?c(p,m):m.isShadowMaterial?(p.color.value.copy(m.color),p.opacity.value=m.opacity):m.isShaderMaterial&&(m.uniformsNeedUpdate=!1)}function s(p,m){p.opacity.value=m.opacity,m.color&&p.diffuse.value.copy(m.color),m.emissive&&p.emissive.value.copy(m.emissive).multiplyScalar(m.emissiveIntensity),m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.bumpMap&&(p.bumpMap.value=m.bumpMap,t(m.bumpMap,p.bumpMapTransform),p.bumpScale.value=m.bumpScale,m.side===_n&&(p.bumpScale.value*=-1)),m.normalMap&&(p.normalMap.value=m.normalMap,t(m.normalMap,p.normalMapTransform),p.normalScale.value.copy(m.normalScale),m.side===_n&&p.normalScale.value.negate()),m.displacementMap&&(p.displacementMap.value=m.displacementMap,t(m.displacementMap,p.displacementMapTransform),p.displacementScale.value=m.displacementScale,p.displacementBias.value=m.displacementBias),m.emissiveMap&&(p.emissiveMap.value=m.emissiveMap,t(m.emissiveMap,p.emissiveMapTransform)),m.specularMap&&(p.specularMap.value=m.specularMap,t(m.specularMap,p.specularMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest);const y=e.get(m),x=y.envMap,M=y.envMapRotation;x&&(p.envMap.value=x,Mr.copy(M),Mr.x*=-1,Mr.y*=-1,Mr.z*=-1,x.isCubeTexture&&x.isRenderTargetTexture===!1&&(Mr.y*=-1,Mr.z*=-1),p.envMapRotation.value.setFromMatrix4(JM.makeRotationFromEuler(Mr)),p.flipEnvMap.value=x.isCubeTexture&&x.isRenderTargetTexture===!1?-1:1,p.reflectivity.value=m.reflectivity,p.ior.value=m.ior,p.refractionRatio.value=m.refractionRatio),m.lightMap&&(p.lightMap.value=m.lightMap,p.lightMapIntensity.value=m.lightMapIntensity,t(m.lightMap,p.lightMapTransform)),m.aoMap&&(p.aoMap.value=m.aoMap,p.aoMapIntensity.value=m.aoMapIntensity,t(m.aoMap,p.aoMapTransform))}function o(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform))}function a(p,m){p.dashSize.value=m.dashSize,p.totalSize.value=m.dashSize+m.gapSize,p.scale.value=m.scale}function l(p,m,y,x){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.size.value=m.size*y,p.scale.value=x*.5,m.map&&(p.map.value=m.map,t(m.map,p.uvTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function c(p,m){p.diffuse.value.copy(m.color),p.opacity.value=m.opacity,p.rotation.value=m.rotation,m.map&&(p.map.value=m.map,t(m.map,p.mapTransform)),m.alphaMap&&(p.alphaMap.value=m.alphaMap,t(m.alphaMap,p.alphaMapTransform)),m.alphaTest>0&&(p.alphaTest.value=m.alphaTest)}function u(p,m){p.specular.value.copy(m.specular),p.shininess.value=Math.max(m.shininess,1e-4)}function f(p,m){m.gradientMap&&(p.gradientMap.value=m.gradientMap)}function h(p,m){p.metalness.value=m.metalness,m.metalnessMap&&(p.metalnessMap.value=m.metalnessMap,t(m.metalnessMap,p.metalnessMapTransform)),p.roughness.value=m.roughness,m.roughnessMap&&(p.roughnessMap.value=m.roughnessMap,t(m.roughnessMap,p.roughnessMapTransform)),m.envMap&&(p.envMapIntensity.value=m.envMapIntensity)}function d(p,m,y){p.ior.value=m.ior,m.sheen>0&&(p.sheenColor.value.copy(m.sheenColor).multiplyScalar(m.sheen),p.sheenRoughness.value=m.sheenRoughness,m.sheenColorMap&&(p.sheenColorMap.value=m.sheenColorMap,t(m.sheenColorMap,p.sheenColorMapTransform)),m.sheenRoughnessMap&&(p.sheenRoughnessMap.value=m.sheenRoughnessMap,t(m.sheenRoughnessMap,p.sheenRoughnessMapTransform))),m.clearcoat>0&&(p.clearcoat.value=m.clearcoat,p.clearcoatRoughness.value=m.clearcoatRoughness,m.clearcoatMap&&(p.clearcoatMap.value=m.clearcoatMap,t(m.clearcoatMap,p.clearcoatMapTransform)),m.clearcoatRoughnessMap&&(p.clearcoatRoughnessMap.value=m.clearcoatRoughnessMap,t(m.clearcoatRoughnessMap,p.clearcoatRoughnessMapTransform)),m.clearcoatNormalMap&&(p.clearcoatNormalMap.value=m.clearcoatNormalMap,t(m.clearcoatNormalMap,p.clearcoatNormalMapTransform),p.clearcoatNormalScale.value.copy(m.clearcoatNormalScale),m.side===_n&&p.clearcoatNormalScale.value.negate())),m.dispersion>0&&(p.dispersion.value=m.dispersion),m.iridescence>0&&(p.iridescence.value=m.iridescence,p.iridescenceIOR.value=m.iridescenceIOR,p.iridescenceThicknessMinimum.value=m.iridescenceThicknessRange[0],p.iridescenceThicknessMaximum.value=m.iridescenceThicknessRange[1],m.iridescenceMap&&(p.iridescenceMap.value=m.iridescenceMap,t(m.iridescenceMap,p.iridescenceMapTransform)),m.iridescenceThicknessMap&&(p.iridescenceThicknessMap.value=m.iridescenceThicknessMap,t(m.iridescenceThicknessMap,p.iridescenceThicknessMapTransform))),m.transmission>0&&(p.transmission.value=m.transmission,p.transmissionSamplerMap.value=y.texture,p.transmissionSamplerSize.value.set(y.width,y.height),m.transmissionMap&&(p.transmissionMap.value=m.transmissionMap,t(m.transmissionMap,p.transmissionMapTransform)),p.thickness.value=m.thickness,m.thicknessMap&&(p.thicknessMap.value=m.thicknessMap,t(m.thicknessMap,p.thicknessMapTransform)),p.attenuationDistance.value=m.attenuationDistance,p.attenuationColor.value.copy(m.attenuationColor)),m.anisotropy>0&&(p.anisotropyVector.value.set(m.anisotropy*Math.cos(m.anisotropyRotation),m.anisotropy*Math.sin(m.anisotropyRotation)),m.anisotropyMap&&(p.anisotropyMap.value=m.anisotropyMap,t(m.anisotropyMap,p.anisotropyMapTransform))),p.specularIntensity.value=m.specularIntensity,p.specularColor.value.copy(m.specularColor),m.specularColorMap&&(p.specularColorMap.value=m.specularColorMap,t(m.specularColorMap,p.specularColorMapTransform)),m.specularIntensityMap&&(p.specularIntensityMap.value=m.specularIntensityMap,t(m.specularIntensityMap,p.specularIntensityMapTransform))}function _(p,m){m.matcap&&(p.matcap.value=m.matcap)}function g(p,m){const y=e.get(m).light;p.referencePosition.value.setFromMatrixPosition(y.matrixWorld),p.nearDistance.value=y.shadow.camera.near,p.farDistance.value=y.shadow.camera.far}return{refreshFogUniforms:n,refreshMaterialUniforms:i}}function ey(r,e,t,n){let i={},s={},o=[];const a=r.getParameter(r.MAX_UNIFORM_BUFFER_BINDINGS);function l(y,x){const M=x.program;n.uniformBlockBinding(y,M)}function c(y,x){let M=i[y.id];M===void 0&&(_(y),M=u(y),i[y.id]=M,y.addEventListener("dispose",p));const R=x.program;n.updateUBOMapping(y,R);const w=e.render.frame;s[y.id]!==w&&(h(y),s[y.id]=w)}function u(y){const x=f();y.__bindingPointIndex=x;const M=r.createBuffer(),R=y.__size,w=y.usage;return r.bindBuffer(r.UNIFORM_BUFFER,M),r.bufferData(r.UNIFORM_BUFFER,R,w),r.bindBuffer(r.UNIFORM_BUFFER,null),r.bindBufferBase(r.UNIFORM_BUFFER,x,M),M}function f(){for(let y=0;y<a;y++)if(o.indexOf(y)===-1)return o.push(y),y;return console.error("THREE.WebGLRenderer: Maximum number of simultaneously usable uniforms groups reached."),0}function h(y){const x=i[y.id],M=y.uniforms,R=y.__cache;r.bindBuffer(r.UNIFORM_BUFFER,x);for(let w=0,E=M.length;w<E;w++){const D=Array.isArray(M[w])?M[w]:[M[w]];for(let O=0,v=D.length;O<v;O++){const T=D[O];if(d(T,w,O,R)===!0){const N=T.__offset,z=Array.isArray(T.value)?T.value:[T.value];let W=0;for(let K=0;K<z.length;K++){const G=z[K],X=g(G);typeof G=="number"||typeof G=="boolean"?(T.__data[0]=G,r.bufferSubData(r.UNIFORM_BUFFER,N+W,T.__data)):G.isMatrix3?(T.__data[0]=G.elements[0],T.__data[1]=G.elements[1],T.__data[2]=G.elements[2],T.__data[3]=0,T.__data[4]=G.elements[3],T.__data[5]=G.elements[4],T.__data[6]=G.elements[5],T.__data[7]=0,T.__data[8]=G.elements[6],T.__data[9]=G.elements[7],T.__data[10]=G.elements[8],T.__data[11]=0):(G.toArray(T.__data,W),W+=X.storage/Float32Array.BYTES_PER_ELEMENT)}r.bufferSubData(r.UNIFORM_BUFFER,N,T.__data)}}}r.bindBuffer(r.UNIFORM_BUFFER,null)}function d(y,x,M,R){const w=y.value,E=x+"_"+M;if(R[E]===void 0)return typeof w=="number"||typeof w=="boolean"?R[E]=w:R[E]=w.clone(),!0;{const D=R[E];if(typeof w=="number"||typeof w=="boolean"){if(D!==w)return R[E]=w,!0}else if(D.equals(w)===!1)return D.copy(w),!0}return!1}function _(y){const x=y.uniforms;let M=0;const R=16;for(let E=0,D=x.length;E<D;E++){const O=Array.isArray(x[E])?x[E]:[x[E]];for(let v=0,T=O.length;v<T;v++){const N=O[v],z=Array.isArray(N.value)?N.value:[N.value];for(let W=0,K=z.length;W<K;W++){const G=z[W],X=g(G),V=M%R,re=V%X.boundary,C=V+re;M+=re,C!==0&&R-C<X.storage&&(M+=R-C),N.__data=new Float32Array(X.storage/Float32Array.BYTES_PER_ELEMENT),N.__offset=M,M+=X.storage}}}const w=M%R;return w>0&&(M+=R-w),y.__size=M,y.__cache={},this}function g(y){const x={boundary:0,storage:0};return typeof y=="number"||typeof y=="boolean"?(x.boundary=4,x.storage=4):y.isVector2?(x.boundary=8,x.storage=8):y.isVector3||y.isColor?(x.boundary=16,x.storage=12):y.isVector4?(x.boundary=16,x.storage=16):y.isMatrix3?(x.boundary=48,x.storage=48):y.isMatrix4?(x.boundary=64,x.storage=64):y.isTexture?console.warn("THREE.WebGLRenderer: Texture samplers can not be part of an uniforms group."):console.warn("THREE.WebGLRenderer: Unsupported uniform value type.",y),x}function p(y){const x=y.target;x.removeEventListener("dispose",p);const M=o.indexOf(x.__bindingPointIndex);o.splice(M,1),r.deleteBuffer(i[x.id]),delete i[x.id],delete s[x.id]}function m(){for(const y in i)r.deleteBuffer(i[y]);o=[],i={},s={}}return{bind:l,update:c,dispose:m}}class ty{constructor(e={}){const{canvas:t=Hg(),context:n=null,depth:i=!0,stencil:s=!1,alpha:o=!1,antialias:a=!1,premultipliedAlpha:l=!0,preserveDrawingBuffer:c=!1,powerPreference:u="default",failIfMajorPerformanceCaveat:f=!1}=e;this.isWebGLRenderer=!0;let h;if(n!==null){if(typeof WebGLRenderingContext<"u"&&n instanceof WebGLRenderingContext)throw new Error("THREE.WebGLRenderer: WebGL 1 is not supported since r163.");h=n.getContextAttributes().alpha}else h=o;const d=new Uint32Array(4),_=new Int32Array(4);let g=null,p=null;const m=[],y=[];this.domElement=t,this.debug={checkShaderErrors:!0,onShaderError:null},this.autoClear=!0,this.autoClearColor=!0,this.autoClearDepth=!0,this.autoClearStencil=!0,this.sortObjects=!0,this.clippingPlanes=[],this.localClippingEnabled=!1,this._outputColorSpace=ai,this.toneMapping=or,this.toneMappingExposure=1;const x=this;let M=!1,R=0,w=0,E=null,D=-1,O=null;const v=new Nt,T=new Nt;let N=null;const z=new at(0);let W=0,K=t.width,G=t.height,X=1,V=null,re=null;const C=new Nt(0,0,K,G),ae=new Nt(0,0,K,G);let Be=!1;const We=new Gp;let q=!1,Q=!1;const fe=new Ot,oe=new Ot,we=new Y,ye=new Nt,Ve={background:null,fog:null,environment:null,overrideMaterial:null,isScene:!0};let Ge=!1;function Ne(){return E===null?X:1}let P=n;function rt(b,U){return t.getContext(b,U)}try{const b={alpha:!0,depth:i,stencil:s,antialias:a,premultipliedAlpha:l,preserveDrawingBuffer:c,powerPreference:u,failIfMajorPerformanceCaveat:f};if("setAttribute"in t&&t.setAttribute("data-engine",`three.js r${Ju}`),t.addEventListener("webglcontextlost",J,!1),t.addEventListener("webglcontextrestored",le,!1),t.addEventListener("webglcontextcreationerror",ce,!1),P===null){const U="webgl2";if(P=rt(U,b),P===null)throw rt(U)?new Error("Error creating WebGL context with your selected attributes."):new Error("Error creating WebGL context.")}}catch(b){throw console.error("THREE.WebGLRenderer: "+b.message),b}let Fe,ze,F,je,De,A,S,H,j,te,Z,Se,ie,de,He,ne,ve,xe,Ie,ge,Xe,Oe,st,L;function ee(){Fe=new oS(P),Fe.init(),Oe=new XM(P,Fe),ze=new Qx(P,Fe,e,Oe),F=new GM(P),ze.reverseDepthBuffer&&F.buffers.depth.setReversed(!0),je=new cS(P),De=new AM,A=new WM(P,Fe,F,De,ze,Oe,je),S=new tS(x),H=new sS(x),j=new m0(P),st=new jx(P,j),te=new aS(P,j,je,st),Z=new hS(P,te,j,je),Ie=new uS(P,ze,A),ne=new eS(De),Se=new wM(x,S,H,Fe,ze,st,ne),ie=new QM(x,De),de=new CM,He=new NM(Fe),xe=new Zx(x,S,H,F,Z,h,l),ve=new kM(x,Z,ze),L=new ey(P,je,ze,F),ge=new Jx(P,Fe,je),Xe=new lS(P,Fe,je),je.programs=Se.programs,x.capabilities=ze,x.extensions=Fe,x.properties=De,x.renderLists=de,x.shadowMap=ve,x.state=F,x.info=je}ee();const $=new jM(x,P);this.xr=$,this.getContext=function(){return P},this.getContextAttributes=function(){return P.getContextAttributes()},this.forceContextLoss=function(){const b=Fe.get("WEBGL_lose_context");b&&b.loseContext()},this.forceContextRestore=function(){const b=Fe.get("WEBGL_lose_context");b&&b.restoreContext()},this.getPixelRatio=function(){return X},this.setPixelRatio=function(b){b!==void 0&&(X=b,this.setSize(K,G,!1))},this.getSize=function(b){return b.set(K,G)},this.setSize=function(b,U,B=!0){if($.isPresenting){console.warn("THREE.WebGLRenderer: Can't change size while VR device is presenting.");return}K=b,G=U,t.width=Math.floor(b*X),t.height=Math.floor(U*X),B===!0&&(t.style.width=b+"px",t.style.height=U+"px"),this.setViewport(0,0,b,U)},this.getDrawingBufferSize=function(b){return b.set(K*X,G*X).floor()},this.setDrawingBufferSize=function(b,U,B){K=b,G=U,X=B,t.width=Math.floor(b*B),t.height=Math.floor(U*B),this.setViewport(0,0,b,U)},this.getCurrentViewport=function(b){return b.copy(v)},this.getViewport=function(b){return b.copy(C)},this.setViewport=function(b,U,B,k){b.isVector4?C.set(b.x,b.y,b.z,b.w):C.set(b,U,B,k),F.viewport(v.copy(C).multiplyScalar(X).round())},this.getScissor=function(b){return b.copy(ae)},this.setScissor=function(b,U,B,k){b.isVector4?ae.set(b.x,b.y,b.z,b.w):ae.set(b,U,B,k),F.scissor(T.copy(ae).multiplyScalar(X).round())},this.getScissorTest=function(){return Be},this.setScissorTest=function(b){F.setScissorTest(Be=b)},this.setOpaqueSort=function(b){V=b},this.setTransparentSort=function(b){re=b},this.getClearColor=function(b){return b.copy(xe.getClearColor())},this.setClearColor=function(){xe.setClearColor.apply(xe,arguments)},this.getClearAlpha=function(){return xe.getClearAlpha()},this.setClearAlpha=function(){xe.setClearAlpha.apply(xe,arguments)},this.clear=function(b=!0,U=!0,B=!0){let k=0;if(b){let I=!1;if(E!==null){const se=E.texture.format;I=se===rh||se===ih||se===nh}if(I){const se=E.texture.type,_e=se===zi||se===Wr||se===Po||se===zs||se===eh||se===th,he=xe.getClearColor(),ue=xe.getClearAlpha(),Ae=he.r,Ue=he.g,be=he.b;_e?(d[0]=Ae,d[1]=Ue,d[2]=be,d[3]=ue,P.clearBufferuiv(P.COLOR,0,d)):(_[0]=Ae,_[1]=Ue,_[2]=be,_[3]=ue,P.clearBufferiv(P.COLOR,0,_))}else k|=P.COLOR_BUFFER_BIT}U&&(k|=P.DEPTH_BUFFER_BIT,P.clearDepth(this.capabilities.reverseDepthBuffer?0:1)),B&&(k|=P.STENCIL_BUFFER_BIT,this.state.buffers.stencil.setMask(4294967295)),P.clear(k)},this.clearColor=function(){this.clear(!0,!1,!1)},this.clearDepth=function(){this.clear(!1,!0,!1)},this.clearStencil=function(){this.clear(!1,!1,!0)},this.dispose=function(){t.removeEventListener("webglcontextlost",J,!1),t.removeEventListener("webglcontextrestored",le,!1),t.removeEventListener("webglcontextcreationerror",ce,!1),de.dispose(),He.dispose(),De.dispose(),S.dispose(),H.dispose(),Z.dispose(),st.dispose(),L.dispose(),Se.dispose(),$.dispose(),$.removeEventListener("sessionstart",ct),$.removeEventListener("sessionend",pe),Le.stop()};function J(b){b.preventDefault(),console.log("THREE.WebGLRenderer: Context Lost."),M=!0}function le(){console.log("THREE.WebGLRenderer: Context Restored."),M=!1;const b=je.autoReset,U=ve.enabled,B=ve.autoUpdate,k=ve.needsUpdate,I=ve.type;ee(),je.autoReset=b,ve.enabled=U,ve.autoUpdate=B,ve.needsUpdate=k,ve.type=I}function ce(b){console.error("THREE.WebGLRenderer: A WebGL context could not be created. Reason: ",b.statusMessage)}function Ye(b){const U=b.target;U.removeEventListener("dispose",Ye),_t(U)}function _t(b){Tt(b),De.remove(b)}function Tt(b){const U=De.get(b).programs;U!==void 0&&(U.forEach(function(B){Se.releaseProgram(B)}),b.isShaderMaterial&&Se.releaseShaderCache(b))}this.renderBufferDirect=function(b,U,B,k,I,se){U===null&&(U=Ve);const _e=I.isMesh&&I.matrixWorld.determinant()<0,he=dt(b,U,B,k,I);F.setMaterial(k,_e);let ue=B.index,Ae=1;if(k.wireframe===!0){if(ue=te.getWireframeAttribute(B),ue===void 0)return;Ae=2}const Ue=B.drawRange,be=B.attributes.position;let ot=Ue.start*Ae,it=(Ue.start+Ue.count)*Ae;se!==null&&(ot=Math.max(ot,se.start*Ae),it=Math.min(it,(se.start+se.count)*Ae)),ue!==null?(ot=Math.max(ot,0),it=Math.min(it,ue.count)):be!=null&&(ot=Math.max(ot,0),it=Math.min(it,be.count));const mt=it-ot;if(mt<0||mt===1/0)return;st.setup(I,k,he,B,ue);let Xt,Je=ge;if(ue!==null&&(Xt=j.get(ue),Je=Xe,Je.setIndex(Xt)),I.isMesh)k.wireframe===!0?(F.setLineWidth(k.wireframeLinewidth*Ne()),Je.setMode(P.LINES)):Je.setMode(P.TRIANGLES);else if(I.isLine){let Pe=k.linewidth;Pe===void 0&&(Pe=1),F.setLineWidth(Pe*Ne()),I.isLineSegments?Je.setMode(P.LINES):I.isLineLoop?Je.setMode(P.LINE_LOOP):Je.setMode(P.LINE_STRIP)}else I.isPoints?Je.setMode(P.POINTS):I.isSprite&&Je.setMode(P.TRIANGLES);if(I.isBatchedMesh)if(I._multiDrawInstances!==null)Je.renderMultiDrawInstances(I._multiDrawStarts,I._multiDrawCounts,I._multiDrawCount,I._multiDrawInstances);else if(Fe.get("WEBGL_multi_draw"))Je.renderMultiDraw(I._multiDrawStarts,I._multiDrawCounts,I._multiDrawCount);else{const Pe=I._multiDrawStarts,Jt=I._multiDrawCounts,ut=I._multiDrawCount,ti=ue?j.get(ue).bytesPerElement:1,qr=De.get(k).currentProgram.getUniforms();for(let Pn=0;Pn<ut;Pn++)qr.setValue(P,"_gl_DrawID",Pn),Je.render(Pe[Pn]/ti,Jt[Pn])}else if(I.isInstancedMesh)Je.renderInstances(ot,mt,I.count);else if(B.isInstancedBufferGeometry){const Pe=B._maxInstanceCount!==void 0?B._maxInstanceCount:1/0,Jt=Math.min(B.instanceCount,Pe);Je.renderInstances(ot,mt,Jt)}else Je.render(ot,mt)};function nt(b,U,B){b.transparent===!0&&b.side===Di&&b.forceSinglePass===!1?(b.side=_n,b.needsUpdate=!0,Lt(b,U,B),b.side=hr,b.needsUpdate=!0,Lt(b,U,B),b.side=Di):Lt(b,U,B)}this.compile=function(b,U,B=null){B===null&&(B=b),p=He.get(B),p.init(U),y.push(p),B.traverseVisible(function(I){I.isLight&&I.layers.test(U.layers)&&(p.pushLight(I),I.castShadow&&p.pushShadow(I))}),b!==B&&b.traverseVisible(function(I){I.isLight&&I.layers.test(U.layers)&&(p.pushLight(I),I.castShadow&&p.pushShadow(I))}),p.setupLights();const k=new Set;return b.traverse(function(I){if(!(I.isMesh||I.isPoints||I.isLine||I.isSprite))return;const se=I.material;if(se)if(Array.isArray(se))for(let _e=0;_e<se.length;_e++){const he=se[_e];nt(he,B,I),k.add(he)}else nt(se,B,I),k.add(se)}),y.pop(),p=null,k},this.compileAsync=function(b,U,B=null){const k=this.compile(b,U,B);return new Promise(I=>{function se(){if(k.forEach(function(_e){De.get(_e).currentProgram.isReady()&&k.delete(_e)}),k.size===0){I(b);return}setTimeout(se,10)}Fe.get("KHR_parallel_shader_compile")!==null?se():setTimeout(se,10)})};let Re=null;function Te(b){Re&&Re(b)}function ct(){Le.stop()}function pe(){Le.start()}const Le=new Vp;Le.setAnimationLoop(Te),typeof self<"u"&&Le.setContext(self),this.setAnimationLoop=function(b){Re=b,$.setAnimationLoop(b),b===null?Le.stop():Le.start()},$.addEventListener("sessionstart",ct),$.addEventListener("sessionend",pe),this.render=function(b,U){if(U!==void 0&&U.isCamera!==!0){console.error("THREE.WebGLRenderer.render: camera is not an instance of THREE.Camera.");return}if(M===!0)return;if(b.matrixWorldAutoUpdate===!0&&b.updateMatrixWorld(),U.parent===null&&U.matrixWorldAutoUpdate===!0&&U.updateMatrixWorld(),$.enabled===!0&&$.isPresenting===!0&&($.cameraAutoUpdate===!0&&$.updateCamera(U),U=$.getCamera()),b.isScene===!0&&b.onBeforeRender(x,b,U,E),p=He.get(b,y.length),p.init(U),y.push(p),oe.multiplyMatrices(U.projectionMatrix,U.matrixWorldInverse),We.setFromProjectionMatrix(oe),Q=this.localClippingEnabled,q=ne.init(this.clippingPlanes,Q),g=de.get(b,m.length),g.init(),m.push(g),$.enabled===!0&&$.isPresenting===!0){const se=x.xr.getDepthSensingMesh();se!==null&&Ce(se,U,-1/0,x.sortObjects)}Ce(b,U,0,x.sortObjects),g.finish(),x.sortObjects===!0&&g.sort(V,re),Ge=$.enabled===!1||$.isPresenting===!1||$.hasDepthSensing()===!1,Ge&&xe.addToRenderList(g,b),this.info.render.frame++,q===!0&&ne.beginShadows();const B=p.state.shadowsArray;ve.render(B,b,U),q===!0&&ne.endShadows(),this.info.autoReset===!0&&this.info.reset();const k=g.opaque,I=g.transmissive;if(p.setupLights(),U.isArrayCamera){const se=U.cameras;if(I.length>0)for(let _e=0,he=se.length;_e<he;_e++){const ue=se[_e];Dt(k,I,b,ue)}Ge&&xe.render(b);for(let _e=0,he=se.length;_e<he;_e++){const ue=se[_e];ke(g,b,ue,ue.viewport)}}else I.length>0&&Dt(k,I,b,U),Ge&&xe.render(b),ke(g,b,U);E!==null&&(A.updateMultisampleRenderTarget(E),A.updateRenderTargetMipmap(E)),b.isScene===!0&&b.onAfterRender(x,b,U),st.resetDefaultState(),D=-1,O=null,y.pop(),y.length>0?(p=y[y.length-1],q===!0&&ne.setGlobalState(x.clippingPlanes,p.state.camera)):p=null,m.pop(),m.length>0?g=m[m.length-1]:g=null};function Ce(b,U,B,k){if(b.visible===!1)return;if(b.layers.test(U.layers)){if(b.isGroup)B=b.renderOrder;else if(b.isLOD)b.autoUpdate===!0&&b.update(U);else if(b.isLight)p.pushLight(b),b.castShadow&&p.pushShadow(b);else if(b.isSprite){if(!b.frustumCulled||We.intersectsSprite(b)){k&&ye.setFromMatrixPosition(b.matrixWorld).applyMatrix4(oe);const _e=Z.update(b),he=b.material;he.visible&&g.push(b,_e,he,B,ye.z,null)}}else if((b.isMesh||b.isLine||b.isPoints)&&(!b.frustumCulled||We.intersectsObject(b))){const _e=Z.update(b),he=b.material;if(k&&(b.boundingSphere!==void 0?(b.boundingSphere===null&&b.computeBoundingSphere(),ye.copy(b.boundingSphere.center)):(_e.boundingSphere===null&&_e.computeBoundingSphere(),ye.copy(_e.boundingSphere.center)),ye.applyMatrix4(b.matrixWorld).applyMatrix4(oe)),Array.isArray(he)){const ue=_e.groups;for(let Ae=0,Ue=ue.length;Ae<Ue;Ae++){const be=ue[Ae],ot=he[be.materialIndex];ot&&ot.visible&&g.push(b,_e,ot,B,ye.z,be)}}else he.visible&&g.push(b,_e,he,B,ye.z,null)}}const se=b.children;for(let _e=0,he=se.length;_e<he;_e++)Ce(se[_e],U,B,k)}function ke(b,U,B,k){const I=b.opaque,se=b.transmissive,_e=b.transparent;p.setupLightsView(B),q===!0&&ne.setGlobalState(x.clippingPlanes,B),k&&F.viewport(v.copy(k)),I.length>0&&qe(I,U,B),se.length>0&&qe(se,U,B),_e.length>0&&qe(_e,U,B),F.buffers.depth.setTest(!0),F.buffers.depth.setMask(!0),F.buffers.color.setMask(!0),F.setPolygonOffset(!1)}function Dt(b,U,B,k){if((B.isScene===!0?B.overrideMaterial:null)!==null)return;p.state.transmissionRenderTarget[k.id]===void 0&&(p.state.transmissionRenderTarget[k.id]=new Xr(1,1,{generateMipmaps:!0,type:Fe.has("EXT_color_buffer_half_float")||Fe.has("EXT_color_buffer_float")?Lo:zi,minFilter:Dr,samples:4,stencilBuffer:s,resolveDepthBuffer:!1,resolveStencilBuffer:!1,colorSpace:ft.workingColorSpace}));const se=p.state.transmissionRenderTarget[k.id],_e=k.viewport||v;se.setSize(_e.z,_e.w);const he=x.getRenderTarget();x.setRenderTarget(se),x.getClearColor(z),W=x.getClearAlpha(),W<1&&x.setClearColor(16777215,.5),x.clear(),Ge&&xe.render(B);const ue=x.toneMapping;x.toneMapping=or;const Ae=k.viewport;if(k.viewport!==void 0&&(k.viewport=void 0),p.setupLightsView(k),q===!0&&ne.setGlobalState(x.clippingPlanes,k),qe(b,B,k),A.updateMultisampleRenderTarget(se),A.updateRenderTargetMipmap(se),Fe.has("WEBGL_multisampled_render_to_texture")===!1){let Ue=!1;for(let be=0,ot=U.length;be<ot;be++){const it=U[be],mt=it.object,Xt=it.geometry,Je=it.material,Pe=it.group;if(Je.side===Di&&mt.layers.test(k.layers)){const Jt=Je.side;Je.side=_n,Je.needsUpdate=!0,bt(mt,B,k,Xt,Je,Pe),Je.side=Jt,Je.needsUpdate=!0,Ue=!0}}Ue===!0&&(A.updateMultisampleRenderTarget(se),A.updateRenderTargetMipmap(se))}x.setRenderTarget(he),x.setClearColor(z,W),Ae!==void 0&&(k.viewport=Ae),x.toneMapping=ue}function qe(b,U,B){const k=U.isScene===!0?U.overrideMaterial:null;for(let I=0,se=b.length;I<se;I++){const _e=b[I],he=_e.object,ue=_e.geometry,Ae=k===null?_e.material:k,Ue=_e.group;he.layers.test(B.layers)&&bt(he,U,B,ue,Ae,Ue)}}function bt(b,U,B,k,I,se){b.onBeforeRender(x,U,B,k,I,se),b.modelViewMatrix.multiplyMatrices(B.matrixWorldInverse,b.matrixWorld),b.normalMatrix.getNormalMatrix(b.modelViewMatrix),I.onBeforeRender(x,U,B,k,b,se),I.transparent===!0&&I.side===Di&&I.forceSinglePass===!1?(I.side=_n,I.needsUpdate=!0,x.renderBufferDirect(B,U,k,I,b,se),I.side=hr,I.needsUpdate=!0,x.renderBufferDirect(B,U,k,I,b,se),I.side=Di):x.renderBufferDirect(B,U,k,I,b,se),b.onAfterRender(x,U,B,k,I,se)}function Lt(b,U,B){U.isScene!==!0&&(U=Ve);const k=De.get(b),I=p.state.lights,se=p.state.shadowsArray,_e=I.state.version,he=Se.getParameters(b,I.state,se,U,B),ue=Se.getProgramCacheKey(he);let Ae=k.programs;k.environment=b.isMeshStandardMaterial?U.environment:null,k.fog=U.fog,k.envMap=(b.isMeshStandardMaterial?H:S).get(b.envMap||k.environment),k.envMapRotation=k.environment!==null&&b.envMap===null?U.environmentRotation:b.envMapRotation,Ae===void 0&&(b.addEventListener("dispose",Ye),Ae=new Map,k.programs=Ae);let Ue=Ae.get(ue);if(Ue!==void 0){if(k.currentProgram===Ue&&k.lightsStateVersion===_e)return gt(b,he),Ue}else he.uniforms=Se.getUniforms(b),b.onBeforeCompile(he,x),Ue=Se.acquireProgram(he,ue),Ae.set(ue,Ue),k.uniforms=he.uniforms;const be=k.uniforms;return(!b.isShaderMaterial&&!b.isRawShaderMaterial||b.clipping===!0)&&(be.clippingPlanes=ne.uniform),gt(b,he),k.needsLights=yt(b),k.lightsStateVersion=_e,k.needsLights&&(be.ambientLightColor.value=I.state.ambient,be.lightProbe.value=I.state.probe,be.directionalLights.value=I.state.directional,be.directionalLightShadows.value=I.state.directionalShadow,be.spotLights.value=I.state.spot,be.spotLightShadows.value=I.state.spotShadow,be.rectAreaLights.value=I.state.rectArea,be.ltc_1.value=I.state.rectAreaLTC1,be.ltc_2.value=I.state.rectAreaLTC2,be.pointLights.value=I.state.point,be.pointLightShadows.value=I.state.pointShadow,be.hemisphereLights.value=I.state.hemi,be.directionalShadowMap.value=I.state.directionalShadowMap,be.directionalShadowMatrix.value=I.state.directionalShadowMatrix,be.spotShadowMap.value=I.state.spotShadowMap,be.spotLightMatrix.value=I.state.spotLightMatrix,be.spotLightMap.value=I.state.spotLightMap,be.pointShadowMap.value=I.state.pointShadowMap,be.pointShadowMatrix.value=I.state.pointShadowMatrix),k.currentProgram=Ue,k.uniformsList=null,Ue}function Mt(b){if(b.uniformsList===null){const U=b.currentProgram.getUniforms();b.uniformsList=Ba.seqWithValue(U.seq,b.uniforms)}return b.uniformsList}function gt(b,U){const B=De.get(b);B.outputColorSpace=U.outputColorSpace,B.batching=U.batching,B.batchingColor=U.batchingColor,B.instancing=U.instancing,B.instancingColor=U.instancingColor,B.instancingMorph=U.instancingMorph,B.skinning=U.skinning,B.morphTargets=U.morphTargets,B.morphNormals=U.morphNormals,B.morphColors=U.morphColors,B.morphTargetsCount=U.morphTargetsCount,B.numClippingPlanes=U.numClippingPlanes,B.numIntersection=U.numClipIntersection,B.vertexAlphas=U.vertexAlphas,B.vertexTangents=U.vertexTangents,B.toneMapping=U.toneMapping}function dt(b,U,B,k,I){U.isScene!==!0&&(U=Ve),A.resetTextureUnits();const se=U.fog,_e=k.isMeshStandardMaterial?U.environment:null,he=E===null?x.outputColorSpace:E.isXRRenderTarget===!0?E.texture.colorSpace:dr,ue=(k.isMeshStandardMaterial?H:S).get(k.envMap||_e),Ae=k.vertexColors===!0&&!!B.attributes.color&&B.attributes.color.itemSize===4,Ue=!!B.attributes.tangent&&(!!k.normalMap||k.anisotropy>0),be=!!B.morphAttributes.position,ot=!!B.morphAttributes.normal,it=!!B.morphAttributes.color;let mt=or;k.toneMapped&&(E===null||E.isXRRenderTarget===!0)&&(mt=x.toneMapping);const Xt=B.morphAttributes.position||B.morphAttributes.normal||B.morphAttributes.color,Je=Xt!==void 0?Xt.length:0,Pe=De.get(k),Jt=p.state.lights;if(q===!0&&(Q===!0||b!==O)){const Wn=b===O&&k.id===D;ne.setState(k,b,Wn)}let ut=!1;k.version===Pe.__version?(Pe.needsLights&&Pe.lightsStateVersion!==Jt.state.version||Pe.outputColorSpace!==he||I.isBatchedMesh&&Pe.batching===!1||!I.isBatchedMesh&&Pe.batching===!0||I.isBatchedMesh&&Pe.batchingColor===!0&&I.colorTexture===null||I.isBatchedMesh&&Pe.batchingColor===!1&&I.colorTexture!==null||I.isInstancedMesh&&Pe.instancing===!1||!I.isInstancedMesh&&Pe.instancing===!0||I.isSkinnedMesh&&Pe.skinning===!1||!I.isSkinnedMesh&&Pe.skinning===!0||I.isInstancedMesh&&Pe.instancingColor===!0&&I.instanceColor===null||I.isInstancedMesh&&Pe.instancingColor===!1&&I.instanceColor!==null||I.isInstancedMesh&&Pe.instancingMorph===!0&&I.morphTexture===null||I.isInstancedMesh&&Pe.instancingMorph===!1&&I.morphTexture!==null||Pe.envMap!==ue||k.fog===!0&&Pe.fog!==se||Pe.numClippingPlanes!==void 0&&(Pe.numClippingPlanes!==ne.numPlanes||Pe.numIntersection!==ne.numIntersection)||Pe.vertexAlphas!==Ae||Pe.vertexTangents!==Ue||Pe.morphTargets!==be||Pe.morphNormals!==ot||Pe.morphColors!==it||Pe.toneMapping!==mt||Pe.morphTargetsCount!==Je)&&(ut=!0):(ut=!0,Pe.__version=k.version);let ti=Pe.currentProgram;ut===!0&&(ti=Lt(k,U,I));let qr=!1,Pn=!1,hl=!1;const It=ti.getUniforms(),Hi=Pe.uniforms;if(F.useProgram(ti.program)&&(qr=!0,Pn=!0,hl=!0),k.id!==D&&(D=k.id,Pn=!0),qr||O!==b){ze.reverseDepthBuffer?(fe.copy(b.projectionMatrix),Vg(fe),Wg(fe),It.setValue(P,"projectionMatrix",fe)):It.setValue(P,"projectionMatrix",b.projectionMatrix),It.setValue(P,"viewMatrix",b.matrixWorldInverse);const Wn=It.map.cameraPosition;Wn!==void 0&&Wn.setValue(P,we.setFromMatrixPosition(b.matrixWorld)),ze.logarithmicDepthBuffer&&It.setValue(P,"logDepthBufFC",2/(Math.log(b.far+1)/Math.LN2)),(k.isMeshPhongMaterial||k.isMeshToonMaterial||k.isMeshLambertMaterial||k.isMeshBasicMaterial||k.isMeshStandardMaterial||k.isShaderMaterial)&&It.setValue(P,"isOrthographic",b.isOrthographicCamera===!0),O!==b&&(O=b,Pn=!0,hl=!0)}if(I.isSkinnedMesh){It.setOptional(P,I,"bindMatrix"),It.setOptional(P,I,"bindMatrixInverse");const Wn=I.skeleton;Wn&&(Wn.boneTexture===null&&Wn.computeBoneTexture(),It.setValue(P,"boneTexture",Wn.boneTexture,A))}I.isBatchedMesh&&(It.setOptional(P,I,"batchingTexture"),It.setValue(P,"batchingTexture",I._matricesTexture,A),It.setOptional(P,I,"batchingIdTexture"),It.setValue(P,"batchingIdTexture",I._indirectTexture,A),It.setOptional(P,I,"batchingColorTexture"),I._colorsTexture!==null&&It.setValue(P,"batchingColorTexture",I._colorsTexture,A));const fl=B.morphAttributes;if((fl.position!==void 0||fl.normal!==void 0||fl.color!==void 0)&&Ie.update(I,B,ti),(Pn||Pe.receiveShadow!==I.receiveShadow)&&(Pe.receiveShadow=I.receiveShadow,It.setValue(P,"receiveShadow",I.receiveShadow)),k.isMeshGouraudMaterial&&k.envMap!==null&&(Hi.envMap.value=ue,Hi.flipEnvMap.value=ue.isCubeTexture&&ue.isRenderTargetTexture===!1?-1:1),k.isMeshStandardMaterial&&k.envMap===null&&U.environment!==null&&(Hi.envMapIntensity.value=U.environmentIntensity),Pn&&(It.setValue(P,"toneMappingExposure",x.toneMappingExposure),Pe.needsLights&&Cn(Hi,hl),se&&k.fog===!0&&ie.refreshFogUniforms(Hi,se),ie.refreshMaterialUniforms(Hi,k,X,G,p.state.transmissionRenderTarget[b.id]),Ba.upload(P,Mt(Pe),Hi,A)),k.isShaderMaterial&&k.uniformsNeedUpdate===!0&&(Ba.upload(P,Mt(Pe),Hi,A),k.uniformsNeedUpdate=!1),k.isSpriteMaterial&&It.setValue(P,"center",I.center),It.setValue(P,"modelViewMatrix",I.modelViewMatrix),It.setValue(P,"normalMatrix",I.normalMatrix),It.setValue(P,"modelMatrix",I.matrixWorld),k.isShaderMaterial||k.isRawShaderMaterial){const Wn=k.uniformsGroups;for(let dl=0,nm=Wn.length;dl<nm;dl++){const lh=Wn[dl];L.update(lh,ti),L.bind(lh,ti)}}return ti}function Cn(b,U){b.ambientLightColor.needsUpdate=U,b.lightProbe.needsUpdate=U,b.directionalLights.needsUpdate=U,b.directionalLightShadows.needsUpdate=U,b.pointLights.needsUpdate=U,b.pointLightShadows.needsUpdate=U,b.spotLights.needsUpdate=U,b.spotLightShadows.needsUpdate=U,b.rectAreaLights.needsUpdate=U,b.hemisphereLights.needsUpdate=U}function yt(b){return b.isMeshLambertMaterial||b.isMeshToonMaterial||b.isMeshPhongMaterial||b.isMeshStandardMaterial||b.isShadowMaterial||b.isShaderMaterial&&b.lights===!0}this.getActiveCubeFace=function(){return R},this.getActiveMipmapLevel=function(){return w},this.getRenderTarget=function(){return E},this.setRenderTargetTextures=function(b,U,B){De.get(b.texture).__webglTexture=U,De.get(b.depthTexture).__webglTexture=B;const k=De.get(b);k.__hasExternalTextures=!0,k.__autoAllocateDepthBuffer=B===void 0,k.__autoAllocateDepthBuffer||Fe.has("WEBGL_multisampled_render_to_texture")===!0&&(console.warn("THREE.WebGLRenderer: Render-to-texture extension was disabled because an external texture was provided"),k.__useRenderToTexture=!1)},this.setRenderTargetFramebuffer=function(b,U){const B=De.get(b);B.__webglFramebuffer=U,B.__useDefaultFramebuffer=U===void 0},this.setRenderTarget=function(b,U=0,B=0){E=b,R=U,w=B;let k=!0,I=null,se=!1,_e=!1;if(b){const ue=De.get(b);if(ue.__useDefaultFramebuffer!==void 0)F.bindFramebuffer(P.FRAMEBUFFER,null),k=!1;else if(ue.__webglFramebuffer===void 0)A.setupRenderTarget(b);else if(ue.__hasExternalTextures)A.rebindTextures(b,De.get(b.texture).__webglTexture,De.get(b.depthTexture).__webglTexture);else if(b.depthBuffer){const be=b.depthTexture;if(ue.__boundDepthTexture!==be){if(be!==null&&De.has(be)&&(b.width!==be.image.width||b.height!==be.image.height))throw new Error("WebGLRenderTarget: Attached DepthTexture is initialized to the incorrect size.");A.setupDepthRenderbuffer(b)}}const Ae=b.texture;(Ae.isData3DTexture||Ae.isDataArrayTexture||Ae.isCompressedArrayTexture)&&(_e=!0);const Ue=De.get(b).__webglFramebuffer;b.isWebGLCubeRenderTarget?(Array.isArray(Ue[U])?I=Ue[U][B]:I=Ue[U],se=!0):b.samples>0&&A.useMultisampledRTT(b)===!1?I=De.get(b).__webglMultisampledFramebuffer:Array.isArray(Ue)?I=Ue[B]:I=Ue,v.copy(b.viewport),T.copy(b.scissor),N=b.scissorTest}else v.copy(C).multiplyScalar(X).floor(),T.copy(ae).multiplyScalar(X).floor(),N=Be;if(F.bindFramebuffer(P.FRAMEBUFFER,I)&&k&&F.drawBuffers(b,I),F.viewport(v),F.scissor(T),F.setScissorTest(N),se){const ue=De.get(b.texture);P.framebufferTexture2D(P.FRAMEBUFFER,P.COLOR_ATTACHMENT0,P.TEXTURE_CUBE_MAP_POSITIVE_X+U,ue.__webglTexture,B)}else if(_e){const ue=De.get(b.texture),Ae=U||0;P.framebufferTextureLayer(P.FRAMEBUFFER,P.COLOR_ATTACHMENT0,ue.__webglTexture,B||0,Ae)}D=-1},this.readRenderTargetPixels=function(b,U,B,k,I,se,_e){if(!(b&&b.isWebGLRenderTarget)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");return}let he=De.get(b).__webglFramebuffer;if(b.isWebGLCubeRenderTarget&&_e!==void 0&&(he=he[_e]),he){F.bindFramebuffer(P.FRAMEBUFFER,he);try{const ue=b.texture,Ae=ue.format,Ue=ue.type;if(!ze.textureFormatReadable(Ae)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in RGBA or implementation defined format.");return}if(!ze.textureTypeReadable(Ue)){console.error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not in UnsignedByteType or implementation defined type.");return}U>=0&&U<=b.width-k&&B>=0&&B<=b.height-I&&P.readPixels(U,B,k,I,Oe.convert(Ae),Oe.convert(Ue),se)}finally{const ue=E!==null?De.get(E).__webglFramebuffer:null;F.bindFramebuffer(P.FRAMEBUFFER,ue)}}},this.readRenderTargetPixelsAsync=async function(b,U,B,k,I,se,_e){if(!(b&&b.isWebGLRenderTarget))throw new Error("THREE.WebGLRenderer.readRenderTargetPixels: renderTarget is not THREE.WebGLRenderTarget.");let he=De.get(b).__webglFramebuffer;if(b.isWebGLCubeRenderTarget&&_e!==void 0&&(he=he[_e]),he){const ue=b.texture,Ae=ue.format,Ue=ue.type;if(!ze.textureFormatReadable(Ae))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in RGBA or implementation defined format.");if(!ze.textureTypeReadable(Ue))throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: renderTarget is not in UnsignedByteType or implementation defined type.");if(U>=0&&U<=b.width-k&&B>=0&&B<=b.height-I){F.bindFramebuffer(P.FRAMEBUFFER,he);const be=P.createBuffer();P.bindBuffer(P.PIXEL_PACK_BUFFER,be),P.bufferData(P.PIXEL_PACK_BUFFER,se.byteLength,P.STREAM_READ),P.readPixels(U,B,k,I,Oe.convert(Ae),Oe.convert(Ue),0);const ot=E!==null?De.get(E).__webglFramebuffer:null;F.bindFramebuffer(P.FRAMEBUFFER,ot);const it=P.fenceSync(P.SYNC_GPU_COMMANDS_COMPLETE,0);return P.flush(),await Gg(P,it,4),P.bindBuffer(P.PIXEL_PACK_BUFFER,be),P.getBufferSubData(P.PIXEL_PACK_BUFFER,0,se),P.deleteBuffer(be),P.deleteSync(it),se}else throw new Error("THREE.WebGLRenderer.readRenderTargetPixelsAsync: requested read bounds are out of range.")}},this.copyFramebufferToTexture=function(b,U=null,B=0){b.isTexture!==!0&&(Oa("WebGLRenderer: copyFramebufferToTexture function signature has changed."),U=arguments[0]||null,b=arguments[1]);const k=Math.pow(2,-B),I=Math.floor(b.image.width*k),se=Math.floor(b.image.height*k),_e=U!==null?U.x:0,he=U!==null?U.y:0;A.setTexture2D(b,0),P.copyTexSubImage2D(P.TEXTURE_2D,B,0,0,_e,he,I,se),F.unbindTexture()},this.copyTextureToTexture=function(b,U,B=null,k=null,I=0){b.isTexture!==!0&&(Oa("WebGLRenderer: copyTextureToTexture function signature has changed."),k=arguments[0]||null,b=arguments[1],U=arguments[2],I=arguments[3]||0,B=null);let se,_e,he,ue,Ae,Ue;B!==null?(se=B.max.x-B.min.x,_e=B.max.y-B.min.y,he=B.min.x,ue=B.min.y):(se=b.image.width,_e=b.image.height,he=0,ue=0),k!==null?(Ae=k.x,Ue=k.y):(Ae=0,Ue=0);const be=Oe.convert(U.format),ot=Oe.convert(U.type);A.setTexture2D(U,0),P.pixelStorei(P.UNPACK_FLIP_Y_WEBGL,U.flipY),P.pixelStorei(P.UNPACK_PREMULTIPLY_ALPHA_WEBGL,U.premultiplyAlpha),P.pixelStorei(P.UNPACK_ALIGNMENT,U.unpackAlignment);const it=P.getParameter(P.UNPACK_ROW_LENGTH),mt=P.getParameter(P.UNPACK_IMAGE_HEIGHT),Xt=P.getParameter(P.UNPACK_SKIP_PIXELS),Je=P.getParameter(P.UNPACK_SKIP_ROWS),Pe=P.getParameter(P.UNPACK_SKIP_IMAGES),Jt=b.isCompressedTexture?b.mipmaps[I]:b.image;P.pixelStorei(P.UNPACK_ROW_LENGTH,Jt.width),P.pixelStorei(P.UNPACK_IMAGE_HEIGHT,Jt.height),P.pixelStorei(P.UNPACK_SKIP_PIXELS,he),P.pixelStorei(P.UNPACK_SKIP_ROWS,ue),b.isDataTexture?P.texSubImage2D(P.TEXTURE_2D,I,Ae,Ue,se,_e,be,ot,Jt.data):b.isCompressedTexture?P.compressedTexSubImage2D(P.TEXTURE_2D,I,Ae,Ue,Jt.width,Jt.height,be,Jt.data):P.texSubImage2D(P.TEXTURE_2D,I,Ae,Ue,se,_e,be,ot,Jt),P.pixelStorei(P.UNPACK_ROW_LENGTH,it),P.pixelStorei(P.UNPACK_IMAGE_HEIGHT,mt),P.pixelStorei(P.UNPACK_SKIP_PIXELS,Xt),P.pixelStorei(P.UNPACK_SKIP_ROWS,Je),P.pixelStorei(P.UNPACK_SKIP_IMAGES,Pe),I===0&&U.generateMipmaps&&P.generateMipmap(P.TEXTURE_2D),F.unbindTexture()},this.copyTextureToTexture3D=function(b,U,B=null,k=null,I=0){b.isTexture!==!0&&(Oa("WebGLRenderer: copyTextureToTexture3D function signature has changed."),B=arguments[0]||null,k=arguments[1]||null,b=arguments[2],U=arguments[3],I=arguments[4]||0);let se,_e,he,ue,Ae,Ue,be,ot,it;const mt=b.isCompressedTexture?b.mipmaps[I]:b.image;B!==null?(se=B.max.x-B.min.x,_e=B.max.y-B.min.y,he=B.max.z-B.min.z,ue=B.min.x,Ae=B.min.y,Ue=B.min.z):(se=mt.width,_e=mt.height,he=mt.depth,ue=0,Ae=0,Ue=0),k!==null?(be=k.x,ot=k.y,it=k.z):(be=0,ot=0,it=0);const Xt=Oe.convert(U.format),Je=Oe.convert(U.type);let Pe;if(U.isData3DTexture)A.setTexture3D(U,0),Pe=P.TEXTURE_3D;else if(U.isDataArrayTexture||U.isCompressedArrayTexture)A.setTexture2DArray(U,0),Pe=P.TEXTURE_2D_ARRAY;else{console.warn("THREE.WebGLRenderer.copyTextureToTexture3D: only supports THREE.DataTexture3D and THREE.DataTexture2DArray.");return}P.pixelStorei(P.UNPACK_FLIP_Y_WEBGL,U.flipY),P.pixelStorei(P.UNPACK_PREMULTIPLY_ALPHA_WEBGL,U.premultiplyAlpha),P.pixelStorei(P.UNPACK_ALIGNMENT,U.unpackAlignment);const Jt=P.getParameter(P.UNPACK_ROW_LENGTH),ut=P.getParameter(P.UNPACK_IMAGE_HEIGHT),ti=P.getParameter(P.UNPACK_SKIP_PIXELS),qr=P.getParameter(P.UNPACK_SKIP_ROWS),Pn=P.getParameter(P.UNPACK_SKIP_IMAGES);P.pixelStorei(P.UNPACK_ROW_LENGTH,mt.width),P.pixelStorei(P.UNPACK_IMAGE_HEIGHT,mt.height),P.pixelStorei(P.UNPACK_SKIP_PIXELS,ue),P.pixelStorei(P.UNPACK_SKIP_ROWS,Ae),P.pixelStorei(P.UNPACK_SKIP_IMAGES,Ue),b.isDataTexture||b.isData3DTexture?P.texSubImage3D(Pe,I,be,ot,it,se,_e,he,Xt,Je,mt.data):U.isCompressedArrayTexture?P.compressedTexSubImage3D(Pe,I,be,ot,it,se,_e,he,Xt,mt.data):P.texSubImage3D(Pe,I,be,ot,it,se,_e,he,Xt,Je,mt),P.pixelStorei(P.UNPACK_ROW_LENGTH,Jt),P.pixelStorei(P.UNPACK_IMAGE_HEIGHT,ut),P.pixelStorei(P.UNPACK_SKIP_PIXELS,ti),P.pixelStorei(P.UNPACK_SKIP_ROWS,qr),P.pixelStorei(P.UNPACK_SKIP_IMAGES,Pn),I===0&&U.generateMipmaps&&P.generateMipmap(Pe),F.unbindTexture()},this.initRenderTarget=function(b){De.get(b).__webglFramebuffer===void 0&&A.setupRenderTarget(b)},this.initTexture=function(b){b.isCubeTexture?A.setTextureCube(b,0):b.isData3DTexture?A.setTexture3D(b,0):b.isDataArrayTexture||b.isCompressedArrayTexture?A.setTexture2DArray(b,0):A.setTexture2D(b,0),F.unbindTexture()},this.resetState=function(){R=0,w=0,E=null,F.reset(),st.reset()},typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}get coordinateSystem(){return Ni}get outputColorSpace(){return this._outputColorSpace}set outputColorSpace(e){this._outputColorSpace=e;const t=this.getContext();t.drawingBufferColorSpace=e===sh?"display-p3":"srgb",t.unpackColorSpace=ft.workingColorSpace===ll?"display-p3":"srgb"}}class ny extends An{constructor(){super(),this.isScene=!0,this.type="Scene",this.background=null,this.environment=null,this.fog=null,this.backgroundBlurriness=0,this.backgroundIntensity=1,this.backgroundRotation=new ki,this.environmentIntensity=1,this.environmentRotation=new ki,this.overrideMaterial=null,typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("observe",{detail:this}))}copy(e,t){return super.copy(e,t),e.background!==null&&(this.background=e.background.clone()),e.environment!==null&&(this.environment=e.environment.clone()),e.fog!==null&&(this.fog=e.fog.clone()),this.backgroundBlurriness=e.backgroundBlurriness,this.backgroundIntensity=e.backgroundIntensity,this.backgroundRotation.copy(e.backgroundRotation),this.environmentIntensity=e.environmentIntensity,this.environmentRotation.copy(e.environmentRotation),e.overrideMaterial!==null&&(this.overrideMaterial=e.overrideMaterial.clone()),this.matrixAutoUpdate=e.matrixAutoUpdate,this}toJSON(e){const t=super.toJSON(e);return this.fog!==null&&(t.object.fog=this.fog.toJSON()),this.backgroundBlurriness>0&&(t.object.backgroundBlurriness=this.backgroundBlurriness),this.backgroundIntensity!==1&&(t.object.backgroundIntensity=this.backgroundIntensity),t.object.backgroundRotation=this.backgroundRotation.toArray(),this.environmentIntensity!==1&&(t.object.environmentIntensity=this.environmentIntensity),t.object.environmentRotation=this.environmentRotation.toArray(),t}}class iy extends Fo{constructor(e){super(),this.isPointsMaterial=!0,this.type="PointsMaterial",this.color=new at(16777215),this.map=null,this.alphaMap=null,this.size=1,this.sizeAttenuation=!0,this.fog=!0,this.setValues(e)}copy(e){return super.copy(e),this.color.copy(e.color),this.map=e.map,this.alphaMap=e.alphaMap,this.size=e.size,this.sizeAttenuation=e.sizeAttenuation,this.fog=e.fog,this}}const Gf=new Ot,yu=new Ip,Ma=new cl,ya=new Y;class Kp extends An{constructor(e=new fi,t=new iy){super(),this.isPoints=!0,this.type="Points",this.geometry=e,this.material=t,this.updateMorphTargets()}copy(e,t){return super.copy(e,t),this.material=Array.isArray(e.material)?e.material.slice():e.material,this.geometry=e.geometry,this}raycast(e,t){const n=this.geometry,i=this.matrixWorld,s=e.params.Points.threshold,o=n.drawRange;if(n.boundingSphere===null&&n.computeBoundingSphere(),Ma.copy(n.boundingSphere),Ma.applyMatrix4(i),Ma.radius+=s,e.ray.intersectsSphere(Ma)===!1)return;Gf.copy(i).invert(),yu.copy(e.ray).applyMatrix4(Gf);const a=s/((this.scale.x+this.scale.y+this.scale.z)/3),l=a*a,c=n.index,f=n.attributes.position;if(c!==null){const h=Math.max(0,o.start),d=Math.min(c.count,o.start+o.count);for(let _=h,g=d;_<g;_++){const p=c.getX(_);ya.fromBufferAttribute(f,p),Vf(ya,p,l,i,e,t,this)}}else{const h=Math.max(0,o.start),d=Math.min(f.count,o.start+o.count);for(let _=h,g=d;_<g;_++)ya.fromBufferAttribute(f,_),Vf(ya,_,l,i,e,t,this)}}updateMorphTargets(){const t=this.geometry.morphAttributes,n=Object.keys(t);if(n.length>0){const i=t[n[0]];if(i!==void 0){this.morphTargetInfluences=[],this.morphTargetDictionary={};for(let s=0,o=i.length;s<o;s++){const a=i[s].name||String(s);this.morphTargetInfluences.push(0),this.morphTargetDictionary[a]=s}}}}}function Vf(r,e,t,n,i,s,o){const a=yu.distanceSqToPoint(r);if(a<t){const l=new Y;yu.closestPointToPoint(r,l),l.applyMatrix4(n);const c=i.ray.origin.distanceTo(l);if(c<i.near||c>i.far)return;s.push({distance:c,distanceToRay:Math.sqrt(a),point:l,index:e,face:null,faceIndex:null,barycoord:null,object:o})}}class Zp extends gn{constructor(e,t,n,i,s,o,a,l,c){super(e,t,n,i,s,o,a,l,c),this.isCanvasTexture=!0,this.needsUpdate=!0}}class ah extends fi{constructor(e=1,t=32,n=16,i=0,s=Math.PI*2,o=0,a=Math.PI){super(),this.type="SphereGeometry",this.parameters={radius:e,widthSegments:t,heightSegments:n,phiStart:i,phiLength:s,thetaStart:o,thetaLength:a},t=Math.max(3,Math.floor(t)),n=Math.max(2,Math.floor(n));const l=Math.min(o+a,Math.PI);let c=0;const u=[],f=new Y,h=new Y,d=[],_=[],g=[],p=[];for(let m=0;m<=n;m++){const y=[],x=m/n;let M=0;m===0&&o===0?M=.5/t:m===n&&l===Math.PI&&(M=-.5/t);for(let R=0;R<=t;R++){const w=R/t;f.x=-e*Math.cos(i+w*s)*Math.sin(o+x*a),f.y=e*Math.cos(o+x*a),f.z=e*Math.sin(i+w*s)*Math.sin(o+x*a),_.push(f.x,f.y,f.z),h.copy(f).normalize(),g.push(h.x,h.y,h.z),p.push(w+M,1-x),y.push(c++)}u.push(y)}for(let m=0;m<n;m++)for(let y=0;y<t;y++){const x=u[m][y+1],M=u[m][y],R=u[m+1][y],w=u[m+1][y+1];(m!==0||o>0)&&d.push(x,M,w),(m!==n-1||l<Math.PI)&&d.push(M,R,w)}this.setIndex(d),this.setAttribute("position",new Si(_,3)),this.setAttribute("normal",new Si(g,3)),this.setAttribute("uv",new Si(p,2))}copy(e){return super.copy(e),this.parameters=Object.assign({},e.parameters),this}static fromJSON(e){return new ah(e.radius,e.widthSegments,e.heightSegments,e.phiStart,e.phiLength,e.thetaStart,e.thetaLength)}}class ry{constructor(e=!0){this.autoStart=e,this.startTime=0,this.oldTime=0,this.elapsedTime=0,this.running=!1}start(){this.startTime=Wf(),this.oldTime=this.startTime,this.elapsedTime=0,this.running=!0}stop(){this.getElapsedTime(),this.running=!1,this.autoStart=!1}getElapsedTime(){return this.getDelta(),this.elapsedTime}getDelta(){let e=0;if(this.autoStart&&!this.running)return this.start(),0;if(this.running){const t=Wf();e=(t-this.oldTime)/1e3,this.oldTime=t,this.elapsedTime+=e}return e}}function Wf(){return performance.now()}typeof __THREE_DEVTOOLS__<"u"&&__THREE_DEVTOOLS__.dispatchEvent(new CustomEvent("register",{detail:{revision:Ju}}));typeof window<"u"&&(window.__THREE__?console.warn("WARNING: Multiple instances of Three.js being imported."):window.__THREE__=Ju);const sy=`
  uniform float uTime;
  uniform float uStorm;
  uniform sampler2D uRippleTex;
  uniform float uRippleScale;
  uniform float uHasRipple;

  varying vec3 vWorldPos;
  varying vec3 vNormal;
  varying float vFoam;
  varying float vRipple;

  #define PI 3.14159265359

  vec3 gerstner(vec2 pos, vec2 dir, float steepness, float wavelength, float speed, float t, inout vec3 tangent, inout vec3 binormal) {
    float k = 2.0 * PI / wavelength;
    vec2 d = normalize(dir);
    float f = k * (dot(d, pos) - speed * t);
    float a = steepness / k;
    float sinF = sin(f);
    float cosF = cos(f);

    tangent += vec3(
      -d.x * d.x * steepness * sinF,
       d.x * steepness * cosF,
      -d.x * d.y * steepness * sinF
    );
    binormal += vec3(
      -d.x * d.y * steepness * sinF,
       d.y * steepness * cosF,
      -d.y * d.y * steepness * sinF
    );

    return vec3(d.x * a * cosF, a * sinF, d.y * a * cosF);
  }

  void main() {
    vec3 tangent = vec3(1.0, 0.0, 0.0);
    vec3 binormal = vec3(0.0, 0.0, 1.0);
    vec2 xz = position.xz;

    // Keep sum(steepness_i * amp) comfortably under 1.0 — Gerstner waves
    // fold into sharp, faceted cusps past that, which reads as broken
    // low-poly geometry rather than a rougher sea.
    float amp = mix(0.35, 1.15, uStorm);
    vec3 wave = vec3(0.0);
    wave += gerstner(xz, vec2(1.0, 0.28), 0.30 * amp, 22.0, 1.05, uTime, tangent, binormal);
    wave += gerstner(xz, vec2(0.55, -0.83), 0.22 * amp, 12.5, 1.55, uTime, tangent, binormal);
    wave += gerstner(xz, vec2(-0.42, 0.91), 0.16 * amp, 6.8, 2.05, uTime, tangent, binormal);
    wave += gerstner(xz, vec2(0.88, 0.47), 0.095 * amp, 3.3, 2.75, uTime, tangent, binormal);
    wave += gerstner(xz, vec2(-0.66, -0.52), 0.055 * amp, 1.6, 3.6, uTime, tangent, binormal);

    vec3 p = position + wave;

    float ripple = 0.0;
    if (uHasRipple > 0.5) {
      vec2 rUv = xz * uRippleScale + 0.5;
      if (rUv.x > 0.0 && rUv.x < 1.0 && rUv.y > 0.0 && rUv.y < 1.0) {
        ripple = texture2D(uRippleTex, rUv).r;
        p.y += ripple * 0.55;
      }
    }

    vec3 normal = normalize(cross(binormal, tangent));

    vWorldPos = (modelMatrix * vec4(p, 1.0)).xyz;
    vNormal = normalize(mat3(modelMatrix) * normal);
    vFoam = clamp(length(wave.xz) * 1.15 - 0.16, 0.0, 1.0) * mix(0.12, 1.0, uStorm) + ripple * 0.7;
    vRipple = ripple;

    vec4 mvPosition = modelViewMatrix * vec4(p, 1.0);
    gl_Position = projectionMatrix * mvPosition;
  }
`,oy=`
  uniform vec3 uDeepColor;
  uniform vec3 uShallowColor;
  uniform vec3 uSkyHorizon;
  uniform vec3 uSkyZenith;
  uniform vec3 uMoonColor;
  uniform vec3 uMoonDir;
  uniform vec3 uCameraPos;
  uniform float uFogDensity;
  uniform vec3 uFogColor;
  uniform float uMoonIntensity;
  uniform float uNearFoam;

  varying vec3 vWorldPos;
  varying vec3 vNormal;
  varying float vFoam;
  varying float vRipple;

  float hash(vec2 p) {
    return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453123);
  }

  void main() {
    vec3 N = normalize(vNormal);
    vec3 V = normalize(uCameraPos - vWorldPos);

    float fresnelRaw = pow(1.0 - clamp(dot(N, V), 0.0, 1.0), 4.0);
    float fresnel = mix(0.02, 0.92, fresnelRaw);

    vec3 reflColor = mix(uSkyHorizon, uSkyZenith, clamp(N.y * 0.5 + 0.5, 0.0, 1.0));
    vec3 baseWater = mix(uDeepColor, uShallowColor, clamp(N.y, 0.0, 1.0) * 0.35);

    vec3 color = mix(baseWater, reflColor, fresnel);

    // Real specular "masking" fades a grazing-angle highlight out rather
    // than letting it saturate — without this, a directional moon smears
    // into a hard, faceted band right along the low-poly horizon.
    float grazing = smoothstep(0.0, 0.22, dot(N, V));

    vec3 H = normalize(V + uMoonDir);
    float ndh = max(dot(N, H), 0.0);
    float spec = pow(ndh, 260.0) * uMoonIntensity;
    float specWide = pow(ndh, 60.0) * 0.09 * uMoonIntensity;
    color += uMoonColor * (spec * 1.1 + specWide) * grazing;

    float foam = clamp(vFoam, 0.0, 1.0);
    color = mix(color, vec3(0.85, 0.90, 0.93), foam * 0.85);

    float dist = length(uCameraPos - vWorldPos);
    float nearFoam = uNearFoam * smoothstep(6.0, 0.6, dist);
    color = mix(color, vec3(0.88, 0.92, 0.95), nearFoam * 0.6);

    float fogFactor = 1.0 - exp(-uFogDensity * uFogDensity * dist * dist * 0.0011);
    color = mix(color, uFogColor, clamp(fogFactor, 0.0, 1.0));

    color += (hash(gl_FragCoord.xy) - 0.5) * 0.006;

    gl_FragColor = vec4(color, 1.0);
  }
`,ay=`
  varying vec3 vPos;
  void main() {
    vPos = position;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`,ly=`
  uniform vec3 uZenith;
  uniform vec3 uHorizon;
  uniform vec3 uFogColor;
  uniform vec3 uMoonDir;
  uniform vec3 uMoonColor;
  uniform float uMoonIntensity;
  uniform float uStars;
  uniform float uTime;

  varying vec3 vPos;

  float hash(vec3 p) {
    return fract(sin(dot(p, vec3(12.9898, 78.233, 37.719))) * 43758.5453123);
  }

  void main() {
    vec3 dir = normalize(vPos);
    float h = clamp(dir.y * 0.5 + 0.5, 0.0, 1.0);
    vec3 sky = mix(uHorizon, uZenith, pow(h, 0.55));

    float band = 1.0 - smoothstep(0.0, 0.22, abs(dir.y - 0.02));
    sky = mix(sky, uFogColor, band * 0.55);

    float starN = hash(floor(dir * 480.0));
    float twinkle = 0.55 + 0.45 * sin(uTime * 1.6 + starN * 62.0);
    float star = smoothstep(0.9955, 1.0, starN) * uStars * twinkle * step(0.05, dir.y);
    sky += vec3(star);

    vec3 md = normalize(uMoonDir);
    float moonDot = dot(dir, md);
    float moonDisc = smoothstep(0.99820, 0.99880, moonDot);
    float moonGlow = pow(max(moonDot, 0.0), 200.0) * 0.55 + pow(max(moonDot, 0.0), 8.0) * 0.10;
    sky += uMoonColor * (moonDisc * 1.3 + moonGlow) * uMoonIntensity;

    // dark, near-flat gradients band badly at 8-bit — a whisper of dither
    // (well under a step) breaks the banding without reading as noise.
    sky += (hash(dir * 913.7 + uTime * 0.01) - 0.5) * 0.006;

    gl_FragColor = vec4(sky, 1.0);
  }
`;class cy{constructor(e=160){this.size=e,this.canvas=document.createElement("canvas"),this.canvas.width=e,this.canvas.height=e,this.ctx=this.canvas.getContext("2d"),this.texture=new Zp(this.canvas),this.texture.wrapS=Ii,this.texture.wrapT=Ii,this.ripples=[],this.active=!1}add(e,t){this.ripples.push({u:e,v:t,born:performance.now()}),this.ripples.length>10&&this.ripples.shift(),this.active=!0}update(){if(!this.active)return;const{ctx:e,size:t}=this;e.clearRect(0,0,t,t);const n=performance.now();let i=!1;for(const s of this.ripples){const o=(n-s.born)/1e3,a=2.6;if(o>a)continue;i=!0;const l=o/a,c=l*t*.42,u=(1-l)*.85,f=s.u*t,h=(1-s.v)*t,d=e.createRadialGradient(f,h,Math.max(c-6,0),f,h,c);d.addColorStop(0,"rgba(255,255,255,0)"),d.addColorStop(.72,`rgba(255,255,255,${u*.9})`),d.addColorStop(1,"rgba(255,255,255,0)"),e.strokeStyle=d,e.lineWidth=2.2,e.beginPath(),e.arc(f,h,c,0,Math.PI*2),e.stroke()}this.texture.needsUpdate=!0,i||(this.active=!1,e.clearRect(0,0,t,t),this.texture.needsUpdate=!0)}dispose(){this.texture.dispose()}}function jp(r=64){const e=document.createElement("canvas");e.width=e.height=r;const t=e.getContext("2d"),n=t.createRadialGradient(r/2,r/2,0,r/2,r/2,r/2);n.addColorStop(0,"rgba(255,255,255,0.95)"),n.addColorStop(.4,"rgba(255,255,255,0.35)"),n.addColorStop(1,"rgba(255,255,255,0)"),t.fillStyle=n,t.fillRect(0,0,r,r);const i=new Zp(e);return i.needsUpdate=!0,i}class uy{constructor(e=420){this.count=e;const t=new Float32Array(e*3),n=new Float32Array(e),i=new Float32Array(e);for(let o=0;o<e;o++){const a=Math.random()*Math.PI*2,l=3+Math.random()*22;t[o*3]=Math.cos(a)*l,t[o*3+1]=Math.random()*4.2-.4,t[o*3+2]=Math.sin(a)*l-6,n[o]=Math.random()*1e3,i[o]=.4+Math.random()*1.3}const s=new fi;s.setAttribute("position",new Zt(t,3)),s.setAttribute("aSeed",new Zt(n,1)),s.setAttribute("aSize",new Zt(i,1)),this.material=new ei({transparent:!0,depthWrite:!1,blending:zr,uniforms:{uTime:{value:0},uOpacity:{value:0},uMap:{value:jp()},uPixelRatio:{value:Math.min(devicePixelRatio||1,2)}},vertexShader:`
        uniform float uTime;
        uniform float uPixelRatio;
        attribute float aSeed;
        attribute float aSize;
        varying float vFade;
        void main() {
          vec3 p = position;
          p.x += sin(uTime * 0.06 + aSeed) * 1.4;
          p.y += sin(uTime * 0.05 + aSeed * 1.7) * 0.25 + 0.15;
          p.z += cos(uTime * 0.045 + aSeed * 0.6) * 1.1;
          vec4 mv = modelViewMatrix * vec4(p, 1.0);
          float dist = -mv.z;
          gl_PointSize = aSize * uPixelRatio * 46.0 / dist;
          vFade = smoothstep(26.0, 4.0, dist) * smoothstep(0.0, 3.0, dist);
          gl_Position = projectionMatrix * mv;
        }
      `,fragmentShader:`
        uniform sampler2D uMap;
        uniform float uOpacity;
        varying float vFade;
        void main() {
          vec4 tex = texture2D(uMap, gl_PointCoord);
          gl_FragColor = vec4(vec3(0.86,0.90,0.94), tex.a * vFade * uOpacity * 0.5);
        }
      `}),this.points=new Kp(s,this.material),this.points.frustumCulled=!1}update(e,t){this.material.uniforms.uTime.value=e,this.material.uniforms.uOpacity.value=t}dispose(){this.points.geometry.dispose(),this.material.dispose(),this.material.uniforms.uMap.value.dispose()}}class hy{constructor(e=260){this.count=e;const t=new Float32Array(e),n=new Float32Array(e),i=new Float32Array(e),s=new Float32Array(e);for(let l=0;l<e;l++)t[l]=Math.random(),n[l]=Math.random()*Math.PI*2,i[l]=Math.pow(Math.random(),1.4)*.62,s[l]=.5+Math.random()*1.6;const o=new Float32Array(e*3),a=new fi;a.setAttribute("position",new Zt(o,3)),a.setAttribute("aSeed",new Zt(t,1)),a.setAttribute("aAngle",new Zt(n,1)),a.setAttribute("aDelay",new Zt(i,1)),a.setAttribute("aSize",new Zt(s,1)),this.material=new ei({transparent:!0,depthWrite:!1,depthTest:!1,blending:Uc,uniforms:{uProgress:{value:0},uMap:{value:jp()},uPixelRatio:{value:Math.min(devicePixelRatio||1,2)}},vertexShader:`
        uniform float uProgress;
        uniform float uPixelRatio;
        attribute float aSeed;
        attribute float aAngle;
        attribute float aDelay;
        attribute float aSize;
        varying float vAlpha;

        float easeOutCubic(float x){ return 1.0 - pow(1.0 - x, 3.0); }

        void main() {
          float t = clamp((uProgress - aDelay) / (1.0 - aDelay), 0.0, 1.0);
          float e = easeOutCubic(t);

          float radius0 = 0.12 + aSeed * 0.28;
          vec3 start = vec3(cos(aAngle) * radius0, sin(aAngle) * radius0 * 0.6, -1.35);

          float spread = 1.6 + aSeed * 3.4;
          vec3 end = vec3(
            cos(aAngle) * spread,
            sin(aAngle) * spread * 0.5 - 1.4 - aSeed * 1.2,
            -1.35 + e * (1.55 + aSeed * 0.6)
          );

          vec3 p = mix(start, end, e);

          // Points is a child of the camera, so local space === view space:
          // skip modelViewMatrix and project the local position directly.
          vec4 mvPosition = vec4(p, 1.0);
          gl_Position = projectionMatrix * mvPosition;

          float distScale = 1.0 / max(-mvPosition.z + 1.6, 0.4);
          gl_PointSize = aSize * uPixelRatio * 30.0 * distScale;

          vAlpha = (1.0 - smoothstep(0.72, 1.0, t)) * smoothstep(0.0, 0.08, t) * step(0.001, uProgress);
        }
      `,fragmentShader:`
        uniform sampler2D uMap;
        varying float vAlpha;
        void main() {
          vec4 tex = texture2D(uMap, gl_PointCoord);
          gl_FragColor = vec4(vec3(0.90, 0.94, 0.98), tex.a * vAlpha * 0.85);
        }
      `}),this.points=new Kp(a,this.material),this.points.frustumCulled=!1,this.points.renderOrder=999}setProgress(e){this.material.uniforms.uProgress.value=e}dispose(){this.points.geometry.dispose(),this.material.dispose(),this.material.uniforms.uMap.value.dispose()}}const fy=(r,e,t)=>r+(e-r)*t,nl=(r,e,t,n)=>fy(r,e,1-Math.exp(-t*n)),si={deep:new at("#050a12"),shallow:new at("#16222c"),skyHorizon:new at("#1a2632"),skyZenith:new at("#050708"),moon:new at("#eef3f7"),fog:new at("#0a0f16")};class dy{constructor(e,{quality:t="high",reducedMotion:n=!1}={}){this.canvas=e,this.quality=t,this.reducedMotion=n,this.clock=new ry,this.elapsed=0,this.mouseX=0,this.mouseY=0,this.mouseXd=0,this.mouseYd=0,this._initRenderer(),this._initScene(),this._initWater(),this._initSky(),this._initParticles(),this.state={storm:.08,fog:.35,moonIntensity:.35,camHeight:2.1,camDist:9.5,camDriftAmp:1,breakProgress:0,nearFoam:0,stars:.5,intimacy:0}}_initRenderer(){const e=this.quality==="low";this.renderer=new ty({canvas:this.canvas,antialias:!e,alpha:!1,powerPreference:"high-performance",stencil:!1}),this.renderer.setClearColor(si.skyZenith,1);const t=e?1.6:2;this.renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,t)),this.renderer.outputColorSpace=ai}_initScene(){this.scene=new ny,this.camera=new Kn(52,1,.1,900),this.camera.position.set(0,2.1,9.5),this.camera.lookAt(0,.6,-8),this.scene.add(this.camera)}_initWater(){const e=this.quality==="low"?130:this.quality==="mid"?200:300,t=340,n=new Bo(t,t,e,e);n.rotateX(-Math.PI/2),this.ripple=new cy(160),this.waterUniforms={uTime:{value:0},uStorm:{value:.08},uRippleTex:{value:this.ripple.texture},uRippleScale:{value:1/60},uHasRipple:{value:0},uDeepColor:{value:si.deep},uShallowColor:{value:si.shallow},uSkyHorizon:{value:si.skyHorizon},uSkyZenith:{value:si.skyZenith},uMoonColor:{value:si.moon},uMoonDir:{value:new Y(.32,.58,-.62).normalize()},uCameraPos:{value:this.camera.position},uFogDensity:{value:.35},uFogColor:{value:si.fog},uMoonIntensity:{value:.35},uNearFoam:{value:0}};const i=new ei({uniforms:this.waterUniforms,vertexShader:sy,fragmentShader:oy});this.water=new hi(n,i),this.scene.add(this.water)}_initSky(){const e=new ah(480,48,32);this.skyUniforms={uZenith:{value:si.skyZenith},uHorizon:{value:si.skyHorizon},uFogColor:{value:si.fog},uMoonDir:{value:this.waterUniforms.uMoonDir.value},uMoonColor:{value:si.moon},uMoonIntensity:{value:.35},uStars:{value:.5},uTime:{value:0}};const t=new ei({uniforms:this.skyUniforms,vertexShader:ay,fragmentShader:ly,side:_n,depthWrite:!1,fog:!1});this.sky=new hi(e,t),this.scene.add(this.sky)}_initParticles(){const e=this.quality==="low"?120:this.quality==="mid"?260:420;this.mist=new uy(e),this.scene.add(this.mist.points);const t=this.quality==="low"?90:this.quality==="mid"?170:260;this.spray=new hy(t),this.camera.add(this.spray.points)}setSize(e,t){this.renderer.setSize(e,t,!1),this.camera.aspect=e/t,this.camera.updateProjectionMatrix()}setMouse(e,t){this.mouseX=e,this.mouseY=t}addRipple(e,t){this.ripple.add(e*.5+.5,t*.5+.5),this.waterUniforms.uHasRipple.value=1}setState(e){Object.assign(this.state,e)}update(e){const t=Math.min(e??this.clock.getDelta(),.05);this.elapsed+=t;const n=this.state;if(this.mouseXd=nl(this.mouseXd,this.mouseX,3.2,t),this.mouseYd=nl(this.mouseYd,this.mouseY,3.2,t),!this.reducedMotion){this.ripple.update();const i=n.camDriftAmp,s=this.elapsed,o=Math.sin(s*.05)*.55+Math.sin(s*.021)*.3,a=n.breakProgress,l=n.camHeight-a*(n.camHeight-.28)+this.mouseYd*.1*(1-a*.6),c=n.camDist-a*(n.camDist-1.35),u=o*.5*i+this.mouseXd*.55;this.camera.position.set(u,l,c);const f=this.mouseXd*.9+o*.18*i,h=l-.35-a*.05;this.camera.lookAt(f,h,c-9),this.waterUniforms.uTime.value=this.elapsed,this.waterUniforms.uStorm.value=n.storm,this.waterUniforms.uFogDensity.value=n.fog,this.waterUniforms.uMoonIntensity.value=n.moonIntensity,this.waterUniforms.uNearFoam.value=n.nearFoam,this.skyUniforms.uTime.value=this.elapsed,this.skyUniforms.uMoonIntensity.value=n.moonIntensity,this.skyUniforms.uStars.value=n.stars,this.mist.update(this.elapsed,Math.min(1,.4+n.fog*.6)),this.spray.setProgress(n.breakProgress)}this.renderer.render(this.scene,this.camera)}dispose(){this.water.geometry.dispose(),this.water.material.dispose(),this.sky.geometry.dispose(),this.sky.material.dispose(),this.mist.dispose(),this.spray.dispose(),this.ripple.dispose(),this.renderer.dispose()}}class py{constructor(){this.ctx=null,this.ready=!1,this.muted=!0,this.master=null,this._targets={wave:0,wind:0,rumble:0}}_makeNoiseBuffer(e=4){const t=this.ctx,n=t.createBuffer(1,t.sampleRate*e,t.sampleRate),i=n.getChannelData(0);let s=0,o=0,a=0;for(let l=0;l<i.length;l++){const c=Math.random()*2-1;s=.997*s+c*.03,o=.985*o+c*.06,a=.94*a+c*.12,i[l]=(s+o+a)*.7}return n}init(){if(this.ctx)return;const e=window.AudioContext||window.webkitAudioContext;this.ctx=new e;const t=this.ctx;this.master=t.createGain(),this.master.gain.value=0,this.master.connect(t.destination);const n=t.createBufferSource();n.buffer=this._makeNoiseBuffer(6),n.loop=!0;const i=t.createBiquadFilter();i.type="lowpass",i.frequency.value=420,i.Q.value=.4,this.waveGain=t.createGain(),this.waveGain.gain.value=.5;const s=t.createOscillator();s.frequency.value=.085;const o=t.createGain();o.gain.value=.22,s.connect(o),o.connect(this.waveGain.gain),n.connect(i).connect(this.waveGain).connect(this.master),n.start(),s.start();const a=t.createBufferSource();a.buffer=this._makeNoiseBuffer(5),a.loop=!0;const l=t.createBiquadFilter();l.type="bandpass",l.frequency.value=900,l.Q.value=.6,this.windGain=t.createGain(),this.windGain.gain.value=.18;const c=t.createOscillator();c.frequency.value=.19;const u=t.createGain();u.gain.value=.09,c.connect(u),u.connect(this.windGain.gain),a.connect(l).connect(this.windGain).connect(this.master),a.start(),c.start(),this.windFilter=l;const f=t.createBufferSource();f.buffer=this._makeNoiseBuffer(7),f.loop=!0;const h=t.createBiquadFilter();h.type="lowpass",h.frequency.value=140,this.rumbleGain=t.createGain(),this.rumbleGain.gain.value=0,f.connect(h).connect(this.rumbleGain).connect(this.master),f.start(),this.waveFilter=i,this.ready=!0}async unlock(){this.init(),this.ctx.state==="suspended"&&await this.ctx.resume()}setMuted(e){if(this.muted=e,!this.ctx)return;const t=this.ctx.currentTime;this.master.gain.cancelScheduledValues(t),this.master.gain.setTargetAtTime(e?0:.62,t,.9)}setIntensity(e,t=0){if(!this.ready)return;const n=this.ctx.currentTime,i=.32+e*.5,s=.08+e*.34,o=Math.max(0,e-.35)*.5,a=1-t*.82;this.waveGain.gain.setTargetAtTime(i*a,n,1.4),this.windGain.gain.setTargetAtTime(s*a,n,1.4),this.rumbleGain.gain.setTargetAtTime(o*a,n,1.6),this.waveFilter.frequency.setTargetAtTime(320+e*420,n,1.8),this.windFilter.frequency.setTargetAtTime(700+e*900,n,1.8)}}function my(r=document){const e=r.querySelectorAll("[data-line]");return e.forEach(t=>{const n=t.textContent;t.textContent="";const i=document.createElement("span");i.className="line-mask";const s=document.createElement("span");s.className="line-inner",s.textContent=n,i.appendChild(s),t.appendChild(i)}),Array.from(e).map(t=>t.querySelector(".line-inner"))}kr.registerPlugin(Ze);function _y(r,e,t,n){e&&(r.fromTo(e,{yPercent:62,filter:"blur(14px)",opacity:0},{yPercent:0,filter:"blur(0px)",opacity:1,ease:"power2.out",duration:n},t),r.to(e,{yPercent:-30,filter:"blur(6px)",opacity:0,ease:"power1.in",duration:n*.7},t+n+n*.55))}function gy(r,e,t,n){e&&(r.fromTo(e,{opacity:0},{opacity:1,ease:"none",duration:n},t),r.to(e,{opacity:0,ease:"none",duration:n*.6},t+n+n*.55))}function fs(r,e,t,n,i=1.2){e&&(r.to(e,{opacity:1,duration:i,ease:"power1.inOut"},t),r.to(e,{opacity:0,duration:i,ease:"power1.inOut"},n))}function vy(r){const{motionOK:e}=r,t=!!r.oceanState,n=kr.timeline({scrollTrigger:{trigger:"#scroll-space",start:"top top",end:"bottom bottom",scrub:e?1:!0},defaults:{ease:"none"}}),i=e?_y:gy;return n.to(r.veil,{opacity:0,ease:"power1.in",duration:7},2),t&&n.to(r.oceanState,{fog:.55,moonIntensity:.16,stars:.22,storm:.06,camDriftAmp:.25,duration:8},0),t&&n.to(r.oceanState,{fog:.3,moonIntensity:.5,stars:.55,storm:.14,camHeight:2,camDist:9.3,camDriftAmp:1,duration:8},8),fs(n,r.verses[1],9,19),i(n,r.lines[1][0],10.2,2.3),i(n,r.lines[1][1],13.4,2.3),t&&n.to(r.oceanState,{fog:.28,moonIntensity:.52,duration:10},20),e&&(n.set(r.frame,{width:"0vw",height:"0vh",borderRadius:10},20),n.to(r.frame,{width:"34vw",height:"21vh",duration:7,ease:"power2.out"},22),n.to(r.frame,{borderColor:"rgba(205,217,226,0.30)",duration:6},22),n.to(r.frame,{"--inset-a":.05,"--edge-glow":.16,"--outside-a":.82,"--frame-blur":.6,duration:6},22),n.to([r.frameGlare,r.frameScan],{opacity:.55,duration:5},23),n.to(r.frameEdges,{opacity:.4,duration:5},24)),fs(n,r.verses[2],23,33),i(n,r.lines[2][0],24.2,2.2),i(n,r.lines[2][1],27.2,2.2),t&&n.to(r.oceanState,{storm:.32,duration:12},34),e&&(n.to(r.frame,{width:"37vw",height:"23vh",duration:6},36),n.to(r.domState,{tiltAmp:1,duration:3},35),n.to(r.domState,{tiltAmp:0,duration:3},46)),fs(n,r.verses[3],35.5,49),i(n,r.lines[3][0],36.6,2),i(n,r.lines[3][1],39.4,2),i(n,r.lines[3][2],42.2,2),i(n,r.lines[3][3],45,2),t&&n.to(r.oceanState,{storm:.03,camDriftAmp:0,fog:.24,stars:.42,duration:6},50),fs(n,r.verses[4],52,65),i(n,r.lines[4][0],53.2,2.4),i(n,r.lines[4][1],60,1.9),i(n,r.lines[4][2],62.2,1.9),i(n,r.lines[4][3],64,1.6),t&&n.to(r.oceanState,{fog:.2,moonIntensity:.6,storm:.12,duration:10},66),e&&(n.set(r.frame,{className:"+=has-warp"},67.5),n.to(r.frameWarpDisp,{attr:{scale:26},duration:4,ease:"sine.inOut"},69),n.to(r.frameWarpDisp,{attr:{scale:0},duration:3,ease:"power2.out"},76),n.set(r.frame,{className:"-=has-warp"},80),n.to(r.frame,{width:"100vw",height:"100vh",borderRadius:0,duration:9,ease:"power3.inOut"},70),n.to(r.frame,{"--inset-a":0,"--edge-glow":0,"--outside-a":0,duration:8},71),n.to([r.frameGlare,r.frameScan],{opacity:0,duration:5},72),n.to(r.frameEdges,{opacity:.7,duration:3},70),n.to(r.frameEdges,{opacity:0,duration:4},76)),fs(n,r.verses[5],67.5,79.5),i(n,r.lines[5][0],68.6,2.1),i(n,r.lines[5][1],71.2,2.1),i(n,r.lines[5][2],73.8,2.1),i(n,r.lines[5][3],76.4,1.9),e&&n.to(r.frame,{borderColor:"rgba(205,217,226,0)","--frame-blur":0,duration:2},80),t&&n.to(r.oceanState,{storm:.55,fog:.16,moonIntensity:.7,stars:.5,duration:6},81),fs(n,r.verses[6],81.5,90.5,1.8),i(n,r.lines[6][0],82.6,2.1),i(n,r.lines[6][1],85,2.1),i(n,r.lines[6][2],87.4,2.1),i(n,r.lines[6][3],89.6,2),t&&(n.to(r.oceanState,{breakProgress:1,nearFoam:.6,camDriftAmp:0,duration:6,ease:"power2.in"},88.5),n.to(r.oceanState,{storm:.02,moonIntensity:.95,duration:1.4,ease:"power2.in"},90.6),n.to(r.oceanState,{storm:.14,fog:.12,moonIntensity:.62,nearFoam:0,camDriftAmp:.5,duration:4},93),n.to(r.oceanState,{intimacy:1,duration:2},90.4),n.to(r.oceanState,{intimacy:.55,duration:4},93)),n.to(r.breakFlash,{opacity:.85,duration:.9,ease:"power2.in"},91),n.to(r.breakFlash,{opacity:0,duration:2.6,ease:"power2.out"},91.9),n.to(r.finalWord,{opacity:1,duration:4,ease:"power1.out"},95),n}kr.registerPlugin(Ze);const xy=window.matchMedia("(prefers-reduced-motion: reduce)").matches;function Sy(){const r=matchMedia("(pointer: coarse)").matches,e=navigator.hardwareConcurrency||4,t=window.innerWidth<760;return r&&(t||e<=4)?"low":r||e<=6?"mid":"high"}function My(){try{const r=document.createElement("canvas");return!!(window.WebGLRenderingContext&&(r.getContext("webgl2")||r.getContext("webgl")))}catch{return!1}}const yy=Sy(),zo=!xy,Ey=My(),Ty=zo&&Ey,Kt={app:document.getElementById("app"),canvas:document.getElementById("ocean-canvas"),veil:document.getElementById("scene0-veil"),frame:document.getElementById("frame"),frameGlare:document.querySelector(".frame-glare"),frameScan:document.querySelector(".frame-scan"),frameEdges:Array.from(document.querySelectorAll(".frame-edge")),frameWarpDisp:document.getElementById("frame-warp-disp"),finalWord:document.getElementById("final-word"),scrollHint:document.getElementById("scroll-hint"),soundToggle:document.getElementById("sound-toggle"),breakFlash:document.getElementById("break-flash"),poem:document.getElementById("poem")},Jp={};document.querySelectorAll(".verse").forEach(r=>{Jp[r.dataset.scene]=r});my(document);const Qp={};document.querySelectorAll(".verse").forEach(r=>{Qp[r.dataset.scene]=Array.from(r.querySelectorAll(".line-inner"))});let vn=null;if(Ty)try{vn=new dy(Kt.canvas,{quality:yy,reducedMotion:!1}),vn.setSize(window.innerWidth,window.innerHeight)}catch{vn=null}vn||Kt.app.classList.add("no-webgl");zo||document.body.classList.add("reduced-motion");const em={tiltAmp:0},by={motionOK:zo,oceanState:vn?vn.state:null,domState:em,veil:Kt.veil,frame:Kt.frame,frameGlare:Kt.frameGlare,frameScan:Kt.frameScan,frameEdges:Kt.frameEdges,frameWarpDisp:Kt.frameWarpDisp,verses:Jp,lines:Qp,finalWord:Kt.finalWord,breakFlash:Kt.breakFlash};vy(by);let sc=null;zo&&(sc=new j_({duration:1.15,smoothWheel:!0,smoothTouch:!1,touchMultiplier:1.4}),sc.on("scroll",Ze.update),kr.ticker.add(r=>sc.raf(r*1e3)),kr.ticker.lagSmoothing(0));const za=new py;let ms=!1;Kt.soundToggle.addEventListener("click",async()=>{ms=!ms,Kt.soundToggle.setAttribute("aria-pressed",String(ms)),Kt.soundToggle.setAttribute("aria-label",ms?"Выключить звук":"Включить звук"),ms?(await za.unlock(),za.setMuted(!1)):za.setMuted(!0)});let Eu=!1;const wy=setTimeout(()=>{Eu||(Kt.scrollHint.style.opacity="1",Kt.soundToggle.classList.add("is-visible"))},3200);function Cs(){Eu||(Eu=!0,clearTimeout(wy),kr.to(Kt.scrollHint,{opacity:0,duration:.8,ease:"power1.out"}),Kt.soundToggle.classList.add("is-visible"),window.removeEventListener("wheel",Cs),window.removeEventListener("touchmove",Cs),window.removeEventListener("scroll",Cs))}window.addEventListener("wheel",Cs,{passive:!0});window.addEventListener("touchmove",Cs,{passive:!0});window.addEventListener("scroll",Cs,{passive:!0});let Tu=0,bu=0,oc=0,ac=0;function Ay(r,e){Tu=r/window.innerWidth*2-1,bu=e/window.innerHeight*2-1,vn&&vn.setMouse(Tu,-bu)}window.addEventListener("pointermove",r=>Ay(r.clientX,r.clientY),{passive:!0});function Ry(r,e){if(!vn)return;const t=r/window.innerWidth*2-1,n=e/window.innerHeight*2-1;vn.addRipple(t,-n)}window.addEventListener("pointerdown",r=>Ry(r.clientX,r.clientY));let lc=0,cc=0;function Cy(r){if(!zo)return;lc+=r;const e=em.tiltAmp;cc=e<.001?0:(Math.sin(lc*.6)*1+Math.sin(lc*1.35+1.1)*.4)*e,document.documentElement.style.setProperty("--tilt",`${cc.toFixed(3)}deg`),oc=nl(oc,Tu*-.8,3,r),ac=nl(ac,-bu*-.6,3,r),Kt.poem.style.transform=`rotate(${cc.toFixed(3)}deg) translate(${oc.toFixed(3)}%, ${ac.toFixed(3)}%)`}function Py(){vn&&vn.setSize(window.innerWidth,window.innerHeight),Ze.refresh()}let Xf;window.addEventListener("resize",()=>{clearTimeout(Xf),Xf=setTimeout(Py,200)});let Yf=performance.now();function tm(r){const e=Math.min((r-Yf)/1e3,.05);if(Yf=r,Cy(e),vn&&(vn.update(e),ms)){const t=vn.state;za.setIntensity(t.storm,t.intimacy||0)}requestAnimationFrame(tm)}requestAnimationFrame(tm);setTimeout(()=>{document.body.classList.remove("is-loading")},260);
