!function(e){var t={};function o(n){if(t[n])return t[n].exports;var r=t[n]={i:n,l:!1,exports:{}};return e[n].call(r.exports,r,r.exports,o),r.l=!0,r.exports}o.m=e,o.c=t,o.d=function(e,t,n){o.o(e,t)||Object.defineProperty(e,t,{enumerable:!0,get:n})},o.r=function(e){"undefined"!=typeof Symbol&&Symbol.toStringTag&&Object.defineProperty(e,Symbol.toStringTag,{value:"Module"}),Object.defineProperty(e,"__esModule",{value:!0})},o.t=function(e,t){if(1&t&&(e=o(e)),8&t)return e;if(4&t&&"object"==typeof e&&e&&e.__esModule)return e;var n=Object.create(null);if(o.r(n),Object.defineProperty(n,"default",{enumerable:!0,value:e}),2&t&&"string"!=typeof e)for(var r in e)o.d(n,r,function(t){return e[t]}.bind(null,r));return n},o.n=function(e){var t=e&&e.__esModule?function(){return e.default}:function(){return e};return o.d(t,"a",t),t},o.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},o.p="",o(o.s=0)}([function(e,t,o){"use strict";o.r(t);const n=customElements.get("home-assistant-main")?Object.getPrototypeOf(customElements.get("home-assistant-main")):Object.getPrototypeOf(customElements.get("hui-view"));n.prototype.html,n.prototype.css;let r=function(){if(window.fully&&"function"==typeof fully.getDeviceId)return fully.getDeviceId();if(!localStorage["lovelace-player-device-id"]){const e=()=>Math.floor(1e5*(1+Math.random())).toString(16).substring(1);localStorage["lovelace-player-device-id"]=`${e()}${e()}-${e()}${e()}`}return localStorage["lovelace-player-device-id"]}();function s(e,t,o=null){if((e=new Event(e,{bubbles:!0,cancelable:!1,composed:!0})).detail=t||{},o)o.dispatchEvent(e);else{var n=document.querySelector("home-assistant");(n=(n=(n=(n=(n=(n=(n=(n=(n=(n=(n=n&&n.shadowRoot)&&n.querySelector("home-assistant-main"))&&n.shadowRoot)&&n.querySelector("app-drawer-layout partial-panel-resolver"))&&n.shadowRoot||n)&&n.querySelector("ha-panel-lovelace"))&&n.shadowRoot)&&n.querySelector("hui-root"))&&n.shadowRoot)&&n.querySelector("ha-app-layout #view"))&&n.firstElementChild)&&n.dispatchEvent(e)}}customElements.whenDefined("ha-markdown").then(()=>{const e=customElements.get("ha-markdown"),t=["svg","path","ha-icon"],o=e.prototype._render;e.prototype._render=function(){0===this._scriptLoaded||this._renderScheduled||(this.oldFilterXSS||(this.oldFilterXSS=this.filterXSS),this.filterXSS=function(e,o){return-1==e?1:this.oldFilterXSS(e,{onIgnoreTag:this.allowSvg?(e,o)=>t.indexOf(e)>=0?o:null:null})},o.bind(this)())},s("ll-rebuild",{})}),customElements.whenDefined("hui-markdown-card").then(()=>{const e=customElements.get("hui-markdown-card");e.prototype.updated=function(e){const t=this.shadowRoot.querySelector("ha-markdown");t&&(t.allowSvg=!0,this._hass&&async function(e,t,o={}){for(var n in e||(e=e()),o={},o=Object.assign({user:e.user.name,browser:r,hash:location.hash.substr(1)||" "},o)){var s=new RegExp(`\\{${n}\\}`,"g");t=t.replace(s,o[n])}return e.callApi("POST","template",{template:t})}(this._hass,this._config.content).then(e=>t.content=e))},e.prototype.firstUpdated=function(){window.addEventListener("location-changed",()=>this._requestUpdate())},Object.defineProperty(e.prototype,"hass",{get(){return this._hass},set(e){if(e!==this._hass){const t=this._hass;this._hass=e,this._requestUpdate("hass",t)}}}),s("ll-rebuild",{})})}]);
