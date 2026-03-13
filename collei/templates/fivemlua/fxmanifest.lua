fx_version "cerulean"
games { "gta5" }

author "{{ input.author }}"
description "{{ input.description }}"
version "{{ input.version }}"

lua54 "yes"

{% if input.lib %}dependency "ox_lib"{% endif %}
{% if input.target %}dependency "ox_target"{% endif %}
{% if input.inventory %}dependency "ox_inventory"{% endif %}
{% if input.sql %}dependency "oxmysql"{% endif %}
dependency "/onesync"

shared_script "config.lua"
shared_script "shared.lua"
{% if input.lib %}shared_script "@ox_lib/init.lua"{% endif %}

client_script "client.lua"

{% if input.sql %}shared_script "@oxmysql/lib/MySQL.lua"{% endif %}
server_script "server.lua"

files {
    "locales/*.json"
}

escrow_ignore {
    "config.lua"
}
