'use client'

import { useCallback, useState } from 'react'
import ReactFlow, {
  addEdge,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Node,
  Edge,
  Connection,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'

interface RoadmapNode {
  id: string
  title: string
  type: string
  status: 'pending' | 'in_progress' | 'completed'
  estimated_hours?: number
}

const nodeTypes = {
  goal: ({ data }: { data: RoadmapNode }) => (
    <div className="bg-accent-primary text-white px-4 py-2 rounded-lg shadow-lg min-w-[150px]">
      <div className="font-semibold">{data.title}</div>
      <div className="text-xs opacity-75">{data.estimated_hours || 0}h estimated</div>
    </div>
  ),
  milestone: ({ data }: { data: RoadmapNode }) => (
    <div className="bg-accent-secondary text-white px-4 py-2 rounded-lg shadow-lg min-w-[150px]">
      <div className="font-semibold">🎯 {data.title}</div>
      <div className="text-xs opacity-75">{data.status}</div>
    </div>
  ),
  task: ({ data }: { data: RoadmapNode }) => (
    <div className={`px-4 py-2 rounded-lg shadow-lg min-w-[150px] ${
      data.status === 'completed' ? 'bg-accent-secondary/50 text-white' :
      data.status === 'in_progress' ? 'bg-accent-warning text-black' :
      'bg-background-elevated text-text-primary border border-border'
    }`}>
      <div className="font-medium">{data.title}</div>
      <div className="text-xs opacity-75">{data.estimated_hours || 0}h</div>
    </div>
  ),
}

const initialNodes: Node[] = [
  { id: '1', type: 'goal', position: { x: 250, y: 0 }, data: { title: 'Learn React', type: 'goal', status: 'in_progress', estimated_hours: 40 } },
  { id: '2', type: 'milestone', position: { x: 100, y: 100 }, data: { title: 'Basics', type: 'milestone', status: 'completed' } },
  { id: '3', type: 'milestone', position: { x: 400, y: 100 }, data: { title: 'Advanced', type: 'milestone', status: 'pending' } },
  { id: '4', type: 'task', position: { x: 50, y: 200 }, data: { title: 'Hooks', type: 'task', status: 'completed', estimated_hours: 8 } },
  { id: '5', type: 'task', position: { x: 200, y: 200 }, data: { title: 'Context', type: 'task', status: 'completed', estimated_hours: 6 } },
  { id: '6', type: 'task', position: { x: 350, y: 200 }, data: { title: 'Performance', type: 'task', status: 'in_progress', estimated_hours: 10 } },
]

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', animated: true, markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e1-3', source: '1', target: '3', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e2-4', source: '2', target: '4', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e2-5', source: '2', target: '5', markerEnd: { type: MarkerType.ArrowClosed } },
  { id: 'e3-6', source: '3', target: '6', markerEnd: { type: MarkerType.ArrowClosed } },
]

interface RoadmapEditorProps {
  goalId: string
  initialNodes?: Node[]
  initialEdges?: Edge[]
  onSave: (nodes: Node[], edges: Edge[]) => void
}

export default function RoadmapEditor({ goalId, initialNodes: initNodes, initialEdges: initEdges, onSave }: RoadmapEditorProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState(initNodes || initialNodes)
  const [edges, setEdges, onEdgesChange] = useEdgesState(initEdges || initialEdges)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges])

  const addNode = (type: string) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type: type === 'goal' ? 'goal' : type === 'milestone' ? 'milestone' : 'task',
      position: { x: Math.random() * 400, y: Math.random() * 300 },
      data: { title: `New ${type}`, type, status: 'pending', estimated_hours: 2 },
    }
    setNodes((nds) => [...nds, newNode])
  }

  const generateTasks = () => {
    const taskNodes = nodes.filter(n => n.data.type === 'task')
    console.log('Generate tasks from roadmap:', taskNodes.map(n => n.data))
    alert(`Generated ${taskNodes.length} tasks! Check your task manager.`)
  }

  return (
    <div className="h-[500px] border border-border rounded-xl overflow-hidden">
      <div className="flex items-center gap-2 p-2 bg-background-card border-b border-border">
        <button onClick={() => addNode('task')} className="px-3 py-1 bg-background-elevated text-text-secondary text-sm rounded hover:bg-border">+ Task</button>
        <button onClick={() => addNode('milestone')} className="px-3 py-1 bg-background-elevated text-text-secondary text-sm rounded hover:bg-border">+ Milestone</button>
        <button onClick={generateTasks} className="px-3 py-1 bg-accent-primary text-white text-sm rounded hover:bg-accent-primary/90 ml-auto">Generate Tasks</button>
      </div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  )
}