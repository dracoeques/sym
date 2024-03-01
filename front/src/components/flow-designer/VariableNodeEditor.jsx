import React from 'react';

class VariableNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                variable_name: props.variable_name ? props.variable_name : "",
            },
        }
        this.updateVariableName = this.updateVariableName.bind(this);
    }

    updateVariableName(e){
        let data = this.state.data;
        data.variable_name = e.target.value
        this.props.updateNodeData(data);
        
    }

    

    render(){
        return (
            <div>
                <h3 className="text-light">Variable Editor</h3>
                

                <h5 className='text-light'>Variable Name</h5>
                <input
                    className="form-control" 
                    value={this.props.variable_name}
                    onChange={this.updateVariableName}
                ></input>
                <hr></hr>
                
            </div>
        )
    }


}

export default VariableNodeEditor;