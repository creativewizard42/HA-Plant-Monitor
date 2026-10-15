# Plant Monitor branding

Original AI-generated plant/pot/water-drop emblem, created for this project
on 15 October 2026. It does not use Home Assistant's or HACS's logo.

- `icon.png`: transparent 256 × 256 PNG.
- `icon@2x.png`: transparent 512 × 512 PNG.

The same square emblem serves as the logo through Home Assistant's normal
icon-to-logo fallback. These assets are distributed with the project under
its MIT licence to the extent applicable.

Home Assistant 2026.3 introduced local custom-integration brand assets.
After updating this integration, restart Home Assistant and refresh HACS.
Older versions can still request the legacy central brands service and show
“icon not available”, even when these files are correctly installed.

Before-installation previews also depend on the HACS/frontend version and
its image lookup mechanism. Bundling these files cannot change an old HACS
client's CDN URL. A first-install HACS preview has not been verified against
a live instance.

The Home Assistant brands project now directs custom integrations to bundle
assets themselves rather than submitting new custom-integration logos:
https://github.com/home-assistant/brands#marketplace-icons

Brand responses may remain cached. HACS's old CDN paths and the new Home
Assistant Marketplace paths are different; support for the latter does not
imply a particular HACS version uses it.
