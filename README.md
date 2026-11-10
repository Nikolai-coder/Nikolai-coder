<!-- Probe: how GitHub treats srcset candidates and the sizes attribute. Temporary branch, to be deleted. -->

<p>
<picture>
<source media="(prefers-color-scheme: light)" srcset="assets/gate.day.tall.svg 400w, assets/gate.day.wide.svg 880w" sizes="(max-width: 600px) 10px, 20000px">
<source media="(prefers-color-scheme: dark)" srcset="assets/gate.night.tall.svg 400w, assets/gate.night.wide.svg 880w" sizes="(max-width: 600px) 10px, 20000px">
<img src="assets/gate.night.wide.svg" width="100%" alt="V1 two themed sources with srcset and sizes">
</picture>
</p>

<p>
<a href="https://github.com/Nikolai-coder/diavlo-wav-releases">
<picture>
<source media="(prefers-color-scheme: light)" srcset="assets/line.diavlo-wav-releases.day.tall.svg 400w, assets/line.diavlo-wav-releases.day.wide.svg 880w" sizes="(max-width: 600px) 10px, 20000px">
<img src="assets/line.diavlo-wav-releases.night.wide.svg" srcset="assets/line.diavlo-wav-releases.night.tall.svg 400w, assets/line.diavlo-wav-releases.night.wide.svg 880w" sizes="(max-width: 600px) 10px, 20000px" width="100%" alt="V2 one themed source and an img that carries srcset and sizes, inside a link">
</picture>
</a>
</p>
