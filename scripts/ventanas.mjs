import { ID, estado, esc, pedir, personajes } from "./estado.mjs";
import { FRENTES, PRESENTES, PRESION, EPILOGOS, CONDICIONES_RESACA } from "./frentes-datos.mjs";
import { culpaDe } from "./reglas.mjs";

const { ApplicationV2 } = foundry.applications.api;

class Ventana extends ApplicationV2 {
  static DEFAULT_OPTIONS = { classes: ["mrreq"], window: { resizable: true }, position: { width: 520, height: "auto" } };
  constructor(opciones = {}) {
    // Memoria de ventana: se reabre donde se dejó
    const id = (new.target.DEFAULT_OPTIONS.id);
    let guardada = {};
    try { guardada = game.settings.get(ID, "ventanas")?.[id] ?? {}; } catch (e) { /* sin memoria */ }
    super(foundry.utils.mergeObject({ position: guardada }, opciones));
    this._h = () => this.render();
    Hooks.on("mrreq.estado", this._h);
  }
  _onPosition(pos) {
    super._onPosition?.(pos);
    clearTimeout(this._tpos);
    this._tpos = setTimeout(() => {
      const todas = foundry.utils.deepClone(game.settings.get(ID, "ventanas") ?? {});
      todas[this.id] = { left: this.position.left, top: this.position.top, width: this.position.width, height: this.position.height };
      game.settings.set(ID, "ventanas", todas);
    }, 400);
  }
  async _renderHTML() { return this.html(); }
  _replaceHTML(res, content) {
    content.innerHTML = res;
    // Accesibilidad: tamaño de texto y contraste según los ajustes de cliente
    this.element.classList.toggle("mrreq-grande", game.settings.get(ID, "textoGrande"));
    this.element.classList.toggle("mrreq-contraste", game.settings.get(ID, "altoContraste"));
    content.setAttribute("role", "region"); content.setAttribute("aria-label", this.options.window?.title ?? "");
    content.onclick = (ev) => { const b = ev.target.closest("[data-a]"); if (b) this.accion(b.dataset.a, b, content); };
  }
  _onClose(o) { Hooks.off("mrreq.estado", this._h); return super._onClose?.(o); }
  static abrir() {
    this._inst = this._inst?.rendered ? this._inst : new this();
    this._inst.render({ force: true });
    return this._inst;
  }
}

// ---------- Panel de Frentes (GM)
export class PanelFrentes extends Ventana {
  static DEFAULT_OPTIONS = { ...Ventana.DEFAULT_OPTIONS, id: "mrreq-frentes", window: { title: "Panel de Frentes", resizable: true }, position: { width: 560, height: "auto" } };
  html() {
    const e = estado(), esc_ = e.escena;
    const filas = FRENTES.map(f => {
      const n = e.frentes[f.id];
      const cajas = [1, 2, 3, 4].map(i => `<button type="button" class="paso ${i <= n ? "on" : ""}" data-a="paso" data-f="${f.id}" data-n="${i === n ? i - 1 : i}" aria-pressed="${i <= n}" aria-label="${esc(f.nombre)}, paso ${i}: ${esc(f.pasos[i - 1][0])}" title="${esc(f.pasos[i - 1][0])}: ${esc(f.pasos[i - 1][1])}">${i}</button>`).join("");
      return `<div class="fila ${e.congelados[f.id] ? "frio" : ""}"><div class="nom"><strong>${esc(f.nombre)}</strong><small>${esc(f.quiere)}</small></div>
        <div class="pasos">${cajas}</div><div class="etq">${n ? esc(f.pasos[n - 1][0]) : "—"}</div>
        <button type="button" data-a="congelar" data-f="${f.id}" aria-pressed="${!!e.congelados[f.id]}" aria-label="Congelar o descongelar ${esc(f.nombre)}" title="Congelar o descongelar el frente"><i class="fa-solid fa-snowflake"></i></button></div>`;
    }).join("");
    const opts = FRENTES.map(f => `<option value="${f.id}">${esc(f.nombre)}</option>`).join("");
    return `<div class="mrreq-panel"><p class="sub">Escena actual: <strong>${esc(esc_ ? (game.scenes.find(s => s.getFlag(ID, "escena") === esc_)?.name ?? esc_) : "ninguna")}</strong></p>${filas}
      <div class="barra"><label>Todos menos <select name="menos">${opts}</select></label><button type="button" data-a="todos"><i class="fa-solid fa-forward-step"></i> Avanzar</button></div></div>`;
  }
  accion(a, b, c) {
    if (a === "paso") pedir("frente", { id: b.dataset.f, paso: Number(b.dataset.n) });
    if (a === "congelar") pedir("congelar", { id: b.dataset.f });
    if (a === "todos") {
      const menos = c.querySelector("[name=menos]").value, e = estado();
      for (const f of FRENTES) if (f.id !== menos && !e.congelados[f.id] && e.frentes[f.id] < 4) pedir("frente", { id: f.id, paso: e.frentes[f.id] + 1 });
    }
  }
}

// ---------- Pizarra de Investigación (todos; el GM edita)
export class Pizarra extends Ventana {
  static DEFAULT_OPTIONS = { ...Ventana.DEFAULT_OPTIONS, id: "mrreq-pizarra", window: { title: "Pizarra de Investigación", resizable: true }, position: { width: 640, height: 420 } };
  html() {
    const gm = game.user.isGM, p = estado().pizarra.filter(x => gm || x.vis);
    const col = (c, tit) => `<div class="col"><h3>${tit}</h3>${p.filter(x => x.col === c).map(x => `<div class="nota ${x.vis ? "" : "oculta"}">
      <span>${esc(x.t)}</span>${gm ? `<span class="ctl"><button type="button" data-a="vis" data-id="${x.id}" aria-label="Visible para jugadores" title="Visible para jugadores"><i class="fa-solid ${x.vis ? "fa-eye" : "fa-eye-slash"}"></i></button>
      <button type="button" data-a="col" data-id="${x.id}" aria-label="Pasar a la otra columna" title="Pasar a la otra columna"><i class="fa-solid fa-right-left"></i></button>
      <button type="button" data-a="del" data-id="${x.id}" aria-label="Borrar nota" title="Borrar"><i class="fa-solid fa-trash"></i></button></span>` : ""}</div>`).join("") || "<p class='vacio'>Nada todavía.</p>"}</div>`;
    const alta = gm ? `<div class="barra"><input type="text" name="t" aria-label="Pista o pregunta" placeholder="Pista o pregunta"><select name="c"><option value="sabemos">Lo que sabemos</option><option value="falta">Lo que falta</option></select><button type="button" data-a="add" aria-label="Añadir nota"><i class="fa-solid fa-plus" aria-hidden="true"></i></button></div>` : "";
    return `<div class="mrreq-panel pizarra"><div class="cols">${col("sabemos", "Lo que sabemos")}${col("falta", "Lo que hay que averiguar")}</div>${alta}</div>`;
  }
  accion(a, b, c) {
    if (a === "add") { const t = c.querySelector("[name=t]").value.trim(); if (t) pedir("pizarra-add", { t, col: c.querySelector("[name=c]").value }); }
    if (a === "vis") pedir("pizarra-vis", { id: b.dataset.id });
    if (a === "col") pedir("pizarra-col", { id: b.dataset.id });
    if (a === "del") pedir("pizarra-del", { id: b.dataset.id });
  }
}

// ---------- Presión de Princesa (GM)
export class PanelPresion extends Ventana {
  static DEFAULT_OPTIONS = { ...Ventana.DEFAULT_OPTIONS, id: "mrreq-presion", window: { title: "Presión de Princesa", resizable: false }, position: { width: 420, height: "auto" } };
  html() {
    const n = estado().presion;
    return `<div class="mrreq-panel"><div class="pasos grande" role="img" aria-label="Presión de Princesa: ${n} de 4">${[1, 2, 3, 4].map(i => `<span class="paso ${i <= n ? "on" : ""} ${i === 4 ? "rojo" : ""}" aria-hidden="true">${i}</span>`).join("")}</div>
      <p class="sub" aria-live="polite">${esc(PRESION[n])}</p>
      <div class="barra"><button type="button" data-a="menos"><i class="fa-solid fa-minus"></i> Baja</button><button type="button" data-a="mas"><i class="fa-solid fa-plus"></i> Sube</button></div>
      <p class="nota-pie">Sube con ruido o con un intento precipitado. Baja con comida grasienta, una orden de Tyson, silencio o una dosis bien calculada. Mientras siga encerrada no baja de 1.</p></div>`;
  }
  accion(a) { pedir("presion", { delta: a === "mas" ? 1 : -1 }); }
}

// ---------- Contador de Culpa
export class ContadorCulpa extends Ventana {
  static DEFAULT_OPTIONS = { ...Ventana.DEFAULT_OPTIONS, id: "mrreq-culpa", window: { title: "Contador de Culpa", resizable: true }, position: { width: 560, height: "auto" } };
  html() {
    const gm = game.user.isGM, conf = estado().resaca.confesiones ?? {};
    const filas = personajes().map(a => {
      const n = culpaDe(a.id), puede = gm || a.isOwner;
      return `<div class="fila"><div class="nom"><strong>${esc(a.name)}</strong><small>${esc(EPILOGOS[n])}</small></div>
        <div class="pasos" role="img" aria-label="Culpa de ${esc(a.name)}: ${n} de 3">${[1, 2, 3].map(i => `<span class="paso ${i <= n ? "on rojo" : ""}" aria-hidden="true">${i}</span>`).join("")}</div>
        ${gm ? `<button type="button" data-a="mas" data-id="${a.id}" aria-label="Sumar Culpa a ${esc(a.name)}" title="Sumar Culpa"><i class="fa-solid fa-plus"></i></button><button type="button" data-a="menos" data-id="${a.id}" aria-label="Restar Culpa a ${esc(a.name)}" title="Restar Culpa (Deseo cumplido)"><i class="fa-solid fa-minus"></i></button>` : ""}
        ${puede ? `<button type="button" data-a="confesar" data-id="${a.id}" ${conf[a.id] ? "disabled" : ""}><i class="fa-solid fa-comment"></i> Confesar</button>` : ""}</div>`;
    }).join("") || "<p class='vacio'>No hay protagonistas en el mundo. Ejecuta Configuración Inicial.</p>";
    return `<div class="mrreq-panel">${filas}</div>`;
  }
  accion(a, b) {
    if (a === "mas") pedir("culpa", { id: b.dataset.id, delta: 1 });
    if (a === "menos") pedir("culpa", { id: b.dataset.id, delta: -1 });
    if (a === "confesar") pedir("confesion", { id: b.dataset.id });
  }
}

// ---------- El Parmesano Ruso (GM)
export class Parmesano extends Ventana {
  static DEFAULT_OPTIONS = { ...Ventana.DEFAULT_OPTIONS, id: "mrreq-parmesano", window: { title: "El Parmesano Ruso", resizable: true }, position: { width: 520, height: "auto" } };
  html() {
    const m = estado().parmesano;
    if (!m) return `<div class="mrreq-panel"><p>Seis quesos, dos con guindilla. El dado encoge y los extremos queman. Las tiradas son tuyas y en oculto.</p><div class="barra"><button type="button" data-a="nuevo"><i class="fa-solid fa-cheese"></i> Poner la bandeja</button></div></div>`;
    const pjs = personajes().map(a => `<option value="${a.id}">${esc(a.name)} (${m.preguntas[a.id] ?? 0} preguntas)</option>`).join("");
    const quesos = Array.from({ length: m.q }, () => `<span class="queso">▲</span>`).join("");
    return `<div class="mrreq-panel"><p class="sub">Quesos en la bandeja: <strong>${m.q}</strong>. Con guindilla: <strong class="gm">${m.p}</strong> (solo lo ves tú). Cortesía de la casa: ${m.cortesia ? "disponible" : "gastada"}.</p>
      <div class="quesos">${quesos || "Bandeja vacía."}</div>
      ${m.bruno ? `<p class="aviso">Bruno se ha retirado: lo cuenta todo.</p>` : ""}
      <div class="barra"><select name="pj">${pjs}</select><button type="button" data-a="turno" ${m.q ? "" : "disabled"}><i class="fa-solid fa-dice"></i> Come y tira</button></div>
      <div class="barra"><label><input type="checkbox" name="forzar"> Le obligan a comer a ciegas</label><button type="button" data-a="bruno" ${m.q ? "" : "disabled"}>Turno de Bruno</button><button type="button" data-a="nuevo">Reiniciar</button></div>
      <ul class="log">${m.log.map(l => `<li>${esc(l)}</li>`).join("")}</ul></div>`;
  }
  accion(a, b, c) {
    if (a === "nuevo") pedir("parmesano-nuevo");
    if (a === "turno") pedir("parmesano-turno", { id: c.querySelector("[name=pj]").value });
    if (a === "bruno") pedir("parmesano-bruno", { forzar: c.querySelector("[name=forzar]").checked });
  }
}
