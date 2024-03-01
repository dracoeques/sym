import React, { useState, useRef, useCallback } from 'react';
import ReactFlow, {
  ReactFlowProvider,
  addEdge,
  Panel,
  MiniMap,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
} from 'reactflow';
import 'reactflow/dist/style.css';

import DndSidebar from './DndSidebar1';

//import 'reactflow/dist/style.css';
import './DndFlow.css';

const initialNodes = [
  {
      "id": "dndnode_0",
      "data": {
          "label": "start"
      },
      "type": "start",
      "width": 54,
      "height": 40,
      "position": {
          "x": 209.73390891902923,
          "y": -25.748811590125115
      },
      "positionAbsolute": {
          "x": 209.73390891902923,
          "y": -25.748811590125115
      }
  }
]


import startNode from './startNode';
import promptNode from './promptNode';
import storageNode from './storageNode';
import textInputNode from './textInputNode';
import finishNode from './finishNode';
import continueNode from './continueNode';

const nodeTypes = {
    start: startNode,
    prompt: promptNode,
    storage: storageNode,
    textInput: textInputNode,
    finish: finishNode,
    continue: continueNode,
  };

//let id = 0;
//const getId = () => `dndnode_${id++}`;

const DnDFlow = (props) => {

  const getId = props.getId;
  const updateFlow = props.updateFlow;
  

  const initialNodes = props.network.nodes;
  const initialEdges = props.network.edges;
  
  const reactFlowWrapper = useRef(null);
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [reactFlowInstance, setReactFlowInstance] = useState(null);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), []);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event) => {
      event.preventDefault();

      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');

      // check if the dropped element is valid
      if (typeof type === 'undefined' || !type) {
        return;
      }

      const position = reactFlowInstance.project({
        x: event.clientX - reactFlowBounds.left,
        y: event.clientY - reactFlowBounds.top,
      });
      const newNode = {
        id: getId(),
        type,
        position,
        data: { label: `${type}` },
      };

      setNodes((nds) => nds.concat(newNode));

      //optionally update source flow
      //NOTE: this is disabled, since we don't currently have an undo
      //this means that refresh is our "undo"
      //let flow = reactFlowInstance.toObject();
      //flow.nodes = flow.nodes.concat(newNode)
      //updateFlow(flow);
      
    },
    [reactFlowInstance]
  );

  const minimapStyle = {
    height: 60,
    width: 60,
  };

  const saveCallback = props.onSave;
  const onSave = useCallback(() => {
    if (reactFlowInstance){
        const flow = reactFlowInstance.toObject();
        //console.log(flow);
        //console.log(saveCallback);
        saveCallback(flow);
    }
  })

  //console.log("dnd props", props);

  //todo: if a new flow, use defaultViewport={{x: 0, y:0, zoom:0.9}}
  //else: use fitView

  return (
    <div className="dndflow">
      <ReactFlowProvider>
      <DndSidebar />
        <div className="reactflow-wrapper" ref={reactFlowWrapper}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onInit={setReactFlowInstance}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onNodeClick={props.onNodeClick}
            nodeTypes={nodeTypes}
            //fitView
            defaultViewport={{x: 0, y:0, zoom:0.9}}
            // 
          >
            <MiniMap style={minimapStyle} zoomable pannable />
            <Controls />
            <Panel position="top-right">
                <button onClick={onSave}>save</button>
                {/* <button onClick={onRestore}>restore</button>
                <button onClick={onAdd}>add node</button> */}
            </Panel>
            <Background color="#aaa" gap={16} />
          </ReactFlow>
        </div>
        
      </ReactFlowProvider>
    </div>
  );
};

export default DnDFlow;