fx_version "cerulean"
games { "gta5" }

{% if input.client %}client_script "{{ input.name }}.Client.net.dll"{% endif %}
server_script "{{ input.name }}.Server.net.dll"
{% if input.json %}file "Newtonsoft.Json.dll"{% endif %}
{% if input.lemonui %}file "LemonUI.FiveM.dll"{% endif %}
