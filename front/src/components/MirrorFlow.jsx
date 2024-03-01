import React from 'react';

import Api from './api.js';

import { withRouter } from './utils.jsx';

import ReactMarkdown from 'react-markdown'

import PromptFlowChat from './PromptFlowChat';


import * as amplitude from '@amplitude/analytics-browser';

import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:


class MirrorFlow extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        api:new Api(),
        sidebarHeight:window.innerHeight,
        loaded:false,
        searchTerm: '',
        context: null,
        topic: null,
        context_response: 'This is your personalized recommendation system',
        profile: {},

        flowObj:(<div>Loading...</div>),

        currentFlow:"",
        flowOrder:["values", "personality", "interests", "opportunity", "mirror"],

        flows:{
            "values":{
                flowId:201, //162
                runId:null,
                completed:false,
            },
            "interests":{
                flowId:200, //163
                runId:null,
                completed:false,
            },
            "personality":{
                flowId: 196, //196, //164
                runId:null,
                completed:false,
            },
            "opportunity":{
                flowId:202,
                runId:null,
                completed:false,
            },
            "mirror":{
                flowId:168,
                runId:null,
                completed:false,
            }
        },
        

      };
      
      this.changeFlow = this.changeFlow.bind(this);
      this.flowFinished = this.flowFinished.bind(this);
      this.getNextFlow = this.getNextFlow.bind(this);
      this.renderFlowSidebar = this.renderFlowSidebar.bind(this);

      this.getFlowStatus = this.getFlowStatus.bind(this);
      this.startKVETL = this.startKVETL.bind(this);
    }

    componentDidMount(){
        //this.loadProfiles();
        amplitude.track('Mirror Flow Test');

        this.init()
    }

    init(){
        this.getMe().then(profile => {
            this.setState({profile:profile})
        })

        this.getFlowStatus().then(status => {
            this.setState({flows:status}, () =>{
                this.getNextFlow();
            });
            
        })
    }

    async getMe(){
        try {
            const response = await this.state.api.me()
            console.log(response);
            return response
        } catch (error) {
            console.error("Error fetching data:", error);
            return {};
        }
    }

    async getFlowStatus(){
        try {
            //payload of flow ids, and whether it has been completed
            const response = await this.state.api.getFlowStatus(this.state.flows);
            console.log("Get flow response", response);
            return response; 
        } catch (error) {
            console.error("Error fetching data:", error);
            return {};
        }
    }

    async startKVETL(){

        this.state.api.runKVETL()
            .then(response => {
                console.log("KVETL", response);
                // Process the response here if needed
            })
            .catch(error => {
                console.error("Error fetching data:", error);
            });
    }
  
    changeFlow(flow){
        console.log("changing to flow", flow);
        
        //this.setState({currentFlow:flow});
    }

    getNextFlow(){
        let newCurrentFlow = null;
        for (const i in this.state.flowOrder){
            const flowName = this.state.flowOrder[i];
            const flowFinished = this.state.flows[flowName].completed;
            if (flowFinished !== true){
                newCurrentFlow = flowName;
                break
            }
        }

        this.setState({currentFlow:newCurrentFlow});

        //TODO:
        //what to do if all flows have been finished
        //first project

    }

    flowFinished(flow){
        console.log("flow finished", flow);
        //finish the flow, move to the next flow in the list
        let flows = this.state.flows;
        flows[this.state.currentFlow].completed = true;

        
        //parse any key values
        this.startKVETL();

        //now move to next flow in the list
        this.getNextFlow();

    }

    createFlow(flowId){
        console.log("CreateFlow", flowId);
        return (<PromptFlowChat 
            key={flowId}
            height={this.state.innerHeight - 100}
            promptFlowId={flowId}
            doResize={false}
            finishCallback={this.flowFinished}
           
        />)
    }

    renderFlowSidebarItem(){

    }

    renderFlowSidebar(){

        let flowNiceName = {}

        
        let sidebarItems = this.state.flowOrder.map(function(flowName){
            const flowData = this.state.flows[flowName];
            console.log(flowData);

            return (
                <div className="form-check"
                        
                        onClick={() => this.changeFlow("values")}
                    >
                        <input className="form-check-input" type="checkbox" id="flexCheckDefault" 
                            checked={this.state.flows["values"].completed}
                        />
                        <label 
                            style={{cursor:"pointer"}}
                            className="form-check-label" for="flexCheckDefault">
                        Core Values
                        </label>
                    </div>
            )

        }.bind(this))



        return (
            <fieldset className="form-group">
                        <legend className="mt-4">Getting to know you</legend>
                        <div className="form-check"
                            
                            onClick={() => this.changeFlow("values")}
                        >
                            <input className="form-check-input" type="checkbox" id="flexCheckDefault" 
                                checked={this.state.flows["values"].completed}
                            />
                            <label 
                                style={{cursor:"pointer"}}
                                className="form-check-label" for="flexCheckDefault">
                            Core Values
                            </label>
                        </div>
                        <div className="form-check"
                            onClick={() => this.changeFlow("personality")}
                        >
                            <input 
                                checked={this.state.flows["personality"].completed}
                                className="form-check-input" type="checkbox" value="" id="flexCheckChecked"  />
                            <label 
                                style={{cursor:"pointer"}}
                                className="form-check-label" for="flexCheckChecked">
                            Personality
                            </label>
                        </div>

                        <div className="form-check"
                            onClick={() => this.changeFlow("interests")}
                        >
                            <input 
                                checked={this.state.flows["interests"].completed}
                                className="form-check-input" type="checkbox" value="" id="flexCheckChecked"  />
                            <label 
                                style={{cursor:"pointer"}}
                                className="form-check-label" for="flexCheckChecked">
                            Interests
                            </label>
                        </div>
                        <div className="form-check"
                            onClick={() => this.changeFlow("opportunity")}
                        >
                            <input 
                                checked={this.state.flows["opportunity"].completed}
                                className="form-check-input" type="checkbox" value="" id="flexCheckChecked"  />
                            <label 
                                style={{cursor:"pointer"}}
                                className="form-check-label" for="flexCheckChecked">
                            Opportunities and goals
                            </label>
                        </div>
                        <div className="form-check"
                            onClick={() => this.changeFlow("values")}
                        >
                            <input className="form-check-input" type="checkbox" value="" id="flexCheckChecked"  />
                            <label 
                                style={{cursor:"pointer"}}
                                className="form-check-label" for="flexCheckChecked">
                            Mirror
                            </label>
                        </div>
                    </fieldset>
        )
    }
  
    render() {

        let flow = (<div>Loading...</div>);
        if (this.state.currentFlow){
            let currentFlowId = this.state.flows[this.state.currentFlow].flowId;
            console.log("Currentflowid", currentFlowId);
            
            if (currentFlowId){
                flow = this.createFlow(currentFlowId);
            }
        }

        let flowSidebar = this.renderFlowSidebar();


        return (
        <div className="bg-light"
            style={{height:window.innerHeight}}
        >
            <div className='container nopad nomargin'>

            <div className='row'>
                <div className='col-sm-4 bg-body-tertiary' style={{height:window.innerHeight, padding:40}}>
                    <div style={{
                        width:"100%",
                        height: 77,
                        borderRadius: 16,
                        padding:25,
                        backgroundColor: "#98A2B3"}}>
                        <div className='row'>
                            <div className='col-sm-10'>
                                <span>{this.state.profile.email}</span>
                            </div>
                            <div className='col-sm-2'>
                                <span>Icon</span>
                            </div>
                        </div>
                    </div>
                    <hr></hr>
                    
                    {flowSidebar}

                </div>
                <div className='col-sm-8'>
                    <span className='' style={{backgroundColor:"purple", padding:10, borderRadius: 10}}><img src="https://sym-public-assets.s3.us-west-2.amazonaws.com/icons/zap.svg"></img></span>
                    {flow}
                </div>
            </div>
                <br></br>
            
            
            
          
          </div>
        </div>
      );
    }
  }


export default withRouter(MirrorFlow);