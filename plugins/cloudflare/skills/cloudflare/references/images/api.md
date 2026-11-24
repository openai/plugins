# Images API Selection

| Operation | Documentation |
|-----------|---------------|
| Optimize image bytes in a Worker; select input, transform, output, and response methods | [Optimize with Workers](https://developers.cloudflare.com/images/optimization/binding/index.md#methods) |
| Upload, list, retrieve, update, or delete hosted images from a Worker | [Manage hosted images with Workers](https://developers.cloudflare.com/images/storage/binding/index.md) |
| Upload or manage images through HTTP | [Upload methods](https://developers.cloudflare.com/images/storage/upload-images/methods/index.md#upload-using-api) and its linked Images API reference |
| Accept uploads directly from a client | [Direct Creator Upload](https://developers.cloudflare.com/images/storage/upload-images/direct-creator-upload/index.md) |
| Construct hosted-image delivery URLs | [Serve uploaded images](https://developers.cloudflare.com/images/optimization/hosted-images/serve-uploaded-images/index.md) |
| Apply URL optimization parameters or select fit, quality, and format | [Optimization features](https://developers.cloudflare.com/images/optimization/features/index.md) |
| Draw overlays or watermarks | [Draw overlays](https://developers.cloudflare.com/images/optimization/draw-overlays/index.md) |

Do not transfer URL parameters or HTTP request shapes directly into binding calls. Read the contract for the selected interface, including output format handling. Use the project's generated binding types and existing error handling. See [configuration](configuration.md) for setup and [troubleshooting](gotchas.md) for failures and limits.
