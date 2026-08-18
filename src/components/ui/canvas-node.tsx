"use client";

import { useState, useRef, useEffect, useCallback, memo } from "react";
import { Handle, Position } from "@xyflow/react";
import { getGroupColor, type VisualizationSource } from "@/lib/canvas-types";
import { cn } from "@/lib/utils";
import { BookOpen, ExternalLink, Sparkles, X } from "lucide-react";

interface SourcePopoverProps {
  sources: VisualizationSource[];
  nodeLabel: string;
  onClose: () => void;
  anchorRect: DOMRect | null;
}

export function SourcePopover({ sources, nodeLabel, onClose, anchorRect }: SourcePopoverProps) {
  const popoverRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  if (!sources.length || !anchorRect) return null;

  const left = Math.min(Math.max(16, anchorRect.right + 12), window.innerWidth - 320);
  const top = Math.min(Math.max(16, anchorRect.top - 20), window.innerHeight - 360);

  return (
    <div
      ref={popoverRef}
      className="source-popover"
      style={{
        position: "fixed",
        left: `${left}px`,
        top: `${top}px`,
        zIndex: 9999,
      }}
    >
      <div className="flex items-center justify-between border-b border-white/10 pb-2 mb-2.5">
        <div className="flex items-center gap-1.5">
          <BookOpen className="h-3.5 w-3.5 text-cyan-400" />
          <span className="text-[11px] font-semibold tracking-wider uppercase text-zinc-300">
            Grounding &bull; {nodeLabel}
          </span>
        </div>
        <button
          type="button"
          onClick={onClose}
          className="text-zinc-500 hover:text-zinc-300 p-0.5 rounded transition-colors"
        >
          <X className="h-3 w-3" />
        </button>
      </div>

      <ul className="source-popover-list max-h-60 overflow-y-auto pr-1">
        {sources.map((src, i) => (
          <li key={`${src.source_id}-${i}`} className="source-popover-item">
            <div className="source-popover-header">
              <span className="source-popover-title">{src.title}</span>
              {src.section && (
                <span className="rounded bg-white/5 px-1.5 py-0.5 text-[9px] text-zinc-400">
                  {src.section}
                </span>
              )}
            </div>
            {src.excerpt && (
              <p className="source-popover-excerpt">&ldquo;{src.excerpt}&rdquo;</p>
            )}
            {src.url && (
              <a
                href={src.url}
                target="_blank"
                rel="noreferrer"
                className="mt-2 inline-flex items-center gap-1 text-[10px] text-cyan-400 hover:underline"
              >
                <span>View Source</span>
                <ExternalLink className="h-2.5 w-2.5" />
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

// Interactive Custom React Flow Node

export interface CanvasNodeData {
  label: string;
  group: string;
  description?: string;
  sources: VisualizationSource[];
  animationDelay?: number;
  isNew?: boolean;
}

function CanvasNodeComponentImpl({
  data,
  selected,
}: {
  data: CanvasNodeData;
  selected?: boolean;
}) {
  const [showSources, setShowSources] = useState(false);
  const [anchorRect, setAnchorRect] = useState<DOMRect | null>(null);
  const nodeRef = useRef<HTMLDivElement>(null);
  const colors = getGroupColor(data.group);

  const handleSourceClick = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      if (data.sources.length > 0 && nodeRef.current) {
        setAnchorRect(nodeRef.current.getBoundingClientRect());
        setShowSources((prev) => !prev);
      }
    },
    [data.sources],
  );

  const delay = data.animationDelay ?? 0;

  return (
    <div
      ref={nodeRef}
      className={cn(
        "canvas-node group",
        selected && "canvas-node--selected",
        data.sources.length > 0 && "canvas-node--has-sources",
      )}
      style={{
        borderColor: selected ? "rgba(34, 211, 238, 0.7)" : colors.border,
        backgroundColor: colors.bg,
        animationDelay: `${delay}ms`,
      }}
    >
      {/* Target connection handles positioned at top and left of node */}
      <Handle
        type="target"
        position={Position.Top}
        id="top"
        className="canvas-handle"
      />
      <Handle
        type="target"
        position={Position.Left}
        id="left"
        className="canvas-handle"
      />

      {/* Glow ambient background aura */}
      <div
        className="canvas-node-glow"
        style={{
          background: `radial-gradient(circle at center, ${colors.border} 0%, transparent 70%)`,
        }}
      />

      {/* Group tag */}
      <div className="flex items-center justify-between w-full mb-1">
        <span
          className="canvas-node-group-tag"
          style={{ color: colors.text, borderColor: colors.border }}
        >
          {data.group.toUpperCase()}
        </span>

        {data.sources.length > 0 && (
          <button
            type="button"
            onClick={handleSourceClick}
            title={`${data.sources.length} verified source(s). Click to view.`}
            className="canvas-node-citation-badge"
            style={{
              borderColor: colors.border,
              color: colors.text,
            }}
          >
            <Sparkles className="h-2.5 w-2.5 text-cyan-400" />
            <span>{data.sources.length}</span>
          </button>
        )}
      </div>

      {/* Node Main Content */}
      <div className="w-full flex flex-col items-center text-center">
        <span className="canvas-node-label" style={{ color: colors.text }}>
          {data.label}
        </span>
        {data.description && (
          <span className="canvas-node-desc">{data.description}</span>
        )}
      </div>

      {/* Source connection handles positioned at bottom and right of node */}
      <Handle
        type="source"
        position={Position.Right}
        id="right"
        className="canvas-handle"
      />
      <Handle
        type="source"
        position={Position.Bottom}
        id="bottom"
        className="canvas-handle"
      />

      {showSources && (
        <SourcePopover
          sources={data.sources}
          nodeLabel={data.label}
          onClose={() => setShowSources(false)}
          anchorRect={anchorRect}
        />
      )}
    </div>
  );
}

export const CanvasNodeComponent = memo(CanvasNodeComponentImpl);
