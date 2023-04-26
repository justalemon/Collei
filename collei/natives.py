import string
import sys
from pathlib import Path
from typing import TextIO

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


def write_native_namespace(file: TextIO, n_format: str, caller: bool, namespace: str, natives: dict):
    print(f"Writing native namespace {namespace}")

    if n_format == "shvdn" or n_format == "cfxmono":
        file.write(f"        // {namespace}\n")
    elif n_format == "cfxlua":
        file.write(f"-- {namespace}\n\n")

    for nhash, data in natives.items():
        name = data["name"]
        comment = data.get("comment", None)

        if n_format == "shvdn" or n_format == "cfxmono":
            if comment is not None:
                file.write(f"        /// <summary>\n")
                for line in comment.splitlines():
                    file.write(f"        /// {line}\n")
                file.write(f"        /// </summary>\n")

            file.write(f"        {name} = {nhash},\n")
        elif n_format == "cfxlua":
            parameter_names = []

            if comment is not None:
                for line in comment.splitlines():
                    file.write(f"--- {line}\n")

            for parameter in data["params"]:
                param_name = parameter["name"]
                param_desc = parameter.get("description", "")
                param_type = LUA_EQUIVALENTS.get(parameter["type"], None) or parameter["type"]

                if param_name in LUA_KEYWORDS:
                    param_name = f"_{param_name}"

                if param_name in parameter_names:
                    param_name = f"{param_name}_{len(parameter_names)}"

                file.write(f"--- @param {param_name} {param_type} {param_desc}\n")

                parameter_names.append(param_name)

            name = format_lua_name(name)
            parameters = ", ".join(parameter_names)

            if caller:
                file.write(f"function {name}({parameters})\n")
                if parameters:
                    parameters = f", {parameters}"
                file.write(f"    return Citizen.Invoke({nhash}{parameters})\n")
                file.write(f"end\n\n")
            else:
                file.write(f"function {name}({parameters}) end\n\n")


def write_natives(path: Path, n_format: str, should_call: bool, all_natives: dict[str, dict]):
    path.parent.mkdir(exist_ok=True)

    with open(path, "w", encoding="utf-8") as file:
        write_header(file, n_format)

        for game, namespaces in all_natives.items():
            for namespace, natives in namespaces.items():
                write_native_namespace(file, n_format, should_call, namespace, natives)

        write_footer(file, n_format)


def write_natives_to(path: str, n_format: str, lists: list[str], should_call: bool):
    path = Path(path).absolute()

    print(f"Starting fetching of natives to {path} in format {n_format}")

    natives = fetch_natives(lists)

    if natives is None:
        return 1

    write_natives(path, n_format, should_call, natives)
