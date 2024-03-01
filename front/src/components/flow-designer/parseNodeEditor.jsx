import React from 'react';

class ParseNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                parse_character: props.parse_character ? props.parse_character : "-",
                variable_name: props.variable_name ? props.variable_name : "v",
            },
        }
        this.updateParseCharacter = this.updateParseCharacter.bind(this);
        this.updateVariableName = this.updateVariableName.bind(this);
    }

    updateParseCharacter(e){
        let data = this.state.data;
        data.parse_character = e.target.value
        this.props.updateNodeData(data);
        
    }

    updateVariableName(e){
        let data = this.state.data;
        data.variable_name = e.target.value
        this.props.updateVariableName(data);
        
    }

    render(){
        return (
            <div>
                <h3 className="text-light">Parse Node</h3>
                

                <h5 className='text-light'>Parse character</h5>
                
                 <input
                    className="form-control" 
                    

                    value={this.state.parse_character}
                    onChange={this.updateParseCharacter}
                />
                <hr></hr>

                <h5 className='text-light'>Variable Name</h5>
                
                 <input
                    className="form-control" 
                    

                    value={this.state.variable_name}
                    onChange={this.updateVariableName}
                />
                <p> Variables can be used as such</p>
                <p>{"{"}{this.state.variable_name}{"_1}"}</p>
                <p>{"{"}{this.state.variable_name}{"_2}"}</p>
                <p>{"{"}{this.state.variable_name}{"_3}"}</p>
                <p>{"..."}</p>
                <p>{"{"}{this.state.variable_name}{"_N}"}</p>
                <hr></hr>
                
            </div>
        )
    }


}

export default ParseNodeEditor;