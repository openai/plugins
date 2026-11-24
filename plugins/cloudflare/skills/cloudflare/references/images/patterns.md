# Images Patterns

Choose the workflow that matches the existing storage and delivery architecture, then read its implementation guide.

| Workflow | Documentation |
|----------|---------------|
| Let users upload without exposing account credentials | [Direct Creator Upload](https://developers.cloudflare.com/images/storage/upload-images/direct-creator-upload/index.md) |
| Serve images for different layouts and display densities | [Make responsive images](https://developers.cloudflare.com/images/optimization/make-responsive-images/index.md) |
| Select output format for hosted images | [Hosted-image format optimization](https://developers.cloudflare.com/images/optimization/hosted-images/serve-uploaded-images/index.md#optimize-format) |
| Select output format for a Worker pipeline | [Workers optimization binding](https://developers.cloudflare.com/images/optimization/binding/index.md) |
| Optimize user uploads, add a watermark, and store the result in R2 | [Transform user-uploaded images before uploading to R2](https://developers.cloudflare.com/images/tutorials/optimize-user-uploaded-image/index.md) |
| Compose overlays and watermarks | [Draw overlays](https://developers.cloudflare.com/images/optimization/draw-overlays/index.md) |
| Cache a Worker transformation response | [Binding methods and caching guidance](https://developers.cloudflare.com/images/optimization/binding/index.md#methods) |
| Configure hosted-image browser caching | [Browser TTL](https://developers.cloudflare.com/images/optimization/hosted-images/browser-ttl/index.md) |

Adapt dimensions and quality to the actual layout and representative source images. Keep upload credentials server-side, preserve the application's access checks, and validate both the resulting image and its response headers. Consult [limits and troubleshooting](gotchas.md) before choosing batch sizes or retry behavior.
