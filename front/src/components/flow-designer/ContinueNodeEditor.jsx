import React from 'react';

import ComboBox from '../ComboBox';

class ContinueNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                //prompt: props.prompt ? props.prompt : "",
                system: props.system ? props.system : "You are a helpful AI assistant",
                model: props.model ? props.model : "gpt-3.5-turbo",
            },
            
        }

        //this.updatePrompt = this.updatePrompt.bind(this);
        this.updateSystem = this.updateSystem.bind(this);
        this.updateModel = this.updateModel.bind(this);
    }

    updatePrompt(e){
        let data = this.state.data;
        data.prompt = e.target.value;
        this.props.updateNodeData(data);
    }

    updateSystem(e){
        let data = this.state.data;
        data.system = e.target.value;
        this.props.updateNodeData(data);
    }

    updateModel(x){
        let data = this.state.data;
        data.model = x.selectedOption.value;
        this.props.updateNodeData(data);
    }


    render(){
        console.log(this.props);

        const model_options = [
            {label:"gpt-3.5-turbo", value:"gpt-3.5-turbo"},
            {label:"gpt-4", value:"gpt-4"}
        ]
        let model = {label:"gpt-3.5-turbo", value:"gpt-3.5-turbo"};
        if (this.props.model){
            model = {label:this.props.model, value:this.props.model}
        }

        return (
            <div>
                <h3 className="text-light">Loop Editor</h3>
                

                
                <hr></hr>
                <h5 className='text-light'>System</h5>
                <textarea
                    className="form-control" 
                    
                    rows="3"
                    value={this.props.system ? this.props.system : "You are a helpful AI assistant"}
                    onChange={this.updateSystem}
                ></textarea>
                <hr></hr>
                <ComboBox 
                    options={model_options}
                    selectedOption={model}
                    updateValue={this.updateModel}
                />
            </div>
        )
    }


}

export default ContinueNodeEditor;