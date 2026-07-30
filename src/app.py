"""Microsoft Training Assistant 的命令行交互入口。"""

import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.agent.training_agent import create_training_agent


def main() -> None:
    console = Console()
    console.print(
        Panel.fit(
            "[bold cyan]Microsoft Training Assistant[/bold cyan]\n"
            "基于 Azure AI Foundry Agent Service 的微软培训助手\n"
            "输入问题开始对话，输入 [bold yellow]exit[/bold yellow] 或 [bold yellow]quit[/bold yellow] 退出。",
            title="欢迎使用",
        )
    )

    try:
        agent = create_training_agent()
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]初始化智能体失败：{exc}[/red]")
        sys.exit(1)

    thread_id = agent.create_thread()
    console.print(f"[dim]会话线程已创建：{thread_id}[/dim]\n")

    try:
        while True:
            user_input = console.input("[bold green]你：[/bold green] ")
            if not user_input.strip():
                continue
            if user_input.strip().lower() in {"exit", "quit", "退出"}:
                console.print("[dim]再见！[/dim]")
                break

            try:
                response = agent.send_message(thread_id, user_input)
                console.print(Markdown(f"**助手：** {response}"))
            except Exception as exc:  # noqa: BLE001
                console.print(f"[red]请求失败：{exc}[/red]")
    finally:
        agent.close()


if __name__ == "__main__":
    main()
