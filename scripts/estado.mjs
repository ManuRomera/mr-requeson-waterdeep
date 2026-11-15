export const ID = "mr-requeson-waterdeep";

const BASE = {
  frentes: { rastro: 0, sindicato: 0, tyson: 0, acreedores: 0 },
  congelados: {}, presion: 0, escena: null, villaSalida: false,
  culpa: {}, resaca: { escenas: {}, actores: {} }, pizarra: [], parmesano: null
};

export function estado() {
  return foundry.utils.mergeObject(foundry.utils.deepClone(BASE), game.settings.get(ID, "estado") ?? {}, { inplace: false });
}

/** Solo el GM escribe. Aplica fn a una copia y guarda. */
export async function guardar(fn) {
  const e = estado();
  fn(e);
  await game.settings.set(ID, "estado", e);
  return e;
}

export const chatGM = (content) => ChatMessage.create({ content, whisper: ChatMessage.getWhisperRecipients("GM").map(u => u.id) });
export const chatPublico = (content) => ChatMessage.create({ content });
export const esc = (s) => foundry.utils.escapeHTML(String(s ?? ""));

// ---- Peticiones de jugadores al GM (los ajustes de mundo solo los escribe el GM)
const ACC = {};
export const registrarAccion = (nombre, fn) => { ACC[nombre] = fn; };
// Las acciones se ejecutan de una en una: dos peticiones simultáneas leerían el mismo estado y una pisaría a la otra.
let cola = Promise.resolve();
const enSerie = (fn) => { const p = cola.then(fn); cola = p.catch((e) => console.error(ID, e)); return p; };
export function pedir(nombre, datos = {}) {
  if (game.user.isGM) return enSerie(() => ACC[nombre]?.(datos, game.user.id));
  game.socket.emit(`module.${ID}`, { nombre, datos, de: game.user.id });
}
export function iniciarSocket(alEfecto) {
  game.socket.on(`module.${ID}`, (m) => {
    if (m.efecto) return alEfecto?.(m.efecto, m.visual);
    if (!game.user.isActiveGM) return;
    enSerie(() => ACC[m.nombre]?.(m.datos, m.de));
  });
}

// ---- Inventario de Mausritter: huecos de patas y cuerpo (mismo sistema de coordenadas que la hoja)
const HUECOS = [[-270, -20], [-270, -150], [-140, -20], [-140, -150]];
function ocupadas(actor) {
  const s = new Set();
  for (const i of actor.items) {
    const x = i.system.sheet?.currentX ?? 0, y = i.system.sheet?.currentY ?? 0;
    const w = i.system.size?.width ?? 1, h = i.system.size?.height ?? 1;
    for (let dx = 0; dx < w; dx++) for (let dy = 0; dy < h; dy++) s.add(`${x + 130 * dx},${y + 130 * dy}`);
  }
  return s;
}
export function huecoLibre(actor) {
  const o = ocupadas(actor);
  return HUECOS.find(([x, y]) => !o.has(`${x},${y}`)) ?? null;
}

/** Añade una condición (RESACA, ARDIDO...) a un actor, en un hueco libre de pata o cuerpo. */
export async function darCondicion(actor, nombre) {
  const base = game.items.find(i => i.type === "condition" && i.name === nombre);
  if (!base) { ui.notifications.warn(`Falta el objeto de condición ${nombre}. Ejecuta Configuración Inicial.`); return null; }
  const hueco = huecoLibre(actor);
  const datos = base.toObject();
  delete datos._id;
  if (hueco) { datos.system.sheet.currentX = hueco[0]; datos.system.sheet.currentY = hueco[1]; datos.system.sheet.initialX = hueco[0]; datos.system.sheet.initialY = hueco[1]; }
  const [creada] = await actor.createEmbeddedDocuments("Item", [datos]);
  if (!hueco) chatGM(`<p><strong>${esc(actor.name)}</strong> no tiene hueco libre en patas ni cuerpo para ${esc(nombre)}: queda sobrecargado. Colócala tú.</p>`);
  return creada;
}

export const personajes = () => game.actors.filter(a => a.getFlag(ID, "tipo") === "pj");
