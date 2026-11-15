# prompts reutilizables del catálogo anterior y del manuscrito
ICO=lambda s:f"RPG game item icon of {s}. Centered, dark fantasy, gritty realistic texture, isolated on pure solid black background"
NEW={ # sustituyen a los prompts genéricos del catálogo anterior
'llave-de-mantenimiento':ICO("a small brass maintenance key with a square shaft and a worn red cord loop, human-sized key scaled for a mouse"),
'llave-de-jaula':ICO("a tiny steel key for a pet travel cage, a small paw-print tag tied to it with string"),
'documento-de-embargo':ICO("a long official seizure notice with an itemised list of furniture, curtains and ears, a heavy red stamp, one corner chewed, highly detailed paper texture")+"",
'carrete-de-hilo-resistente':ICO("a small spool of strong waxed thread, dark purple, needle stuck in it"),
'medio-contrato-del-sindicato':ICO("the torn left half of a formal contract, fine ink claw-shaped seal, a faint smudge of a gloved fingerprint"),
'panuelo-con-sello-gralhund':ICO("a folded fine linen handkerchief embroidered with a black and gold noble crest, one corner stained"),
'recibo-de-una-segunda-jarra':ICO("a crumpled tavern receipt for a second jug, ink blots, a ring stain from a thimble cup"),
'pinza-fina':ICO("a pair of fine polished steel tweezers, mouse-sized, with a tiny hook at the tip"),
'sales-aromaticas':ICO("a tiny glass smelling-salts bottle with pale green crystals and a cork stopper"),
'cuentagotas-vacio':ICO("an empty glass dropper with a rubber bulb, a faint emerald residue at the tip"),
'bufanda-purpura-de-la-manada':ICO("a ragged deep purple wool scarf rolled into a tight coil"),
'cuerda-corta':ICO("a short coil of rough hemp cord with a frayed end"),
'casco-de-agente-abollado':ICO("a dented, badly painted brass guard helmet, mouse-sized, the paint flaking to show the metal"),
'bolsa-de-objetos-inutiles':ICO("a small drawstring pouch spilling a bent spoon, three buttons joined by thread and half a nut painted blue"),
'llave-pequena-de-jaula':ICO("a tiny brass key hanging from a loop of string, as if dangling from a mouse finger"),
'fajin-lila-de-la-manada':ICO("a wrinkled lilac ceremonial sash, folded, with a few threads loose"),
'alianza-de-alambre':ICO("a crooked wedding ring bent from thin copper wire"),
'foto-nupcial-borrosa':ICO("a blurry square instant photo print of a wedding, motion-smeared figures, a torn corner, no readable text"),
'buscado':"RPG condition status icon of a torn wanted poster pinned by a tiny dagger, a crude drawing of five mice in scarves, ink smudged. Centered, abstract game symbol, dark fantasy, no readable text, isolated on pure solid black background",
'compromiso-familiar':"RPG condition status icon of a crooked copper wire ring tied with a lilac ribbon, a tiny bat-pup footprint pressed into wax beside it. Centered, abstract game symbol, dark fantasy, isolated on pure solid black background",
'ardido':"RPG condition status icon of a blistered cube of white cheese with a glowing red chili pepper pressed into it, heat shimmer rising. Centered, abstract game symbol, dark fantasy, isolated on pure solid black background",
'empapado':"RPG condition status icon of a tiny soaked cloth sock dripping water into a small puddle. Centered, abstract game symbol, dark fantasy, isolated on pure solid black background",
'el-bebe-carga':ICO("a tiny newborn bat pup swaddled in a linen napkin, mouth wide open mid-shriek, absurdly large ears"),
}
# alias: objetos que reutilizan el prompt del handout equivalente
ALIAS={'recibo-del-intercambio':'recibo-del-intercambio','acta-de-boda':'acta-de-boda','parte-de-incidencias':'acta-de-redada','plano-de-pazos':'plano-de-pazos','nota-lacrada-de-nixyus':'nota-de-nixyus','tarjeta-vip-del-dado':None,'etiqueta-de-calma-comadrejas':'etiqueta-de-calma-comadrejas','dos-cintas-de-botella-intercambiadas':None}
HANDOUT_PROMPTS={ # prompts del manuscrito (Herramientas del DJ), con el aspecto de la tabla
'recibo-del-intercambio':"RPG game item icon of a tiny handwritten receipt rolled inside a brass ring, ink signature and a time scrawled at the bottom, edges worn. Centered, dark fantasy, highly detailed paper texture, isolated on pure solid black background",
'nota-de-nixyus':"RPG game item icon of a small folded letter written in nervous slanted handwriting, sealed with dark red wax bearing a lute symbol, one corner burned. Centered, dark fantasy, detailed parchment texture, isolated on pure solid black background",
'etiqueta-de-calma-comadrejas':"RPG game item icon of a peeling apothecary bottle label with bold warning typography and a small weasel silhouette, faded green ink, glue residue at the edges. Centered, flat-on view, dark fantasy, isolated on pure solid black background",
'pagare-de-parmesano':"RPG game item icon of an unrolled promissory note covered in cramped clauses, a dark red wax seal shaped like a cheese wedge, a large drunken scrawl crossed out in different ink, grease stains. Centered, dark fantasy, isolated on pure solid black background",
'acta-de-boda':"RPG game item icon of a small marriage certificate with ornate borders, two illegible signatures and a smudged inked paw print used as a witness mark, one corner chewed. Centered, dark fantasy, aged paper, isolated on pure solid black background",
'acta-de-redada':"RPG game item icon of an official watch report form with two timestamped entries, a city seal stamped crooked, ink blots and a bent corner. Centered, dark fantasy, bureaucratic paper texture, isolated on pure solid black background",
'plano-de-pazos':"RPG game item icon of a chaotic hand-drawn plan on a crumpled sheet, seven arrows pointing in different directions, five crude portraits circled, a word written over and over in the margins. Centered, dark fantasy, obsessive detail, isolated on pure solid black background",
'manual-de-la-mandibula-negra':"RPG game item icon of a tiny greasy instruction booklet for a brass machine, exploded diagram of gears on the open page, thumb smudges, corner torn off. Centered, dark fantasy, isolated on pure solid black background",
'pared-de-la-villa':"RPG game item icon of a hand-painted sign on a scrap of card, two lines of bold uneven lettering, one much smaller than the other, wine stain across the corner. Centered, dark fantasy, isolated on pure solid black background",
'acuerdo-de-mesa-lineas-y-velos':"RPG game item icon of a folded table agreement sheet with two columns of empty ruled lines, a small pause symbol drawn in the corner, a paperclip and a coffee ring. Centered, flat-on view, dark fantasy, no readable text, isolated on pure solid black background",
'tarjeta-vip-del-dado':"RPG game item icon of a small embossed casino membership card, mother-of-pearl inlay, a table number stamped in gold, one edge bent from a pocket. Centered, dark fantasy, isolated on pure solid black background",
'dos-cintas-de-botella-intercambiadas':"RPG game item icon of two narrow silk ribbons side by side, one deep purple and torn, one white and intact, both showing knot creases. Centered, macro detail, dark fantasy, isolated on pure solid black background",
}
