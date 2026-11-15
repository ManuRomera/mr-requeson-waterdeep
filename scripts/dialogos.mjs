import { ID, estado, guardar, esc, pedir, chatGM, chatPublico, personajes } from "./estado.mjs";
import { FRENTES, CONDICIONES_RESACA } from "./frentes-datos.mjs";
import { avanzarAEscena } from "./reglas.mjs";

const { DialogV2 } = foundry.applications.api;
const datos = (b) => new foundry.applications.ux.FormDataExtended(b.form).object;
const opciones = (lista) => lista.map(([v, t]) => `<option value="${esc(v)}">${esc(t)}</option>`).join("");

// ---------- Avanzar a Escena
export async function avanzarEscena() {
  const escenas = game.scenes.filter(s => s.getFlag(ID, "escena")).sort((a, b) => a.getFlag(ID, "escena").localeCompare(b.getFlag(ID, "escena")));
  if (!escenas.length) return ui.notifications.warn("No hay escenas del módulo. Ejecuta Configuración Inicial.");
  const actual = estado().escena;
  const r = await DialogV2.prompt({
    window: { title: "Avanzar a Escena" },
    content: `<p>Al salir de la escena actual avanzan los frentes que no estaban en ella. La apertura es gratis.</p>
      <div class="form-group"><label>Escena</label><select name="id">${opciones(escenas.map(s => [s.id, `${s.getFlag(ID, "escena")} · ${s.name}${s.getFlag(ID, "escena") === actual ? " (actual)" : ""}`]))}</select></div>`,
    ok: { label: "Avanzar", icon: "fa-solid fa-forward", callback: (ev, b) => datos(b).id }, rejectClose: false
  });
  if (r) await avanzarAEscena(game.scenes.get(r));
}

// ---------- Mostrar Handout
export async function mostrarHandout() {
  const lista = [];
  for (const j of game.journal.filter(j => j.getFlag(ID, "tipo") === "Handouts")) {
    if (j.name.startsWith("Fotografías")) { for (const p of j.pages.filter(p => p.type === "image")) lista.push([p.uuid, `Foto · ${p.name}`]); }
    else lista.push([j.uuid, j.name]);
  }
  if (!lista.length) return ui.notifications.warn("No hay handouts. Ejecuta Configuración Inicial.");
  const uuid = await DialogV2.prompt({
    window: { title: "Mostrar Handout" },
    content: `<div class="form-group"><label>Handout</label><select name="u">${opciones(lista)}</select></div>`,
    ok: { label: "Mostrar a todos", icon: "fa-solid fa-eye", callback: (ev, b) => datos(b).u }, rejectClose: false
  });
  if (!uuid) return;
  const doc = await fromUuid(uuid);
  const pagImg = doc.documentName === "JournalEntryPage" ? doc : doc.pages.find(p => p.type === "image");
  const pagTxt = doc.documentName === "JournalEntry" ? doc.pages.find(p => p.type === "text") : null;
  if (pagImg?.src) {
    const ip = new foundry.applications.apps.ImagePopout({ src: pagImg.src, window: { title: pagImg.parent?.name ?? doc.name } });
    await ip.render({ force: true });
    ip.shareImage();
  }
  if (pagTxt) chatPublico(`<div class="mrreq-chat"><h3>${esc(doc.name)}</h3>${pagTxt.text.content}</div>`);
}

// ---------- Resaca Narrativa
export async function resacaNarrativa() {
  const mios = personajes().filter(a => game.user.isGM || a.isOwner);
  if (!mios.length) return ui.notifications.warn("No tienes ningún protagonista.");
  const r = await DialogV2.prompt({
    window: { title: "Resaca Narrativa" },
    content: `<p>Declara algo que hiciste anoche y que te sirve ahora. Es cierto. Una declaración por escena para toda la mesa y como máximo dos por jugador.</p>
      <div class="form-group"><label>Quién</label><select name="id">${opciones(mios.map(a => [a.id, a.name]))}</select></div>
      <div class="form-group"><label>Qué hiciste</label><textarea name="texto" rows="3" placeholder="Anoche le caí bien al portero de la Notaría."></textarea></div>
      <div class="form-group"><label>Lo pagas con</label><select name="pago"><option value="frente">Avanzar un frente</option><option value="condicion">Aceptar una condición</option><option value="culpa">Marcar Culpa</option></select></div>
      <div class="form-group"><label>Frente o condición</label><select name="valor">${opciones([...FRENTES.map(f => [f.id, `Frente: ${f.nombre}`]), ...CONDICIONES_RESACA.map(c => [c, `Condición: ${c}`])])}</select></div>`,
    ok: { label: "Declarar", icon: "fa-solid fa-comment-dots", callback: (ev, b) => datos(b) }, rejectClose: false
  });
  if (!r || !r.texto.trim()) return;
  if (r.pago === "frente" && !FRENTES.some(f => f.id === r.valor)) return ui.notifications.warn("Elige un frente.");
  if (r.pago === "condicion" && !CONDICIONES_RESACA.includes(r.valor)) return ui.notifications.warn("Elige una condición.");
  pedir("resaca", { id: r.id, texto: r.texto.trim(), pago: r.pago, valor: r.valor });
}

// ---------- Fichas Confidenciales (GM)
export async function fichasConfidenciales() {
  const fichas = game.journal.filter(j => j.getFlag(ID, "tipo") === "Fichas confidenciales");
  if (!fichas.length) return ui.notifications.warn("No hay fichas confidenciales. Ejecuta Configuración Inicial.");
  const usuarios = game.users.filter(u => !u.isGM);
  const filas = fichas.map(j => `<div class="form-group"><label>${esc(j.name.replace("Ficha confidencial · ", ""))}</label><select name="${j.id}"><option value="">Sin asignar</option>${opciones(usuarios.map(u => [u.id, u.name]))}</select></div>`).join("");
  const r = await DialogV2.prompt({
    window: { title: "Fichas Confidenciales" },
    content: `<p>Cada ficha se da en propiedad solo al jugador elegido y se le susurra el enlace. Vuelve a ejecutar la macro para reasignar: las demás se mantienen.</p>${filas}`,
    ok: { label: "Repartir", icon: "fa-solid fa-envelope", callback: (ev, b) => datos(b) }, rejectClose: false
  });
  if (!r) return;
  for (const j of fichas) {
    const uid = r[j.id]; if (!uid) continue;
    await j.update({ ownership: { default: 0, [uid]: 3 } });
    await ChatMessage.create({ content: `<p>Tu ficha confidencial: @UUID[${j.uuid}]{${esc(j.name)}}. Solo la ves tú.</p>`, whisper: [uid] });
  }
  ui.notifications.info("Fichas repartidas.");
}

// ---------- Tirada en Tabla
export async function tiradaEnTabla() {
  const tablas = game.tables.filter(t => t.folder?.name === "Tablas");
  if (!tablas.length) return ui.notifications.warn("No hay tablas del módulo. Ejecuta Configuración Inicial.");
  const id = await DialogV2.prompt({
    window: { title: "Tirada en Tabla" },
    content: `<div class="form-group"><label>Tabla</label><select name="t">${opciones(tablas.map(t => [t.id, `${t.name} (${t.formula})`]))}</select></div>`,
    ok: { label: "Tirar", icon: "fa-solid fa-dice", callback: (ev, b) => datos(b).t }, rejectClose: false
  });
  if (id) await game.tables.get(id).draw();
}

// ---------- Configuración Inicial (GM)
export async function configuracionInicial() {
  if (!game.user.isGM) return;
  const pack = game.packs.get(`${ID}.aventura`);
  if (!pack) return ui.notifications.error("No se encuentra el pack del módulo.");
  const hecho = game.scenes.some(s => s.getFlag(ID, "escena"));
  const ok = await DialogV2.confirm({
    window: { title: "Configuración Inicial" },
    content: `<p>Se importan al mundo las escenas, actores, objetos, diarios, tablas y macros de MR- Requesón en Waterdeep.${hecho ? " <strong>Ya hay contenido importado: se sobrescribirá.</strong>" : ""}</p>
      <p>Después se activa la portada. Las fichas confidenciales se reparten con la macro Fichas Confidenciales.</p>`,
    yes: { label: "Importar", icon: "fa-solid fa-download" }, rejectClose: false
  });
  if (!ok) return;
  const [adv] = await pack.getDocuments();
  if (!adv) return ui.notifications.error("El pack del módulo está vacío o no se pudo leer.");
  await adv.sheet.render({ force: true });
  ui.notifications.info("Pulsa «Importar» en la ventana de la aventura.");
  await game.settings.set(ID, "importada", true);
}

// ---------- Cambiar Ambiente (GM): cambia la música sin salir de la escena
export async function cambiarAmbiente() {
  if (!game.user.isGM) return;
  const lista = game.playlists.filter(p => p.sounds.contents.some(x => x.flags?.[ID]?.slug));
  const ambientes = lista.find(p => p.name.startsWith("Ambientes"))?.sounds.contents ?? [];
  if (!ambientes.length) return ui.notifications.warn("No hay ambientes. Ejecuta Configuración Inicial.");
  const escena = game.scenes.viewed?.playlistSound;
  const op = [["__escena", "Volver a la música de la escena"], ...ambientes.map(s => [s.id, s.name])];
  const id = await DialogV2.prompt({
    window: { title: "Cambiar Ambiente" },
    content: `<p>Cambia la música con un fundido y sin salir de la escena.</p><div class="form-group"><label>Ambiente</label><select name="a">${opciones(op)}</select></div>`,
    ok: { label: "Poner", icon: "fa-solid fa-music", callback: (ev, b) => datos(b).a }, rejectClose: false
  });
  if (!id) return;
  for (const p of lista) for (const s of p.sounds.contents) if (s.playing) await p.stopSound(s);
  const destino = id === "__escena" ? escena : ambientes.find(s => s.id === id);
  if (destino) await destino.parent.playSound(destino);
}
