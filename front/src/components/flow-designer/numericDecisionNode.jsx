import React, { memo } from 'react';
import { Handle, Position } from 'reactflow';

export default memo(({ data, isConnectable }) => {
  return (
    <div style={{
        fontSize: 12,
        padding:10,
        backgroundColor: "#eeeeee",
        border: "1px solid #555",
        borderRadius: 1,
        textAlign: "center",
        width: 100,
        height: 50,
    }}>
      
      <Handle
        type="target"
        position={Position.Top}
        style={{  background: '#555' }}
        onConnect={(params) => console.log('handle onConnect', params)}
        isConnectable={isConnectable}
      ></Handle>
      <Handle
        type="source"
        id="next-a"
        position={Position.Bottom}
        style={{ background: '#555', left: 10 }}
        onConnect={(params) => console.log('handle onConnect', params)}
        isConnectable={isConnectable}
        
      >A</Handle>
      <Handle
        type="source"
        id="next-b"
        position={Position.Bottom}
        style={{ background: '#555', left: 90 }}
        onConnect={(params) => console.log('handle onConnect', params)}
        isConnectable={isConnectable}
      >B</Handle>
     
      
      <div>
         <strong>Numeric Decision</strong>
      </div>
      {/* <input className="nodrag" type="color" onChange={data.onChange} defaultValue={data.color} /> */}
      
      
    </div>
  );
});
