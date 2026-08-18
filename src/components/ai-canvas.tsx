"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  type Node,
  type Edge,
  type NodeTypes,
  type Connection,
  Background,
  BackgroundVariant,
  useNodesState,
  useEdgesState,
  addEdge,
  Position,
  MarkerType,
} from "@xyflow/react";
import dagre from "@dagrejs/dagre";
import "@xyflow/react/dist/style.css";

import { CanvasNodeComponent } from "@/components/ui/canvas-node";
import type {
  VisualizationData,
  VisualizationNode,
  VisualizationEdge,
} from "@/lib/canvas-types";
import { cn } from "@/lib/utils";
import {
  X,
  Maximize2,
  RotateCcw,
  Plus,
  Sparkles,
  Layers,
  Move,
} from "lucide-react";

// Dagre Auto-Layout Helper

const NODE_WIDTH = 210;
const NODE_HEIGHT = 80;

type LayoutDirection = "TB" | "LR";

function getLayoutDirection(type: string): LayoutDirection {
  return type === "timeline" ? "LR" : "TB";
}

function computeLayout(
  vizNodes: VisualizationNode[],
  vizEdges: VisualizationEdge[],
  direction: LayoutDirection,
): { nodes: Node[]; edges: Edge[] } {
  const g = new dagre.graphlib.Graph();
  g.setDefaultEdgeLabel(() => ({}));
  g.setGraph({
    rankdir: direction,
    nodesep: 50,
    ranksep: 80,
    marginx: 40,
    marginy: 40,
  });

  for (const vn of vizNodes) {
    g.setNode(vn.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  }

  for (const ve of vizEdges) {
    g.setEdge(ve.from, ve.to);
  }

  dagre.layout(g);

  const isHorizontal = direction === "LR";
  const nodes: Node[] = vizNodes.map((vn, index) => {
    const pos = g.node(vn.id) || { x: 100 * index, y: 100 * index };
    return {
      id: vn.id,
      type: "canvasNode",
      position: {
        x: pos.x - NODE_WIDTH / 2,
        y: pos.y - NODE_HEIGHT / 2,
      },
      data: {
        label: vn.label,
        group: vn.group || "default",
        description: vn.description,
        sources: vn.sources || [],
        animationDelay: index * 80,
      },
      sourcePosition: isHorizontal ? Position.Right : Position.Bottom,
      targetPosition: isHorizontal ? Position.Left : Position.Top,
    };
  });

  const edges: Edge[] = vizEdges.map((ve, index) => ({
    id: `e-${ve.from}-${ve.to}-${index}`,
    source: ve.from,
    target: ve.to,
    sourceHandle: isHorizontal ? "right" : "bottom",
    targetHandle: isHorizontal ? "left" : "top",
    label: ve.label,
    animated: true,
    type: "smoothstep",
    style: {
      stroke: "#22d3ee",
      strokeWidth: 2,
      opacity: 0.9,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      width: 14,
      height: 14,
      color: "#22d3ee",
    },
    labelStyle: {
      fill: "rgba(244, 244, 245, 0.75)",
      fontSize: 10,
      fontWeight: 600,
      fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
    },
    labelBgStyle: {
      fill: "#0a0a0c",
      fillOpacity: 0.85,
      rx: 4,
      ry: 4,
    },
  }));

  return { nodes, edges };
}

// Node Type Registry

const nodeTypes: NodeTypes = {
  canvasNode: CanvasNodeComponent,
};

// Interactive AI Canvas Component

interface AICanvasProps {
  data: VisualizationData;
  onDismiss: () => void;
}

export function AICanvas({ data, onDismiss }: AICanvasProps) {
  const direction = getLayoutDirection(data.type);

  const initialLayout = useMemo(
    () => computeLayout(data.nodes, data.edges, direction),
    [data.nodes, data.edges, direction],
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialLayout.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialLayout.edges);
  const [visible, setVisible] = useState(false);
  const [reactFlowInstance, setReactFlowInstance] = useState<any>(null);
  const [isDrawing, setIsDrawing] = useState(true);

  // Sync state whenever input data changes
  useEffect(() => {
    const layout = computeLayout(data.nodes, data.edges, direction);
    setNodes(layout.nodes);
    setEdges(layout.edges);
    setIsDrawing(true);
    const timer = setTimeout(() => setIsDrawing(false), 1200);
    return () => clearTimeout(timer);
  }, [data, direction, setNodes, setEdges]);

  // Trigger smooth enter animation
  useEffect(() => {
    const id = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(id);
  }, []);

  // Connect new edges interactively by dragging between handles
  const onConnect = useCallback(
    (params: Connection) => {
      setEdges((eds) =>
        addEdge(
          {
            ...params,
            animated: true,
            type: "smoothstep",
            style: {
              stroke: "#38bdf8",
              strokeWidth: 2,
            },
            markerEnd: {
              type: MarkerType.ArrowClosed,
              width: 14,
              height: 14,
              color: "#38bdf8",
            },
          },
          eds,
        ),
      );
    },
    [setEdges],
  );

  // Interactive Re-Layout / Organize Action
  const handleAutoLayout = useCallback(() => {
    const vizNodes = nodes.map((n) => ({
      id: n.id,
      label: (n.data as any).label,
      group: (n.data as any).group,
      description: (n.data as any).description,
      sources: (n.data as any).sources || [],
    }));
    const vizEdges = edges.map((e) => ({
      from: e.source,
      to: e.target,
      label: typeof e.label === "string" ? e.label : undefined,
    }));
    const layout = computeLayout(vizNodes, vizEdges, direction);
    setNodes(layout.nodes);
    setEdges(layout.edges);
    setTimeout(() => {
      reactFlowInstance?.fitView({ duration: 400, padding: 0.25 });
    }, 50);
  }, [nodes, edges, direction, setNodes, setEdges, reactFlowInstance]);

  // Interactive Add Node Action
  const handleAddNode = useCallback(() => {
    const id = `node-${Date.now().toString().slice(-4)}`;
    const newNode: Node = {
      id,
      type: "canvasNode",
      position: {
        x: (Math.random() - 0.5) * 120 + 200,
        y: (Math.random() - 0.5) * 100 + 150,
      },
      data: {
        label: "Custom Node",
        group: "concept",
        description: "User attached note",
        sources: [],
        animationDelay: 0,
      },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  const handleFitView = useCallback(() => {
    reactFlowInstance?.fitView({ duration: 400, padding: 0.25 });
  }, [reactFlowInstance]);

  const handleDismiss = useCallback(() => {
    setVisible(false);
    setTimeout(onDismiss, 300);
  }, [onDismiss]);

  const sourceCount = data.metadata?.total_sources ?? 0;

  return (
    <div className={cn("ai-canvas-container", visible && "ai-canvas-container--visible")}>
      {/* Canvas Header Bar */}
      <div className="ai-canvas-header">
        <div className="ai-canvas-header-left">
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
            </span>
            <h3 className="ai-canvas-title">{data.title}</h3>
          </div>

          <div className="flex items-center gap-1.5">
            <span className="ai-canvas-type-badge">
              {data.type.replace("_", " ")}
            </span>
            {sourceCount > 0 && (
              <span className="ai-canvas-source-count flex items-center gap-1">
                <Sparkles className="h-2.5 w-2.5 text-cyan-400" />
                {sourceCount} verified source{sourceCount !== 1 ? "s" : ""}
              </span>
            )}
          </div>
        </div>

        {/* Toolbar controls */}
        <div className="flex items-center gap-1">
          <button
            type="button"
            onClick={handleAddNode}
            title="Add Custom Node"
            className="ai-canvas-tool-btn"
          >
            <Plus className="h-3.5 w-3.5" />
            <span className="hidden sm:inline text-[10px]">Add Node</span>
          </button>

          <button
            type="button"
            onClick={handleAutoLayout}
            title="Organize / Auto Layout"
            className="ai-canvas-tool-btn"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span className="hidden sm:inline text-[10px]">Re-align</span>
          </button>

          <button
            type="button"
            onClick={handleFitView}
            title="Fit View"
            className="ai-canvas-tool-btn"
          >
            <Maximize2 className="h-3.5 w-3.5" />
          </button>

          <button
            type="button"
            onClick={handleDismiss}
            title="Dismiss visualization"
            className="ai-canvas-dismiss ml-1"
          >
            <X className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      {/* Interactive React Flow Canvas */}
      <div className="ai-canvas-flow relative">
        {isDrawing && (
          <div className="absolute top-3 left-4 z-10 pointer-events-none flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-950/60 border border-cyan-500/30 text-[10px] text-cyan-300 backdrop-blur-md animate-pulse">
            <Move className="h-2.5 w-2.5 animate-spin" />
            <span>Interactive diagram ready &bull; Drag nodes or wire ports</span>
          </div>
        )}

        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onInit={setReactFlowInstance}
          nodeTypes={nodeTypes}
          nodesDraggable={true}
          nodesConnectable={true}
          elementsSelectable={true}
          fitView
          fitViewOptions={{ padding: 0.25 }}
          minZoom={0.3}
          maxZoom={2}
          proOptions={{ hideAttribution: true }}
          defaultEdgeOptions={{
            animated: true,
            type: "smoothstep",
          }}
        >
          <Background
            variant={BackgroundVariant.Lines}
            color="rgba(255, 255, 255, 0.025)"
            gap={24}
            size={1}
          />
        </ReactFlow>
      </div>

      {/* Bottom Hint Bar */}
      <div className="ai-canvas-footer">
        <span className="text-[10px] text-zinc-500 flex items-center gap-1">
          <Layers className="h-3 w-3 text-zinc-600" />
          Drag nodes to reposition &bull; Pull port handles to connect &bull; Click badges for source citations
        </span>
      </div>
    </div>
  );
}
