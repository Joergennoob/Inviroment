"use client";

type GraphNode = { id: string; name: string; column: number };
type GraphEdge = { id: string; from: string; to: string; label: string };

const COLUMN: Record<string, number> = {
  lobbyist: 0,
  lobbying_firm: 1,
  organization: 2,
  bill: 3,
  problem: 3,
  politician: 4,
  lawmaker: 4,
};

export default function MiniGraph({
  nodes,
  edges,
  activeId,
  onPick,
}: {
  nodes: { id: string; name: string; type: string }[];
  edges: GraphEdge[];
  activeId: string;
  onPick: (id: string) => void;
}) {
  const placed: GraphNode[] = nodes.slice(0, 18).map((node) => ({
    id: node.id,
    name: node.name,
    column: COLUMN[node.type] ?? 2,
  }));
  const byColumn = [0, 1, 2, 3, 4].map((column) => placed.filter((node) => node.column === column));
  const pos = new Map<string, { x: number; y: number }>();
  byColumn.forEach((group, column) => {
    group.forEach((node, index) => {
      pos.set(node.id, { x: 70 + column * 150, y: 36 + index * 54 });
    });
  });
  const height = Math.max(180, ...byColumn.map((group) => 50 + group.length * 54));

  return (
    <div className="graphwrap">
      <svg viewBox={`0 0 760 ${height}`} role="img" aria-label="Koblinger rundt det du valgte">
        {edges.slice(0, 24).map((edge) => {
          const a = pos.get(edge.from);
          const b = pos.get(edge.to);
          if (!a || !b) return null;
          const midX = (a.x + b.x) / 2;
          const midY = (a.y + b.y) / 2;
          return (
            <g key={edge.id}>
              <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} className="graphline" />
              {edge.label ? (
                <text x={midX} y={midY - 4} textAnchor="middle" className="edgelabel">
                  {edge.label}
                </text>
              ) : null}
            </g>
          );
        })}
        {placed.map((node) => {
          const point = pos.get(node.id);
          if (!point) return null;
          const on = node.id === activeId;
          return (
            <g key={node.id} onClick={() => onPick(node.id)} className="graphnode">
              <rect x={point.x - 58} y={point.y - 16} width="116" height="32" rx="8" className={on ? "on" : ""} />
              <text x={point.x} y={point.y + 4} textAnchor="middle">
                {node.name.length > 16 ? `${node.name.slice(0, 15)}…` : node.name}
              </text>
            </g>
          );
        })}
      </svg>
      <p className="note">Klikk en boks. Linjene er registrering, pengegave eller stemme. Det er ikke et bevis på at pengene styrte stemmen.</p>
    </div>
  );
}
