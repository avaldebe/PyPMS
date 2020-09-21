from typer import echo, style, colors, Abort


def missing_optional_module(name: str, module: str):
    extras = {"paho-mqtt": "mqtt", "influxdb": "influxdb"}
    if module not in extras:  # pragma: no cover
        return
    package = style("pypms", fg=colors.GREEN, bold=True)
    name = style(name, fg=colors.GREEN, bold=True)
    extra = style(extras[module], fg=colors.RED, bold=True)
    module = style(module, fg=colors.RED, bold=True)
    pip = style("python3 -m pip instal --upgrade", fg=colors.GREEN)
    pipx = style("pipx inject", fg=colors.GREEN)
    echo(
        f"""
{name} provides additional functionality to {package}.
This functionality requires the {module} module, which is not installed.
You can install this additional dependency with
\t{pip} {package}[{extra}]
Or, if you installed {package} with pipx
\t{pipx} {package} {module}
"""
    )
    raise Abort()
