import { ID, estado, guardar, chatGM, chatPublico, esc, registrarAccion, darCondicion, personajes } from "./estado.mjs";
import { FRENTES, PRESENTES, PRESION, EPILOGOS } from "./frentes-datos.mjs";

const frente = (id) => FRENTES.find(f => f.id === id);
const tarjetaPaso = (f, n) => `<div class="mrreq-chat"><h3>${esc(f.nombre)} · paso ${n}: ${esc(f.pasos[n - 1][0])}</h3><p>${esc(f.pasos[n - 1][1])}</p></div>`;

// ---------- Frentes
export async function moverFrente(id, nuevo) {
  const f = frente(id);
  const antes = estado().frentes[id];
  nuevo = Math.max(0, Math.min(4, nuevo));
  await guardar(e => { e.frentes[id] = nuevo; });
  if (nuevo > antes) for (let n = antes + 1; n <= nuevo; n++) chatGM(tarjetaPaso(f, n));
}
export const alternarCongelado = (id) => guardar(e => { e.congelados[id] = !e.congelados[id]; });
registrarAccion("frente", ({ id, paso }) => moverFrente(id, paso));
registrarAccion("congelar", ({ id }) => alternarCongelado(id));

/** Regla motor: avanzan los frentes que no están en la escena que se deja. */
export async function aplicarMotor(codigoSale, extraPresente = null) {
  const e0 = estado();
  const gratis = codigoSale === "01" && !e0.villaSalida;
  const log = [];
  if (!gratis && codigoSale !== null && codigoSale !== "09") {
    const presentes = new Set([...(PRESENTES[codigoSale] ?? []), ...(extraPresente ? [extraPresente] : [])]);
    for (const f of FRENTES) {
      const s = estado();
      if (presentes.has(f.id) || s.congelados[f.id] || s.frentes[f.id] >= 4) continue;
      await moverFrente(f.id, s.frentes[f.id] + 1);
      log.push(f.nombre);
    }
  }
  if (codigoSale === "01") await guardar(e => { e.villaSalida = true; });
  return { gratis, log };
}

export async function avanzarAEscena(scene) {
  const nuevo = scene.getFlag(ID, "escena");
  const sale = estado().escena;
  const { gratis, log } = await aplicarMotor(sale);
  await guardar(e => { e.escena = nuevo; });
  await scene.activate();
  const txt = sale === null ? "Primera escena." : gratis ? "La apertura es gratis: ningún frente avanza." : log.length ? `Avanzan: ${log.map(esc).join(", ")}.` : "Ningún frente avanza.";
  chatGM(`<div class="mrreq-chat"><h3>${esc(scene.name)}</h3><p>${txt}</p></div>`);
}

// ---------- Presión de Princesa
export async function moverPresion(delta) {
  const n0 = estado().presion;
  const n = delta > 0 ? Math.min(4, Math.max(1, n0 + delta)) : (n0 === 0 ? 0 : Math.max(1, n0 + delta));
  await guardar(x => { x.presion = n; });
  chatGM(`<div class="mrreq-chat ${n === 4 ? "mrreq-alerta" : ""}"><h3>Presión de Princesa: ${n}/4</h3><p>${esc(PRESION[n])}</p></div>`);
  if (n === 4 && delta > 0) chatPublico(`<div class="mrreq-chat mrreq-alerta"><p><em>Un chirrido metálico. Un chorro de agua. La grifería ya no está en la pared.</em></p></div>`);
}
registrarAccion("presion", ({ delta }) => moverPresion(delta));

// ---------- Culpa
export const culpaDe = (id) => estado().culpa[id] ?? 0;
export async function cambiarCulpa(id, delta) {
  await guardar(e => { e.culpa[id] = Math.max(0, Math.min(3, (e.culpa[id] ?? 0) + delta)); });
}
registrarAccion("culpa", ({ id, delta }) => cambiarCulpa(id, delta));
registrarAccion("confesion", async ({ id }) => {
  const a = game.actors.get(id); if (!a) return;
  const e = estado();
  if (e.resaca.confesiones?.[id]) return chatGM(`<p>${esc(a.name)} ya ha confesado.</p>`);
  await guardar(x => { x.resaca.confesiones ??= {}; x.resaca.confesiones[id] = true; });
  await cambiarCulpa(id, 1);
  chatPublico(`<div class="mrreq-chat"><h3>${esc(a.name)} confiesa</h3><p>Lee en voz alta «Lo que temes haber hecho». El grupo elige: <strong>una relanzada</strong> (repetir una tirada fallada, una vez) o <strong>quitar una condición</strong> a quien quiera. Culpa de ${esc(a.name)}: ${culpaDe(id)}/3.</p></div>`);
});
export const epilogo = (n) => EPILOGOS[n];

// ---------- Resaca narrativa
registrarAccion("resaca", async ({ id, texto, pago, valor }, userId) => {
  const a = game.actors.get(id); if (!a) return;
  const e = estado(); const esc_ = e.escena ?? "-";
  const enEscena = e.resaca.escenas[esc_] ?? 0, delActor = e.resaca.actores[id] ?? 0;
  const rechazo = enEscena >= 1 ? "Ya hay una declaración en esta escena." : delActor >= 2 ? `${a.name} ya ha declarado dos veces.` : null;
  if (rechazo) return ChatMessage.create({ content: `<p>${esc(rechazo)}</p>`, whisper: [userId] });
  await guardar(x => { x.resaca.escenas[esc_] = enEscena + 1; x.resaca.actores[id] = delActor + 1; });
  let precio = "";
  if (pago === "frente") { const f = frente(valor); await moverFrente(valor, estado().frentes[valor] + 1); precio = `avanza el frente ${f.nombre}`; }
  else if (pago === "condicion") { await darCondicion(a, valor); precio = `acepta ${valor}`; }
  else { await cambiarCulpa(id, 1); precio = `marca Culpa (${culpaDe(id)}/3)`; }
  chatPublico(`<div class="mrreq-chat"><h3>${esc(a.name)} recuerda algo de anoche</h3><p><em>${esc(texto)}</em></p><p>Es cierto. Precio: ${esc(precio)}.</p></div>`);
});

// ---------- El Parmesano Ruso (quesos restantes q y picantes restantes p)
const nuevaPartida = () => ({ q: 6, p: 2, cortesia: true, preguntas: {}, log: [], bruno: false });
export const parmesanoNuevo = () => guardar(e => { e.parmesano = nuevaPartida(); });
function quema(q, p, r) { return (p === 2 && (r === 1 || r === q)) || (p === 1 && r === 1); }
export async function turnoParmesano(actorId) {
  const e = estado(); const m = e.parmesano; if (!m || m.q <= 0) return;
  const a = game.actors.get(actorId); if (!a) return;
  let r = (await new Roll(`1d${m.q}`).evaluate()).total, nota = "";
  const quemaria = m.p === m.q ? true : quema(m.q, m.p, r);
  if (quemaria && m.cortesia) { r = (await new Roll(`1d${m.q}`).evaluate()).total; nota = " (cortesía de la casa: repite)"; }
  const q2 = m.p === m.q ? true : quema(m.q, m.p, r);
  await guardar(x => {
    const y = x.parmesano; y.cortesia = false; y.q -= 1;
    if (q2) y.p -= 1; else y.preguntas[actorId] = (y.preguntas[actorId] ?? 0) + 1;
    y.log.push(`${a.name}: d${m.q}=${r}${nota} ${q2 ? "QUEMA" : "queso bueno"}`);
  });
  chatGM(`<p><strong>${esc(a.name)}</strong> tira d${m.q}: ${r}${nota}. ${q2 ? "Queso con guindilla." : "Queso bueno: una pregunta."}</p>`);
  if (q2) { chatPublico(`<div class="mrreq-chat mrreq-alerta"><p>${esc(a.name)} se traga el cubo y los ojos se le llenan de lágrimas. Queda <strong>ARDIDO</strong>.</p></div>`); await darCondicion(a, "ARDIDO"); }
  else chatPublico(`<div class="mrreq-chat"><p>${esc(a.name)} se traga el cubo sin pestañear. Bruno asiente: tiene derecho a una pregunta.</p></div>`);
}
export async function turnoBruno(forzar) {
  const m = estado().parmesano; if (!m || m.q <= 0) return;
  if (!forzar && m.q === m.p) {
    await guardar(x => { x.parmesano.bruno = true; });
    return chatPublico(`<div class="mrreq-chat"><p>Bruno se levanta, se limpia las manos con un pañuelo y dice que ya está bien. «Basta. Sois gente seria. Preguntad lo que queráis.» Lo cuenta todo.</p></div>`);
  }
  if (!forzar) {
    await guardar(x => { x.parmesano.q -= 1; x.parmesano.log.push("Bruno: elige un queso bueno"); });
    return chatPublico(`<div class="mrreq-chat"><p>Bruno coge un cubo con la pata, sin mirar, mientras habla de otra cosa, y se lo come sin inmutarse.</p></div>`);
  }
  const r = (await new Roll(`1d${m.q}`).evaluate()).total, q2 = m.p === m.q ? true : quema(m.q, m.p, r);
  await guardar(x => { x.parmesano.q -= 1; if (q2) x.parmesano.p -= 1; x.parmesano.log.push(`Bruno a ciegas: d${m.q}=${r} ${q2 ? "QUEMA" : "bueno"}`); });
  chatPublico(`<div class="mrreq-chat ${q2 ? "mrreq-alerta" : ""}"><p>Bruno come a ciegas y tira d${m.q}: ${r}. ${q2 ? "¡Guindilla! Se va debajo de su propia mesa, llorando, con los dos cobradores mirando al techo." : "Queso bueno. Suspira."}</p></div>`);
}
registrarAccion("parmesano-nuevo", parmesanoNuevo);
registrarAccion("parmesano-turno", ({ id }) => turnoParmesano(id));
registrarAccion("parmesano-bruno", ({ forzar }) => turnoBruno(forzar));

// ---------- Pizarra
registrarAccion("pizarra-add", ({ t, col }) => guardar(e => { e.pizarra.push({ id: foundry.utils.randomID(), t, col, vis: true }); }));
registrarAccion("pizarra-vis", ({ id }) => guardar(e => { const p = e.pizarra.find(x => x.id === id); if (p) p.vis = !p.vis; }));
registrarAccion("pizarra-col", ({ id }) => guardar(e => { const p = e.pizarra.find(x => x.id === id); if (p) p.col = p.col === "sabemos" ? "falta" : "sabemos"; }));
registrarAccion("pizarra-del", ({ id }) => guardar(e => { e.pizarra = e.pizarra.filter(x => x.id !== id); }));
