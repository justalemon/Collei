# {{ input.name }}<br>{% if input.actions and github %}[![GitHub Actions][actions-img]][actions-url] {% endif %}{% if input.patreon %}[![Patreon][patreon-img]][patreon-url] {% endif %}{% if input.paypal %}[![PayPal][paypal-img]][paypal-url] {% endif %}{% if input.discord %}[![Discord][discord-img]][discord-url]{% endif %}

{{ input.description }}

## Download

{% if github %}* [GitHub Releases](https://github.com/{{ github.user }}/{{ github.repo }}/releases){% endif %}
{% if input.actions and github %}* [GitHub Actions](https://github.com/{{ github.user }}/{{ github.repo }}/actions) (experimental versions){% endif %}

## Installation

{{ input.installation }}

## Usage

{{ input.usage }}

{% if input.actions and github %}[actions-img]: https://img.shields.io/github/actions/workflow/status/{{ github.user }}/{{ github.repo }}/main.yml?branch=master&label=actions
[actions-url]: https://github.com/{{ github.user }}/{{ github.repo }}/actions{% endif %}
{% if input.patreon %}[patreon-img]: https://img.shields.io/badge/support-patreon-FF424D.svg
[patreon-url]: https://www.patreon.com/{{ input.patreon }}{% endif %}
{% if input.paypal %}[paypal-img]: https://img.shields.io/badge/support-paypal-0079C1.svg
[paypal-url]: https://paypal.me/{{ input.paypal }}{% endif %}
{% if input.discord %}[discord-img]: https://img.shields.io/badge/discord-join-7289DA.svg
[discord-url]: https://discord.gg/{{ input.discord }}{% endif %}

