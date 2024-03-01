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

        }
        this.onEmailChange = this.onEmailChange.bind(this);
        this.onPasswordChange = this.onPasswordChange.bind(this);
        this.submitLogin = this.submitLogin.bind(this);
        this.gotoRegister = this.gotoRegister.bind(this);
        this.onRunPrompt = this.onRunPrompt.bind(this);
    }

    componentDidMount(){
        const routerParams = this.props.params;
        if (routerParams.promptViewId){
            const viewId = parseInt(routerParams.promptViewId);
            this.onLoad(promptViewId);
        } else if (this.props.promptViewId) {
            const viewId = parseInt(this.props.promptViewId);
            this.onLoad(viewId);
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

    async submitLogin(){
        const payload = {"email":this.state.email, "password":this.state.password};
        try {
            const token = await this.state.api.login(payload);
            console.log('login:', token);
            window.location.href = "/";

            
        } catch (error) {
            console.error('Error submitLogin:', error, error.response.data.Message);
            this.setState({"error":error.response.data.Message});
        }
    }

    render(){

        let errorComponent = (<div></div>)
        if (this.state.error !== null){
            errorComponent = (<span className="text-danger">{this.state.error}</span>)
        }

        const routerParams = this.props.params;
        
        console.log(routerParams);
        


        return(

            <div className="container-fluid bg-dark">
                
                <div className="row ">
                    <div className="col-sm-4">
                        
                       
                    
                    </div>
                    <div className="col-sm-4 main-content" style={{minHeight:this.state.contentHeight}} >
                        
                        <div className="card mb-3 nopad bg-dark">
                        <h3 className="card-header"></h3>
                        <div className="card-body ">
                        <PromptTemplate 
                            promptLibId={4}
                            onRunPrompt={this.onRunPrompt}

                        />
                        </div>
                        <div className="card-footer">
                           
                        </div>
                        </div>
                    </div>
                    <div className="col-sm-4" >
                    <h3>{this.state.prompt}</h3>
                        
                    </div>
                </div>

            </div>
        )

    }
}

export default withRouter(PromptView);