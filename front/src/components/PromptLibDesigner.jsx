import React from 'react';

import Api from './api.js';

import { withRouter } from './utils.jsx';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import ComboBox from './ComboBox.jsx';
import SidebarItemList from './SidebarItemList.jsx';

class PromptLibDesigner extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            api:new Api(),
            sidebarLoaded:false,
            promptLibLoaded:false,
            
            //sidebar
            sidebarHeight:window.innerHeight,
            flows:[],

            id:null,
            name:"",
            description:"",
            category:"",
            subcategory:"",
            rawtext:"",
            system:"", //todo variables for system?

        }

        this.handleResize = this.handleResize.bind(this);
       
        this.onSave = this.onSave.bind(this);

        this.updateName = this.updateName.bind(this);
        this.updateCategory = this.updateCategory.bind(this);
        this.updateSubCategory = this.updateSubCategory.bind(this);
        this.onChangeDescription = this.onChangeDescription.bind(this);

        this.onChangeTextarea = this.onChangeTextarea.bind(this);
        this.onChangeSystem = this.onChangeSystem.bind(this);
       

        //sidebar actions
        this.loadSidebarItems = this.loadSidebarItems.bind(this);
        this.clickSidebarItem = this.clickSidebarItem.bind(this);
        

    }

    componentDidMount(){
    
        window.addEventListener('resize', this.handleResize);
        // const promptInputBox = document.getElementById("promptInputBox");
        // promptInputBox.addEventListener('keypress', function(e){
        //     if (e.key === 'Enter') {
        //         console.log("Enter pressed");
        //         this.handleWebsocketSendMessage();
        //     }
        // }.bind(this));
        // this.configureWebsocket();

        //load the sidebar items
        this.loadSidebarItems();

        const routerParams = this.props.params;
        
        console.log(routerParams);
        if (routerParams.promptLibId){
            const libId = parseInt(routerParams.promptLibId);
            this.onLoad(libId);
        } else {
            this.setState({promptLibLoaded:true})
        }
        //console.log(this.state.prompt);

    }


    updateName(e){
        this.setState({name:e.target.value});
    }

    updateCategory(x){
        //console.log("updateCategory", x.selectedOption.value);
        this.setState({category:x.selectedOption.value});
    }

    updateSubCategory(x){
        //console.log("updatesubcategory", x.selectedOption.value);
        this.setState({subcategory:x.selectedOption.value});
    }

    onChangeDescription(e){
        this.setState({description:e.target.value});
    }

    onChangeTextarea(e){
        this.setState({rawtext:e.target.value});
    }

    onChangeSystem(e){
        this.setState({system:e.target.value});
    }
    

    handleResize(){
        
        const innerHeight = window.innerHeight;
        //console.log("resize",innerHeight);
        this.setState({sidebarHeight:innerHeight})
    }

    
    async onSave(){
       
        let payload = {};
        if (this.state.rawtext){
            payload.rawtext = this.state.rawtext;
        }
        if (this.state.id){
            payload.id = this.state.id
        }
        if (this.state.name){
            payload.name = this.state.name;
        }
        if (this.state.description){
            payload.description = this.state.description;
        }
        if (this.state.category){
            payload.category = this.state.category;
        }
        if (this.state.subcategory) {
            payload.subcategory = this.state.subcategory;
        }
        if (this.state.system){
            payload.system = this.state.system;
        }

        console.log("onSave", payload);

        try {
            const data = await this.state.api.savePromptLib(payload);
            console.log('savePromptLib result:', data);
            
            //if we saved a new lib, navigate to the url
            const routerParams = this.props.params;
            if (!routerParams.promptLibId){
                window.location.href = `/app/prompt-lib-designer/${data.id}`;
            } else {
                let newState = {
                    loaded:true,
                    id:data.id,
                    name:data.name,
                    description:data.description,
                    category:data.category,
                    subcategory:data.subcategory,
                    variables:data.variables,
                    options:data.options,
                    system:data.system,
                }
    
                this.setState(newState)
            }
            
        } catch (error) {
            console.error('Error savePromptLib:', error);
            this.setState({"error":error.response.data.Message});
        }
    }

    async onLoad(promptLibId){
        console.log("onLoad");
        try {
            const data = await this.state.api.loadPromptLib(promptLibId);
            console.log('loadPromptLib:', data);
            //window.location.href = "/";

            let newState = {
                loaded:true,
                id:data.id,
                name:data.name,
                description:data.description,
                category:data.category,
                subcategory:data.subcategory,
                variables:data.variables,
                options:data.options,
                rawtext:data.rawtext,
                system:data.system,
                promptLibLoaded:true,
            }

            this.setState(newState)

            
        } catch (error) {
            console.error('Error loadPromptFlow:', error);
            this.setState({"error":error.response.data.Message});
        }
    }


    async loadSidebarItems(){

        try {
            const data = await this.state.api.loadPromptLibs();
            console.log('loadSidebarItems:', data);
            //window.location.href = "/";
            this.setState({
                flows:data.flows,
                sidebarFlowsLoaded:true,
            })

            
        } catch (error) {
            console.error('Error loadSidebarItems:', error);
            //this.setState({"error":error.response.data.Message});
        }
    }

    clickSidebarItem(item){
        console.log("clickSidebarItem", item);
        window.location.href = `/app/promptdesigner/${item.id}`;
    }


    render(){

        const routerParams = this.props.params;
        
        //console.log(routerParams);
        //console.log(this.state.prompt);

       
        //console.log("state.network", this.state.network);

        if (!this.state.promptLibLoaded){
            return (<div 
                    className='container-fluid bg-primary'
                    style={{height:window.innerHeight}}
                    >Loading...</div>)
        }

        let category = {}
        if (this.state.category){
            category = {label:this.state.category, value:this.state.category}
        }

        let subcategory = {}
        if (this.state.subcategory){
            subcategory = {label:this.state.subcategory, value:this.state.subcategory}
        }

        let testButton = (<div></div>)
        if (routerParams.promptLibId){
            const url = `/app/prompt-lib/${routerParams.promptLibId}`
            testButton = (<a className='btn btn-outline-success'
            style={{width:"100%"}}
            href={url}
        >Test Prompt Lib</a>)
        }

        return (
            <div className='container-fluid'>
                <div className='row'>
                    <div className='col-sm-2 bg-primary nomargin'
                        style={{
                            height:this.state.sidebarHeight,
                            overflowY:"scroll",
                        }}
                    >
                        <div
                           
                            >
                                <hr></hr>
                            
                        </div>
                      
                    </div>
                    <div className='col-sm-5 bg-dark nomargin'>

                       
                            
                        <div
                            style={{
                                height:this.state.sidebarHeight-166,
                                width:"100%",
                            }}
                        >
                            <div className="form-group row">



                                <label className="col-sm-4 col-form-label text-light">Name: </label>
                                <div className="col-sm-8 " style={{padding:10}}>
                                    <input type="text" value={this.state.name} className="form-control-plaintext bg-light" 
                                        onChange={this.updateName}
                                    /> 
                                </div>

                                
                                <label className="col-sm-4 col-form-label text-light">Category: </label>
                                <div className="col-sm-8">
                                    <ComboBox 
                                        selectedOption={category}
                                        updateValue={this.updateCategory}
                                    />
                                </div>
                                <label for="staticEmail" className="col-sm-4 col-form-label text-light">Subcategory: </label>
                                <div className="col-sm-8">
                                    <ComboBox 
                                        selectedOption={subcategory}
                                        updateValue={this.updateSubCategory}
                                    />
                                </div>

                                
                                <label className="col-sm-4 col-form-label text-light">Description: </label>
                                <div className="col-sm-8">
                                <textarea
                                    style={{
                                        width:"100%",
                                    }}
                                    value={this.state.description}
                                    onChange={this.onChangeDescription}
                                    rows={2}
                                />
                                </div>
                                
                            </div>
                            
                            <hr></hr>
                            <h3 className='text-light'>Prompt: </h3>
                            <textarea
                                style={{
                                    width:"100%",
                                }}
                                value={this.state.rawtext}
                                onChange={this.onChangeTextarea}
                                rows={5}
                            />

                            <hr></hr>
                            <h3 className='text-light'>System: </h3>
                            <textarea
                                style={{
                                    width:"100%",
                                }}
                                value={this.state.system}
                                onChange={this.onChangeSystem}
                                rows={5}
                            />
                            <hr></hr>
                            <div className='row'>
                                <div className='col-sm-3'></div>
                                <div className='col-sm-6'>
                                    <div className='btn btn-outline-success'
                                        style={{width:"100%"}}
                                        onClick={this.onSave}
                                    >Save</div>

                                </div>
                                <div className='col-sm-3'>

                                </div>
                                
                            </div>
                        </div>
                    </div>

                    
                    <div className='col-sm-5 bg-primary nomargin'>
                    <hr></hr>
                        {testButton}
                        <hr></hr>
                        
                    </div>



                    
                </div>
                
            </div>
        )
    }

}

export default withRouter(PromptLibDesigner);