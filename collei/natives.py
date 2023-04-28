import string
import sys
from pathlib import Path
from typing import TextIO, Optional

from requests import get

TYPES = [
    "shvdn",
    "cfxmono",
    "cfxlua"
]
NATIVES = {
    "gtav": "https://raw.githubusercontent.com/alloc8or/gta5-nativedb-data/master/natives.json",
    "rdr3": "https://raw.githubusercontent.com/alloc8or/rdr3-nativedb-data/master/natives.json",
    "fivem": "https://runtime.fivem.net/doc/natives_cfx.json"
}
LUA_EQUIVALENTS = {
    "int": "number",
    "const char*": "string",
    "Any*": "any",
    "Hash": "number",
    "float": "number",
    "Ped": "number",
    "BOOL": "boolean",
    "Any": "any",
    "Entity": "number",
    "Vehicle": "number",
    "float*": "number",
    "int*": "int",
    "Object": "any",
    "Cam": "number",
    "Player": "number",
    "BOOL*": "boolean",
    "Vector3": "vector3",
    "Vector3*": "vector3",
    "ScrHandle*": "number",
    "ScrHandle": "number",
    "Entity*": "number",
    "Ped*": "number",
    "Vehicle*": "number",
    "Object*": "number",
    "Hash*": "number",
    "FireId": "number",
    "Blip": "number",
    "Pickup": "number",
    "Blip*": "number",
    "Interior": "number",
    "char*": "string",  # not sure
    "func": "function",
    "long": "number",
    "bool": "boolean",
    "object": "any"
}
# From Lua Manual: 2.1 - Lexical Conventions
LUA_KEYWORDS = [
    "and",
    "break",
    "do",
    "else",
    "elseif",
    "end",
    "false",
    "for",
    "function",
    "if",
    "in",
    "local",
    "nil",
    "not",
    "or",
    "repeat",
    "return",
    "then",
    "true",
    "until",
    "while"
]


def format_lua_name(name: str):
    return string.capwords(name.lower().replace("0x", "N_0x").replace("_", " ")).replace(" ", "")


def fetch_natives(lists: list[str]):
    result = {}

    for native_list in lists:
        url = NATIVES[native_list]
        response = get(url)

        if not response.ok:
            print(f"Unable to fetch {url}", file=sys.stderr)
            return None

        data = response.json()
        result[native_list] = data

    return result


def write_header(file: TextIO, n_format: str):
    if n_format == "cfxlua":
        return

    if n_format == "shvdn":
        file.write("namespace GTA.Native\n")
    elif n_format == "cfxmono":
        file.write("namespace CitizenFX.Core.Native\n")

    if n_format == "shvdn" or n_format == "cfxmono":
        file.write("{\n")
        file.write("    public enum Hash : ulong\n")
        file.write("    {\n")


def write_footer(file: TextIO, n_format: str):
    if n_format == "cfxlua":
        return

    if n_format == "shvdn" or n_format == "cfxmono":
        file.write("    }\n")
        file.write("}\n")


def write_cs_function(file: TextIO, name: str, nhash: str, comment: Optional[str]):
    if comment is not None and comment:
        file.write("        /// <summary>\n")
        for line in comment.splitlines():
            file.write(f"        /// {line}\n")
        file.write("        /// </summary>\n")

    file.write(f"        {name} = {nhash},\n")


def write_lua_function(file: TextIO, name: str, nhash: str, parameters: list[dict[str, str]], calls: bool,
                       comment: Optional[str]):
    if comment is not None and comment:
        for line in comment.splitlines():
            file.write(f"--- {line}\n")

    parameter_names = []

    for parameter in parameters:
        param_name = parameter["name"]
        param_desc = parameter.get("description", "")
        param_type = LUA_EQUIVALENTS.get(parameter["type"], None) or parameter["type"]

        if param_name in LUA_KEYWORDS:
            param_name = f"_{param_name}"
        if param_name in parameter_names:
            param_name = f"{param_name}_{len(parameter_names)}"
        if comment is not None:
            file.write(f"--- @param {param_name} {param_type} {param_desc}\n")

        parameter_names.append(param_name)

    formatted_parameters = ", ".join(parameter_names)

    if calls:
        file.write(f"function {name}({formatted_parameters})\n")
        if formatted_parameters:
            formatted_parameters = f", {formatted_parameters}"
        file.write(f"    return Citizen.Invoke({nhash}{formatted_parameters})\n")
        file.write("end\n\n")
    else:
        file.write(f"function {name}({formatted_parameters}) end\n")


def write_extras(file: TextIO, n_format: str):
    if n_format != "cfxlua":
        return

    print("Writing extra functions")

    # dummy variables

    file.write("source = 0\n")
    file.write("Citizen = {}\n")

    # fxmanifest.lua declarations

    write_lua_function(file, "fx_version", "0x0", [
        {
            "name": "version",
            "type": "string",
            "description": "The manifest version. This needs to be adamant, bodacious or cerulean."
        }
    ], False, "Sets a specific fxmanifest version.")
    write_lua_function(file, "game", "0x0", [
        {
            "name": "game",
            "type": "string",
            "description": "The supported game. This needs to be common, gta4, gta5 or rdr3."
        }
    ], False, "Sets the game that this resource supports.")
    write_lua_function(file, "games", "0x0", [
        {
            "name": "games",
            "type": "table",
            "description": "The supported game(s). This needs to be common, gta4, gta5 or rdr3."
        }
    ], False, "Sets the multiple games that this resource supports.")
    write_lua_function(file, "client_script", "0x0", [
        {
            "name": "script",
            "type": "string",
            "description": "The script to load in the client."
        }
    ], False, "Sets a specific script to be loaded in the client.")
    write_lua_function(file, "client_scripts", "0x0", [
        {
            "name": "scripts",
            "type": "table",
            "description": "The scripts to load in the client."
        }
    ], False, "Sets the specific scripts to be loaded in the client.")
    write_lua_function(file, "server_script", "0x0", [
        {
            "name": "script",
            "type": "string",
            "description": "The script to load in the server."
        }
    ], False, "Sets a specific script to be loaded in the server.")
    write_lua_function(file, "server_scripts", "0x0", [
        {
            "name": "scripts",
            "type": "table",
            "description": "The scripts to load in the server."
        }
    ], False, "Sets the specific scripts to be loaded in the server.")

    # actual functions

    write_lua_function(file, "TriggerServerEvent", "0x0", [
        {
            "name": "name",
            "type": "string",
            "description": "The name of the event to trigger."
        },
        {
            "name": "...",
            "type": "any",
            "description": "The data to send to the server event."
        }
    ], False, "Triggers a new networked server event.")
    write_lua_function(file, "TriggerClientEvent", "0x0", [
        {
            "name": "name",
            "type": "string",
            "description": "The name of the event to trigger."
        },
        {
            "name": "playerId",
            "type": "number",
            "description": "The ID of the client to trigger. Setting this to -1 triggers every client."
        },
        {
            "name": "...",
            "type": "any",
            "description": "The data to send to the client event."
        }
    ], False, "Triggers a new networked client event.")
    write_lua_function(file, "RegisterNetEvent", "0x0", [
        {
            "name": "name",
            "type": "string",
            "description": "The name of the event to be registered."
        },
        {
            "name": "cb",
            "type": "function",
            "description": "The callback to trigger when the event is called."
        }
    ], False, "Registers an event as a network event.")
    write_lua_function(file, "GetPlayers", "0x0", [], False, "Gets a table with all of the active player IDs.")
    write_lua_function(file, "Citizen.CreateThread", "0x0", [
        {
            "name": "func",
            "type": "function",
            "description": "The function to use to create a thread"
        }
    ], False, "Creates a new scope for code execution, each thread is a coroutine which will be executed "
              "in a semi-consistent order.")


def write_namespace(file: TextIO, n_format: str, caller: bool, namespace: str, natives: dict, comments: bool):
    print(f"Writing native namespace {namespace}")

    if comments:
        if n_format == "shvdn" or n_format == "cfxmono":
            file.write(f"        // {namespace}\n")
        elif n_format == "cfxlua":
            file.write(f"-- {namespace}\n\n")

    for nhash, data in natives.items():
        name = data["name"]
        comment = data.get("comment", "") or data.get("description", "") if comments else None

        if n_format == "shvdn" or n_format == "cfxmono":
            write_cs_function(file, name, nhash, comment)
        elif n_format == "cfxlua":
            write_lua_function(file, format_lua_name(name), nhash, data["params"], caller, comment)


def write_natives(path: str, n_format: str, lists: list[str], should_call: bool, comments: bool,
                  no_extras: bool):
    path = Path(path).absolute()

    print(f"Starting fetching of natives to {path} in format {n_format}")

    natives = fetch_natives(lists)

    if natives is None:
        return 1

    path.parent.mkdir(exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        write_header(file, n_format)

        for game, namespaces in natives.items():
            for namespace, ns_natives in namespaces.items():
                write_namespace(file, n_format, should_call, namespace, ns_natives, comments)

        if not no_extras:
            write_extras(file, n_format)

        write_footer(file, n_format)
