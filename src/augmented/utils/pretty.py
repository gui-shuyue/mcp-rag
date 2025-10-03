from dataclasses import dataclass, field
from typing import Self
from rich.panel import Panel
from rich.layout import Layout


from rich.console import RenderableType
from rich.rule import Rule
from rich.text import Text
from rich import print as rprint

def log_title(text: str | Text, rule_style="bright_black"):
    rprint(Rule(title=text, style=rule_style))


@dataclass
class APanel:
    title: str = "-"
    renderables: list[RenderableType] = field(default_factory=list)

    def with_content(
        self,
        renderable: RenderableType = "",
        print_now: bool = False,
    ) -> Self:
        if isinstance(renderable, str):
            renderable = Text(renderable)
        if renderable:
            self.renderables.append(renderable)
        if print_now:
            rprint(renderable)
        return self

    def print(self):
        root = Layout()
        root.split_column(*[Layout(renderable) for renderable in self.renderables])
        rprint(
            Panel.fit(
                root,
                title=self.title,
            )
        )

# Panel
# 用途: 创建带边框的面板容器
# 功能: 可以将文本或其他内容包装在一个带标题的矩形边框中
# 特点: 支持自定义边框样式、颜色、标题位置等

# rich.print
# 用途: Rich 库的增强版 print 函数
# 功能: 替代标准的 print() 函数，支持丰富的文本格式化
# 特点:
# 支持颜色、样式（粗体、斜体等）
# 支持表格、进度条等复杂组件
# 自动语法高亮
# 支持 Markdown 渲染

# RenderableType
# 用途: 类型提示接口
# 功能: 定义可以被 Rich 渲染的对象类型
# 包含: 字符串、Panel、Table、Progress 等所有可渲染的 Rich 组件