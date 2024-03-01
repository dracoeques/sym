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
        id="next"
        position={Position.Bottom}
        style={{ background: '#555' }}
        onConnect={(params) => console.log('handle onConnect', params)}
        isConnectable={isConnectable}
      ></Handle>
     
      
      <div>
         <strong>Parse</strong>
      </div>
      {/* <input className="nodrag" type="color" onChange={data.onChange} defaultValue={data.color} /> */}
      
      
    </div>
  );
});
