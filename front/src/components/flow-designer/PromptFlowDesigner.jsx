import React from 'react';

import Api from '../api.js';

import { withRouter } from '../utils.jsx';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:

import ReactFlow, {
    addEdge,
    MiniMap,
    Controls,
    Background,
    useNodesState,
    useEdgesState,
  } from 'reactflow';


import PromptNodeEditor from "./PromptNodeEditor.jsx"
import VariableNodeEditor from './variableNodeEditor.jsx';
import TextInputNodeEditor from './TextInputNodeEditor.jsx';
import FinishNodeEditor from './FinishNodeEditor.jsx';
import StartNodeEditor from './StartNodeEditor.jsx';
import ContinueNodeEditor from './ContinueNodeEditor.jsx';
import NumericDecisionNodeEditor from './numericDecisionNodeEditor.jsx';
import ParseNodeEditor from './parseNodeEditor.jsx';
import PersonalizeNodeEditor from './personalizeNodeEditor.jsx';
import PdfNodeEditor from './PdfNodeEditor.jsx';
import SidebarItemList from '../SidebarItemList.jsx';
import DisplayTextNodeEditor from './DisplayTextNodeEditor.jsx';

import DnDFlow from './DndFlow.jsx';
import ComboBox from '../ComboBox.jsx';

class PromptFlowDesigner extends React.Component {

    constructor(props){
        super(props);
        this.state = {
            api:new Api(),
            sidebarFlowsLoaded:false,
            promptFlowLoaded:false,
            
            //sidebar
            sidebarHeight:window.innerHeight,
            flows:[],

            //view
            currentView:"standard", //standard, expand-right-column

            //prompt designer
            currentNode:null,
            
            id:null,
            name:"",
            description:"",
            category:"",
            subcategory:"",
            network: {
                nodes:[],
                edges:[],
            },
            node_data:{},
            version:2,

            
        }


        this.handleResize = this.handleResize.bind(this);
        this.nodeClick = this.nodeClick.bind(this);
        this.updateNodeData = this.updateNodeData.bind(this);
        this.onSave = this.onSave.bind(this);

        this.updateName = this.updateName.bind(this);
        this.updateCategory = this.updateCategory.bind(this);
        this.updateSubCategory = this.updateSubCategory.bind(this);
        this.onChangeDescription = this.onChangeDescription.bind(this);
        this.getNodeId = this.getNodeId.bind(this);
        this.updateFlow = this.updateFlow.bind(this);

        //sidebar actions
        this.loadSidebarItems = this.loadSidebarItems.bind(this);
        this.clickSidebarItem = this.clickSidebarItem.bind(this);

        this.expandView = this.expandView.bind(this);
        this.showTitleEditor = this.showTitleEditor.bind(this);
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
        if (routerParams.promptFlowId){
            const flowId = parseInt(routerParams.promptFlowId);
            this.onLoad(flowId);
        } else {
            this.setState({promptFlowLoaded:true})
        }
        //console.log(this.state.prompt);

    }

    showTitleEditor(){
        //set current node to none, and title editor will render
        this.setState({currentNode:null});
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

    initialNetwork(){
        return this.state.network;
    }

    getNodeId(){
        
        //const i =  this.state.network.nodes.length+1;
        const nodeId = `node_${Date.now()}`
        //console.log("getNodeId", nodeId);
        //console.log("currentNodes",  this.state.network.nodes);
        return nodeId
    }

    expandView(){
        
        const currentView = this.state.currentView;
        console.log("expand", currentView);
        if (currentView === "standard"){
            this.setState({currentView:"expand-right-column"});
        } else {
            this.setState({currentView:"standard"});
        }
    }
    

    handleResize(){
        
        const innerHeight = window.innerHeight;
        //console.log("resize",innerHeight);
        this.setState({sidebarHeight:innerHeight})
    }

    nodeClick(e, node){
        //console.log("nodeClick", node);
        this.setState({currentNode:node});
    }

    updateFlow(g){
        //console.log("updateFlow", g);
        this.setState({network:g})
    }

    async onSave(g){
        const node_data = this.state.node_data;
        const payload = {
            node_data:node_data,
            network:g,
        }
        const d = {
            id: this.state.id,
            name: this.state.name,
            description: this.state.description,
            category: this.state.category,
            subcategory: this.state.subcategory,
            payload: payload,
            version:this.state.version,
        }
        console.log("onSave", d);

        if (this.state.version === 1){
            //todo save version 1
            alert("Save version 1")
        } else if (this.state.version === 2) {
            try {
                const data = await this.state.api.savePromptFlow(d);
                console.log('savePromptFlow:', data);
                
                //Note this refresh can be disabled for debugging
                const routerParams = this.props.params;
                if (!routerParams.promptFlowId){
                    window.location.href = `/app/prompt-flow-designer/${data.id}`;
                } 
                //Note this refresh can be disabled for debugging
                window.location.href = `/app/prompt-flow-designer/${data.id}`;
                
    
                // let newState = {
                //     id:data.id,
                //     name:data.name,
                //     description:data.description,
                //     category: data.category,
                //     subcategory: data.subcategory,
    
                // };
    
                // if (data.payload.network){
                //     newState.network = data.payload.network;
                // }
    
                // if (data.payload.node_data){
                //     newState.node_data = data.payload.node_data;
                // }
                
                // this.setState(newState);
                
                //redirect
    
                
            } catch (error) {
                console.error('Error savePromptFlow:', error);
                this.setState({"error":error.response.data.Message});
            }
        }

        
    }

    async onLoad(flowId){
        try {
            const data = await this.state.api.loadPromptFlow(flowId);
            console.log('loadPromptFlow:', data);
            //window.location.href = "/";

            let newState = {
                loaded:true,
                id:data.id,
                name:data.name,
                description:data.description,
                category:data.category,
                subcategory:data.subcategory,
                promptFlowLoaded:true,
                version:data.version,
            }

            if (data.payload.network){
                console.log("assigning network", data.payload.network);
                newState.network = data.payload.network;
            }

            if (data.payload.node_data){
                newState.node_data = data.payload.node_data;
            }

            this.setState(newState)

            
        } catch (error) {
            console.error('Error loadPromptFlow:', error);
            this.setState({"error":error.response.data.Message});
        }
    }

    async loadSidebarItems(){

        try {
            const data = await this.state.api.loadPromptFlows();
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


    renderEditor(n){
        
        let data = {};
        //console.log(n.id, this.state.node_data, n.id in this.state.node_data);
        if (n.id in this.state.node_data){
            
            data = this.state.node_data[n.id];
            //console.log("data in nodeData", data);
        }


        switch(n.data.label){

            case "start":
                return <StartNodeEditor
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}
                    {...data}

                />
            
            case "prompt":
                return <PromptNodeEditor 
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}

                   
                />
            case "variable":
                return <VariableNodeEditor 
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}
                />
            case "pdf":
                return <PdfNodeEditor 
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}
                />
            case "question":
                return <TextInputNodeEditor 
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}
                />
            case "text_input":
                return <TextInputNodeEditor 
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}
                />
            case "finish":
                return <FinishNodeEditor 
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}
                />
            case "loop":
                return <ContinueNodeEditor 
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}
                />
            case "parse":
                return <ParseNodeEditor
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}
                />
            case "binary_numeric_decision":
                return <NumericDecisionNodeEditor
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}
                />
            case "personalize":
                return <PersonalizeNodeEditor
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}

                />
            case "display_text":
                return <DisplayTextNodeEditor
                    key={n.id}
                    id={n.id}
                    updateNodeData={this.updateNodeData}

                    {...data}

                />
            default:
                console.log(`Prompt Flow Editor not defined for: ${n.data.label}`)
                return <div></div>
        }
       
    }

    updateNodeData(d){
        //console.log("updateNodeData", d);
        let node_data = this.state.node_data;
        node_data[d.id] = d;
        //console.log("updateNodeData", nodeData);
        this.setState({node_data:node_data});
    }

    
    clickSidebarItem(item){
        console.log("clickSidebarItem", item);
        window.location.href = `/app/prompt-flow-designer/${item.id}`;
    }


    render(){

        const routerParams = this.props.params;
        
        //console.log(routerParams);
        //console.log(this.state.prompt);

        

        if (this.state.promptFlowLoaded === false){
            return (<div 
                className='container-fluid bg-primary'
                style={{
                height:this.state.sidebarHeight,
                overflowY:"scroll",
            }} >Loading...</div>)
        }

        let category = {}
        if (this.state.category){
            category = {label:this.state.category, value:this.state.category}
        }

        let subcategory = {}
        if (this.state.subcategory){
            subcategory = {label:this.state.subcategory, value:this.state.subcategory}
        }

        let editor = (<div className='form-inline'>
            <label className="col-sm-4 col-form-label text-light">Name: </label>
            <div className="col-sm-8 ">
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
            <label htmlFor="staticEmail" className="col-sm-4 col-form-label text-light">Subcategory: </label>
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

        </div>);

        let sidebar = (<div></div>)
        if (this.state.sidebarFlowsLoaded === true){
            let currentFlow = {id:null, title:null}
            if (this.state.id){
                currentFlow.id = this.state.id;
                currentFlow.title = this.state.name;
            }
            sidebar = (<SidebarItemList 
                items={this.state.flows}
                onClickItem={this.clickSidebarItem}
                selectedItem={currentFlow}
                />)
        }
        
        if (this.state.currentNode){
            //console.log("currentNode", this.state.currentNode);
            
            editor = this.renderEditor(this.state.currentNode);
        }

        let test_prompt_flow_button = (<div></div>);
        if (routerParams.promptFlowId){
            let url_test = `/app/prompt-flow-chat/${routerParams.promptFlowId}`; //default is version 2
            if (this.state.version === 1){
                url_test = `/app/prompt-chat/${routerParams.promptFlowId}`;   
            }

            test_prompt_flow_button = (<a 
                href={url_test} 
                className='btn btn-outline-success'
                target="_blank"
                >Test Prompt Flow</a>)
            

            
        }

        //console.log("state.network", this.state.network);

        //expand right column logic
        let leftColCls = "col-sm-8 bg-dark nomargin nopad";
        let rightColCls = "col-sm-4 bg-primary nomargin";
        let expandButtonText = "expand right column";
        if (this.state.currentView === "expand-right-column"){
            leftColCls = "col-sm-4 bg-dark nomargin nopad";
            rightColCls = "col-sm-8 bg-primary nomargin";
            expandButtonText = "Reduce right column"
        }


        return (
            <div className='container-fluid'>
                <div className='row'>
                    
                    <div className={leftColCls}
                    
                        style={{
                            height:this.state.sidebarHeight,
                           
                        }}
                    >
                
                        <div className='bg-primary nomargin' style={{padding:10}}>
                            <ol className="breadcrumb">
                                <li className="breadcrumb-item "><a className="text-light" href="/app/flow-dashboard">Prompt Flows</a></li>
                                <li className="breadcrumb-item active "><span >v2</span></li>
                                <li 
                                    style={{cursor:"pointer"}}
                                    onClick={this.showTitleEditor}
                                    className="breadcrumb-item active"><span className="text-light" >{this.state.name}</span></li>
                            </ol>
                        </div>

                       
                            
                        <div
                            style={{
                                height:this.state.sidebarHeight-250,
                                width:"100%",
                            }}
                        >
                           
                            
                            <hr></hr>
                            
                            <DnDFlow
                                getId={this.getNodeId}
                                
                                network={this.state.network}
                                onNodeClick={this.nodeClick}
                                onSave={this.onSave}
                                updateFlow={this.updateFlow}
                            />
                        </div>
                    </div>

                    
                    <div className={rightColCls}>
                            <button onClick={this.expandView} className='btn btn-primary'>{expandButtonText}</button>
                    <hr></hr>

                        {test_prompt_flow_button}
                        <hr></hr>
                        {editor}
                    </div>
                </div>
            </div>
        )
    }

}

export default withRouter(PromptFlowDesigner);