/**
 * Ventanas que caben en cualquier pantalla (estándar de la casa, kit mr-pantallas): toda ventana del módulo se escala en proporción
 * a la pantalla, nunca se sale, se desplaza por dentro y deja el botón a la vista. El ajuste «Tamaño de las ventanas» fija una escala propia.
 */
import { ID } from "./estado.mjs";
import { escalaDeVentana } from "./ventanas-core.mjs";

const nuestra = (app) => Boolean(app?.element?.classList?.contains("mrreq"));

export function ajustarVentana(app) {
  if (!nuestra(app) || !app.rendered || app.minimized) return;
  const el = app.element, doc = document.documentElement;
  const hotbar = parseFloat(getComputedStyle(document.body).getPropertyValue("--hotbar-height")) || 0;
  const vista = { ancho: doc.clientWidth, alto: doc.clientHeight - 1.5 * hotbar, total: doc.clientHeight };
  const primera = !app._mrAjustada;
  app._mrAjustada = true;
  const pedido = app.options?.position ?? {}, ahora = app.position ?? {};
  const medida = (pide, tiene, medir) => (primera && Number.isFinite(pide) ? pide : Number.isFinite(tiene) ? tiene : medir());
  const ancho = medida(pedido.width, ahora.width, () => el.offsetWidth);
  const alto = medida(pedido.height, ahora.height, () => {
    const tope = el.style.maxHeight; el.style.maxHeight = "none";
    const h = el.offsetHeight; el.style.maxHeight = tope; return h;
  });
  const escala = escalaDeVentana(ancho, alto, vista, Number(game.settings.get(ID, "escalaVentanas")) || 0);
  el.style.setProperty("--rw-esc-ventana", String(escala));
  if (!primera && Math.abs((ahora.scale ?? 1) - escala) < 0.004) return;
  const cambio = { scale: escala };
  if (primera && Number.isFinite(pedido.width)) cambio.width = pedido.width;
  if (primera && Number.isFinite(pedido.height)) cambio.height = pedido.height;
  app.setPosition(cambio);
}

let espera = 0;
export function reajustarVentanas() {
  clearTimeout(espera);
  espera = setTimeout(() => { for (const app of foundry.applications.instances.values()) ajustarVentana(app); }, 150);
}

export function registrarVentanas() {
  game.settings.register(ID, "escalaVentanas", {
    name: "MRREQ.Settings.escalaVentanas.Name", hint: "MRREQ.Settings.escalaVentanas.Hint",
    scope: "client", config: true, type: Number, default: 0, range: { min: 0, max: 150, step: 5 }, onChange: reajustarVentanas
  });
  Hooks.on("renderApplicationV2", (app) => ajustarVentana(app));
  window.addEventListener("resize", reajustarVentanas);
}
