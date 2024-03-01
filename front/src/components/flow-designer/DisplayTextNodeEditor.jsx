import React from 'react';

class DisplayTextNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                message_template: props.message_template ? props.message_template : "",
            },
        }
        this.updateVariable = this.updateVariable.bind(this);
    }

    updateVariable(e){
        let data = this.state.data;
        data.message_template = e.target.value
        this.props.updateNodeData(data);
        
    }

    

    render(){
        return (
            <div>
                <h3 className="text-light">Display Text Editor</h3>
                

                <h5 className='text-light'>Text</h5>
                <textarea
                    className="form-control" 
                    value={this.props.message_template}
                    onChange={this.updateVariable}
                ></textarea>
                <hr></hr>
                
            </div>
        )
    }


}

export default DisplayTextNodeEditor;