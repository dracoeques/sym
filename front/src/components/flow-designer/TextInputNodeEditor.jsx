import React from 'react';

class TextInputNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                question: props.question ? props.question : "",
                hint: props.hint ? props.hint : "",
                variable: props.variable ? props.variable: "",
            },
            
            
            
        }
        
        this.updateQuestion = this.updateQuestion.bind(this);
        this.updateHint = this.updateHint.bind(this);
        this.updateVariable = this.updateVariable.bind(this);
    }

    updateQuestion(e){

        let data = this.state.data;
        data.question = e.target.value
        this.props.updateNodeData(data);

        // this.setState({question:e.target.value}, () => {
        //     this.props.updateNodeData(this.state);
        // });
    }

    updateHint(e){
        let data = this.state.data;
        data.hint = e.target.value
        this.props.updateNodeData(data);
        
    }

    updateVariable(e){
        let data = this.state.data;
        data.variable = e.target.value
        this.props.updateNodeData(data);
    }

    render(){
        return (
            <div>
                <h3 className="text-light">Question Editor</h3>
                

                <h5 className='text-light'>Question</h5>
                <textarea
                    className="form-control" 
                    rows="3"

                    value={this.props.question}
                    onChange={this.updateQuestion}
                ></textarea>

                <h5 className='text-light'>Variable Name</h5>
                <textarea
                    className="form-control" 
                    rows="1"

                    value={this.props.variable}
                    onChange={this.updateVariable}
                ></textarea>
                
                <hr></hr>

               
                
            </div>
        )
    }


}

export default TextInputNodeEditor;