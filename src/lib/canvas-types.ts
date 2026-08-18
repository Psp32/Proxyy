// Canvas visualization types — shared between the data channel and renderer

export interface VisualizationSource {
  source_id: string;
  title: string;
  section?: string;
  excerpt?: string;
  url?: string;
}

export interface VisualizationNode {
  id: string;
  label: string;
  group: string;
  description?: string;
  sources: VisualizationSource[];
}

export interface VisualizationEdge {
  from: string;
  to: string;
  label?: string;
}

export type VisualizationType =
  | "architecture"
  | "comparison"
  | "timeline"
  | "workflow"
  | "skill_graph"
  | "clear";

export interface VisualizationData {
  type: VisualizationType;
  title: string;
  nodes: VisualizationNode[];
  edges: VisualizationEdge[];
  metadata?: {
    query?: string;
    total_sources?: number;
  };
}

// Group → color mapping for node theming (dark-mode palette)

export const GROUP_COLORS: Record<string, { bg: string; border: string; text: string }> = {
  frontend: {
    bg: "rgba(34, 211, 238, 0.06)",
    border: "rgba(34, 211, 238, 0.25)",
    text: "rgb(165, 243, 252)",
  },
  backend: {
    bg: "rgba(167, 139, 250, 0.06)",
    border: "rgba(167, 139, 250, 0.25)",
    text: "rgb(196, 181, 253)",
  },
  data: {
    bg: "rgba(251, 191, 36, 0.06)",
    border: "rgba(251, 191, 36, 0.25)",
    text: "rgb(253, 224, 71)",
  },
  ai: {
    bg: "rgba(52, 211, 153, 0.06)",
    border: "rgba(52, 211, 153, 0.25)",
    text: "rgb(167, 243, 208)",
  },
  realtime: {
    bg: "rgba(244, 114, 182, 0.06)",
    border: "rgba(244, 114, 182, 0.25)",
    text: "rgb(251, 207, 232)",
  },
  infrastructure: {
    bg: "rgba(148, 163, 184, 0.06)",
    border: "rgba(148, 163, 184, 0.25)",
    text: "rgb(203, 213, 225)",
  },
  // Comparison-specific groups
  left: {
    bg: "rgba(34, 211, 238, 0.06)",
    border: "rgba(34, 211, 238, 0.25)",
    text: "rgb(165, 243, 252)",
  },
  right: {
    bg: "rgba(167, 139, 250, 0.06)",
    border: "rgba(167, 139, 250, 0.25)",
    text: "rgb(196, 181, 253)",
  },
  shared: {
    bg: "rgba(251, 191, 36, 0.06)",
    border: "rgba(251, 191, 36, 0.25)",
    text: "rgb(253, 224, 71)",
  },
  // Timeline groups
  past: {
    bg: "rgba(148, 163, 184, 0.06)",
    border: "rgba(148, 163, 184, 0.25)",
    text: "rgb(203, 213, 225)",
  },
  present: {
    bg: "rgba(52, 211, 153, 0.06)",
    border: "rgba(52, 211, 153, 0.25)",
    text: "rgb(167, 243, 208)",
  },
  // Skill graph groups
  language: {
    bg: "rgba(34, 211, 238, 0.06)",
    border: "rgba(34, 211, 238, 0.25)",
    text: "rgb(165, 243, 252)",
  },
  framework: {
    bg: "rgba(167, 139, 250, 0.06)",
    border: "rgba(167, 139, 250, 0.25)",
    text: "rgb(196, 181, 253)",
  },
  tool: {
    bg: "rgba(251, 191, 36, 0.06)",
    border: "rgba(251, 191, 36, 0.25)",
    text: "rgb(253, 224, 71)",
  },
  concept: {
    bg: "rgba(244, 114, 182, 0.06)",
    border: "rgba(244, 114, 182, 0.25)",
    text: "rgb(251, 207, 232)",
  },
  // Default fallback
  default: {
    bg: "rgba(255, 255, 255, 0.04)",
    border: "rgba(255, 255, 255, 0.10)",
    text: "rgb(228, 228, 231)",
  },
};

export function getGroupColor(group: string) {
  return GROUP_COLORS[group] ?? GROUP_COLORS.default;
}
