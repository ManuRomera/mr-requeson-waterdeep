const cache = new Map();

async function existe(url) {
  if (cache.has(url)) return cache.get(url);
  let ok = false;
  try { ok = (await fetch(url, { method: "HEAD" })).ok; } catch (e) { ok = false; }
  cache.set(url, ok);
  return ok;
}

/** Comprueba cada ruta del asset-manifest.json. Devuelve { total, faltan, porTipo }. */
export async function verificarAssets(id, { aviso = false } = {}) {
  let manifest;
  try { manifest = await (await fetch(`modules/${id}/asset-manifest.json`)).json(); }
  catch (e) { ui.notifications.error(game.i18n.localize("MRREQ.Verify.NoManifest")); return null; }
  const lista = manifest.assets.filter(a => a.path && !a.reuse_of);
  const faltan = [];
  for (let i = 0; i < lista.length; i += 8) {
    const lote = lista.slice(i, i + 8);
    const res = await Promise.all(lote.map(a => existe(`modules/${id}/${a.path}`)));
    lote.forEach((a, j) => { if (!res[j]) faltan.push(a); });
  }
  const porTipo = {};
  for (const a of faltan) (porTipo[a.kind] ??= []).push(a.path);
  console.log(`${id} | assets que faltan: ${faltan.length}/${lista.length}`, porTipo);
  if (aviso) {
    if (faltan.length) ui.notifications.warn(game.i18n.format("MRREQ.Verify.Missing", { n: faltan.length, total: lista.length }));
    else ui.notifications.info(game.i18n.localize("MRREQ.Verify.Ok"));
  }
  return { total: lista.length, faltan: faltan.length, porTipo };
}

/** Ruta lista para usar: el archivo si existe, o el placeholder de su tipo. */
export async function rutaConFallback(id, path, kind) {
  return (await existe(`modules/${id}/${path}`)) ? `modules/${id}/${path}` : `modules/${id}/assets/_placeholders/${kind}.svg`;
}
