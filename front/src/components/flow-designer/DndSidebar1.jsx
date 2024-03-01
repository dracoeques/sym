import React from 'react';

export default () => {
  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside style={{padding:10}}>
      <hr></hr>
      <div className="dndnode input text-light" onDragStart={(event) => onDragStart(event, 'start')} draggable>
        Start
      </div>
      <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'text_input')} draggable>
        Text Input
      </div>
      <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'prompt')} draggable>
        Prompt
      </div>
      <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'storage')} draggable>
        Storage
      </div>
      <div className="dndnode output text-light" onDragStart={(event) => onDragStart(event, 'finish')} draggable>
        Finish
      </div>
      {/* <div className="dndnode output text-light" onDragStart={(event) => onDragStart(event, 'continue')} draggable>
        Loop
      </div> */}
    </aside>
  );
};