import { ID } from "./estado.mjs";

const SFX = { tuberia: "tuberia-cede", ritual: "ritual-pulso", timbre: "timbre-recepcion", queso: "queso-guindilla", puerta: "puerta-de-tyson", mandibula: "mandibula-negra" };

function quiereMovimiento() {
  if (!game.settings.get(ID, "efectosVisuales")) return false;
  return !(window.matchMedia?.("(prefers-reduced-motion: reduce)").matches);
}

/** Se ejecuta en cada cliente: sonido y destello, ambos opcionales y respetando la preferencia de movimiento reducido. */
export function reproducir(clave, visual = null) {
  if (game.settings.get(ID, "efectosSonido") && SFX[clave]) {
    foundry.audio.AudioHelper.play({ src: `modules/${ID}/assets/audio/sfx/${SFX[clave]}.ogg`, volume: game.settings.get(ID, "volumenEfectos"), autoplay: true, loop: false }, false);
  }
  if (visual && quiereMovimiento()) {
    const d = document.createElement("div");
    d.className = `mrreq-flash mrreq-flash-${visual}`; d.setAttribute("aria-hidden", "true");
    d.addEventListener("animationend", () => d.remove(), { once: true });
    document.body.appendChild(d);
  }
}

/** El GM lo dispara en su cliente y avisa al resto por socket. */
export function efecto(clave, visual = null) {
  reproducir(clave, visual);
  game.socket.emit(`module.${ID}`, { efecto: clave, visual });
}
