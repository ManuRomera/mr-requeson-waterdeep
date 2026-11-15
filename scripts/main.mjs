import { verificarAssets, rutaConFallback } from "./verify-assets.mjs";
import { ID, iniciarSocket } from "./estado.mjs";
import { reproducir } from "./efectos.mjs";
import "./reglas.mjs";
import { PanelFrentes, Pizarra, PanelPresion, ContadorCulpa, Parmesano } from "./ventanas.mjs";
import { avanzarEscena, mostrarHandout, resacaNarrativa, fichasConfidenciales, tiradaEnTabla, configuracionInicial } from "./dialogos.mjs";

Hooks.once("init", () => {
  game.settings.register(ID, "verificarAlIniciar", {
    name: "MRREQ.Settings.Verificar.Name", hint: "MRREQ.Settings.Verificar.Hint",
    scope: "world", config: true, type: Boolean, default: false
  });
  const cli = (clave, tipo, def, extra = {}) => game.settings.register(ID, clave, { name: `MRREQ.Settings.${clave}.Name`, hint: `MRREQ.Settings.${clave}.Hint`, scope: "client", config: true, type: tipo, default: def, ...extra });
  cli("efectosSonido", Boolean, true);
  cli("volumenEfectos", Number, 0.8, { range: { min: 0, max: 1, step: 0.05 } });
  cli("efectosVisuales", Boolean, true);
  cli("textoGrande", Boolean, false);
  cli("altoContraste", Boolean, false);
  game.settings.register(ID, "estiloToken", { name: "MRREQ.Settings.estiloToken.Name", hint: "MRREQ.Settings.estiloToken.Hint", scope: "world", config: true, type: String, default: "cuerpo",
    choices: { cuerpo: "MRREQ.Settings.estiloToken.Cuerpo", redondo: "MRREQ.Settings.estiloToken.Redondo" } });
  game.settings.register(ID, "ventanas", { scope: "client", config: false, type: Object, default: {} });
  game.settings.register(ID, "estado", { scope: "world", config: false, type: Object, default: {}, onChange: () => Hooks.callAll("mrreq.estado") });
  game.settings.register(ID, "migracion", { scope: "world", config: false, type: String, default: "" });
  game.settings.register(ID, "importada", { scope: "world", config: false, type: Boolean, default: false });
});

const API = {
  configuracionInicial, avanzarEscena, mostrarHandout, resacaNarrativa, fichasConfidenciales, tiradaEnTabla,
  panelFrentes: () => PanelFrentes.abrir(), pizarra: () => Pizarra.abrir(), presionPrincesa: () => PanelPresion.abrir(),
  contadorCulpa: () => ContadorCulpa.abrir(), parmesanoRuso: () => Parmesano.abrir()
};

Hooks.once("ready", async () => {
  const modulo = game.modules.get(ID);
  modulo.api = {
    ...API,
    verificarAssets: (opts = { aviso: true }) => verificarAssets(ID, opts),
    rutaConFallback: (path, kind) => rutaConFallback(ID, path, kind)
  };
  iniciarSocket(reproducir);
  const dir = game.modules.get("mr-direccion");
  if (dir?.active && dir.api) registrarDireccion(dir.api);
  if (game.user.isGM) {
    // Las macros del pack llevan un autor ficticio: se reasignan al GM que las importa.
    for (const m of game.macros.filter(m => m.getFlag(ID, "macro") && !game.users.has(m.author?.id))) await m.update({ author: game.user.id });
    await repararMundo();
    if (game.settings.get(ID, "verificarAlIniciar")) verificarAssets(ID, { aviso: true });
    if (!game.settings.get(ID, "importada") && !game.scenes.some(s => s.getFlag(ID, "escena"))) configuracionInicial();
  }
});

// Mundos importados con una versión anterior: faltan las marcas (slug) que MR- Dirección necesita y las fichas siguen redondas.
async function repararMundo() {
  const version = game.modules.get(ID).version;
  if (game.settings.get(ID, "migracion") === version || !game.scenes.some(s => s.flags?.[ID]?.escena)) return;
  const man = await (await fetch(`modules/${ID}/asset-manifest.json`)).json();
  const lista = man.assets;
  const slugEscena = (n) => lista.find(a => a.kind === "scene" && a.id.split(".")[1].startsWith(`${n}-`))?.id.split(".")[1];
  const esc = game.scenes.contents.filter(s => s.flags?.[ID]?.escena && s.flags[ID].slug !== slugEscena(s.flags[ID].escena))
    .map(s => ({ _id: s.id, [`flags.${ID}.slug`]: slugEscena(s.flags[ID].escena) }));
  if (esc.length) await Scene.updateDocuments(esc);
  for (const p of game.playlists) {
    const cambios = p.sounds.contents.filter(x => x.path?.includes(`modules/${ID}/assets/audio/`) && !x.flags?.[ID]?.slug)
      .map(x => ({ _id: x.id, [`flags.${ID}.slug`]: x.path.split("/").pop().replace(/\.[^.]+$/, "") }));
    if (cambios.length) await p.updateEmbeddedDocuments("PlaylistSound", cambios);
  }
  if (game.settings.get(ID, "estiloToken") === "cuerpo") {
    const act = game.actors.contents.filter(a => a.flags?.[ID]?.slug && !a.prototypeToken.texture.src?.includes("/figures/") && lista.some(f => f.id === `figure.${a.flags[ID].slug}`))
      .map(a => ({ _id: a.id, "prototypeToken.texture.src": `modules/${ID}/assets/actors/figures/${a.flags[ID].slug}.webp`, "prototypeToken.ring.enabled": false }));
    if (act.length) await Actor.updateDocuments(act);
  }
  await game.settings.set(ID, "migracion", version);
  console.log(`${ID} | mundo actualizado a ${version}: ${esc.length} escenas, fichas ${game.actors.contents.length}`);
}

// Integración opcional con MR- Dirección: si está activo, recibe un paquete con escenas, motivos, efectos, figuras y relojes.
let direccionRegistrada = false;
async function registrarDireccion(api) {
  if (!api?.registerPack || direccionRegistrada) return;
  try {
    const pack = await (await fetch(`modules/${ID}/content/direccion-es.json`)).json();
    api.registerPack(pack); direccionRegistrada = true;
  } catch (e) { console.error(`${ID} | no se pudo registrar el paquete de MR- Dirección`, e); }
}
Hooks.on("mrDireccion.ready", (api) => registrarDireccion(api));

// Estilo de ficha: cuerpo entero sin fondo (predeterminado) o redondo.
Hooks.on("preCreateToken", (token) => {
  const slug = token.actor?.flags?.[ID]?.slug;
  if (!slug || game.settings.get(ID, "estiloToken") !== "redondo") return;
  token.updateSource({ "texture.src": `modules/${ID}/assets/actors/tokens/${slug}.webp` });
});

// Barra de herramientas: lo que usan los jugadores no necesita permiso de macros.
Hooks.on("getSceneControlButtons", (controls) => {
  const gm = game.user.isGM;
  const herr = (name, title, icon, fn, soloGM = false) => ({ name, title, icon, button: true, visible: gm || !soloGM, onChange: () => fn() });
  const tools = [
    herr("pizarra", "Pizarra de Investigación", "fa-solid fa-note-sticky", API.pizarra),
    herr("resaca", "Resaca Narrativa", "fa-solid fa-comment-dots", API.resacaNarrativa),
    herr("culpa", "Contador de Culpa", "fa-solid fa-scale-unbalanced", API.contadorCulpa),
    herr("frentes", "Panel de Frentes", "fa-solid fa-clock", API.panelFrentes, true),
    herr("escena", "Avanzar a Escena", "fa-solid fa-forward", API.avanzarEscena, true),
    herr("handout", "Mostrar Handout", "fa-solid fa-file-image", API.mostrarHandout, true),
    herr("presion", "Presión de Princesa", "fa-solid fa-droplet", API.presionPrincesa, true),
    herr("parmesano", "El Parmesano Ruso", "fa-solid fa-cheese", API.parmesanoRuso, true),
    herr("fichas", "Fichas Confidenciales", "fa-solid fa-envelope", API.fichasConfidenciales, true),
    herr("tabla", "Tirada en Tabla", "fa-solid fa-dice", API.tiradaEnTabla, true)
  ];
  controls["mrreq"] = { name: "mrreq", title: "Requesón en Waterdeep", icon: "fa-solid fa-cheese", order: 90, visible: true, activeTool: "", tools: Object.fromEntries(tools.map((t, i) => [t.name, { ...t, order: i }])) };
});

// La hoja de Mausritter es un lienzo libre: no impide dejar la pulsera ni las condiciones en el equipaje.
// Este control lo impone. Las columnas de patas y cuerpo terminan en x = 0; el equipaje empieza en x = 10.
Hooks.on("preUpdateItem", (item, changes) => {
  if (item.getFlag(ID, "zona") !== "patas-cuerpo") return;
  const x = foundry.utils.getProperty(changes, "system.sheet.currentX");
  if (x === undefined) return;
  const ancho = item.system.size?.width ?? 1;
  if (x + ancho * 130 > 5) {
    ui.notifications.warn(game.i18n.format("MRREQ.Zona.Aviso", { nombre: item.name }));
    return false;
  }
});
