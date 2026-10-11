"""Generate an ER diagram directly from the SQLAlchemy model metadata."""

from pathlib import Path
from graphviz import Digraph
from models import db


def generate_diagram():
    diagram = Digraph("StarWars", format="png")
    diagram.attr(rankdir="LR")
    diagram.attr("node", shape="record")

    for table in db.metadata.sorted_tables:
        fields = []
        for column in table.columns:
            markers = []
            if column.primary_key:
                markers.append("PK")
            if column.foreign_keys:
                markers.append("FK")
            prefix = f"{' / '.join(markers)} " if markers else ""
            fields.append(f"{prefix}{column.name}: {column.type}")
        label = "{" + table.name + "|" + "\\l".join(fields) + "\\l}"
        diagram.node(table.name, label=label)

    for table in db.metadata.sorted_tables:
        for foreign_key in table.foreign_keys:
            diagram.edge(
                table.name,
                foreign_key.column.table.name,
                label=foreign_key.parent.name,
            )

    destination = Path(__file__).resolve().parent.parent / "diagram"
    diagram.render(filename=str(destination), cleanup=True)
    print(f"Diagram generated: {destination}.png")


if __name__ == "__main__":
    generate_diagram()
