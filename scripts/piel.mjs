// Piel de Requesón en Waterdeep para lo nativo de Mausritter: fichas de actor, tarjetas de tirada del chat y diálogos de tirada.
// Solo añade la clase .mrreq-piel (y el CSS hace el resto): no toca el HTML, los datos ni los botones que meten
// MR- Mausritter en español o Combat Carousel. Se apaga con el ajuste «pielTiradas».
import { ID } from "./estado.mjs";

const DIALOGO = 'select[name="advantage"], select[name="enhanced"], select[name="stat"], input[name="power"]';
const raiz = (x) => x?.[0] ?? x;

export function registrarPiel() {
  game.settings.register(ID, "pielTiradas", { name: "MRREQ.Settings.pielTiradas.Name", hint: "MRREQ.Settings.pielTiradas.Hint",
    scope: "client", config: true, type: Boolean, default: true, onChange: (v) => document.body.classList.toggle("mrreq-piel-on", v) });
  Hooks.once("ready", () => document.body.classList.toggle("mrreq-piel-on", game.settings.get(ID, "pielTiradas")));
  Hooks.on("renderChatMessageHTML", (_m, html) => {
    if (html.querySelector?.(".mausritter .rollcontainer")) html.classList.add("mrreq-piel");
  });
  Hooks.on("renderDialog", (app, html) => {
    const el = raiz(app.element) ?? raiz(html);
    if (el?.querySelector?.(DIALOGO)) el.classList.add("mrreq-piel", "mrreq-piel-dialogo");
  });
  Hooks.on("renderActorSheet", (app, html) => {
    const el = raiz(app.element) ?? raiz(html);
    el?.classList.add("mrreq-piel", "mrreq-piel-ficha");
  });
}

/** Portada del mundo: si el mundo no tiene imagen de fondo (o descripción), pone las de Requesón en Waterdeep. Se ven en la
 *  pantalla de entrada y en la tarjeta del mundo. Nunca pisa lo que el DJ haya puesto. */
export async function ponerPortada() {
  if (!game.user.isGM) return;
  const cambios = {};
  if (!game.world.background) cambios.background = `modules/${ID}/assets/portada-mundo.webp`;
  if (!game.world.description?.trim()) cambios.description = game.i18n.localize("MRREQ.DescripcionMundo");
  if (!Object.keys(cambios).length) return;
  try {
    const r = await foundry.utils.fetchJsonWithTimeout(foundry.utils.getRoute("setup"), {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "editWorld", id: game.world.id, ...cambios })
    });
    if (r?.error) console.warn(`${ID} | portada del mundo:`, r.error);
  } catch (e) { console.warn(`${ID} | portada del mundo:`, e); }
}
