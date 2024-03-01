import React from 'react';

import Api from './api.js';


import { withRouter } from './utils.jsx';

import ReactMarkdown from 'react-markdown'


import 'bootswatch/dist/lux/bootstrap.min.css'; // Added this :boom:


class PersonalKV extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        api:new Api(),
        sidebarHeight:window.innerHeight,
        loaded:false,
        datums: [
            // {"id":1, "key":"hello", "value":"world", "liked":null},
            // {"id":2, "key":"Favorite cuisine", "value":"French", "liked":null}
        ],
        searchTerm: '',
        context: null,
        topic: null,
        context_response: 'This is your personalized recommendation system',
        
      };
      this.updateSearch = this.updateSearch.bind(this);
      this.doSearch = this.doSearch.bind(this);
      this.doVote = this.doVote.bind(this);
    }

    componentDidMount(){
        //this.loadProfiles();
    }
  
    updateSearch = (event) => {
      this.setState({ searchTerm: event.target.value });
    }

    async doVote(id_datum, liked){
        console.log(id_datum, liked);
        let datums = this.state.datums;
        for (const i in datums){
            const datum = datums[i];
            if (datum.id === id_datum){
                datums[i].liked = liked;
                break
            }
        }
        this.setState({datums:datums});

        //now send upvote data to api
        const payload = {
            "id_profile_datum":id_datum,
            "id_text":this.state.context.id,
            "liked":liked,
        }
        
        try {
            const data = await this.state.api.votePersonalKV(payload);
            console.log('votePersonalKV:', data);
            //window.location.href = "/";
            // this.setState({
            //     topic:data.topic,
            //     datums:data.profile_datums,
            //     context: data.context,
            // })

            
        } catch (error) {
            console.error('Error votePersonalKV:', error);
            //this.setState({"error":error.response.data.Message});
        }
    }

    async doSearch(){

        console.log(this.state.searchTerm);

        try {
            const data = await this.state.api.doPersonalKVSearch(this.state.searchTerm);
            console.log('doPersonalKVSearch:', data);
            //window.location.href = "/";
            this.setState({
                topic:data.topic,
                all_datums:data.profile_datums,
                datums:data.evaluator_datums,
                context: data.context,
                context_response: data.context_response,
            })

            
        } catch (error) {
            console.error('Error doPersonalKVSearch:', error);
            //this.setState({"error":error.response.data.Message});
        }
    }

  
    render() {
    //   const filteredFlows = this.state.flows.filter(flow =>
    //     flow.title.toLowerCase().includes(this.state.searchTerm.toLowerCase())
    //   );

      let datums = this.state.datums.map(function(p, index) {

        let rowCls = ""
        if (p.liked === true){
            rowCls = "table-success"
        } else if (p.liked === false){
            rowCls = "table-danger"
        }

        return (
            <tr key={p.id}
            className={rowCls}
           
        >
          
          <td>{p.key}</td>
          <td>{p.value}</td>
          <td><button 
            className='btn btn-primary'
            onClick={() => this.doVote(p.id, true)} >👍</button></td>
          <td><button 
            className='btn btn-primary'
            onClick={() => this.doVote(p.id, false)} >👎</button></td>
          
          
          
        </tr>
        )
      }.bind(this))
   
  
      return (
        <div className="bg-primary"
            style={{height:window.innerHeight}}
        >
            <div className='container'>
                <br></br>
            <h1 className='text-light'>Personalized Key Values</h1>
            
            <hr></hr>
            <input
                type="text"
                className="form-control mb-3"
                placeholder="Type your task..."
                value={this.state.searchTerm}
                onChange={this.updateSearch}
                />
            <button 
                onClick={this.doSearch}
                className='btn btn-outline-success'>Search</button>
            
          <hr></hr>
          <div
            style={{height:600, overflowY:"auto"}}
          >
          <table className="table table-dark table-striped table-hover"
           
          >
            <thead
              
            >
              <tr>
                <th>Key</th>
                <th>Value</th>
                
                <th>Up</th>
                <th>Down</th>
                
                
                
              </tr>
            </thead>
            <tbody
                 
            >
           
              {datums}
              
            </tbody>
          </table>

          <hr></hr>
          <ReactMarkdown  className='text-light' children={this.state.context_response}></ReactMarkdown>
          
          </div>
          </div>
        </div>
      );
    }
  }


export default withRouter(PersonalKV);