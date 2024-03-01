import React from 'react';

import ComboBox from '../ComboBox';

class PromptNodeEditor extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            data:{
                id:props.id,
                prompt: props.prompt ? props.prompt : "",
                system: props.system ? props.system : "You are a helpful AI assistant",
                model: props.model ? props.model : "gpt-3.5-turbo",
                temperature: props.temperature ? props.temperature : 0.5,
                history: props.history ? props.history : true,
                display: props.display ? props.display : true,
            },
            
        }

        //since negation shouldn't be default we manually check for history
        if (props.history === false) {
            this.state.data.history = false;
        } 

        //same as above, if we don't want to display set that here
        if (props.display === false){
            this.state.data.display = false;
        }

        this.updatePrompt = this.updatePrompt.bind(this);
        this.updateSystem = this.updateSystem.bind(this);
        this.updateModel = this.updateModel.bind(this);
        this.updateTemperature = this.updateTemperature.bind(this);
        this.updateHistory = this.updateHistory.bind(this);
        this.updateDisplay = this.updateDisplay.bind(this);
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

    updateTemperature(e){
        const t = parseFloat(e.target.value);
        let data = this.state.data;
        data.temperature = t
        this.props.updateNodeData(data);
    }

    updateHistory(e){
        let checked = false;
        if (e.target.checked){
            checked = true;
        }
        let data = this.state.data;
        data.history = checked
        this.props.updateNodeData(data);
    }

    updateDisplay(e){
        let checked = false;
        if (e.target.checked){
            checked = true;
        }
        let data = this.state.data;
        data.display = checked
        this.props.updateNodeData(data);
    }


    render(){
        console.log(this.props);

        const model_options = [
            {label:"gpt-3.5-turbo", value:"gpt-3.5-turbo"},
            {label:"gpt-4", value:"gpt-4"},
            {label:"gpt-4-turbo-preview", value:"gpt-4-turbo-preview"},
            {label:"gpt-4-1106-preview", value:"gpt-4-1106-preview"},
            {label:"gpt-4-0613", value:"gpt-4-0613"},
            {label:"gpt-4-0125-preview", value:"gpt-4-0125-preview"},
            {label:"gpt-3.5-turbo-16k-0613", value:"gpt-3.5-turbo-16k-0613"},
            {label:"gpt-3.5-turbo-16k", value:"gpt-3.5-turbo-16k"},
            {label:"gpt-3.5-turbo-1106", value:"gpt-3.5-turbo-1106"},
            {label:"gpt-3.5-turbo-0613", value:"gpt-3.5-turbo-0613"},
            {label:"gpt-3.5-turbo-0125", value:"gpt-3.5-turbo-0125"},

        ]
        let model = {label:"gpt-3.5-turbo", value:"gpt-3.5-turbo"};
        if (this.props.model){
            model = {label:this.props.model, value:this.props.model}
        }

        //history summary
        let include_history = "Include previous message history"
        if (this.props.history === false){
            include_history = "Do not include previous message history"
        }

        //display summary
        let display = "Display output to user";
        if (this.props.display === false){
            display = "Do not display output to user";
        }

        return (
            <div>
                <h3 className="text-light">Prompt Editor</h3>
                

                <h5 className='text-light'>Prompt</h5>
                <textarea
                    className="form-control" 
                    rows="5"
                    value={this.props.prompt}
                    onChange={this.updatePrompt}
                ></textarea>
                <hr></hr>
                <h5 className='text-light'>System Prompt</h5>
                <textarea
                    className="form-control" 
                    
                    rows="3"
                    value={this.props.system ? this.props.system : "You are a helpful AI assistant"}
                    onChange={this.updateSystem}
                ></textarea>
                <hr></hr>
                <h5 className='text-light'>Model</h5>
                <ComboBox 
                    options={model_options}
                    selectedOption={model}
                    updateValue={this.updateModel}
                />
                <hr></hr>
                <h5 className='text-light'>Temperature</h5>
                <input 
                    onChange={this.updateTemperature}
                    value={this.props.temperature ? this.props.temperature : 0.5}
                
                    type="number" min="0.0" max="2.0" step="0.1" />
                <hr></hr>
                <h5 className='text-light'>Include chat history</h5>
                
                <div className="form-check form-switch"
                   
                >
                    <input 
                     style={{padding:10, backgroundColor: "#757575"}}
                        checked={this.props.history}
                        onChange={this.updateHistory}
                        defaultChecked
                        className="form-check-input" 
                        type="checkbox" 
                        id="flexSwitchCheckDefault" />
                    <span className='text-light'>{include_history}</span>
                </div>
                <hr></hr>
                <h5 className='text-light'>Display output</h5>
                
                <div className="form-check form-switch"
                   
                >
                    <input 
                     style={{padding:10, backgroundColor: "#757575"}}
                        checked={this.props.display}
                        onChange={this.updateDisplay}
                        defaultChecked
                        className="form-check-input" 
                        type="checkbox" 
                        id="flexSwitchCheckDefault" />
                    <span className='text-light'>{display}</span>
                </div>
            </div>
        )
    }


}

export default PromptNodeEditor;