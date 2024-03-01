import React from 'react';

import Api from './api.js';


import { withRouter } from './utils.jsx';



import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:



class Dashboard extends React.Component {

  constructor(props){
    super(props);
    this.state = {
      api:new Api(),
      sidebarHeight:window.innerHeight,

    }
  }

  render(){

    return (
      
      <div className='container-fluid'>
          <div className='row'>
              <div className='col-sm-2 bg-primary nomargin'
                  style={{
                      height:this.state.sidebarHeight,
                      overflowY:"scroll",
                  }}
              >
                  <div>
                      
                          <hr></hr>
                     
                  </div>
                
              </div>
              <div className='col-sm-10 bg-dark nomargin'>

                
              </div>
        </div>
      </div>
    )
  }

}


export default withRouter(Dashboard);