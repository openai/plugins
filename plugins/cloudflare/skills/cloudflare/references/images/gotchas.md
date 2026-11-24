# Images Troubleshooting

First identify whether the failure involves hosted-image storage, remote URL transformations, or a Worker binding. Capture the failing operation, response status, relevant headers, and error message before changing options.

| Symptom or question | Documentation |
|---------------------|---------------|
| Resizing is absent, an origin request fails, or a transformation returns an error code | [Troubleshooting](https://developers.cloudflare.com/images/reference/troubleshooting/index.md) |
| Input size, dimensions, animation, or format compatibility | [Limits and formats](https://developers.cloudflare.com/images/get-started/limits/index.md) — choose the section for the affected interface |
| Unexpected fit, quality, format, or crop behavior | [Optimization features](https://developers.cloudflare.com/images/optimization/features/index.md) |
| Binding input, output, or response handling fails | [Binding methods](https://developers.cloudflare.com/images/optimization/binding/index.md#methods) |
| Local behavior differs from production | [Local binding development](https://developers.cloudflare.com/images/optimization/binding/index.md#interact-with-your-images-binding-locally) |
| Private delivery fails or an image is unexpectedly public | [Serve private images](https://developers.cloudflare.com/images/optimization/hosted-images/serve-private-images/index.md) and [variant public access](https://developers.cloudflare.com/images/optimization/hosted-images/create-variants/index.md#public-access) |
| Remote transformations appear stale | [Caching and purging](https://developers.cloudflare.com/images/reference/troubleshooting/index.md#caching-and-purging) |
| Worker transformations repeat unnecessarily | [Binding caching guidance](https://developers.cloudflare.com/images/optimization/binding/index.md#methods) |

Do not apply one interface's limits, error codes, or caching rules to another. Reproduce with a representative image and verify the chosen fix using the project's existing checks. Retry only after identifying a transient failure; changing invalid inputs or access configuration requires a different fix. See [API selection](api.md) and [configuration](configuration.md) when the wrong interface or setup is responsible.
