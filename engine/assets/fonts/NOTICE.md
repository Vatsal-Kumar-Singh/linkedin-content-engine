# Bundled fonts and their licence

**The MIT licence at the root of this repository covers the code, not these files.** The font
binaries in this directory are third-party work under a different licence and are redistributed
under its terms.

| Family | Files | Copyright | Licence |
|---|---|---|---|
| **Inter** | `Inter-300.woff2`, `Inter-400.woff2`, `Inter-500.woff2` | The Inter Project Authors | SIL Open Font License 1.1 |
| **Poppins** | `Poppins-300.woff2`, `Poppins-400.woff2`, `Poppins-600.woff2` | The Poppins Project Authors (Indian Type Foundry, Jonny Pinhorn) | SIL Open Font License 1.1 |

Full licence text: <https://openfontlicense.org/> · Sources:
<https://github.com/rsms/inter> · <https://github.com/itfoundry/poppins>

**Why they are bundled rather than fetched.** The renderer embeds every face as a `data:` URI so a
card renders identically with no network. A font loaded from a CDN at render time makes the output
depend on somebody else's uptime, and a missing face silently becomes a browser-synthesised fake
rather than a failure.

---

## Replacing them with your own

Nothing in the engine knows these names. `config/brand.yaml` declares the families:

```yaml
typography:
  display: { family: "Poppins", weights: [300, 400, 600], file_pattern: "Poppins-{w}.woff2" }
  body:    { family: "Inter",   weights: [300, 400, 500], file_pattern: "Inter-{w}.woff2" }
  font_dir: "assets/fonts"
```

Drop your `.woff2` files here, point `file_pattern` at them, and list **only the weights that
actually exist**. The `@font-face` block is generated from that list, so a family shipping two
weights works as well as one shipping five.

**If you ship a font you did not license for redistribution, that is your exposure, not the
engine's.** Many commercial and system fonts (including those bundled with office software) do not
permit it. Check before committing the binary, and replace this file with the terms that apply.
