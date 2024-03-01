import React, { useRef, useState, useEffect } from 'react';


function ResizableTextarea({ onSubmit }) {
    const [text, setText] = useState('');
    const textareaRef = useRef(null);

    const handleTextChange = (e) => {
        setText(e.target.value);
        adjustHeight();
    }

    const adjustHeight = () => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    }

    const handleSubmit = () => {
        if(onSubmit) onSubmit(text);
    }

    useEffect(() => {
        adjustHeight();
    }, []);

    return (
        <div className="textarea-container">
            <textarea 
                value={text} 
                onChange={handleTextChange} 
                ref={textareaRef}
                className="resizable-textarea"

                placeholder="Type here..." 
                style={{ 
                    
                    
                    
                    overflowY: 'hidden', 
                    resize: 'none',
                    color: "#a0a0a0",
                    backgroundColor: "#fff",
                    outline: "1px solid #ffffff",                        
                    fontSize: "16px",
                
                }}
            />

            <button className="btn btn-secondary" type="button" id="button-addon2"
                                                
                                                onClick={handleSubmit}
                                                style={{
                                                    padding: 0,
                                                }}
                                            ><img 
                                            src="https://uploads-ssl.webflow.com/64ee39d44b81a0ec6c03c3ba/64fb5f064f65e4372c4fb7ad_Screenshot%202023-09-08%20at%2010.50.21%20AM.png" 
                                            loading="lazy" 
                                            alt="" 
                                            style={{
                                                height:59,
                                                borderLeft: "1px solid #fefefe ",
                                            }}
                                            class="image-62"/></button>
        </div>
    );
}


export default ResizableTextarea;