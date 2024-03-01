import React from 'react';

import Api from './api.js';


import { withRouter } from './utils.jsx';



import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:


class ProfileManager extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        api:new Api(),
        sidebarHeight:window.innerHeight,
        loaded:false,
        profiles: [],
        activeProfile:null,
        
      };

      this.loadProfiles = this.loadProfiles.bind(this);
      this.setProfileActive = this.setProfileActive.bind(this);
    }

    componentDidMount(){
        this.loadProfiles();
    }
  
    handleSearch = (event) => {
      this.setState({ searchTerm: event.target.value });
    }

    async loadProfiles(){

        try {
            const data = await this.state.api.loadProfiles();
            console.log('loadProfiles:', data);
            //window.location.href = "/";
            this.setState({
                profiles:data.profiles,
                loaded:true,
            })

            
        } catch (error) {
            console.error('Error loadProfiles:', error);
            //this.setState({"error":error.response.data.Message});
        }
    }

    setProfileActive(profile){

    }
    
  
    render() {
    //   const filteredFlows = this.state.flows.filter(flow =>
    //     flow.title.toLowerCase().includes(this.state.searchTerm.toLowerCase())
    //   );

      let profiles = this.state.profiles.map((p, index) => (
        <tr key={p.id}
            style={{cursor:"pointer"}}
            onClick={() => this.setProfileActive(flow)}
        >
          <td>{p.id}</td>
          <td>{p.name}</td>
          <td>{p.description}</td>
          <td>active</td>
          
          
          
        </tr>
      ))
  
      return (
        <div className="bg-primary"
            style={{height:window.innerHeight}}
        >
            <div className='container'>
                <br></br>
            <h1 className='text-light'>Profiles</h1>
            
            <hr></hr>
          
          <hr></hr>
          <div
            style={{height:600, overflowY:"auto"}}
          >
          <table className="table table-dark table-striped table-hover"
           
          >
            <thead
              
            >
              <tr>
                <th>ID</th>
                <th>Name</th>
                
                <th>Description</th>
                <th>Active Profile</th>
                
                
                
              </tr>
            </thead>
            <tbody
                 
            >
           
              {profiles}
              
            </tbody>
          </table>
          </div>
          </div>
        </div>
      );
    }
  }


export default withRouter(ProfileManager);