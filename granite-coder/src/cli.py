import click
import asyncio
from src.agent import GreedyAgent


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Granite Coder - Token-efficient coding agent using IBM Granite 4"""
    pass


@cli.command()
@click.option("--model", default="ibm/granite4", help="Model to use")
@click.option("--max-iterations", default=3, help="Max RLM iterations (RLM mode only)")
@click.option(
    "--mode",
    type=click.Choice(["direct", "rlm", "responses"]),
    default="direct",
    help="Agent mode",
)
def chat(model, max_iterations, mode):
    """Interactive chat mode"""
    click.echo(f"Granite Coder (using {model}, mode: {mode})")
    click.echo("Type 'exit' to quit, 'clear' to clear history\n")

    agent = GreedyAgent(model_name=model, max_iterations=max_iterations, mode=mode)

    while True:
        try:
            task = click.prompt("You", type=str, default="")
            if task.lower() in ("exit", "quit"):
                break
            if task.lower() == "clear":
                click.echo("\033[2J\033[H")
                continue
            if not task.strip():
                continue

            click.echo("Thinking...")
            result = agent.run(task, ".")
            click.echo(f"\n{result}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            click.echo(f"Error: {e}", err=True)

    click.echo("Goodbye!")


@cli.command()
@click.argument("task")
@click.option("--model", default="ibm/granite4", help="Model to use")
@click.option("--path", default=".", help="Codebase path")
@click.option("--max-iterations", default=3, help="Max RLM iterations (RLM mode only)")
@click.option(
    "--mode",
    type=click.Choice(["direct", "rlm", "responses"]),
    default="direct",
    help="Agent mode",
)
def solve(task, model, path, max_iterations, mode):
    """Solve a single task"""
    agent = GreedyAgent(model_name=model, max_iterations=max_iterations, mode=mode)
    click.echo(f"Granite Coder solving ({mode} mode): {task}\n")
    result = agent.run(task, path)
    click.echo(result)


@cli.command()
def mcp():
    """Start as MCP server (for programmatic access)"""
    from src.server import main

    asyncio.run(main())


@cli.command()
def status():
    """Check agent status"""
    import requests

    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=2)
        if r.ok:
            models = r.json().get("models", [])
            click.echo(f"Ollama: ONLINE ({len(models)} models)")
            granite = [m for m in models if "granite" in m["name"].lower()]
            if granite:
                click.echo(f"Granite: AVAILABLE ({granite[0]['name']})")
            else:
                click.echo("Granite: NOT FOUND")
        else:
            click.echo("Ollama: ERROR")
    except Exception:
        click.echo("Ollama: NOT RUNNING")


def main():
    cli()


if __name__ == "__main__":
    main()
