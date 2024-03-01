import React from 'react';

import ComboBox from './ComboBox';
import { withRouter } from './utils';

import Api from './api.js';

const defaultPrompt = {
    id:1,
    text:"", //Summarize the {art_movement} art movement and its impact on art and culture
    system:"", //You are a helpful AI assistant
    variables:{
        art_movement:{
            id:1,
            selectedOption:null,
            options:[
                { 
                    id:1,
                    "value":"Renaissance", 
                    "label":"Renaissance",
                    "variableKey":"art_movement",
                },
                { 
                    id:2,
                    "value":"Baroque", 
                    "label":"Baroque",
                    "variableKey":"art_movement",
                },
                    // "Baroque",
                    // "Romanticism",
                    // "Impressionism",
                    // "Post-Impressionism",
                    // "Cubism",
                    // "Expressionism",
                    // "Dada",
                    // "Surrealism",
                    // "Abstract Expressionism"
            ]
        }
    }
}

const promptLibs = [defaultPrompt];


class PromptTemplate extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            api:new Api(),
            prompt: props.prompt ? props.prompt : defaultPrompt,


            loaded:false,
        }

        this.updatePrompt = this.updatePrompt.bind(this);
        this.updateSystem = this.updateSystem.bind(this);
        this.updatePlaceholder = this.updatePlaceholder.bind(this);
        this.runPrompt = this.runPrompt.bind(this);
    }

    componentDidMount(){
        const routerParams = this.props.params;
        
        
        if (routerParams.promptLibId){
            const libId = parseInt(routerParams.promptLibId);
            this.onLoad(libId);
        } else if (this.props.promptLibId) {
            const libId = parseInt(this.props.promptLibId);
            this.onLoad(libId);
        } else {
            this.setState({loaded:true})
        }
        //console.log(this.state.prompt);


    }

    async onLoad(promptLibId){
        console.log("onLoad");
        try {
            const data = await this.state.api.loadPromptLib(promptLibId);
            console.log('loadPromptLib:', data);
            //window.location.href = "/";

            let newState = {
                loaded:true,
                prompt:data,
                promptLibLoaded:true,
            }

            this.setState(newState)

            
        } catch (error) {
            console.error('Error loadPromptFlow:', error);
            this.setState({"error":error.response.data.Message});
        }
    }

    runPrompt(){
        console.log("runPrompt");
        const builtPrompt = this.buildPrompt();
        console.log(builtPrompt);
        this.props.onRunPrompt(builtPrompt);
    }

    updatePrompt(e){
        let data = this.state.data;
        data.prompt = e.target.value;
        this.setState(data);
    }

    updateSystem(e){
        let data = this.state.data;
        data.system = e.target.value;
        this.setState(data);
    }

    getPlaceholders(str) {
        const regex = /\{(.*?)\}/g;
        let match;
        const placeholders = [];
        
        while ((match = regex.exec(str)) != null) {
          placeholders.push(match[0], match[1]);
        }
        
        return placeholders;
    }

    updatePlaceholder(x){
        console.log("updatePlaceholder", x);
        const newOption = x.selectedOption
        
        let prompt = this.state.prompt;
        for (const k in prompt.variables){
            console.log(k, x.variableKey, k === x.variableKey);
            if (k === x.variableKey){
                prompt.variables[k].selectedOption = newOption;

            }
            
        }
        
        this.setState({prompt:prompt}, () => {
            console.log("updatePrompt", this.state.prompt);
        });

    }

    buildPrompt(){
        
        let words = this.state.prompt.text.split(/\s/);
        const regex = /\{(.*?)\}/g;

        let newWords = [];
        for (const i in words){
            const word = words[i];

        
            const match = regex.exec(word);
            if (match !== null){

                const v = this.state.prompt.variables[match[1]];
                const newValue = v.selectedOption.value;
                newWords.push(newValue);
                
            } else {
                newWords.push(word)
                
            }
        }

        const str = newWords.join(" ");

        return str;
    }

    renderPromptWithPlaceholders(str){

        let words = str.split(/\s/);
        const regex = /\{(.*?)\}/g;

        let prompt = words.map(function(word){
            const match = regex.exec(word);
            if (match !== null){

                const v = this.state.prompt.variables[match[1]];


                return (
                    
                    <span style={{maxWidth:100}}>
                    <ComboBox 
                        key={v.id}
                        promptId={this.state.prompt.id}
                        variableKey={match[1]}
                        updateValue={this.updatePlaceholder}
                        selectedOption={v.selectedOption}
                        options={v.options}
                    
                    />
                    </span>
                    
                )
            } else {
                return (
                    <span className=''> {word+" "}</span>
                )
            }
        }.bind(this))

        return <div>{prompt}</div>
    }

    render(){

        let promptLib = this.renderPromptWithPlaceholders(this.state.prompt.text);

        return (
            <div className='bg-body-tertiary'>
                
                
                <div className='card bg-body-tertiary border-primary mb-3'>
                
                <div className='card-body'>
                {promptLib}
                </div>
                
                {/* <hr></hr>
                <p>{this.state.prompt.system}</p> */}


                {/* <h5 className='text-light'>System</h5>
                <textarea
                    className="form-control" 
                    
                    rows="3"
                    value={this.props.system ? this.props.system : "You are a helpful AI assistant"}
                    onChange={this.updateSystem}
                ></textarea> */}

                <hr></hr>
                <div className='row'>
                    <div className='col-sm-3'></div>
                    <div className='col-sm-6'>
                        <button 
                        style={{width:"100%"}}
                        onClick={this.runPrompt}
                        className='btn btn-outline-success'>Use Prompt</button>
                    </div>
                    </div>
                    <div className='col-sm-3'></div>
                </div>
                
            </div>
        )
    }


}

export default withRouter(PromptTemplate);