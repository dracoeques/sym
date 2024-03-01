import React from 'react';

import Api from './api.js';


import { withRouter } from './utils.jsx';



import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:


class PromptFlowDashboard extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        api:new Api(),
        sidebarHeight:window.innerHeight,
        flows: [
          { title: 'Flow1', category: 'Cat1', subcategory: 'Subcat1', description: 'Description for Flow1' },
          { title: 'Flow2', category: 'Cat2', subcategory: 'Subcat2', description: 'Description for Flow2' },
          // ... add more flows as required
        ],
        searchTerm: '',
      };

      this.loadFlows = this.loadFlows.bind(this);

    }

    componentDidMount(){
        this.loadFlows();
    }
  
    handleSearch = (event) => {
      this.setState({ searchTerm: event.target.value });
    }

    async loadFlows(){

        try {
            const data = await this.state.api.loadPromptFlows();
            console.log('loadFlows:', data);
            //window.location.href = "/";
            this.setState({
                flows:data.flows,
                sidebarFlowsLoaded:true,
            })

            
        } catch (error) {
            console.error('Error loadFlows:', error);
            //this.setState({"error":error.response.data.Message});
        }
    }

    handleClick(flow) {
       
        console.log("click flow", flow);
        if (flow.version === 1){
            //TODO: go to version 1 editor
            window.location.href = `/app/prompt-flow-designer1/${flow.id}`;
        } else if (flow.version === 2){
            window.location.href = `/app/prompt-flow-designer/${flow.id}`;
        }   
        //window.location.href = `/app/prompt-flow-designer/${flow.id}`;
    
    }
  
    render() {
      const filteredFlows = this.state.flows.filter(flow =>
        flow.title.toLowerCase().includes(this.state.searchTerm.toLowerCase())
      );

      let flows = filteredFlows.map((flow, index) => (
        <tr key={index}
            style={{cursor:"pointer"}}
            onClick={() => this.handleClick(flow)}
        >
          <td>{flow.title}</td>
          <td>{flow.category}</td>
          <td>{flow.subcategory}</td>
          <td>{flow.description}</td>
          <td>{flow.version}</td>
        </tr>
      ))
  
      return (
        <div className="bg-primary"
            style={{height:window.innerHeight}}
        >
            <div className='container'>
                <br></br>
            <h1 className='text-light'>Prompt Flows</h1>
            <button 
                style={{marginRight:10}}
                onClick={()=>{window.location = "/app/prompt-flow-designer1"}}
                className='btn btn-outline-success'>New Prompt Flow v1</button>
            
            <button 
                onClick={()=>{window.location = "/app/prompt-flow-designer"}}
                className='btn btn-outline-success'>New Prompt Flow v2</button>
            
            <hr></hr>
          <input
            type="text"
            className="form-control mb-3"
            placeholder="Search by name..."
            value={this.state.searchTerm}
            onChange={this.handleSearch}
          />
          <hr></hr>
          <div
            style={{height:600, overflowY:"auto"}}
          >
          <table className="table table-dark table-striped table-hover"
           
          >
            <thead
              
            >
              <tr>
                <th>Name</th>
                <th>Category</th>
                <th>Subcategory</th>
                <th>Description</th>
                <th>Version</th>
              </tr>
            </thead>
            <tbody
                 
            >
           
              {flows}
              
            </tbody>
          </table>
          </div>
          </div>
        </div>
      );
    }
  }


export default withRouter(PromptFlowDashboard);