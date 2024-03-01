import react from "react"
import 'animate.css';

import { withRouter } from './utils.jsx';
import Api from "./api.js";

import PromptTemplate from "./PromptTemplate.jsx";



const defaultPrompt = {
    id:1,
    prompt:"Summarize the {art_movement} art movement and its impact on art and culture",
    system:"You are a helpful AI assistant",
    variables:{
        art_movement:{
            id:1,
            options:[
                { 
                    id:1,
                    "value":"Renaissance", 
                    "label":"Renaissance"},
                { 
                    id:2,
                    "value":"Baroque", 
                    "label":"Baroque"
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


class PromptView extends react.Component {

    constructor(props){
        super(props);
        this.state = {
            email:"",
            password:"",
            api:new Api(),
            error:null,
            contentHeight:window.innerHeight,
            prompt:"",

            prompts:[],
            flows:[],

        }
        
        this.onRunPrompt = this.onRunPrompt.bind(this);
    }

    componentDidMount(){
        const routerParams = this.props.params;
        let category = "";
        let subcategory = "";
        if (routerParams.category){
            category = routerParams.category;
            if (routerParams.subcategory){
                subcategory = routerParams.subcategory;
            }
            this.onLoad(category, subcategory);
        } else {
            this.setState({loaded:true})
        }
        //console.log(this.state.prompt);
    }

    onRunPrompt(x){
        console.log("onRunPrompt", x);
        this.setState({prompt:x});
    }

    onEmailChange(e){
        this.setState({email:e.target.value});
    }

    onPasswordChange(e){
        this.setState({password:e.target.value});
    }

    gotoRegister(){
        //this.state.routeFunc("register");

    }

    async onLoad(category, subcategory){
        
        try {
            const data = await this.state.api.loadPromptViewCategory(category, subcategory);
            console.log(' load prompt category:', data);

            this.setState({
                flows:data.flows,
                prompts:data.prompts,
            })
            
        } catch (error) {
            console.error('Error prompt category:', error, error.response.data.Message);
            this.setState({"error":error.response.data.Message});
        }
    }

    renderFlows(){
        const flows = this.state.flows.map(function(f){
            const url = `/app/prompt-flow-chat/${f.id}`
            return (
               

                <div 
                className="card mb-3 nopad bg-primary text-light"
                key={f.id}
                >
                    <h3 className="text-light" >{f.name}</h3>
                    <p className="text-light">{f.description}</p>
                    <a className="text-light" href={url}>Test prompt flow</a>
                </div>
            )
        })
        return flows;
    }

    renderPrompts(){
        const prompts = this.state.prompts.map(function(p){
            return (
               
                <div 
                    className="card mb-3 nopad bg-primary"
                    key={p.id}
                    >
                    <PromptTemplate 
                        promptLibId={p.id}
                        //onRunPrompt={this.onRunPrompt}
                    />
                </div>

                // <div className="card mb-3 nopad bg-dark">
                // <h3 className="card-header"></h3>
                // <div className="card-body ">
                // <PromptTemplate 
                //     promptLibId={4}
                //     onRunPrompt={this.onRunPrompt}

                // />
                // </div>
                // <div className="card-footer">
                
                // </div>
                // </div>
            )
        })
        return prompts;
    }

    render(){

        let errorComponent = (<div></div>)
        if (this.state.error !== null){
            errorComponent = (<span className="text-danger">{this.state.error}</span>)
        }

        const routerParams = this.props.params;
        
        console.log(routerParams);
        
        const flows = this.renderFlows();

        const prompts = this.renderPrompts();

        return(

            <div className=" container-fluid bg-dark">
                
                <div className="row ">
                    <div className="col-sm-4"
                        style={{
                            height:window.innerHeight,
                            overflowY:"scroll",
                        }}
                    >
                        <h3 className="text-light">Flows</h3>
                       {flows}
                    
                    </div>
                    <div className="col-sm-4 main-content" 
                    style={{
                        height:window.innerHeight,
                        overflowY:"scroll",
                    }} >
                    <h3 className="text-light">prompts</h3>
                        {prompts}
                        
                    </div>
                    <div className="col-sm-4" >
                    <h3 className="text-light">Live Chat</h3>
                        
                    </div>
                </div>

            </div>
        )

    }
}

export default withRouter(PromptView);