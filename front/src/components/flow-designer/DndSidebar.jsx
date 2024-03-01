import React from 'react';

export default () => {
  const onDragStart = (event, nodeType) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  return (
    <aside>
      <div className='' style={{padding:10}}>
        
        <hr></hr>
        <div className="dndnode input text-light" onDragStart={(event) => onDragStart(event, 'start')} draggable>
          Start
        </div>
        <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'question')} draggable>
          Question
        </div>
        <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'prompt')} draggable>
          Prompt
        </div>
        <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'variable')} draggable>
          Variable
        </div>
        <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'display_text')} draggable>
          Display Text
        </div>
        <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'personalize')} draggable>
          Personalize
        </div>
        <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'pdf')} draggable>
          PDF
        </div>
        {/* <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'parse')} draggable>
          Parse
        </div> */}
        <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'binary_numeric_decision')} draggable>
          Numeric Decision
        </div>
        
        <div className="dndnode text-light" onDragStart={(event) => onDragStart(event, 'loop')} draggable>
          Loop
        </div>
        <div className="dndnode output text-light" onDragStart={(event) => onDragStart(event, 'finish')} draggable>
          Finish
        </div>
      </div>
     
      
    </aside>
  );
};
