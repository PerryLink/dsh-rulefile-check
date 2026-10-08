# dsh-rulefile-check — Autocomprobación del archivo de reglas según la disciplina de citas y los techos de severidad

`dsh-rulefile-check` lee un archivo de reglas —la cabecera del archivo más una fila por regla— y lo contrasta con la disciplina de citas que impone su familia de plugins: que cada id de regla sea único dentro del archivo, que los dos campos de fundamento estén completos, que ningún extracto sea más corto que la longitud mínima, que toda fuente esté escrita como enlace http(s), que una regla cuyo tipo de fundamento sea `derived-from-principle` o `institutional-configuration` lleve una severidad, que el tipo de comprobación sea uno que el motor admita, y que la cabecera del archivo declare su nombre, su plugin y su versión.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| El mismo id de regla aparece en dos reglas del archivo. | `RF-001` informa del id repetido, porque un duplicado hace que `issue.id` apunte a dos reglas distintas y la coincidencia ya no se puede rastrear. La comparación ignora los espacios en blanco. Solo ve un archivo a la vez: no compara dos archivos entre sí ni consulta ningún registro. |
| Una regla solo trae `document` y no dice nada de la cláusula. | `RF-002` comprueba que al menos uno de los dos campos de fundamento esté relleno, así que una regla con `document` presente pasa. No juzga si la cláusula citada existe realmente ni si guarda relación con la regla. |
| El extracto es una descripción de la cláusula en una frase, no una cita. | `RF-003` exige que el extracto exista y tenga al menos ocho caracteres. La longitud es necesaria, no suficiente: una descripción de veinte caracteres sigue sin ser una cita, y esta regla no distingue — no coteja el extracto con la cláusula original. |
| La fuente dice «某某网站» en lugar de un enlace. | `RF-004` lo informa, porque el campo de fuente tiene que parecer un enlace http(s). Solo comprueba la forma: no visita el enlace, no le dice si el enlace funciona ni si la página contiene realmente la cláusula citada. |
| Una regla derivada de un principio está clasificada como `error`. | `RF-005` confirma que una regla cuyo tipo de fundamento sea `derived-from-principle` o `institutional-configuration` indique alguna severidad. Que esa severidad respete de verdad el techo lo impone el cargador, que rechaza ese archivo con `strongest permitted severity`; esta comprobación solo cubre que el campo exista y no puede sustituir al cargador. |
| El archivo escribe un `check.kind` que el motor no conoce, ¿y declara su `packName` y su `version`? | `RF-006` informa del `check.kind` desconocido, porque esa regla no se ejecuta en silencio. Su lista de tipos admitidos viene vacía, ya que qué tipos existen depende de la versión del motor, de modo que un archivo sin configurar deja esa regla en `skipped` en lugar de aprobarla; solo compara con la lista que usted aporte. `RF-007` comprueba juntos `packName`, `plugin` y `version` en la cabecera, porque sin ellos no se puede saber a qué plugin pertenece un archivo, ni qué revisión, al sustituirlo. Ninguna de las dos verifica que los valores declarados correspondan al plugin realmente en uso. |

## Normas que sigue

Este archivo de reglas no cita ninguna norma pública: el fundamento de cada regla es la disciplina de citas que la propia familia de plugins se impone, su contrato de motor y su contrato de archivo, de modo que las entradas siguientes nombran compromisos internos de la familia y no ninguna ley ni norma nacional.

| Documento | Número | Reglas que lo citan |
|---|---|---|
| 本插件家族的条款引用纪律（自定纪律，非国家标准） | 无编号（本规则库自定） | RF-001, RF-002, RF-003, RF-004, RF-005 |
| 本插件家族的检查引擎契约（自定纪律，非国家标准） | 无编号（本规则库自定） | RF-006 |
| 本插件家族的规则库契约（自定纪律，非国家标准） | 无编号（本规则库自定） | RF-007 |

**Boundary:** this plugin checks a **规则库** (a rule pack) for the citation discipline this plugin family
enforces — that rule ids are unique, that every basis field is present, that an excerpt has real length, that a
source is a link, that a derived or locally configured basis carries a severity, that the check kind is one the
engine supports, and that the pack declares its name, plugin and version.

> ### ⚠️ This checks form, not content — and it says so
>
> **The discipline being checked is self-imposed, not a national standard.** "An excerpt must be a verbatim
> quotation" and "a principle-derived check may not be an `error`" are rules this plugin family enforces in
> `shared/ruleset.ts`; their basis is the general principle of intellectual honesty — never dress a description
> up as a quotation, never dress an inference up as a requirement — **not any statute or standard**. Every
> rule's `basis` says exactly that, which is why every rule here is `warn` or `info`.
>
> **It cannot tell whether a citation is apt.** It checks that fields are filled, that an excerpt is long
> enough, that a source *looks like* a link, and that a severity is stated. It will happily pass a rule that
> cites **a real but irrelevant clause** — that is the documented limit of a form check, and it is why
> automated checking never replaces a human read-through.
>
> Two rules deserve a note. `RF-003`'s floor of eight characters is the ledger-side echo of the load-time guard
> — but **length is necessary, not sufficient**: a twenty-character *description* is still not a quotation, and
> this plugin cannot tell the difference. And `RF-005` can only confirm a severity field is present: whether a
> severity actually respects the ceiling is enforced by the loader, which rejects a violating pack outright with
> `strongest permitted severity`. `RF-006`'s kind vocabulary ships **empty**, because which kinds an engine
> supports depends on the engine version — hard-coding this family's own list would mean editing this plugin
> every time the engine gains a kind.

## Compatibility

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-rulefile-check
dsh --profile <name> --dump-config | grep 'dsh-rulefile-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/rulefile-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-rulefile-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-rulefile-check contributors.
