import React from 'react';

class StartNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                intro_text: props.intro_text ? props.intro_text : "",
            },
        }
        this.updateIntroText = this.updateIntroText.bind(this);
    }

    updateIntroText(e){
        let data = this.state.data;
        data.intro_text = e.target.value
        this.props.updateNodeData(data);
        
    }

    render(){
        return (
            <div>
                <h3 className="text-light">Start Node</h3>
                

                <h5 className='text-light'>Intro message (optional)</h5>
                
                 <textarea
                    className="form-control" 
                    rows="3"

                    value={this.props.intro_text}
                    onChange={this.updateIntroText}
                ></textarea>
                <hr></hr>
                
            </div>
        )
    }


}

export default StartNodeEditor;